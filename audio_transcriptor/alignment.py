from __future__ import annotations

from audio_transcriptor.models import TranscriptSegment


def edited_lines(text: str) -> list[str]:
    """Return the non-empty, stripped lines of an edited transcript."""
    return [line.strip() for line in text.splitlines() if line.strip()]


def _segment_weights(segments: list[TranscriptSegment]) -> list[float]:
    """Weight segments by duration.

    Durations never change while the user edits the text, so repeated exports of
    the same text always produce the same alignment.
    """
    weights: list[float] = []
    for segment in segments:
        span = float(segment.end) - float(segment.start)
        weights.append(span if span > 0 else float(max(1, len(segment.text))))
    return weights


def align_lines_to_segments(
    text: str,
    segments: list[TranscriptSegment],
    attribute: str = "text",
) -> int:
    """Distribute the edited lines over the segments by timing.

    When the user keeps one line per segment the mapping is exact. When lines are
    added or removed, each line goes to the segment whose time span contains the
    middle of the line, so no edit is silently dropped and the order is preserved.
    Segments left without a line are cleared instead of keeping the old text: a
    sentence the user deleted must not come back in the subtitle file.
    Returns the number of segments that received text.
    """
    lines = edited_lines(text)
    if not lines or not segments:
        return 0

    if len(lines) == len(segments):
        for segment, line in zip(segments, lines):
            setattr(segment, attribute, line)
        return len(segments)

    weights = _segment_weights(segments)
    total_weight = sum(weights) or float(len(segments))
    boundaries: list[float] = []
    running = 0.0
    for weight in weights:
        running += weight
        boundaries.append(running / total_weight)

    grouped: list[list[str]] = [[] for _ in segments]
    total_chars = sum(len(line) for line in lines) or 1
    position = 0
    for line in lines:
        center = (position + len(line) / 2) / total_chars
        index = next(
            (position_ for position_, edge in enumerate(boundaries) if center <= edge),
            len(segments) - 1,
        )
        grouped[index].append(line)
        position += len(line)

    updated = 0
    for segment, group in zip(segments, grouped):
        setattr(segment, attribute, " ".join(group))
        if group:
            updated += 1
    return updated
