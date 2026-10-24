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


def _assign_lines(lines: list[str], segments: list[TranscriptSegment]) -> list[int]:
    """Segment index for each non-empty line.

    One line per segment maps exactly. Otherwise each line goes to the segment
    whose share of the audio duration contains the middle of the line's share
    of the text: the same rule the exports use, so playback and subtitles agree.
    """
    if len(lines) == len(segments):
        return list(range(len(lines)))
    weights = _segment_weights(segments)
    total_weight = sum(weights) or float(len(segments))
    boundaries: list[float] = []
    running = 0.0
    for weight in weights:
        running += weight
        boundaries.append(running / total_weight)

    total_chars = sum(len(line) for line in lines) or 1
    position = 0
    assigned: list[int] = []
    for line in lines:
        center = (position + len(line) / 2) / total_chars
        assigned.append(
            next(
                (index for index, edge in enumerate(boundaries) if center <= edge),
                len(segments) - 1,
            )
        )
        position += len(line)
    return assigned


def line_time_spans(
    text: str, segments: list[TranscriptSegment]
) -> list[tuple[float, float] | None]:
    """Audio span for every line of the edited text, blank lines included (None).

    Used by the player: the cursor's line tells where to start listening, and
    the playback position tells which line to highlight.
    """
    raw_lines = text.splitlines()
    filled = [index for index, line in enumerate(raw_lines) if line.strip()]
    spans: list[tuple[float, float] | None] = [None] * len(raw_lines)
    if not filled or not segments:
        return spans
    lines = [raw_lines[index].strip() for index in filled]
    for line_index, segment_index in zip(filled, _assign_lines(lines, segments)):
        segment = segments[segment_index]
        spans[line_index] = (float(segment.start), float(segment.end))
    return spans


def line_at_time(spans: list[tuple[float, float] | None], seconds: float) -> int | None:
    """Index of the line being spoken at ``seconds``: the last line started by then."""
    current = None
    for index, span in enumerate(spans):
        if span is None:
            continue
        if span[0] <= seconds:
            current = index
        else:
            break
    return current


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

    grouped: list[list[str]] = [[] for _ in segments]
    for line, index in zip(lines, _assign_lines(lines, segments)):
        grouped[index].append(line)

    updated = 0
    for segment, group in zip(segments, grouped):
        setattr(segment, attribute, " ".join(group))
        if group:
            updated += 1
    return updated
