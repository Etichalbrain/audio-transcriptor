from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from docx import Document

from audio_transcriptor.exporters import timestamp_srt, write_docx, write_srt, write_txt
from audio_transcriptor.models import TranscriptSegment


class TimestampTests(unittest.TestCase):
    def test_zero(self) -> None:
        self.assertEqual(timestamp_srt(0), "00:00:00,000")

    def test_hours_minutes_seconds(self) -> None:
        self.assertEqual(timestamp_srt(3661.5), "01:01:01,500")

    def test_rounding(self) -> None:
        self.assertEqual(timestamp_srt(0.9996), "00:00:01,000")


class ExporterTests(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.folder = Path(self._tmp.name)

    def test_txt_is_trimmed_with_trailing_newline(self) -> None:
        target = self.folder / "out.txt"
        write_txt(target, "  ciao mondo  \n")
        self.assertEqual(target.read_text(encoding="utf-8"), "ciao mondo\n")

    def test_srt_uses_translation_when_present(self) -> None:
        segments = [
            TranscriptSegment(1, 0.0, 1.5, "ciao", "hello"),
            TranscriptSegment(2, 1.5, 3.0, "come stai", ""),
        ]
        target = self.folder / "out.srt"
        write_srt(target, segments)
        content = target.read_text(encoding="utf-8")
        self.assertIn("1\n00:00:00,000 --> 00:00:01,500\nhello", content)
        self.assertIn("2\n00:00:01,500 --> 00:00:03,000\ncome stai", content)

    def test_srt_skips_empty_segments_and_renumbers(self) -> None:
        segments = [
            TranscriptSegment(1, 0.0, 1.0, "", ""),
            TranscriptSegment(2, 1.0, 2.0, "ciao", ""),
        ]
        target = self.folder / "out.srt"
        write_srt(target, segments, translated=False)
        self.assertEqual(
            target.read_text(encoding="utf-8"),
            "1\n00:00:01,000 --> 00:00:02,000\nciao\n",
        )

    def test_english_export_never_shows_italian_text(self) -> None:
        segments = [
            TranscriptSegment(1, 0.0, 1.0, "ciao", "hello"),
            TranscriptSegment(2, 1.0, 2.0, "testo rimosso", ""),
        ]
        target = self.folder / "out.srt"
        write_srt(target, segments, translated=True)
        content = target.read_text(encoding="utf-8")
        self.assertIn("hello", content)
        self.assertNotIn("testo rimosso", content)

    def test_italian_export_never_shows_translation(self) -> None:
        segments = [TranscriptSegment(1, 0.0, 1.0, "ciao", "hello")]
        target = self.folder / "out.srt"
        write_srt(target, segments, translated=False)
        content = target.read_text(encoding="utf-8")
        self.assertIn("ciao", content)
        self.assertNotIn("hello", content)

    def test_docx_round_trip(self) -> None:
        target = self.folder / "out.docx"
        write_docx(target, "Italian Transcript", "prima riga\n\nseconda riga")
        document = Document(target)
        paragraphs = [p.text for p in document.paragraphs if p.text]
        self.assertEqual(paragraphs[0], "Italian Transcript")
        self.assertEqual(paragraphs[1:], ["prima riga", "seconda riga"])


if __name__ == "__main__":
    unittest.main()
