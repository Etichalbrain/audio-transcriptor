from __future__ import annotations

import json
import unittest

from audio_transcriptor.models import TranscriptSegment
from audio_transcriptor.services import (
    TRANSLATION_BATCH_SIZE,
    TranslationService,
    build_batch_payload,
    parse_batch_translation,
)


class BatchPayloadTests(unittest.TestCase):
    def test_payload_is_numbered_json(self) -> None:
        payload = json.loads(build_batch_payload(["ciao", "come stai"]))
        self.assertEqual(
            payload,
            {
                "segments": [
                    {"id": 1, "text": "ciao"},
                    {"id": 2, "text": "come stai"},
                ]
            },
        )

    def test_payload_keeps_accents_readable(self) -> None:
        self.assertIn("perché", build_batch_payload(["perché"]))


class ParseBatchTests(unittest.TestCase):
    def test_plain_list(self) -> None:
        self.assertEqual(parse_batch_translation('["one", "two"]', 2), ["one", "two"])

    def test_translations_object(self) -> None:
        raw = '{"translations": ["one", "two"]}'
        self.assertEqual(parse_batch_translation(raw, 2), ["one", "two"])

    def test_code_fence(self) -> None:
        raw = '```json\n{"translations": ["one"]}\n```'
        self.assertEqual(parse_batch_translation(raw, 1), ["one"])

    def test_segments_object_with_ids_is_sorted(self) -> None:
        raw = '{"segments": [{"id": 2, "text": "two"}, {"id": 1, "text": "one"}]}'
        self.assertEqual(parse_batch_translation(raw, 2), ["one", "two"])

    def test_wrong_length_is_rejected(self) -> None:
        self.assertIsNone(parse_batch_translation('["one"]', 2))

    def test_empty_value_is_rejected(self) -> None:
        self.assertIsNone(parse_batch_translation('["one", "  "]', 2))

    def test_garbage_is_rejected(self) -> None:
        self.assertIsNone(parse_batch_translation("Sure! Here you go:", 2))
        self.assertIsNone(parse_batch_translation("", 2))


class FakeResponse:
    def __init__(self, output_text: str) -> None:
        self.output_text = output_text


class FakeResponses:
    def __init__(self, handler) -> None:
        self.handler = handler
        self.calls: list[list[dict]] = []

    def create(self, model: str, input: list[dict]) -> FakeResponse:
        self.calls.append(input)
        return FakeResponse(self.handler(len(self.calls), input))


class FakeClient:
    def __init__(self, handler) -> None:
        self.responses = FakeResponses(handler)


def batch_size_of(input_payload: list[dict]) -> int:
    return len(json.loads(input_payload[1]["content"])["segments"])


def numbered_batches(calls: int, input_payload: list[dict]) -> str:
    count = batch_size_of(input_payload)
    return json.dumps({"translations": [f"EN {i}" for i in range(1, count + 1)]})


def make_segments(count: int) -> list[TranscriptSegment]:
    return [
        TranscriptSegment(index=i, start=float(i - 1), end=float(i), text=f"IT {i}")
        for i in range(1, count + 1)
    ]


class TranslateWithClientTests(unittest.TestCase):
    def run_translation(self, client, segments):
        service = TranslationService()
        progress: list[tuple[str, int]] = []
        result = service._translate_with_client(
            client=client,
            segments=segments,
            model_name="gpt-5",
            progress_callback=lambda status, value: progress.append((status, value)),
            cancel_checker=lambda: False,
        )
        return result, progress

    def test_batches_segments_into_few_requests(self) -> None:
        segments = make_segments(TRANSLATION_BATCH_SIZE * 2 + 5)
        client = FakeClient(numbered_batches)
        result, progress = self.run_translation(client, segments)

        self.assertEqual(len(client.responses.calls), 3)
        self.assertEqual(len(result.segments), len(segments))
        self.assertEqual([s.index for s in result.segments], [s.index for s in segments])
        self.assertEqual([s.start for s in result.segments], [s.start for s in segments])
        self.assertEqual(result.text.splitlines()[0], "EN 1")
        self.assertEqual(progress[-1], ("Translation complete", 100))

    def test_bad_batch_falls_back_to_one_request_per_segment(self) -> None:
        segments = make_segments(3)

        def handler(call: int, payload: list[dict]) -> str:
            user_content = payload[1]["content"]
            if user_content.startswith("{"):
                return "Here are your translations!"
            return "Single"

        client = FakeClient(handler)
        result, _progress = self.run_translation(client, segments)

        self.assertEqual(len(client.responses.calls), 4)  # 1 batch + 3 singles
        self.assertEqual([s.translated_text for s in result.segments], ["Single"] * 3)

    def test_cancel_stops_before_any_request(self) -> None:
        client = FakeClient(numbered_batches)
        service = TranslationService()
        with self.assertRaises(RuntimeError):
            service._translate_with_client(
                client=client,
                segments=make_segments(4),
                model_name="gpt-5",
                progress_callback=lambda status, value: None,
                cancel_checker=lambda: True,
            )
        self.assertEqual(client.responses.calls, [])

    def test_empty_input_makes_no_request(self) -> None:
        client = FakeClient(numbered_batches)
        result, progress = self.run_translation(client, [])
        self.assertEqual(client.responses.calls, [])
        self.assertEqual(result.segments, [])
        self.assertEqual(progress[-1], ("Translation complete", 100))


class ModeTests(unittest.TestCase):
    def test_local_mode_is_rejected_instead_of_faking_a_translation(self) -> None:
        with self.assertRaises(RuntimeError):
            TranslationService().translate(
                italian_text="ciao",
                segments=make_segments(1),
                mode="local",
                api_key="",
                model_name="gpt-5",
                progress_callback=lambda status, value: None,
                cancel_checker=lambda: False,
            )

    def test_missing_key_is_reported(self) -> None:
        with self.assertRaises(RuntimeError):
            TranslationService().translate(
                italian_text="ciao",
                segments=make_segments(1),
                mode="openai",
                api_key="   ",
                model_name="gpt-5",
                progress_callback=lambda status, value: None,
                cancel_checker=lambda: False,
            )


if __name__ == "__main__":
    unittest.main()
