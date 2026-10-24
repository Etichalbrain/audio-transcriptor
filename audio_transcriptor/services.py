from __future__ import annotations

import json
import re
import threading
from pathlib import Path

from audio_transcriptor.models import TranscriptionResult, TranscriptSegment, TranslationResult


TRANSLATION_BATCH_SIZE = 20

TRANSLATION_SYSTEM_PROMPT = (
    "You translate Italian interview transcripts into natural, faithful English. "
    "Keep names, numbers and technical terms unchanged. "
    "You receive a JSON object with the segments to translate. "
    'Answer with JSON only, in this exact shape: {"translations": ["...", "..."]} '
    "with exactly one string per input segment, in the same order, no explanations."
)

SINGLE_SEGMENT_PROMPT = (
    "Translate the Italian transcript segment into natural, faithful English. "
    "Return only the translated text. Preserve names and meaning."
)


def build_batch_payload(texts: list[str]) -> str:
    """Build the JSON payload that asks the model for one translation per segment."""
    return json.dumps(
        {"segments": [{"id": index, "text": text} for index, text in enumerate(texts, start=1)]},
        ensure_ascii=False,
    )


def parse_batch_translation(raw: str, expected: int) -> list[str] | None:
    """Parse a batch answer, returning None when it cannot be trusted.

    A None result makes the caller fall back to one request per segment, so a
    malformed answer never shifts translations onto the wrong subtitles.
    """
    if expected <= 0:
        return None
    text = (raw or "").strip()
    if not text:
        return None
    if text.startswith("```"):
        text = re.sub(r"^```[a-zA-Z]*\s*", "", text)
        text = re.sub(r"\s*```$", "", text).strip()

    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        return None

    items = None
    if isinstance(data, dict):
        for key in ("translations", "segments", "results"):
            if isinstance(data.get(key), list):
                items = data[key]
                break
    elif isinstance(data, list):
        items = data

    if not isinstance(items, list) or len(items) != expected:
        return None

    if items and all(isinstance(item, dict) and isinstance(item.get("id"), int) for item in items):
        items = sorted(items, key=lambda item: item["id"])

    results: list[str] = []
    for item in items:
        if isinstance(item, str):
            value = item.strip()
        elif isinstance(item, dict):
            value = str(item.get("text") or item.get("translation") or "").strip()
        else:
            return None
        if not value:
            return None
        results.append(value)
    return results


def _fmt_clock(seconds: float) -> str:
    minutes, secs = divmod(int(seconds), 60)
    hours, minutes = divmod(minutes, 60)
    return f"{hours}:{minutes:02d}:{secs:02d}" if hours else f"{minutes}:{secs:02d}"


def probe_duration(media_path: Path) -> float | None:
    """Public alias used by the UI to show the duration before transcribing."""
    return _probe_duration(media_path)


def _probe_duration(media_path: Path) -> float | None:
    """Best-effort media duration in seconds, used for smooth progress reporting."""
    try:
        import av

        with av.open(str(media_path)) as container:
            duration = container.duration
    except Exception:
        return None
    if not duration or duration <= 0:
        return None
    return duration / 1_000_000


class TranscriptionService:
    def transcribe(
        self,
        media_path: Path,
        model_name: str,
        language: str,
        progress_callback,
        cancel_checker,
    ) -> TranscriptionResult:
        progress_callback("Preparazione del modello Whisper…", 3)
        if cancel_checker():
            raise RuntimeError("Processing cancelled.")
        model = self._load_model(model_name, progress_callback, cancel_checker)

        progress_callback("Trascrizione in corso…", 15)
        whisper_language = None if language == "auto" else language
        raw_segments, _info = model.transcribe(
            str(media_path),
            language=whisper_language,
            vad_filter=True,
            beam_size=5,
        )

        # Progress by elapsed media time so long files move smoothly instead of
        # parking on the old per-segment cap (which made ~1h audio look stuck).
        total_duration = _probe_duration(media_path)

        segments: list[TranscriptSegment] = []
        text_parts: list[str] = []
        for index, segment in enumerate(raw_segments, start=1):
            if cancel_checker():
                raise RuntimeError("Processing cancelled.")
            cleaned = segment.text.strip()
            if cleaned:
                segments.append(
                    TranscriptSegment(
                        index=index,
                        start=float(segment.start),
                        end=float(segment.end),
                        text=cleaned,
                    )
                )
                text_parts.append(cleaned)
            if total_duration:
                fraction = min(1.0, float(segment.end) / total_duration)
                value = 15 + int(80 * fraction)
                # Measured, not estimated: minutes of audio already processed.
                status = (
                    f"Trascrizione in corso: {_fmt_clock(segment.end)} "
                    f"di {_fmt_clock(total_duration)}"
                )
            else:
                value = 15 + index
                status = "Trascrizione in corso…"
            progress_callback(status, min(98, value))

        progress_callback("Trascrizione completata", 100)
        return TranscriptionResult(text="\n".join(text_parts), segments=segments)

    def _load_model(self, model_name: str, progress_callback, cancel_checker):
        """Load Whisper, keeping Cancel responsive while the model downloads.

        The first run downloads a few hundred megabytes. The download itself is
        blocking, so it runs on a helper thread and the worker polls Cancel; the
        Hugging Face cache resumes safely if the download is abandoned.
        """
        from faster_whisper import WhisperModel

        def make_model(location: str):
            progress_callback("Caricamento del modello Whisper…", 8)
            return WhisperModel(location, device="auto", compute_type="auto")

        if Path(model_name).exists():
            return make_model(model_name)

        try:
            from faster_whisper.utils import download_model
        except ImportError:  # older/newer faster-whisper layout: let it download directly
            download_model = None

        if download_model is None:
            return make_model(model_name)

        progress_callback("Download del modello Whisper (solo al primo utilizzo)…", 4)
        outcome: dict[str, object] = {}

        def fetch() -> None:
            try:
                outcome["path"] = download_model(model_name)
            except Exception as exc:  # re-raised on the worker thread below
                outcome["error"] = exc

        thread = threading.Thread(target=fetch, daemon=True)
        thread.start()
        while thread.is_alive():
            if cancel_checker():
                raise RuntimeError("Processing cancelled.")
            thread.join(0.2)

        error = outcome.get("error")
        if isinstance(error, Exception):
            raise error
        if cancel_checker():
            raise RuntimeError("Processing cancelled.")
        return make_model(str(outcome.get("path") or model_name))


class TranslationService:
    def translate(
        self,
        italian_text: str,
        segments: list[TranscriptSegment],
        mode: str,
        api_key: str,
        model_name: str,
        progress_callback,
        cancel_checker,
    ) -> TranslationResult:
        if mode != "openai":
            raise RuntimeError(
                "Only the OpenAI API translation is available. "
                "Open Settings, choose OpenAI API and add a key."
            )
        return self._translate_openai(
            italian_text=italian_text,
            segments=segments,
            api_key=api_key,
            model_name=model_name,
            progress_callback=progress_callback,
            cancel_checker=cancel_checker,
        )

    @staticmethod
    def _create_client(api_key: str):
        from openai import OpenAI

        return OpenAI(api_key=api_key)

    def _translate_openai(
        self,
        italian_text: str,
        segments: list[TranscriptSegment],
        api_key: str,
        model_name: str,
        progress_callback,
        cancel_checker,
    ) -> TranslationResult:
        if not api_key.strip():
            raise RuntimeError("Add an OpenAI API key in Settings before translating.")
        client = self._create_client(api_key.strip())
        return self._translate_with_client(
            client=client,
            segments=segments,
            model_name=model_name,
            progress_callback=progress_callback,
            cancel_checker=cancel_checker,
        )

    def _translate_with_client(
        self,
        client,
        segments: list[TranscriptSegment],
        model_name: str,
        progress_callback,
        cancel_checker,
    ) -> TranslationResult:
        translated_segments: list[TranscriptSegment] = []
        total = max(len(segments), 1)
        done = 0
        progress_callback("Traduzione in corso…", 5)

        for start in range(0, len(segments), TRANSLATION_BATCH_SIZE):
            if cancel_checker():
                raise RuntimeError("Processing cancelled.")
            batch = segments[start : start + TRANSLATION_BATCH_SIZE]
            translations = self._translate_batch(
                client=client,
                model_name=model_name,
                batch=batch,
                cancel_checker=cancel_checker,
            )
            for segment, translated_text in zip(batch, translations):
                translated_segments.append(
                    TranscriptSegment(
                        index=segment.index,
                        start=segment.start,
                        end=segment.end,
                        text=segment.text,
                        translated_text=translated_text,
                    )
                )
            done += len(batch)
            progress_callback(
                f"Traduzione in corso: {done} di {len(segments)} frasi",
                5 + int((done / total) * 90),
            )

        progress_callback("Traduzione completata", 100)
        return TranslationResult(
            text="\n".join(segment.translated_text for segment in translated_segments),
            segments=translated_segments,
        )

    def _translate_batch(
        self,
        client,
        model_name: str,
        batch: list[TranscriptSegment],
        cancel_checker,
    ) -> list[str]:
        response = client.responses.create(
            model=model_name,
            input=[
                {"role": "system", "content": TRANSLATION_SYSTEM_PROMPT},
                {
                    "role": "user",
                    "content": build_batch_payload([segment.text for segment in batch]),
                },
            ],
        )
        parsed = parse_batch_translation(response.output_text, len(batch))
        if parsed is not None:
            return parsed

        # The answer was not usable: ask one segment at a time so a bad batch
        # never puts a translation on the wrong cue.
        fallback: list[str] = []
        for segment in batch:
            if cancel_checker():
                raise RuntimeError("Processing cancelled.")
            fallback.append(self._translate_single(client, model_name, segment.text))
        return fallback

    def _translate_single(self, client, model_name: str, text: str) -> str:
        response = client.responses.create(
            model=model_name,
            input=[
                {"role": "system", "content": SINGLE_SEGMENT_PROMPT},
                {"role": "user", "content": text},
            ],
        )
        return response.output_text.strip()
