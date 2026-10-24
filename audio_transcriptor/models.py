from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


SUPPORTED_EXTENSIONS = {".mp3", ".wav", ".m4a", ".mp4", ".mov", ".mkv"}


@dataclass
class TranscriptSegment:
    index: int
    start: float
    end: float
    text: str
    translated_text: str = ""


@dataclass
class TranscriptionResult:
    text: str
    segments: list[TranscriptSegment]


@dataclass
class TranslationResult:
    text: str
    segments: list[TranscriptSegment]


def is_supported_media(path: str | Path) -> bool:
    return Path(path).suffix.lower() in SUPPORTED_EXTENSIONS
