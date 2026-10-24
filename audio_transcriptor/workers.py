from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import QObject, QRunnable, Signal, Slot

from audio_transcriptor.models import TranscriptionResult, TranslationResult
from audio_transcriptor.services import TranscriptionService, TranslationService
from audio_transcriptor.settings import AppSettings


class WorkerSignals(QObject):
    progress = Signal(str, int, object)
    transcribed = Signal(object)
    translated = Signal(object)
    error = Signal(str)
    finished = Signal()


class BaseWorker(QRunnable):
    def __init__(self) -> None:
        super().__init__()
        self.signals = WorkerSignals()
        self._cancelled = False

    def cancel(self) -> None:
        self._cancelled = True

    def is_cancelled(self) -> bool:
        return self._cancelled

    def emit_progress(self, key: str, value: int, params: dict | None = None) -> None:
        self._emit(self.signals.progress, key, max(0, min(100, value)), params or {})

    def _emit(self, signal: Signal, *args) -> None:
        # The window can be closed while a worker thread is still running; by
        # then the worker's signals may already be gone. Emitting on a deleted
        # QObject raises RuntimeError in the background thread, so swallow it.
        try:
            signal.emit(*args)
        except RuntimeError:
            pass


class TranscriptionWorker(BaseWorker):
    def __init__(self, media_path: Path, settings: AppSettings) -> None:
        super().__init__()
        self.media_path = media_path
        self.settings = settings

    @Slot()
    def run(self) -> None:
        try:
            result: TranscriptionResult = TranscriptionService().transcribe(
                media_path=self.media_path,
                model_name=self.settings.model_name,
                language=self.settings.language,
                progress_callback=self.emit_progress,
                cancel_checker=self.is_cancelled,
            )
            self._emit(self.signals.transcribed, result)
        except Exception as exc:
            self._emit(self.signals.error, str(exc) or "Transcription failed.")
        finally:
            self._emit(self.signals.finished)


class TranslationWorker(BaseWorker):
    def __init__(self, text: str, segments: list, settings: AppSettings) -> None:
        super().__init__()
        self.text = text
        self.segments = segments
        self.settings = settings

    @Slot()
    def run(self) -> None:
        try:
            result: TranslationResult = TranslationService().translate(
                italian_text=self.text,
                segments=self.segments,
                mode=self.settings.translation_mode,
                api_key=self.settings.openai_api_key,
                model_name=self.settings.openai_model,
                progress_callback=self.emit_progress,
                cancel_checker=self.is_cancelled,
            )
            self._emit(self.signals.translated, result)
        except Exception as exc:
            self._emit(self.signals.error, str(exc) or "Translation failed.")
        finally:
            self._emit(self.signals.finished)
