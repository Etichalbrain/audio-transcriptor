from __future__ import annotations

import unittest

from audio_transcriptor.alignment import align_lines_to_segments, edited_lines
from audio_transcriptor.models import TranscriptSegment


def make_segments(count: int = 3) -> list[TranscriptSegment]:
    return [
        TranscriptSegment(index=i, start=float(i - 1), end=float(i), text=f"Italian {i}")
        for i in range(1, count + 1)
    ]


class EditedLinesTests(unittest.TestCase):
    def test_drops_blank_lines_and_strips(self) -> None:
        self.assertEqual(edited_lines("  a \n\n b\n   \n"), ["a", "b"])


class AlignmentTests(unittest.TestCase):
    def test_one_line_per_segment_is_exact(self) -> None:
        segments = make_segments()
        updated = align_lines_to_segments("uno\ndue\ntre", segments)
        self.assertEqual(updated, 3)
        self.assertEqual([s.text for s in segments], ["uno", "due", "tre"])

    def test_empty_text_changes_nothing(self) -> None:
        segments = make_segments()
        self.assertEqual(align_lines_to_segments("   \n\n", segments), 0)
        self.assertEqual([s.text for s in segments], ["Italian 1", "Italian 2", "Italian 3"])

    def test_no_segments_is_safe(self) -> None:
        self.assertEqual(align_lines_to_segments("uno\ndue", []), 0)

    def test_fewer_lines_keep_every_edit(self) -> None:
        segments = make_segments()
        updated = align_lines_to_segments("prima riga\nseconda riga", segments)
        self.assertGreater(updated, 0)
        texts = [s.text for s in segments]
        joined = " ".join(texts)
        self.assertIn("prima riga", joined)
        self.assertIn("seconda riga", joined)
        self.assertLess(joined.index("prima riga"), joined.index("seconda riga"))
        self.assertEqual(texts.count(""), 1, "the cue without text is cleared, not left stale")

    def test_removed_sentence_does_not_come_back(self) -> None:
        segments = make_segments(4)
        align_lines_to_segments("uno\ndue\ntre", segments)
        self.assertNotIn("Italian 1", [s.text for s in segments])
        self.assertNotIn("Italian 2", [s.text for s in segments])
        self.assertNotIn("Italian 3", [s.text for s in segments])

    def test_more_lines_keep_every_edit(self) -> None:
        segments = make_segments()
        text = "\n".join(f"riga {i}" for i in range(1, 7))
        align_lines_to_segments(text, segments)
        joined = " ".join(s.text for s in segments)
        positions = [joined.index(f"riga {i}") for i in range(1, 7)]
        self.assertEqual(positions, sorted(positions), "line order must be preserved")

    def test_alignment_is_stable_across_repeated_exports(self) -> None:
        segments = make_segments(4)
        text = "alfa\nbeta\ngamma"
        align_lines_to_segments(text, segments)
        first = [s.text for s in segments]
        align_lines_to_segments(text, segments)
        self.assertEqual([s.text for s in segments], first)

    def test_translated_attribute(self) -> None:
        segments = make_segments(2)
        align_lines_to_segments("one\ntwo", segments, "translated_text")
        self.assertEqual([s.translated_text for s in segments], ["one", "two"])
        self.assertEqual([s.text for s in segments], ["Italian 1", "Italian 2"])

    def test_weights_follow_timing_not_text_length(self) -> None:
        segments = [
            TranscriptSegment(index=1, start=0.0, end=9.0, text="breve"),
            TranscriptSegment(index=2, start=9.0, end=10.0, text="originale"),
        ]
        lines = ["a" * 5, "b" * 5, "c" * 400]
        align_lines_to_segments("\n".join(lines), segments)

        # 9 of 10 seconds sit in the first segment, so a timing-weighted split
        # sends all three lines there; weighting by text length would not.
        self.assertEqual(segments[0].text.split(), lines)
        self.assertEqual(segments[1].text, "")


if __name__ == "__main__":
    unittest.main()
