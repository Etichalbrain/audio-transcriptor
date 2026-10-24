from __future__ import annotations

import sys

from PySide6.QtWidgets import QApplication

# The implementation lives in audio_transcriptor.ui; these names are re-exported
# so existing imports (scripts, tests, packaging) keep working.
from audio_transcriptor.ui.dialogs import (  # noqa: F401
    AUTHOR,
    LICENSE_NAME,
    MODEL_CHOICES,
    PROJECT_URL,
    AboutDialog,
    ExportDialog,
    SettingsDialog,
    TranslationConfirmDialog,
)
from audio_transcriptor.ui.main_window import MainWindow
from audio_transcriptor.ui.theme import DARK_STYLE, LIGHT_STYLE  # noqa: F401
from audio_transcriptor.workers import TranscriptionWorker, TranslationWorker  # noqa: F401


def main() -> int:
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = MainWindow()
    window.show()
    return app.exec()
