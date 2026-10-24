"""Render the main window to docs/app.png without a display.

Run from the project root with the development dependencies installed:

    QT_QPA_PLATFORM=offscreen .venv/bin/python scripts/capture_screenshot.py [--lang en] [--out docs]

The README screenshots are in English (the default). Pass --lang it/de/fr to
check another interface language.

The window is filled with sample text so the screenshot shows the real
interface instead of empty panes. Nothing is transcribed or sent anywhere.
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path
from unittest.mock import patch

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from audio_transcriptor.app import AboutDialog, MainWindow  # noqa: E402
from audio_transcriptor.models import TranscriptSegment  # noqa: E402
from audio_transcriptor.settings import AppSettings, SettingsStore  # noqa: E402

ITALIAN = (
    "Buongiorno, siamo qui per parlare del nuovo progetto.\n"
    "Il primo passo è capire quante persone parteciperanno.\n"
    "Abbiamo tempo fino alla fine del mese per chiudere il piano.\n"
    "Poi passiamo alla parte tecnica con il team di sviluppo.\n"
    "Perfetto, direi che possiamo cominciare da lunedì."
)

ENGLISH = (
    "Good morning, we are here to talk about the new project.\n"
    "The first step is understanding how many people will take part.\n"
    "We have until the end of the month to close the plan.\n"
    "Then we move on to the technical part with the development team.\n"
    "Perfect, I would say we can start on Monday."
)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--lang", default="en", choices=("en", "it", "de", "fr"))
    parser.add_argument("--out", default=str(ROOT / "docs"))
    args = parser.parse_args()

    app = QApplication(sys.argv[:1])
    app.setStyle("Fusion")
    # Never load a real user's settings/API key or personal output directory.
    with patch.object(SettingsStore, "load", return_value=AppSettings(ui_language=args.lang)):
        window = MainWindow()
    window.resize(1100, 820)
    window.set_selected_file(str(ROOT / "intervista_cliente.mp4"))
    window.italian_text.setPlainText(ITALIAN)
    window.english_text.setPlainText(ENGLISH)
    lines = ITALIAN.splitlines()
    window.transcript_segments = [
        TranscriptSegment(index=index + 1, start=index * 4.0, end=index * 4.0 + 3.5, text=line)
        for index, line in enumerate(lines)
    ]
    window.translation_segments = [
        TranscriptSegment(
            index=index + 1,
            start=index * 4.0,
            end=index * 4.0 + 3.5,
            text=lines[index],
            translated_text=line,
        )
        for index, line in enumerate(ENGLISH.splitlines())
    ]
    window.progress_bar.setValue(100)
    window.set_status("progress.translated", "ok")
    window.en_pane.show()
    window.work_splitter.setSizes([1, 1])
    window.update_stats()
    window.update_actions()

    window.show()
    for _ in range(10):
        app.processEvents()

    docs = Path(args.out)
    docs.mkdir(parents=True, exist_ok=True)
    results = []
    for name, widget in (("app.png", window), ("about.png", AboutDialog())):
        widget.show()
        for _ in range(10):
            app.processEvents()
        target = docs / name
        results.append((target, widget.grab().save(str(target))))

    for target, ok in results:
        print(f"saved={target} ok={ok}")
    return 0 if all(ok for _target, ok in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
