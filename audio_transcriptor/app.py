from __future__ import annotations

import shutil
import sys
from html import escape
from pathlib import Path

from PySide6.QtCore import QByteArray, QLocale, QPointF, QThreadPool, QTimer, Qt, QUrl, Signal
from PySide6.QtGui import (
    QColor,
    QDesktopServices,
    QDragEnterEvent,
    QDropEvent,
    QIcon,
    QPainter,
    QPen,
    QPixmap,
    QPolygonF,
    QKeySequence,
    QShortcut,
    QTextCursor,
    QTextFormat,
)
from PySide6.QtWidgets import (
    QApplication,
    QCheckBox,
    QComboBox,
    QDialog,
    QFileDialog,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QProgressBar,
    QPushButton,
    QSizePolicy,
    QSlider,
    QSplitter,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from audio_transcriptor import __version__, i18n
from audio_transcriptor.diagnostics import legal_document_path
from audio_transcriptor.alignment import align_lines_to_segments, line_at_time, line_time_spans
from audio_transcriptor.exporters import write_docx, write_srt, write_txt
from audio_transcriptor.i18n import tr, tr_n
from audio_transcriptor.models import TranscriptSegment, is_supported_media
from audio_transcriptor.services import probe_duration
from audio_transcriptor.settings import AppSettings, SettingsStore
from audio_transcriptor.workers import BaseWorker, TranscriptionWorker, TranslationWorker


AUTHOR = "Antonio Aversa"
PROJECT_URL = "https://aversa.design"

LICENSE_NAME = "Apache License 2.0 + Commons Clause v1.0"

# Whisper models offered in Settings; their labels live in i18n ("model.<name>").
MODEL_CHOICES = ("small", "medium", "large-v3")

# ---------------------------------------------------------------------------
# New-interface design tokens (light): warm paper-grey background, white cards,
# a slightly deeper blue accent and soft tint surfaces for status states.
# ---------------------------------------------------------------------------
BG = "#f3f5f9"
SURFACE = "#ffffff"
BORDER = "#e6e9f0"
TEXT = "#141a26"
TEXT_MUTED = "#667080"
ACCENT = "#1d45f5"
ACCENT_HOVER = "#1740e0"
ACCENT_TINT = "#e8ecff"
SUCCESS = "#1f9d55"
SUCCESS_TINT = "#e3f6ec"
ERROR = "#d93025"
ERROR_TINT = "#fdecec"
WARN = "#b54708"
WARN_TINT = "#fdf0ea"
DISABLED = "#e4e7ee"
DASH = "#c4cbd9"

# Dark variants of the same palette.
D_BG = "#12161f"
D_SURFACE = "#1a1f2a"
D_BORDER = "#2b3242"
D_TEXT = "#e8ecf2"
D_TEXT_MUTED = "#8b94a3"
D_ACCENT = "#3b6cff"
D_ACCENT_HOVER = "#2f5cf0"
D_ACCENT_TINT = "#25304a"
D_SUCCESS = "#2fb46b"
D_SUCCESS_TINT = "#1c3327"
D_ERROR = "#ff5c5c"
D_ERROR_TINT = "#331f22"
D_WARN = "#e5a24a"
D_WARN_TINT = "#33291f"
D_DISABLED = "#262d3a"
D_DASH = "#3c4557"

# The monogram logo embedded so the branded UI works in dev, in tests and in
# the packaged app without resource-path plumbing.
LOGO_SVG = """<svg width="32" height="33" viewBox="0 0 32 33" fill="none" xmlns="http://www.w3.org/2000/svg">
<path d="M29.5 0C29.5848 1.07412e-09 29.668 0.00734433 29.75 0.0175781C29.832 0.00734432 29.9152 7.08024e-09 30 0C31.1046 1.20275e-07 32 0.895431 32 2V7C32 8.10457 31.1046 9 30 9C28.8954 9 28 8.10457 28 7V4H18V31C18 32.1046 17.1046 33 16 33C14.8954 33 14 32.1046 14 31V4H4V7C4 8.10457 3.10457 9 2 9C0.895431 9 3.10879e-07 8.10457 0 7V2C7.75285e-08 0.895431 0.895431 9.2274e-08 2 0C2.08475 9.22872e-09 2.16802 0.00734435 2.25 0.0175781C2.33198 0.00734438 2.41525 3.70472e-09 2.5 0H29.5ZM9 9C10.1046 9 11 9.89543 11 11V23C11 24.1046 10.1046 25 9 25C7.89543 25 7 24.1046 7 23V11C7 9.89543 7.89543 9 9 9ZM23 9C24.1046 9 25 9.89543 25 11V23C25 24.1046 24.1046 25 23 25C21.8954 25 21 24.1046 21 23V11C21 9.89543 21.8954 9 23 9ZM2 14C3.10457 14 4 14.8954 4 16V19C4 20.1046 3.10457 21 2 21C0.895431 21 4.832e-08 20.1046 0 19V16C0 14.8954 0.895431 14 2 14ZM30 14C31.1046 14 32 14.8954 32 16V19C32 20.1046 31.1046 21 30 21C28.8954 21 28 20.1046 28 19V16C28 14.8954 28.8954 14 30 14Z" fill="url(#paint0_linear_426_1289)"/>
<defs>
<linearGradient id="paint0_linear_426_1289" x1="16.5" y1="0" x2="16.5" y2="33" gradientUnits="userSpaceOnUse">
<stop stop-color="#0513AD"/>
<stop offset="1" stop-color="#020847"/>
</linearGradient>
</defs>
</svg>
"""


# ---------------------------------------------------------------------------
# Styles. The palette above is mirrored into the Qt stylesheet so widgets,
# cards and states share the exact same colours.
# ---------------------------------------------------------------------------
LIGHT_STYLE = f"""
QWidget {{
    font-family: Inter, Arial, sans-serif;
    font-size: 14px;
    color: {TEXT};
    background: {BG};
}}
QMainWindow, QDialog {{ background: {BG}; }}
QLabel {{ color: {TEXT}; background: transparent; }}
QLabel#muted {{ color: {TEXT_MUTED}; }}
QLabel#cardTitle {{ font-size: 13px; font-weight: 600; color: {TEXT_MUTED}; }}
QLabel#paneTitle {{ font-size: 12px; font-weight: 700; color: {TEXT_MUTED}; }}
QLabel#heroTitle {{ font-size: 17px; font-weight: 700; }}
QFrame#chip QLabel {{ color: #59637a; font-size: 12px; }}

QFrame#card {{
    background: {SURFACE};
    border: 1px solid {BORDER};
    border-radius: 12px;
}}
QFrame#dropZone {{
    background: #f7f8fb;
    border: 1.5px dashed {DASH};
    border-radius: 14px;
}}
QFrame#chip {{
    background: {ACCENT_TINT};
    border: 1px solid #d8e0fb;
    border-radius: 14px;
}}
QFrame#bannerError {{
    background: {ERROR_TINT};
    border: 1px solid #f3b9bb;
    border-radius: 10px;
}}
QFrame#bannerOk {{
    background: {SUCCESS_TINT};
    border: 1px solid #b9e3cc;
    border-radius: 10px;
}}
QFrame#bannerWarn {{
    background: {WARN_TINT};
    border: 1px solid #ecccb3;
    border-radius: 10px;
}}

QTextEdit {{
    background: {SURFACE};
    color: {TEXT};
    border: 1px solid {BORDER};
    border-radius: 10px;
    padding: 12px;
    selection-background-color: {ACCENT_TINT};
}}
QTextEdit:focus {{ border: 1.5px solid {ACCENT}; }}

QLineEdit, QComboBox {{
    padding: 8px;
    border: 1px solid {BORDER};
    border-radius: 8px;
    background: {SURFACE};
    color: {TEXT};
    min-height: 22px;
}}
QLineEdit:focus, QComboBox:focus {{ border: 1.5px solid {ACCENT}; }}
QComboBox::drop-down {{ border: none; width: 24px; }}
QComboBox QAbstractItemView {{
    background: {SURFACE};
    color: {TEXT};
    selection-background-color: {ACCENT_TINT};
    selection-color: {TEXT};
}}

QPushButton {{
    padding: 9px 16px;
    border-radius: 8px;
    background: {ACCENT};
    color: #ffffff;
    border: 0;
    font-weight: 600;
}}
QPushButton:hover {{ background: {ACCENT_HOVER}; }}
QPushButton:pressed {{ background: #1436c7; }}
QPushButton:disabled {{
    background: {DISABLED};
    color: #8a94a3;
}}
QPushButton#secondary {{
    background: {SURFACE};
    color: {TEXT};
    border: 1px solid {BORDER};
}}
QPushButton#secondary:hover {{ background: #edf0f6; }}
QPushButton#ghost {{
    background: transparent;
    color: {ACCENT};
    border: 1px solid #d8e0fb;
}}
QPushButton#ghost:hover {{ background: {ACCENT_TINT}; }}
QPushButton#danger {{
    background: {ERROR};
    color: #ffffff;
    border: 0;
}}
QPushButton#danger:hover {{ background: #c22a20; }}
QPushButton#success {{ background: {SUCCESS}; color: #ffffff; border: 0; }}
QPushButton#success:hover {{ background: #1a8a4a; }}

QProgressBar {{
    background: {DISABLED};
    color: {TEXT};
    border: 1px solid {BORDER};
    border-radius: 7px;
    height: 14px;
    text-align: center;
}}
QProgressBar::chunk {{
    background: {ACCENT};
    border-radius: 6px;
}}

QSplitter::handle {{ background: {BORDER}; width: 1px; }}

QScrollBar:vertical {{ background: transparent; width: 10px; margin: 0; }}
QScrollBar::handle:vertical {{ background: #c8cfdb; border-radius: 5px; min-height: 24px; }}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0; }}
QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{ background: transparent; }}
QScrollBar:horizontal {{ background: transparent; height: 10px; margin: 0; }}
QScrollBar::handle:horizontal {{ background: #c8cfdb; border-radius: 5px; min-width: 24px; }}
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{ width: 0; }}
"""

DARK_STYLE = f"""
QWidget {{
    font-family: Inter, Arial, sans-serif;
    font-size: 14px;
    color: {D_TEXT};
    background: {D_BG};
}}
QMainWindow, QDialog {{ background: {D_BG}; }}
QLabel {{ color: {D_TEXT}; background: transparent; }}
QLabel#muted {{ color: {D_TEXT_MUTED}; }}
QLabel#cardTitle {{ font-size: 13px; font-weight: 600; color: {D_TEXT_MUTED}; }}
QLabel#paneTitle {{ font-size: 12px; font-weight: 700; color: #a8b0c0; }}
QLabel#heroTitle {{ font-size: 17px; font-weight: 700; }}
QFrame#chip QLabel {{ color: #a8b0c0; font-size: 12px; }}

QFrame#card {{
    background: {D_SURFACE};
    border: 1px solid {D_BORDER};
    border-radius: 12px;
}}
QFrame#dropZone {{
    background: #161b24;
    border: 1.5px dashed {D_DASH};
    border-radius: 14px;
}}
QFrame#chip {{
    background: {D_ACCENT_TINT};
    border: 1px solid #31406b;
    border-radius: 14px;
}}
QFrame#bannerError {{
    background: {D_ERROR_TINT};
    border: 1px solid #7a3a42;
    border-radius: 10px;
}}
QFrame#bannerOk {{
    background: {D_SUCCESS_TINT};
    border: 1px solid #2f5a44;
    border-radius: 10px;
}}
QFrame#bannerWarn {{
    background: {D_WARN_TINT};
    border: 1px solid #5a4a33;
    border-radius: 10px;
}}

QTextEdit {{
    background: #0d1117;
    color: {D_TEXT};
    border: 1px solid {D_BORDER};
    border-radius: 10px;
    padding: 12px;
    selection-background-color: #27406e;
}}
QTextEdit:focus {{ border: 1.5px solid {D_ACCENT}; }}

QLineEdit, QComboBox {{
    padding: 8px;
    border: 1px solid {D_BORDER};
    border-radius: 8px;
    background: #0d1117;
    color: {D_TEXT};
    min-height: 22px;
}}
QLineEdit:focus, QComboBox:focus {{ border: 1.5px solid {D_ACCENT}; }}
QComboBox::drop-down {{ border: none; width: 24px; }}
QComboBox QAbstractItemView {{
    background: #0d1117;
    color: {D_TEXT};
    selection-background-color: #27406e;
    selection-color: {D_TEXT};
}}

QPushButton {{
    padding: 9px 16px;
    border-radius: 8px;
    background: {D_ACCENT};
    color: #ffffff;
    border: 0;
    font-weight: 600;
}}
QPushButton:hover {{ background: {D_ACCENT_HOVER}; }}
QPushButton:pressed {{ background: #2652d6; }}
QPushButton:disabled {{
    background: {D_DISABLED};
    color: #5b6474;
}}
QPushButton#secondary {{
    background: {D_SURFACE};
    color: {D_TEXT};
    border: 1px solid {D_BORDER};
}}
QPushButton#secondary:hover {{ background: #232a38; }}
QPushButton#ghost {{
    background: transparent;
    color: {D_ACCENT};
    border: 1px solid #31406b;
}}
QPushButton#ghost:hover {{ background: {D_ACCENT_TINT}; }}
QPushButton#danger {{
    background: {D_ERROR};
    color: #ffffff;
    border: 0;
}}
QPushButton#danger:hover {{ background: #ff4444; }}
QPushButton#success {{ background: {D_SUCCESS}; color: #ffffff; border: 0; }}
QPushButton#success:hover {{ background: #279a5c; }}

QProgressBar {{
    background: {D_DISABLED};
    color: {D_TEXT};
    border: 1px solid {D_BORDER};
    border-radius: 7px;
    height: 14px;
    text-align: center;
}}
QProgressBar::chunk {{
    background: {D_ACCENT};
    border-radius: 6px;
}}

QSplitter::handle {{ background: {D_BORDER}; width: 1px; }}

QScrollBar:vertical {{ background: transparent; width: 10px; margin: 0; }}
QScrollBar::handle:vertical {{ background: #39414f; border-radius: 5px; min-height: 24px; }}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0; }}
QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{ background: transparent; }}
QScrollBar:horizontal {{ background: transparent; height: 10px; margin: 0; }}
QScrollBar::handle:horizontal {{ background: #39414f; border-radius: 5px; min-width: 24px; }}
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{ width: 0; }}
"""


def _logo_pixmap(size: int) -> QPixmap:
    """Logo monogram as a pixmap, with a graceful ECMA fallback drawing."""
    pixmap = QPixmap()
    if pixmap.loadFromData(QByteArray(LOGO_SVG.encode("utf-8"))):
        scaled = pixmap.scaled(
            size,
            size,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )
        if not scaled.isNull():
            return scaled

    # Fallback: rounded gradient tile with the monogram letter.
    fallback = QPixmap(size, size)
    fallback.fill(QColor("#0a1b66"))
    painter = QPainter(fallback)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    painter.setPen(QPen(QColor("#4f7dff"), max(3, size // 10)))
    painter.drawLine(size * 0.5, size * 0.18, size * 0.5, size * 0.82)
    painter.drawLine(size * 0.5, size * 0.18, size * 0.18, size * 0.18)
    painter.drawLine(size * 0.18, size * 0.18, size * 0.18, size * 0.62)
    painter.drawLine(size * 0.5, size * 0.18, size * 0.82, size * 0.18)
    painter.drawLine(size * 0.82, size * 0.18, size * 0.82, size * 0.62)
    painter.end()
    return fallback


def _upload_icon(size: int = 96) -> QPixmap | None:
    """Tinted rounded tile with an upward arrow, drawn with QPainter."""
    pixmap = QPixmap(size, size)
    pixmap.fill(QColor(ACCENT_TINT))
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    painter.setBrush(QColor(ACCENT_TINT))
    painter.setPen(QPen(QColor(ACCENT_TINT), 0))
    painter.drawRoundedRect(0, 0, size, size, size * 0.3, size * 0.3)

    pen = QPen(QColor(ACCENT), max(3, size // 14))
    pen.setCapStyle(Qt.PenCapStyle.RoundCap)
    painter.setPen(pen)
    c = size // 2
    painter.drawLine(c, size * 0.70, c, size * 0.42)  # shaft
    head = QPolygonF()
    head.append(QPointF(c, size * 0.18))
    head.append(QPointF(c - size * 0.22, size * 0.34))
    head.append(QPointF(c + size * 0.22, size * 0.34))
    painter.setBrush(QColor(ACCENT))
    painter.setPen(QPen(QColor(ACCENT), 0))
    painter.drawPolygon(head)
    base = QPolygonF()
    base.append(QPointF(c - size * 0.30, size * 0.82))
    base.append(QPointF(c + size * 0.30, size * 0.82))
    base.append(QPointF(c, size * 0.72))
    painter.drawPolygon(base)
    painter.end()
    return pixmap


def _fmt_size(bytes_count: int) -> str:
    value = float(bytes_count)
    for unit in ("B", "KB", "MB", "GB"):
        if value < 1024 or unit == "GB":
            return f"{value:.0f} {unit}" if unit == "B" else f"{value:.1f} {unit}"
        value /= 1024
    return f"{value:.1f} GB"


def _fmt_time(seconds: float) -> str:
    minutes, secs = divmod(int(seconds), 60)
    hours, minutes = divmod(minutes, 60)
    if hours:
        return f"{hours}:{minutes:02d}:{secs:02d}"
    return f"{minutes}:{secs:02d}"


class DropZone(QFrame):
    """Draggable upload surface; drops anywhere in the card select the file."""

    fileDropped = Signal(str)

    def __init__(self) -> None:
        super().__init__()
        self.setObjectName("dropZone")
        self.setAcceptDrops(True)
        self.setMinimumHeight(150)
        self.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed
        )
        self._vbox = QVBoxLayout(self)
        self._vbox.setContentsMargins(18, 16, 18, 16)
        self._vbox.setSpacing(10)

    def vbox(self) -> QVBoxLayout:
        return self._vbox

    def dragEnterEvent(self, event: QDragEnterEvent) -> None:
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event: QDropEvent) -> None:
        urls = event.mimeData().urls()
        if urls:
            self.fileDropped.emit(urls[0].toLocalFile())


def _card(title: str | None = None) -> tuple[QFrame, QVBoxLayout]:
    frame = QFrame()
    frame.setObjectName("card")
    layout = QVBoxLayout(frame)
    layout.setContentsMargins(16, 14, 16, 14)
    layout.setSpacing(10)
    frame.heading = None
    if title is not None:
        heading = QLabel(title)
        heading.setObjectName("cardTitle")
        layout.addWidget(heading)
        frame.heading = heading
    return frame, layout


def _dot_label(color: str) -> QLabel:
    dot = QLabel()
    dot.setFixedSize(10, 10)
    dot.setStyleSheet(f"background: {color}; border-radius: 5px;")
    return dot


def system_ui_languages() -> list[str]:
    """The operating system's preferred interface languages, most preferred first."""
    return list(QLocale.system().uiLanguages()) or [QLocale.system().name()]


class SettingsDialog(QDialog):
    """Settings: transcription model, translation, interface language, output and theme."""

    def __init__(self, settings: AppSettings, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle(tr("header.settings"))
        self.setMinimumWidth(540)

        self.model_combo = QComboBox()
        for value in MODEL_CHOICES:
            self.model_combo.addItem(tr(f"model.{value}"), value)
        self.model_combo.setCurrentIndex(max(0, self.model_combo.findData(settings.model_name)))

        self.language_combo = QComboBox()
        self.language_combo.addItem(tr("settings.audio_italian"), "it")
        self.language_combo.addItem(tr("settings.audio_auto"), "auto")
        self.language_combo.setCurrentIndex(0 if settings.language == "it" else 1)

        self.ui_language_combo = QComboBox()
        self.ui_language_combo.addItem(tr("settings.interface_system"), "system")
        for code in i18n.LANGUAGES:
            # Each language is shown in itself, so it can be found from any language.
            self.ui_language_combo.addItem(i18n.LANGUAGE_NAMES[code], code)
        self.ui_language_combo.setCurrentIndex(
            max(0, self.ui_language_combo.findData(settings.ui_language))
        )

        self.output_edit = QLineEdit(settings.output_folder)
        output_button = QPushButton(tr("action.browse"))
        output_button.setObjectName("secondary")
        output_button.clicked.connect(self.choose_output_folder)
        output_row = QHBoxLayout()
        output_row.addWidget(self.output_edit, stretch=1)
        output_row.addWidget(output_button)

        self.api_key_edit = QLineEdit(settings.openai_api_key)
        self.api_key_edit.setEchoMode(QLineEdit.EchoMode.Password)
        self.openai_model_edit = QLineEdit(settings.openai_model)
        self.confirm_translation_check = QCheckBox(tr("settings.confirm_translation"))
        self.confirm_translation_check.setChecked(settings.confirm_translation)

        self.theme_combo = QComboBox()
        self.theme_combo.addItem(tr("settings.theme_light"), "light")
        self.theme_combo.addItem(tr("settings.theme_dark"), "dark")
        self.theme_combo.setCurrentIndex(0 if settings.theme == "light" else 1)

        root = QVBoxLayout(self)
        root.setContentsMargins(18, 16, 18, 16)
        root.setSpacing(12)

        model_card, model_layout = _card(tr("settings.section_model"))
        grid = QGridLayout()
        grid.setHorizontalSpacing(10)
        grid.setVerticalSpacing(8)
        grid.addWidget(QLabel(tr("settings.whisper_model")), 0, 0)
        grid.addWidget(self.model_combo, 0, 1)
        grid.addWidget(QLabel(tr("settings.audio_language")), 1, 0)
        grid.addWidget(self.language_combo, 1, 1)
        model_layout.addLayout(grid)
        root.addWidget(model_card)

        trans_card, trans_layout = _card(tr("settings.section_translation"))
        hint = QLabel(tr("settings.translation_hint"))
        hint.setObjectName("muted")
        trans_layout.addWidget(hint)
        tgrid = QGridLayout()
        tgrid.setHorizontalSpacing(10)
        tgrid.setVerticalSpacing(8)
        tgrid.addWidget(QLabel(tr("settings.api_key")), 0, 0)
        tgrid.addWidget(self.api_key_edit, 0, 1)
        tgrid.addWidget(QLabel(tr("settings.openai_model")), 1, 0)
        tgrid.addWidget(self.openai_model_edit, 1, 1)
        trans_layout.addLayout(tgrid)
        trans_layout.addWidget(self.confirm_translation_check)
        root.addWidget(trans_card)

        gen_card, gen_layout = _card(tr("settings.section_general"))
        ggrid = QGridLayout()
        ggrid.setHorizontalSpacing(10)
        ggrid.setVerticalSpacing(8)
        ggrid.addWidget(QLabel(tr("settings.interface_language")), 0, 0)
        ggrid.addWidget(self.ui_language_combo, 0, 1)
        ggrid.addWidget(QLabel(tr("settings.output_folder")), 1, 0)
        ggrid.addLayout(output_row, 1, 1)
        ggrid.addWidget(QLabel(tr("settings.theme")), 2, 0)
        ggrid.addWidget(self.theme_combo, 2, 1)
        gen_layout.addLayout(ggrid)
        root.addWidget(gen_card)

        save_button = QPushButton(tr("action.save"))
        cancel_button = QPushButton(tr("action.cancel"))
        cancel_button.setObjectName("secondary")
        save_button.clicked.connect(self.accept)
        cancel_button.clicked.connect(self.reject)
        buttons = QHBoxLayout()
        buttons.addStretch()
        buttons.addWidget(cancel_button)
        buttons.addWidget(save_button)
        root.addLayout(buttons)

    def choose_output_folder(self) -> None:
        folder = QFileDialog.getExistingDirectory(
            self, tr("settings.choose_folder"), self.output_edit.text()
        )
        if folder:
            self.output_edit.setText(folder)

    def updated_settings(self) -> AppSettings:
        return AppSettings(
            model_name=self.model_combo.currentData(),
            language=self.language_combo.currentData(),
            output_folder=self.output_edit.text().strip(),
            openai_api_key=self.api_key_edit.text().strip(),
            openai_model=self.openai_model_edit.text().strip() or "gpt-5",
            translation_mode="openai",
            theme="dark" if self.theme_combo.currentData() == "dark" else "light",
            confirm_translation=self.confirm_translation_check.isChecked(),
            ui_language=self.ui_language_combo.currentData(),
        )


class ExportDialog(QDialog):
    """Export panel: TXT / SRT / DOCX for the Italian text and the English translation."""

    def __init__(
        self,
        parent: QWidget | None,
        flags: dict[str, bool],
        output_folder: str,
    ) -> None:
        super().__init__(parent)
        self.setWindowTitle(tr("export.window"))
        self.setMinimumWidth(560)
        self.flags = flags
        self.output_folder = output_folder

        root = QVBoxLayout(self)
        root.setContentsMargins(18, 16, 18, 16)
        root.setSpacing(12)

        title = QLabel(tr("export.title"))
        title.setStyleSheet("font-size: 17px; font-weight: 700;")
        root.addWidget(title)

        intro = QLabel(tr("export.intro"))
        intro.setObjectName("muted")
        intro.setWordWrap(True)
        root.addWidget(intro)

        grid = QGridLayout()
        grid.setHorizontalSpacing(10)
        grid.setVerticalSpacing(10)
        grid.addWidget(QLabel(""), 0, 0)
        grid.addWidget(QLabel(tr("pane.italian")), 0, 1)
        grid.addWidget(QLabel(tr("pane.english")), 0, 2)
        for row, kind in enumerate(("txt", "srt", "docx"), start=1):
            grid.addWidget(QLabel(kind.upper()), row, 0)
            for col, lang in ((1, "it"), (2, "en")):
                key = f"{lang}_{kind}"
                button = QPushButton(tr("export.button", fmt=kind.upper()))
                button.setObjectName("secondary")
                button.setEnabled(flags.get(key, False))
                button.clicked.connect(
                    lambda checked=False, k=key: self.request_export(k)
                )
                grid.addWidget(button, row, col)
        root.addLayout(grid)

        folder_row = QHBoxLayout()
        folder_label = QLabel(tr("export.folder"))
        folder_label.setObjectName("muted")
        self.folder_label = QLabel(output_folder or tr("export.folder_default"))
        self.folder_label.setObjectName("muted")
        self.folder_label.setWordWrap(True)
        open_button = QPushButton(tr("action.open_folder"))
        open_button.setObjectName("ghost")
        open_button.clicked.connect(self.open_folder)
        folder_row.addWidget(folder_label)
        folder_row.addWidget(self.folder_label, stretch=1)
        folder_row.addWidget(open_button)
        root.addLayout(folder_row)

        close_button = QPushButton(tr("action.close"))
        close_button.setObjectName("secondary")
        close_button.clicked.connect(self.accept)
        buttons = QHBoxLayout()
        buttons.addStretch()
        buttons.addWidget(close_button)
        root.addLayout(buttons)

        self._export_requested: str | None = None

    def open_folder(self) -> None:
        folder = self.output_folder or str(Path.home())
        QDesktopServices.openUrl(QUrl.fromLocalFile(folder))

    def request_export(self, kind: str) -> None:
        self._export_requested = kind
        self.accept()

    def requested_export(self) -> str | None:
        return self._export_requested


class TranslationConfirmDialog(QDialog):
    """Confirms what is sent to OpenAI: the text only, never the audio."""

    def __init__(
        self, parent: QWidget | None, sentences: int, characters: int, model: str
    ) -> None:
        super().__init__(parent)
        self.setWindowTitle(tr("action.translate"))
        self.setMinimumWidth(480)

        root = QVBoxLayout(self)
        root.setContentsMargins(20, 18, 20, 18)
        root.setSpacing(12)

        title = QLabel(tr("confirm.title"))
        title.setStyleSheet("font-size: 17px; font-weight: 700;")
        root.addWidget(title)

        body = QLabel(
            tr(
                "confirm.body",
                sentences=tr_n("work.sentences", sentences),
                chars=i18n.format_int(characters),
                model=escape(model),
            )
        )
        body.setWordWrap(True)
        root.addWidget(body)

        self.dont_ask = QCheckBox(tr("confirm.dont_ask"))
        root.addWidget(self.dont_ask)

        send_button = QPushButton(tr("confirm.send"))
        cancel_button = QPushButton(tr("action.cancel"))
        cancel_button.setObjectName("secondary")
        send_button.clicked.connect(self.accept)
        cancel_button.clicked.connect(self.reject)
        send_button.setDefault(True)
        buttons = QHBoxLayout()
        buttons.addStretch()
        buttons.addWidget(cancel_button)
        buttons.addWidget(send_button)
        root.addLayout(buttons)

    def dont_ask_again(self) -> bool:
        return self.dont_ask.isChecked()


class AboutDialog(QDialog):
    """Credit, privacy, accuracy and license summary, reachable from the main window."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle(tr("header.about"))
        self.setMinimumWidth(560)

        root = QVBoxLayout(self)
        root.setContentsMargins(20, 18, 20, 18)
        root.setSpacing(12)

        head = QHBoxLayout()
        logo = QLabel()
        logo.setPixmap(_logo_pixmap(56))
        head.addWidget(logo)
        title_box = QVBoxLayout()
        title = QLabel(f"AudioTranscriptor {__version__}")
        title.setStyleSheet("font-size: 19px; font-weight: 700;")
        author = QLabel(
            f'{escape(tr("about.made_by", author=AUTHOR))} · '
            f'<a href="{PROJECT_URL}">{PROJECT_URL.replace("https://", "")}</a>'
        )
        author.setObjectName("muted")
        author.setOpenExternalLinks(True)
        title_box.addWidget(title)
        title_box.addWidget(author)
        head.addLayout(title_box, stretch=1)
        root.addLayout(head)

        # Read legal texts shipped with the app, not unverified website routes.
        # The legal documents themselves are in English, whatever the interface.
        urls = {}
        for name in ("LICENSE", "PRIVACY.md", "TERMS.md", "THIRD_PARTY_NOTICES.md"):
            path = legal_document_path(name)
            urls[name] = escape(path.as_uri() if path else PROJECT_URL, quote=True)

        def link(name: str, key: str) -> str:
            return f'<a href="{urls[name]}">{escape(tr(key))}</a>'

        body = QLabel(
            f"<p><b>{tr('about.privacy_title')}</b> "
            f"{tr('about.privacy_body', translate=escape(tr('action.translate')))} "
            f"{link('PRIVACY.md', 'about.privacy_link')}.</p>"
            f"<p><b>{tr('about.accuracy_title')}</b> {tr('about.accuracy_body')} "
            f"{link('TERMS.md', 'about.terms_link')}.</p>"
            f"<p><b>{tr('about.license_title')}</b> "
            f"{tr('about.license_body', license=LICENSE_NAME)} "
            f"{link('LICENSE', 'about.license_link')} · "
            f"{link('THIRD_PARTY_NOTICES.md', 'about.third_party_link')} "
            f"{tr('about.third_party_list')} · {tr('about.permissions')} "
            f'<a href="{PROJECT_URL}">aversa.design</a>.</p>'
        )
        body.setWordWrap(True)
        body.setOpenExternalLinks(True)
        body.setTextInteractionFlags(Qt.TextInteractionFlag.TextBrowserInteraction)
        root.addWidget(body, stretch=1)

        close_button = QPushButton(tr("action.close"))
        close_button.clicked.connect(self.accept)
        buttons = QHBoxLayout()
        buttons.addStretch()
        buttons.addWidget(close_button)
        root.addLayout(buttons)


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle(f"AudioTranscriptor {__version__}")
        self.resize(1120, 780)
        self.setMinimumSize(980, 660)
        self.setWindowIcon(QIcon(_logo_pixmap(64)))

        self.settings_store = SettingsStore()
        self.settings = self.settings_store.load()
        self.apply_language()
        self.thread_pool = QThreadPool.globalInstance()
        self.current_worker: BaseWorker | None = None
        self.selected_file: Path | None = None
        self.transcript_segments: list[TranscriptSegment] = []
        self.translation_segments: list[TranscriptSegment] = []
        self._last_output_folder: Path | None = None
        self._status_kind = "idle"
        self._file_duration: float | None = None
        # What is on screen, kept as i18n keys so a language switch can redraw it.
        self._status: tuple[str, dict] = ("status.ready", {})
        self._error: tuple[str | None, str] | None = None
        self._success: tuple[str, str] | None = None
        self._chip_state = "idle"

        # Status row
        self.status_label = QLabel()
        self.status_dot = _dot_label("#c4cbd9")
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        # The status line carries the measured progress (minutes, sentences);
        # a percentage drawn on the bar was low-contrast and redundant.
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setFixedHeight(8)
        self.progress_bar.hide()
        self.cancel_button = QPushButton()
        self.cancel_button.setObjectName("danger")
        self.cancel_button.clicked.connect(self.cancel_process)

        # Header
        self.about_button = QPushButton()
        self.about_button.setObjectName("ghost")
        self.about_button.clicked.connect(self.show_about)
        self.settings_button = QPushButton()
        self.settings_button.setObjectName("ghost")
        self.settings_button.clicked.connect(self.open_settings)

        # Upload card
        self.hero_icon = QLabel()
        icon = _upload_icon(88)
        if icon is not None:
            self.hero_icon.setPixmap(icon)
        else:
            self.hero_icon.setText("↑")
            self.hero_icon.setStyleSheet(
                "font-size: 44px; color: #1d45f5; background: #e8ecff; "
                "border-radius: 22px; min-width: 88px; min-height: 88px;"
            )
        self.hero_title = QLabel()
        self.hero_title.setObjectName("heroTitle")
        self.hero_hint = QLabel("MP3 · WAV · M4A · MP4 · MOV · MKV")
        self.hero_hint.setObjectName("muted")
        self.select_button = QPushButton()
        self.select_button.setObjectName("secondary")
        self.select_button.clicked.connect(self.choose_file)

        self.file_icon = QLabel("🎞️")
        self.file_icon.setStyleSheet("font-size: 18px;")
        self.filename_label = QLabel()
        self.filename_label.setStyleSheet("font-weight: 600;")
        self.file_meta_label = QLabel("")
        self.file_meta_label.setObjectName("muted")
        self.model_chip = QFrame()
        self.model_chip.setObjectName("chip")
        chip_layout = QHBoxLayout(self.model_chip)
        chip_layout.setContentsMargins(10, 4, 10, 4)
        chip_layout.setSpacing(6)
        self.model_dot = _dot_label("#c4cbd9")
        self.model_chip_label = QLabel()
        self.model_chip_label.setObjectName("chipText")
        chip_layout.addWidget(self.model_dot)
        chip_layout.addWidget(self.model_chip_label)
        chip_layout.addStretch()
        self.remove_file_button = QPushButton("×")
        self.remove_file_button.setObjectName("ghost")
        self.remove_file_button.setFixedSize(24, 24)
        # The global button padding would leave no room for the glyph.
        self.remove_file_button.setStyleSheet(
            "padding: 0; font-size: 16px; font-weight: 600; border-radius: 12px;"
        )
        self.remove_file_button.clicked.connect(self.clear_file)
        chip_layout.addWidget(self.remove_file_button)
        self.transcribe_button = QPushButton()
        self.transcribe_button.clicked.connect(self.start_transcription)
        self.change_file_button = QPushButton()
        self.change_file_button.setObjectName("secondary")
        self.change_file_button.clicked.connect(self.choose_file)

        # Work area
        self.work_title = QLabel()
        self.work_title.setObjectName("cardTitle")
        self.work_stats = QLabel("")
        self.work_stats.setObjectName("muted")
        self.translate_button = QPushButton()
        self.translate_button.clicked.connect(self.start_translation)
        self.export_button = QPushButton()
        self.export_button.setObjectName("secondary")
        self.export_button.clicked.connect(self.open_export_dialog)

        self.italian_text = QTextEdit()
        self.italian_text.textChanged.connect(self.update_actions)
        self.italian_text.textChanged.connect(self.update_stats)
        self.english_text = QTextEdit()
        self.english_text.textChanged.connect(self.update_actions)
        self.english_text.textChanged.connect(self.update_stats)

        self.it_pane_title = QLabel()
        self.it_pane_title.setObjectName("paneTitle")
        self.en_pane_title = QLabel()
        self.en_pane_title.setObjectName("paneTitle")
        self.it_pane_count = QLabel("")
        self.it_pane_count.setObjectName("muted")
        self.en_pane_count = QLabel("")
        self.en_pane_count.setObjectName("muted")

        # Player: listen while correcting. QtMultimedia is created lazily on the
        # first play, so tests, screenshots and machines without an audio
        # backend never pay for it.
        self.player = None
        self._audio_output = None
        self._player_failed = False
        self._player_source: Path | None = None
        self._pending_seek_ms: int | None = None
        self._spans: dict[str, list] = {"it": [], "en": []}
        self._spans_dirty = True
        self._highlighted: dict[str, int | None] = {"it": None, "en": None}
        self._slider_dragging = False
        self.play_button = QPushButton()
        self.play_button.setObjectName("secondary")
        self.play_button.clicked.connect(self.toggle_playback)
        self.back_button = QPushButton("−5 s")
        self.back_button.setObjectName("ghost")
        self.back_button.clicked.connect(lambda: self.seek_relative(-5))
        self.forward_button = QPushButton("+5 s")
        self.forward_button.setObjectName("ghost")
        self.forward_button.clicked.connect(lambda: self.seek_relative(5))
        self.from_cursor_button = QPushButton()
        self.from_cursor_button.setObjectName("ghost")
        self.from_cursor_button.clicked.connect(self.play_from_cursor)
        self.position_slider = QSlider(Qt.Orientation.Horizontal)
        self.position_slider.setRange(0, 0)
        self.position_slider.sliderPressed.connect(self._on_slider_pressed)
        self.position_slider.sliderReleased.connect(self._on_slider_released)
        self.time_label = QLabel("0:00")
        self.time_label.setObjectName("muted")
        self.shortcut_hint = QLabel()
        self.shortcut_hint.setObjectName("muted")
        self.shortcut_hint.setStyleSheet("font-size: 12px;")
        self.player_timer = QTimer(self)
        self.player_timer.setInterval(150)
        self.player_timer.timeout.connect(self._on_player_tick)
        self.italian_text.textChanged.connect(self._mark_spans_dirty)
        self.english_text.textChanged.connect(self._mark_spans_dirty)
        # Esc is free in a text editor and is what transcription tools use;
        # Ctrl maps to Cmd on macOS.
        self.shortcut_play = QKeySequence(Qt.Key.Key_Escape)
        self.shortcut_jump = QKeySequence("Ctrl+J")
        self.shortcut_back = QKeySequence("Ctrl+[")
        self.shortcut_forward = QKeySequence("Ctrl+]")
        for sequence, slot in (
            (self.shortcut_play, self.toggle_playback),
            (self.shortcut_jump, self.play_from_cursor),
            (self.shortcut_back, lambda: self.seek_relative(-5)),
            (self.shortcut_forward, lambda: self.seek_relative(5)),
        ):
            QShortcut(sequence, self, activated=slot)

        # Banners
        self.error_label = QLabel("")
        self.error_label.setWordWrap(True)
        self.error_dismiss = QPushButton()
        self.error_dismiss.setObjectName("secondary")
        self.error_dismiss.clicked.connect(self.hide_error_banner)
        self.success_label = QLabel("")
        self.success_label.setWordWrap(True)
        self.open_folder_button = QPushButton()
        self.open_folder_button.setObjectName("success")
        self.open_folder_button.clicked.connect(self.open_output_folder)

        self.setCentralWidget(self.build_layout())
        self.apply_theme()
        self.retranslate_ui()
        self.update_actions()

    def build_layout(self) -> QWidget:
        root = QWidget()
        layout = QVBoxLayout(root)
        layout.setContentsMargins(26, 16, 26, 18)
        layout.setSpacing(12)

        # --- Header bar -----------------------------------------------------
        header = QHBoxLayout()
        header.setSpacing(10)
        logo = QLabel()
        logo.setPixmap(_logo_pixmap(34))
        logo.setObjectName("logo")
        wordmark = QLabel("AudioTranscriptor")
        wordmark.setStyleSheet("font-size: 18px; font-weight: 700;")
        header.addWidget(logo)
        header.addWidget(wordmark)
        header.addStretch()
        header.addWidget(self.about_button)
        header.addWidget(self.settings_button)
        layout.addLayout(header)

        # --- Upload card -----------------------------------------------------
        self.drop_zone = DropZone()
        self.drop_zone.fileDropped.connect(self.set_selected_file)
        layout.addWidget(self.drop_zone)

        # Hero (empty) panel
        self.hero_panel = QWidget()
        hero_box = QVBoxLayout(self.hero_panel)
        hero_box.setContentsMargins(18, 14, 18, 14)
        hero_box.setSpacing(10)
        hero_box.setAlignment(Qt.AlignmentFlag.AlignCenter)
        hero_icon_row = QHBoxLayout()
        hero_icon_row.addStretch()
        hero_icon_row.addWidget(self.hero_icon)
        hero_icon_row.addStretch()
        hero_box.addLayout(hero_icon_row)
        hero_box.addWidget(self.hero_title, alignment=Qt.AlignmentFlag.AlignCenter)
        hero_box.addWidget(self.hero_hint, alignment=Qt.AlignmentFlag.AlignCenter)
        hero_box.addSpacing(4)
        hero_box.addWidget(self.select_button, alignment=Qt.AlignmentFlag.AlignCenter)
        self.drop_zone.vbox().addWidget(self.hero_panel)

        # Selected-file panel
        self.file_panel = QWidget()
        file_box = QVBoxLayout(self.file_panel)
        file_box.setContentsMargins(14, 12, 14, 12)
        file_box.setSpacing(10)
        row1 = QHBoxLayout()
        row1.setSpacing(8)
        row1.addWidget(self.file_icon)
        file_info = QVBoxLayout()
        file_info.setSpacing(0)
        file_info.addWidget(self.filename_label)
        file_info.addWidget(self.file_meta_label)
        row1.addLayout(file_info, stretch=1)
        row1.addWidget(self.model_chip)
        file_box.addLayout(row1)
        row2 = QHBoxLayout()
        row2.setSpacing(8)
        row2.addWidget(self.change_file_button)
        row2.addStretch()
        row2.addWidget(self.transcribe_button)
        file_box.addLayout(row2)
        self.drop_zone.vbox().addWidget(self.file_panel)

        # --- Status card -----------------------------------------------------
        status_card, status_layout = _card("")
        self.status_title = status_card.heading
        status_row = QHBoxLayout()
        status_row.setSpacing(8)
        status_row.addWidget(self.status_dot)
        status_row.addWidget(self.status_label, stretch=1)
        status_row.addWidget(self.cancel_button)
        status_layout.addLayout(status_row)
        progress_row = QHBoxLayout()
        progress_row.addWidget(self.progress_bar, stretch=1)
        status_layout.addLayout(progress_row)
        layout.addWidget(status_card)

        # --- Error banner (micro-state) -------------------------------------
        self.error_banner = QFrame()
        self.error_banner.setObjectName("bannerError")
        error_layout = QHBoxLayout(self.error_banner)
        error_layout.setContentsMargins(12, 8, 12, 8)
        error_layout.setSpacing(8)
        error_title = QLabel("⚠")
        error_layout.addWidget(error_title)
        error_layout.addWidget(self.error_label, stretch=1)
        error_layout.addWidget(self.error_dismiss)
        self.error_banner.hide()
        layout.addWidget(self.error_banner)

        # --- Work card --------------------------------------------------------
        work_card, work_layout = _card()
        work_head = QHBoxLayout()
        work_head.setSpacing(10)
        work_head.addWidget(self.work_title)
        work_head.addWidget(self.work_stats, stretch=1)
        work_head.addWidget(self.translate_button)
        work_head.addWidget(self.export_button)
        work_layout.addLayout(work_head)

        self.player_bar = QWidget()
        player_box = QVBoxLayout(self.player_bar)
        player_box.setContentsMargins(0, 0, 0, 0)
        player_box.setSpacing(2)
        player_row = QHBoxLayout()
        player_row.setSpacing(8)
        player_row.addWidget(self.play_button)
        player_row.addWidget(self.back_button)
        player_row.addWidget(self.forward_button)
        player_row.addWidget(self.position_slider, stretch=1)
        player_row.addWidget(self.time_label)
        player_row.addWidget(self.from_cursor_button)
        player_box.addLayout(player_row)
        player_box.addWidget(self.shortcut_hint)
        self.player_bar.hide()
        work_layout.addWidget(self.player_bar)

        self.work_splitter = QSplitter()
        self.work_splitter.setChildrenCollapsible(False)

        # Italian pane (card-in-card wrapper)
        it_pane = QFrame()
        it_pane.setObjectName("card")
        it_vbox = QVBoxLayout(it_pane)
        it_vbox.setContentsMargins(12, 10, 12, 10)
        it_vbox.setSpacing(4)
        it_head = QHBoxLayout()
        it_head.addWidget(self.it_pane_title)
        it_head.addStretch()
        it_head.addWidget(self.it_pane_count)
        it_vbox.addLayout(it_head)
        it_vbox.addWidget(self.italian_text, stretch=1)

        # English pane
        self.en_pane = QFrame()
        self.en_pane.setObjectName("card")
        en_vbox = QVBoxLayout(self.en_pane)
        en_vbox.setContentsMargins(12, 10, 12, 10)
        en_vbox.setSpacing(4)
        en_head = QHBoxLayout()
        en_head.addWidget(self.en_pane_title)
        en_head.addStretch()
        en_head.addWidget(self.en_pane_count)
        en_vbox.addLayout(en_head)
        en_vbox.addWidget(self.english_text, stretch=1)
        self.en_pane.hide()

        self.work_splitter.addWidget(it_pane)
        self.work_splitter.addWidget(self.en_pane)
        self.work_splitter.setSizes([1, 1])
        work_layout.addWidget(self.work_splitter, stretch=1)
        layout.addWidget(work_card, stretch=1)

        # --- Success banner ----------------------------------------------------
        self.success_banner = QFrame()
        self.success_banner.setObjectName("bannerOk")
        success_layout = QHBoxLayout(self.success_banner)
        success_layout.setContentsMargins(12, 8, 12, 8)
        success_layout.setSpacing(8)
        ok_title = QLabel("✓")
        ok_title.setStyleSheet(f"color: {SUCCESS}; font-weight: 700;")
        success_layout.addWidget(ok_title)
        success_layout.addWidget(self.success_label, stretch=1)
        success_layout.addWidget(self.open_folder_button)
        self.success_banner.hide()
        layout.addWidget(self.success_banner)

        # --- Footer -------------------------------------------------------------
        footer = QLabel()
        self.footer_label = footer
        footer.setAlignment(Qt.AlignmentFlag.AlignCenter)
        footer.setObjectName("muted")
        footer.setStyleSheet("padding-top: 4px;")
        layout.addWidget(footer)

        self.populate_hero()
        return root

    # --- Upload card states -------------------------------------------------
    def populate_hero(self) -> None:
        if self.selected_file is None:
            self.file_panel.hide()
            self.hero_panel.show()
            self.drop_zone.setMinimumHeight(150)
            return
        self.filename_label.setText(self.selected_file.name)
        parts: list[str] = []
        try:
            parts.append(_fmt_size(self.selected_file.stat().st_size))
        except OSError:
            pass
        if self._file_duration:
            parts.append(tr("file.duration", time=_fmt_time(self._file_duration)))
        self.file_meta_label.setText(" · ".join(parts))
        self.file_meta_label.setVisible(bool(parts))
        self._chip_state = "idle"
        self._render_chip()
        self.hero_panel.hide()
        self.file_panel.show()
        self.drop_zone.setMinimumHeight(84)

    # --- Public actions ------------------------------------------------------
    def closeEvent(self, event) -> None:
        # Ask a running worker to stop before the window is torn down, so its
        # thread does not try to emit on already-destroyed signals.
        if self.current_worker is not None:
            self.current_worker.cancel()
        self.stop_playback()
        super().closeEvent(event)

    def apply_theme(self) -> None:
        QApplication.instance().setStyleSheet(
            DARK_STYLE if self.settings.theme == "dark" else LIGHT_STYLE
        )

    def apply_language(self) -> None:
        i18n.set_language(
            i18n.resolve_language(self.settings.ui_language, system_ui_languages())
        )

    def retranslate_ui(self) -> None:
        """Set every visible string from the current language, keeping the state."""
        self.about_button.setText(tr("header.about"))
        self.settings_button.setText(tr("header.settings"))
        self.hero_title.setText(tr("hero.title"))
        self.select_button.setText(tr("hero.choose"))
        if self.selected_file is None:
            self.filename_label.setText(tr("file.none"))
        self.remove_file_button.setToolTip(tr("file.remove"))
        self.remove_file_button.setAccessibleName(tr("file.remove"))
        self.transcribe_button.setText(tr("action.transcribe"))
        self.change_file_button.setText(tr("file.change"))
        self.cancel_button.setText(tr("action.cancel_job"))
        self.status_title.setText(tr("status.title"))
        self.work_title.setText(tr("work.title"))
        self.translate_button.setText(tr("action.translate"))
        self.export_button.setText(tr("action.export"))
        self.italian_text.setPlaceholderText(tr("placeholder.italian"))
        self.english_text.setPlaceholderText(tr("placeholder.english"))
        self.it_pane_title.setText(tr("pane.italian"))
        self.en_pane_title.setText(tr("pane.english"))
        self.error_dismiss.setText(tr("action.close"))
        self.open_folder_button.setText(tr("action.open_folder"))
        self.footer_label.setText(tr("footer", author=AUTHOR))
        self._render_play_button()
        self.from_cursor_button.setText(tr("player.from_cursor"))
        self.back_button.setToolTip(tr("player.back"))
        self.back_button.setAccessibleName(tr("player.back"))
        self.forward_button.setToolTip(tr("player.forward"))
        self.forward_button.setAccessibleName(tr("player.forward"))
        self.position_slider.setAccessibleName(tr("player.position"))
        native = QKeySequence.SequenceFormat.NativeText
        self.shortcut_hint.setText(
            tr(
                "player.shortcuts",
                play=self.shortcut_play.toString(native),
                jump=self.shortcut_jump.toString(native),
                back=self.shortcut_back.toString(native),
                fwd=self.shortcut_forward.toString(native),
            )
        )
        key, params = self._status
        self.status_label.setText(tr(key, **params))
        if self._error is not None:
            self.error_label.setText(self._error_text())
        if self._success is not None:
            name, folder = self._success
            self.success_label.setText(tr("success.saved", name=name, folder=folder))
        if self.selected_file is not None:
            self.populate_hero()
        self._render_chip()
        self.update_stats()

    def _render_chip(self) -> None:
        name = self.settings.model_name
        if self._chip_state == "downloading":
            text, color = tr("chip.downloading", name=name), ACCENT
        elif self._chip_state == "loading":
            text, color = tr("chip.loading", name=name), ACCENT
        elif self._chip_state == "ready":
            text, color = tr("chip.model", name=name), SUCCESS
        else:
            text, color = tr("chip.model", name=name), "#c4cbd9"
        if getattr(self, "_chip_style", None) != (text, color):
            self._chip_style = (text, color)
            self.model_chip_label.setText(text)
            self.model_dot.setStyleSheet(f"background: {color}; border-radius: 5px;")

    def choose_file(self) -> None:
        path, _ = QFileDialog.getOpenFileName(
            self,
            tr("dialog.open_media"),
            "",
            f"{tr('dialog.media_filter')} (*.mp3 *.wav *.m4a *.mp4 *.mov *.mkv)",
        )
        if path:
            self.set_selected_file(path)

    def set_selected_file(self, path: str) -> None:
        if self.current_worker is not None:
            return
        candidate = Path(path)
        if not is_supported_media(candidate):
            self.show_error_key("error.unsupported")
            return
        self.stop_playback()
        self.selected_file = candidate
        self._file_duration = probe_duration(candidate)
        self.hide_error_banner()
        self.set_status("status.file_selected", "idle")
        self.progress_bar.setValue(0)
        self.populate_hero()
        self.update_actions()

    def clear_file(self) -> None:
        self.stop_playback()
        self.selected_file = None
        self._file_duration = None
        self.transcript_segments = []
        self.translation_segments = []
        self.italian_text.clear()
        self.english_text.clear()
        self.en_pane.hide()
        self.success_banner.hide()
        self._success = None
        self.hide_error_banner()
        self.filename_label.setText(tr("file.none"))
        self.set_status("status.ready", "idle")
        self.progress_bar.setValue(0)
        self.populate_hero()
        self.update_actions()

    def show_about(self) -> None:
        AboutDialog(self).exec()

    def open_settings(self) -> None:
        dialog = SettingsDialog(self.settings, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.settings = dialog.updated_settings()
            self.settings_store.save(self.settings)
            self.apply_theme()
            self.apply_language()
            self.retranslate_ui()
            # refresh theme-dependent inline colours, keeping the current state
            key, params = self._status
            self.set_status(key, self._status_kind, params)
            if self._status_kind == "busy":
                self.set_status_dot_busy()
            self.update_actions()

    # --- Workers -------------------------------------------------------------
    def start_transcription(self) -> None:
        if self.selected_file is None:
            return
        if not self.ensure_disk_space(self.selected_file):
            self.show_error_key("error.disk_precheck")
            return
        self.hide_error_banner()
        self.stop_playback()
        self.set_processing("status.preparing_audio", 0)
        self.italian_text.clear()
        self.english_text.clear()
        self.translation_segments = []
        self.transcript_segments = []
        self.en_pane.hide()
        worker = TranscriptionWorker(self.selected_file, self.settings)
        worker.signals.progress.connect(self.set_processing)
        worker.signals.transcribed.connect(self.on_transcribed)
        worker.signals.error.connect(self.show_error)
        worker.signals.finished.connect(self.on_worker_finished)
        self.current_worker = worker
        self.update_actions()
        self.thread_pool.start(worker)

    def start_translation(self) -> None:
        text = self.italian_text.toPlainText().strip()
        if not text:
            return
        if not self.settings.openai_api_key.strip():
            self.show_error_key("error.api_key")
            return
        self.hide_error_banner()
        self.sync_edited_transcript_to_segments(text)
        if self.settings.confirm_translation and not self.confirm_translation_send(text):
            return
        self.set_processing("progress.translating", 0)
        worker = TranslationWorker(text, self.transcript_segments, self.settings)
        worker.signals.progress.connect(self.set_processing)
        worker.signals.translated.connect(self.on_translated)
        worker.signals.error.connect(self.show_error)
        worker.signals.finished.connect(self.on_worker_finished)
        self.current_worker = worker
        self.update_actions()
        self.thread_pool.start(worker)

    def confirm_translation_send(self, text: str) -> bool:
        """Say exactly what leaves the computer before it leaves."""
        dialog = TranslationConfirmDialog(
            self,
            sentences=len(self.transcript_segments),
            characters=len(text),
            model=self.settings.openai_model,
        )
        accepted = dialog.exec() == QDialog.DialogCode.Accepted
        if accepted and dialog.dont_ask_again():
            self.settings.confirm_translation = False
            self.settings_store.save(self.settings)
        return accepted

    def cancel_process(self) -> None:
        if self.current_worker is not None:
            self.current_worker.cancel()
            self.set_status("status.cancelling", "warn")

    def on_transcribed(self, result) -> None:
        self.transcript_segments = result.segments
        self.italian_text.setPlainText(result.text)
        self.set_status("progress.transcribed", "ok")
        self.progress_bar.setValue(100)
        self._chip_state = "ready"
        self._render_chip()
        self.update_actions()
        self.update_stats()

    def on_translated(self, result) -> None:
        self.translation_segments = result.segments
        self.english_text.setPlainText(result.text)
        self.en_pane.show()
        self.work_splitter.setSizes([1, 1])
        self.set_status("progress.translated", "ok")
        self.progress_bar.setValue(100)
        self.update_actions()
        self.update_stats()

    def on_worker_finished(self) -> None:
        self.current_worker = None
        self.update_actions()

    # --- Player --------------------------------------------------------------
    def _ensure_player(self) -> bool:
        """Create the media player on first use and load the selected file."""
        if self._player_failed or self.selected_file is None:
            return False
        if self.player is None:
            try:
                from PySide6.QtMultimedia import QAudioOutput, QMediaDevices, QMediaPlayer
            except ImportError:
                self._player_unavailable()
                return False
            if not QMediaDevices.audioOutputs():
                # No speakers or headphones right now: say so, but allow a retry
                # once a device is connected.
                self.show_error_key("player.unavailable")
                return False
            self.player = QMediaPlayer(self)
            self._audio_output = QAudioOutput(self)
            self.player.setAudioOutput(self._audio_output)
            self.player.durationChanged.connect(
                lambda ms: self.position_slider.setRange(0, max(0, int(ms)))
            )
            self.player.playbackStateChanged.connect(self._on_playback_state)
            self.player.mediaStatusChanged.connect(self._on_media_status)
            self.player.errorOccurred.connect(self._on_player_error)
        if self._player_source != self.selected_file:
            self._pending_seek_ms = None
            self.player.setSource(QUrl.fromLocalFile(str(self.selected_file)))
            self._player_source = self.selected_file
        return True

    def _on_playback_state(self, _state) -> None:
        # The state arrives asynchronously after play()/pause(): drive the
        # refresh timer from here, not from the call site.
        if self.is_playing():
            self.player_timer.start()
        else:
            self.player_timer.stop()
            self._on_player_tick()
        self._render_play_button()

    def _on_media_status(self, status) -> None:
        from PySide6.QtMultimedia import QMediaPlayer

        loaded = (
            QMediaPlayer.MediaStatus.LoadedMedia,
            QMediaPlayer.MediaStatus.BufferingMedia,
            QMediaPlayer.MediaStatus.BufferedMedia,
        )
        if status in loaded and self._pending_seek_ms is not None:
            self.player.setPosition(self._pending_seek_ms)
            self._pending_seek_ms = None

    def _on_player_error(self, error, message: str = "") -> None:
        if getattr(error, "value", error):  # NoError is 0
            self._player_unavailable()

    def _player_unavailable(self) -> None:
        self._player_failed = True
        self.stop_playback()
        self.show_error_key("player.unavailable")

    def is_playing(self) -> bool:
        if self.player is None:
            return False
        from PySide6.QtMultimedia import QMediaPlayer

        return self.player.playbackState() == QMediaPlayer.PlaybackState.PlayingState

    def toggle_playback(self) -> None:
        if not self.player_bar.isVisible() or not self._ensure_player():
            return
        if self.is_playing():
            self.player.pause()
        else:
            self.player.play()

    def play_from_cursor(self) -> None:
        """Start listening at the sentence under the text cursor."""
        if not self.player_bar.isVisible():
            return
        editor, lang = (
            (self.english_text, "en") if self.english_text.hasFocus() else (self.italian_text, "it")
        )
        spans = self._current_spans(lang)
        line = editor.textCursor().blockNumber()
        start = next(
            (span[0] for span in reversed(spans[: line + 1]) if span is not None), None
        )
        if start is None:
            start = next((span[0] for span in spans if span is not None), 0.0)
        self.seek_to(start, play=True)

    def seek_relative(self, seconds: float) -> None:
        if not self.player_bar.isVisible():
            return
        self.seek_to(max(0.0, self._position_seconds() + seconds), play=None)

    def seek_to(self, seconds: float, play: bool | None) -> None:
        """Move playback to ``seconds``; play=True starts it, None keeps the state."""
        if not self._ensure_player():
            return
        from PySide6.QtMultimedia import QMediaPlayer

        target = int(seconds * 1000)
        if self.player.mediaStatus() in (
            QMediaPlayer.MediaStatus.NoMedia,
            QMediaPlayer.MediaStatus.LoadingMedia,
        ):
            # A seek before the file is loaded is ignored by Qt: apply it on load.
            self._pending_seek_ms = target
        else:
            self.player.setPosition(target)
        if play:
            self.player.play()
        self._on_player_tick(seconds)

    def stop_playback(self) -> None:
        self.player_timer.stop()
        if self.player is not None:
            self.player.stop()
        self._clear_highlight()
        self.position_slider.setValue(0)
        self._render_play_button()

    def _position_seconds(self) -> float:
        if self.player is not None:
            if self._pending_seek_ms is not None:
                return self._pending_seek_ms / 1000
            return self.player.position() / 1000
        return self.position_slider.value() / 1000

    def _on_slider_pressed(self) -> None:
        self._slider_dragging = True

    def _on_slider_released(self) -> None:
        self._slider_dragging = False
        self.seek_to(self.position_slider.value() / 1000, play=None)

    def _on_player_tick(self, seconds: float | None = None) -> None:
        position = self._position_seconds() if seconds is None else seconds
        if not self._slider_dragging:
            self.position_slider.setValue(int(position * 1000))
        self._render_time(position)
        for lang, editor in (("it", self.italian_text), ("en", self.english_text)):
            self._highlight_line(lang, editor, line_at_time(self._current_spans(lang), position))

    def _render_time(self, position: float) -> None:
        total = self._file_duration
        if self.player is not None and self.player.duration() > 0:
            total = self.player.duration() / 1000
        text = _fmt_time(position)
        self.time_label.setText(f"{text} / {_fmt_time(total)}" if total else text)

    def _render_play_button(self) -> None:
        self.play_button.setText(tr("player.pause") if self.is_playing() else tr("player.play"))

    def _mark_spans_dirty(self) -> None:
        self._spans_dirty = True

    def _current_spans(self, lang: str) -> list:
        if self._spans_dirty:
            self._spans = {
                "it": line_time_spans(self.italian_text.toPlainText(), self.transcript_segments),
                "en": line_time_spans(self.english_text.toPlainText(), self.translation_segments),
            }
            self._spans_dirty = False
            self._highlighted = {"it": None, "en": None}
        return self._spans[lang]

    def _highlight_line(self, lang: str, editor: QTextEdit, line: int | None) -> None:
        if self._highlighted.get(lang) == line and editor.extraSelections():
            return
        self._highlighted[lang] = line
        if line is None:
            editor.setExtraSelections([])
            return
        block = editor.document().findBlockByNumber(line)
        if not block.isValid():
            editor.setExtraSelections([])
            return
        selection = QTextEdit.ExtraSelection()
        selection.format.setBackground(
            QColor(ACCENT_TINT if self.settings.theme == "light" else D_ACCENT_TINT)
        )
        selection.format.setProperty(QTextFormat.Property.FullWidthSelection, True)
        selection.cursor = QTextCursor(block)
        editor.setExtraSelections([selection])
        if self.is_playing():
            self._keep_visible(editor, selection.cursor)

    @staticmethod
    def _keep_visible(editor: QTextEdit, cursor: QTextCursor) -> None:
        """Scroll only when the spoken line leaves the view, never on every tick."""
        rect = editor.cursorRect(cursor)
        height = editor.viewport().height()
        if rect.top() < 0 or rect.bottom() > height:
            bar = editor.verticalScrollBar()
            bar.setValue(bar.value() + rect.top() - height // 3)

    def _clear_highlight(self) -> None:
        for lang, editor in (("it", self.italian_text), ("en", self.english_text)):
            self._highlighted[lang] = None
            editor.setExtraSelections([])

    # --- Status / progress / errors -----------------------------------------
    def set_status(self, key: str, kind: str, params: dict | None = None) -> None:
        colors = {
            "idle": "#c4cbd9",
            "busy": ACCENT if self.settings.theme == "light" else D_ACCENT,
            "ok": SUCCESS if self.settings.theme == "light" else D_SUCCESS,
            "warn": "#f0a020",
            "error": ERROR if self.settings.theme == "light" else D_ERROR,
        }
        self._status_kind = kind
        self._dot_color = colors.get(kind, "#c4cbd9")
        self._status = (key, dict(params or {}))
        self.status_label.setText(tr(key, **self._status[1]))
        self._refresh_dot(self._dot_color)
        # The bar is only useful while something runs: once the job is done
        # the space goes back to the transcript.
        self.progress_bar.setVisible(kind in ("busy", "warn"))

    def set_processing(self, key: str, progress: int, params: dict | None = None) -> None:
        self._status_kind = "busy"
        self._status = (key, dict(params or {}))
        self.status_label.setText(tr(key, **self._status[1]))
        self.set_status_dot_busy()
        self.progress_bar.setValue(progress)
        self.progress_bar.show()
        self.update_model_chip_from_status(key)

    def set_status_dot_busy(self) -> None:
        color = ACCENT if self.settings.theme == "light" else D_ACCENT
        self._dot_color = color
        self._refresh_dot(color)

    def _refresh_dot(self, color: str) -> None:
        # setStyleSheet re-polishes the widget: skip it when the color is
        # unchanged so per-segment progress ticks never jank the window.
        if getattr(self, "_dot_style", None) != color:
            self._dot_style = color
            self.status_dot.setStyleSheet(f"background: {color}; border-radius: 5px;")

    def update_model_chip_from_status(self, key: str) -> None:
        if key == "progress.downloading_model":
            self._chip_state = "downloading"
        elif key in ("progress.preparing_model", "progress.loading_model"):
            self._chip_state = "loading"
        elif self._chip_state in ("downloading", "loading"):
            self._chip_state = "idle"
        self._render_chip()

    def show_error(self, message: str) -> None:
        """Show an error raised by a worker (raw text, mapped to a known message)."""
        self._show_error(self.friendly_error(message), message)

    def show_error_key(self, key: str) -> None:
        self._show_error(key, "")

    def _show_error(self, key: str | None, raw: str) -> None:
        self._error = (key, raw)
        self.set_status("status.error", "error")
        self.progress_bar.setValue(0)
        self.success_banner.hide()
        self._success = None
        self.error_label.setText(self._error_text())
        self.error_banner.setObjectName("bannerError")
        self.error_banner.show()
        self.update_actions()

    def _error_text(self) -> str:
        key, raw = self._error or (None, "")
        if key is not None:
            return tr(key)
        return raw.splitlines()[0] if raw else tr("error.generic")

    def hide_error_banner(self) -> None:
        self._error = None
        self.error_banner.hide()

    @staticmethod
    def friendly_error(message: str) -> str | None:
        """Map a worker's raw message to an i18n key; None keeps the raw text."""
        lowered = message.lower()
        if "no space" in lowered or "disk" in lowered:
            return "error.disk"
        if "api key" in lowered:
            return "error.api_key"
        if "cancelled" in lowered:
            return "error.cancelled"
        if "model" in lowered and ("download" in lowered or "connection" in lowered):
            return "error.model_download"
        return None if message else "error.generic"

    # --- Actions -------------------------------------------------------------
    def update_actions(self) -> None:
        busy = self.current_worker is not None
        has_file = self.selected_file is not None
        has_it = bool(self.italian_text.toPlainText().strip())
        has_en = bool(self.english_text.toPlainText().strip())
        self.transcribe_button.setEnabled(has_file and not busy)
        self.change_file_button.setEnabled(not busy)
        self.remove_file_button.setEnabled(not busy)
        self.select_button.setEnabled(not busy)
        self.settings_button.setEnabled(not busy)
        self.translate_button.setEnabled(has_it and not busy)
        self.cancel_button.setEnabled(busy)
        self.export_button.setEnabled((has_it or has_en) and not busy)
        self.cancel_button.setVisible(busy)
        # The player needs timings, which only a transcription provides.
        can_listen = has_file and bool(self.transcript_segments) and not self._player_failed
        self.player_bar.setVisible(can_listen)
        if can_listen and not self.player_timer.isActive():
            self._render_time(self._position_seconds())

    def update_stats(self) -> None:
        it_text = self.italian_text.toPlainText()
        en_text = self.english_text.toPlainText()
        it_words = len(it_text.split())
        en_words = len(en_text.split())
        segments = len(self.transcript_segments)
        self.it_pane_count.setText(tr_n("work.words", it_words))
        self.en_pane_count.setText(tr_n("work.words", en_words))
        if segments:
            self.work_stats.setText(tr_n("work.sentences", segments))
        else:
            self.work_stats.setText("")

    def ensure_disk_space(self, media_path: Path) -> bool:
        try:
            target = Path(self.settings.output_folder) if self.settings.output_folder else media_path.parent
            usage = shutil.disk_usage(target if target.exists() else target.parent)
            return usage.free > media_path.stat().st_size * 2
        except OSError:
            return True

    def sync_edited_transcript_to_segments(self, text: str) -> None:
        if not self.transcript_segments:
            if text.strip():
                self.transcript_segments = [
                    TranscriptSegment(index=1, start=0, end=5, text=text.strip())
                ]
            return
        align_lines_to_segments(text, self.transcript_segments, "text")

    def sync_edited_translation_to_segments(self) -> None:
        align_lines_to_segments(
            self.english_text.toPlainText(),
            self.translation_segments,
            "translated_text",
        )

    def default_export_path(self, suffix: str) -> Path:
        stem = self.selected_file.stem if self.selected_file else "trascrizione"
        folder = Path(self.settings.output_folder) if self.settings.output_folder else (
            self.selected_file.parent if self.selected_file else Path.home()
        )
        return folder / f"{stem}_{suffix}"

    # --- Export --------------------------------------------------------------
    def export_flags(self) -> dict[str, bool]:
        """Which export formats are available right now (SRT needs real segments)."""
        has_it = bool(self.italian_text.toPlainText().strip())
        has_en = bool(self.english_text.toPlainText().strip())
        return {
            "it_txt": has_it,
            "it_docx": has_it,
            "it_srt": has_it and bool(self.transcript_segments),
            "en_txt": has_en,
            "en_docx": has_en,
            "en_srt": has_en and bool(self.translation_segments),
        }

    def open_export_dialog(self) -> None:
        flags = self.export_flags()
        if not any(flags.values()):
            return
        output_folder = self.settings.output_folder or (
            str(self.selected_file.parent) if self.selected_file else ""
        )
        dialog = ExportDialog(self, flags, output_folder)
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return
        kind = dialog.requested_export()
        if kind is None:
            return
        self.export_file(kind)

    def export_file(self, kind: str) -> None:
        default_map = {
            "it_txt": self.default_export_path("it.txt"),
            "en_txt": self.default_export_path("en.txt"),
            "it_srt": self.default_export_path("it.srt"),
            "en_srt": self.default_export_path("en.srt"),
            "it_docx": self.default_export_path("it.docx"),
            "en_docx": self.default_export_path("en.docx"),
        }
        default_path = default_map[kind]
        path, _ = QFileDialog.getSaveFileName(self, tr("dialog.save_file"), str(default_path))
        if not path:
            return
        try:
            target = Path(path)
            if kind == "it_txt":
                write_txt(target, self.italian_text.toPlainText())
            elif kind == "en_txt":
                write_txt(target, self.english_text.toPlainText())
            elif kind == "it_srt":
                self.sync_edited_transcript_to_segments(self.italian_text.toPlainText())
                write_srt(target, self.transcript_segments, translated=False)
            elif kind == "en_srt":
                self.sync_edited_translation_to_segments()
                write_srt(target, self.translation_segments, translated=True)
            elif kind == "it_docx":
                write_docx(target, "Trascrizione", self.italian_text.toPlainText())
            elif kind == "en_docx":
                write_docx(target, "English translation", self.english_text.toPlainText())
            self._last_output_folder = target.parent
            self._success = (target.name, str(target.parent))
            self.success_label.setText(
                tr("success.saved", name=target.name, folder=str(target.parent))
            )
            self.success_banner.setObjectName("bannerOk")
            self.success_banner.show()
            self.hide_error_banner()
            self.set_status("status.saved", "ok", {"name": target.name})
        except OSError:
            self.show_error_key("error.save_failed")

    def open_output_folder(self) -> None:
        folder = self._last_output_folder
        if folder is None:
            folder = Path(self.settings.output_folder) if self.settings.output_folder else (
                self.selected_file.parent if self.selected_file else Path.home()
            )
        QDesktopServices.openUrl(QUrl.fromLocalFile(str(folder)))


def main() -> int:
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = MainWindow()
    window.show()
    return app.exec()