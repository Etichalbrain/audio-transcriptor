from __future__ import annotations

import shutil
import sys
from html import escape
from pathlib import Path

from PySide6.QtCore import QByteArray, QPointF, QThreadPool, Qt, QUrl, Signal
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
    QSplitter,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from audio_transcriptor import __version__
from audio_transcriptor.diagnostics import legal_document_path
from audio_transcriptor.alignment import align_lines_to_segments
from audio_transcriptor.exporters import write_docx, write_srt, write_txt
from audio_transcriptor.models import TranscriptSegment, is_supported_media
from audio_transcriptor.services import probe_duration
from audio_transcriptor.settings import AppSettings, SettingsStore
from audio_transcriptor.workers import BaseWorker, TranscriptionWorker, TranslationWorker


AUTHOR = "Antonio Aversa"
PROJECT_URL = "https://aversa.design"

MODEL_CHOICES = (
    ("small", "small (veloce, circa 0,5 GB da scaricare)"),
    ("medium", "medium (equilibrato, circa 1,5 GB)"),
    ("large-v3", "large-v3 (qualità migliore, circa 3 GB)"),
)

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
    if title:
        heading = QLabel(title)
        heading.setObjectName("cardTitle")
        layout.addWidget(heading)
    return frame, layout


def _dot_label(color: str) -> QLabel:
    dot = QLabel()
    dot.setFixedSize(10, 10)
    dot.setStyleSheet(f"background: {color}; border-radius: 5px;")
    return dot


class SettingsDialog(QDialog):
    """Impostazioni: sections 'Modello' and 'Traduzione', output and theme."""

    def __init__(self, settings: AppSettings, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Impostazioni")
        self.setMinimumWidth(520)

        self.model_combo = QComboBox()
        for value, label in MODEL_CHOICES:
            self.model_combo.addItem(label, value)
        self.model_combo.setCurrentIndex(max(0, self.model_combo.findData(settings.model_name)))

        self.language_combo = QComboBox()
        self.language_combo.addItem("Italiano", "it")
        self.language_combo.addItem("Automatico", "auto")
        self.language_combo.setCurrentIndex(0 if settings.language == "it" else 1)

        self.output_edit = QLineEdit(settings.output_folder)
        output_button = QPushButton("Sfoglia…")
        output_button.setObjectName("secondary")
        output_button.clicked.connect(self.choose_output_folder)
        output_row = QHBoxLayout()
        output_row.addWidget(self.output_edit, stretch=1)
        output_row.addWidget(output_button)

        self.api_key_edit = QLineEdit(settings.openai_api_key)
        self.api_key_edit.setEchoMode(QLineEdit.EchoMode.Password)
        self.openai_model_edit = QLineEdit(settings.openai_model)
        self.confirm_translation_check = QCheckBox(
            "Chiedi conferma prima di inviare il testo a OpenAI"
        )
        self.confirm_translation_check.setChecked(settings.confirm_translation)
        self._settings = settings

        self.theme_combo = QComboBox()
        self.theme_combo.addItem("Chiaro", "light")
        self.theme_combo.addItem("Scuro", "dark")
        self.theme_combo.setCurrentIndex(0 if settings.theme == "light" else 1)

        root = QVBoxLayout(self)
        root.setContentsMargins(18, 16, 18, 16)
        root.setSpacing(12)

        # Modello section
        model_card, model_layout = _card("Modello di trascrizione")
        grid = QGridLayout()
        grid.setHorizontalSpacing(10)
        grid.setVerticalSpacing(8)
        grid.addWidget(QLabel("Modello Whisper"), 0, 0)
        grid.addWidget(self.model_combo, 0, 1)
        grid.addWidget(QLabel("Lingua"), 1, 0)
        grid.addWidget(self.language_combo, 1, 1)
        model_layout.addLayout(grid)
        root.addWidget(model_card)

        # Traduzione section
        trans_card, trans_layout = _card("Traduzione")
        hint = QLabel("La traduzione usa l’API OpenAI con la tua chiave.")
        hint.setObjectName("muted")
        trans_layout.addWidget(hint)
        tgrid = QGridLayout()
        tgrid.setHorizontalSpacing(10)
        tgrid.setVerticalSpacing(8)
        key_label = QLabel("Chiave API")
        api_row = QHBoxLayout()
        api_row.addWidget(self.api_key_edit, stretch=1)
        tgrid.addWidget(key_label, 0, 0)
        tgrid.addLayout(api_row, 0, 1)
        tgrid.addWidget(QLabel("Modello OpenAI"), 1, 0)
        tgrid.addWidget(self.openai_model_edit, 1, 1)
        trans_layout.addLayout(tgrid)
        trans_layout.addWidget(self.confirm_translation_check)
        root.addWidget(trans_card)

        # General section
        gen_card, gen_layout = _card("Generale")
        ggrid = QGridLayout()
        ggrid.setHorizontalSpacing(10)
        ggrid.setVerticalSpacing(8)
        ggrid.addWidget(QLabel("Cartella di output"), 0, 0)
        ggrid.addLayout(output_row, 0, 1)
        ggrid.addWidget(QLabel("Tema"), 1, 0)
        ggrid.addWidget(self.theme_combo, 1, 1)
        gen_layout.addLayout(ggrid)
        root.addWidget(gen_card)

        save_button = QPushButton("Salva")
        cancel_button = QPushButton("Annulla")
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
            self, "Scegli la cartella di output", self.output_edit.text()
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
        )


class ExportDialog(QDialog):
    """Pannello Esporta: TXT / SRT / DOCX per Italiano ed Inglese."""

    def __init__(
        self,
        parent: QWidget | None,
        flags: dict[str, bool],
        output_folder: str,
    ) -> None:
        super().__init__(parent)
        self.setWindowTitle("Esporta")
        self.setMinimumWidth(560)
        self.flags = flags
        self.output_folder = output_folder

        root = QVBoxLayout(self)
        root.setContentsMargins(18, 16, 18, 16)
        root.setSpacing(12)

        title = QLabel("Esporta trascrizione")
        title.setStyleSheet("font-size: 17px; font-weight: 700;")
        root.addWidget(title)

        intro = QLabel("Scegli il formato: i file vengono salvati nella cartella di output.")
        intro.setObjectName("muted")
        intro.setWordWrap(True)
        root.addWidget(intro)

        grid = QGridLayout()
        grid.setHorizontalSpacing(10)
        grid.setVerticalSpacing(10)
        grid.addWidget(QLabel(""), 0, 0)
        grid.addWidget(QLabel("Italiano"), 0, 1)
        grid.addWidget(QLabel("Inglese"), 0, 2)
        for row, kind in enumerate(("txt", "srt", "docx"), start=1):
            grid.addWidget(QLabel(kind.upper()), row, 0)
            for col, lang in ((1, "it"), (2, "en")):
                key = f"{lang}_{kind}"
                button = QPushButton(f"Esporta {kind.upper()}")
                button.setObjectName("secondary")
                button.setEnabled(flags.get(key, False))
                button.clicked.connect(
                    lambda checked=False, k=key: self.request_export(k)
                )
                grid.addWidget(button, row, col)
        root.addLayout(grid)

        folder_row = QHBoxLayout()
        folder_label = QLabel("Cartella:")
        folder_label.setObjectName("muted")
        self.folder_label = QLabel(output_folder or "— (accanto al file selezionato)")
        self.folder_label.setObjectName("muted")
        self.folder_label.setWordWrap(True)
        open_button = QPushButton("Apri cartella")
        open_button.setObjectName("ghost")
        open_button.clicked.connect(self.open_folder)
        folder_row.addWidget(folder_label)
        folder_row.addWidget(self.folder_label, stretch=1)
        folder_row.addWidget(open_button)
        root.addLayout(folder_row)

        close_button = QPushButton("Chiudi")
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
        self.setWindowTitle("Traduci in inglese")
        self.setMinimumWidth(480)

        root = QVBoxLayout(self)
        root.setContentsMargins(20, 18, 20, 18)
        root.setSpacing(12)

        title = QLabel("Il testo verrà inviato a OpenAI")
        title.setStyleSheet("font-size: 17px; font-weight: 700;")
        root.addWidget(title)

        frasi = "1 frase" if sentences == 1 else f"{sentences} frasi"
        caratteri = f"{characters:,}".replace(",", ".")
        body = QLabel(
            f"Invierai <b>{frasi}</b> ({caratteri} caratteri) al modello "
            f"<b>{escape(model)}</b> con la tua chiave API. L’audio resta su questo "
            "computer.<br><br>Il costo dipende dal modello scelto e viene addebitato "
            "sul tuo account OpenAI."
        )
        body.setWordWrap(True)
        root.addWidget(body)

        self.dont_ask = QCheckBox("Non chiedere più (modificabile in Impostazioni)")
        root.addWidget(self.dont_ask)

        send_button = QPushButton("Traduci")
        cancel_button = QPushButton("Annulla")
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
    """Credit, license and privacy summary, reachable from the main window."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Informazioni")
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
            f'Realizzato da {AUTHOR} · '
            f'<a href="{PROJECT_URL}">{PROJECT_URL.replace("https://", "")}</a>'
        )
        author.setObjectName("muted")
        author.setOpenExternalLinks(True)
        title_box.addWidget(title)
        title_box.addWidget(author)
        head.addLayout(title_box, stretch=1)
        root.addLayout(head)

        # Read legal texts shipped with the app, not unverified website routes.
        document_urls = {}
        for name in ("LICENSE", "PRIVACY.md", "TERMS.md", "THIRD_PARTY_NOTICES.md"):
            path = legal_document_path(name)
            document_urls[name] = escape(path.as_uri() if path else PROJECT_URL, quote=True)

        body = QLabel(
            "<p><b>L’audio resta su questo computer.</b> La trascrizione gira in "
            "locale e non vengono raccolti dati di utilizzo. Solo quando premi "
            "<i>Traduci in inglese</i> il testo (mai l’audio) viene inviato "
            "all’API OpenAI con la tua chiave. "
            f"<a href=\"{document_urls['PRIVACY.md']}\">Dettagli sulla privacy</a>.</p>"
            "<p><b>Verifica sempre il testo.</b> Trascrizioni e traduzioni sono "
            "generate da modelli di IA e possono contenere errori, soprattutto "
            "su nomi e cifre. L’app è fornita così com’è, senza garanzia né "
            "obbligo di assistenza; il consenso alla registrazione è tua "
            f'responsabilità. <a href="{document_urls["TERMS.md"]}">Termini di utilizzo</a>.</p>'
            "<p><b>Licenza.</b> Uso personale e professionale gratuito, anche per "
            "lavoro retribuito. Apache License 2.0 + Commons Clause v1.0: "
            "source-available, non open source; non è consentito vendere un "
            "prodotto o servizio basato sostanzialmente su questa app. "
            f'<a href="{document_urls["LICENSE"]}">Licenza completa</a> · '
            f'<a href="{document_urls["THIRD_PARTY_NOTICES.md"]}">componenti di terze parti</a> '
            "(Qt, Whisper e altri) · "
            f'permessi separati su <a href="{PROJECT_URL}">aversa.design</a>.</p>'
        )
        body.setWordWrap(True)
        body.setOpenExternalLinks(True)
        body.setTextInteractionFlags(Qt.TextInteractionFlag.TextBrowserInteraction)
        root.addWidget(body, stretch=1)

        close_button = QPushButton("Chiudi")
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
        self.thread_pool = QThreadPool.globalInstance()
        self.current_worker: BaseWorker | None = None
        self.selected_file: Path | None = None
        self.transcript_segments: list[TranscriptSegment] = []
        self.translation_segments: list[TranscriptSegment] = []
        self._last_output_folder: Path | None = None
        self._status_kind = "idle"
        self._file_duration: float | None = None

        # Status row
        self.status_label = QLabel("Pronto")
        self.status_dot = _dot_label("#c4cbd9")
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        # The status line carries the measured progress (minutes, sentences);
        # a percentage drawn on the bar was low-contrast and redundant.
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setFixedHeight(8)
        self.progress_bar.hide()
        self.cancel_button = QPushButton("Annulla operazione")
        self.cancel_button.setObjectName("danger")
        self.cancel_button.clicked.connect(self.cancel_process)

        # Header
        self.about_button = QPushButton("Informazioni")
        self.about_button.setObjectName("ghost")
        self.about_button.clicked.connect(self.show_about)
        self.settings_button = QPushButton("Impostazioni")
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
        self.hero_title = QLabel("Trascina qui un file audio o video")
        self.hero_title.setObjectName("heroTitle")
        self.hero_hint = QLabel("MP3 · WAV · M4A · MP4 · MOV · MKV")
        self.hero_hint.setObjectName("muted")
        self.select_button = QPushButton("Scegli file")
        self.select_button.setObjectName("secondary")
        self.select_button.clicked.connect(self.choose_file)

        self.file_icon = QLabel("🎞️")
        self.file_icon.setStyleSheet("font-size: 18px;")
        self.filename_label = QLabel("Nessun file selezionato")
        self.filename_label.setStyleSheet("font-weight: 600;")
        self.file_meta_label = QLabel("")
        self.file_meta_label.setObjectName("muted")
        self.model_chip = QFrame()
        self.model_chip.setObjectName("chip")
        chip_layout = QHBoxLayout(self.model_chip)
        chip_layout.setContentsMargins(10, 4, 10, 4)
        chip_layout.setSpacing(6)
        self.model_dot = _dot_label("#c4cbd9")
        self.model_chip_label = QLabel("Modello: small")
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
        self.remove_file_button.setToolTip("Rimuovi file")
        self.remove_file_button.setAccessibleName("Rimuovi file")
        self.remove_file_button.clicked.connect(self.clear_file)
        chip_layout.addWidget(self.remove_file_button)
        self.transcribe_button = QPushButton("Trascrivi in italiano")
        self.transcribe_button.clicked.connect(self.start_transcription)
        self.change_file_button = QPushButton("Cambia file")
        self.change_file_button.setObjectName("secondary")
        self.change_file_button.clicked.connect(self.choose_file)

        # Work area
        self.work_title = QLabel("Trascrizione")
        self.work_title.setObjectName("cardTitle")
        self.work_stats = QLabel("")
        self.work_stats.setObjectName("muted")
        self.translate_button = QPushButton("Traduci in inglese")
        self.translate_button.clicked.connect(self.start_translation)
        self.export_button = QPushButton("Esporta…")
        self.export_button.setObjectName("secondary")
        self.export_button.clicked.connect(self.open_export_dialog)

        self.italian_text = QTextEdit()
        self.italian_text.setPlaceholderText(
            "La trascrizione in italiano apparirà qui. Puoi correggere il testo prima "
            "di tradurlo o esportarlo."
        )
        self.italian_text.textChanged.connect(self.update_actions)
        self.italian_text.textChanged.connect(self.update_stats)
        self.english_text = QTextEdit()
        self.english_text.setPlaceholderText(
            "La traduzione in inglese apparirà qui, accanto all’italiano."
        )
        self.english_text.textChanged.connect(self.update_actions)
        self.english_text.textChanged.connect(self.update_stats)

        self.it_pane_title = QLabel("Italiano")
        self.it_pane_title.setObjectName("paneTitle")
        self.en_pane_title = QLabel("Inglese")
        self.en_pane_title.setObjectName("paneTitle")
        self.it_pane_count = QLabel("")
        self.it_pane_count.setObjectName("muted")
        self.en_pane_count = QLabel("")
        self.en_pane_count.setObjectName("muted")

        # Banners
        self.error_label = QLabel("")
        self.error_label.setWordWrap(True)
        self.error_dismiss = QPushButton("Chiudi")
        self.error_dismiss.setObjectName("secondary")
        self.error_dismiss.clicked.connect(self.hide_error_banner)
        self.success_label = QLabel("")
        self.success_label.setWordWrap(True)
        self.open_folder_button = QPushButton("Apri cartella")
        self.open_folder_button.setObjectName("success")
        self.open_folder_button.clicked.connect(self.open_output_folder)

        self.setCentralWidget(self.build_layout())
        self.apply_theme()
        self.update_actions()
        self.update_stats()

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
        status_card, status_layout = _card("Stato")
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
        footer = QLabel(
            f"AudioTranscriptor di {AUTHOR} · aversa.design · "
            "l’audio resta su questo computer"
        )
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
            parts.append(f"durata {_fmt_time(self._file_duration)}")
        self.file_meta_label.setText(" · ".join(parts))
        self.file_meta_label.setVisible(bool(parts))
        model_name = self.settings.model_name
        self.model_chip_label.setText(f"Modello: {model_name}")
        self.model_dot.setStyleSheet("background: #c4cbd9; border-radius: 5px;")
        self.hero_panel.hide()
        self.file_panel.show()
        self.drop_zone.setMinimumHeight(84)

    # --- Public actions ------------------------------------------------------
    def closeEvent(self, event) -> None:
        # Ask a running worker to stop before the window is torn down, so its
        # thread does not try to emit on already-destroyed signals.
        if self.current_worker is not None:
            self.current_worker.cancel()
        super().closeEvent(event)

    def apply_theme(self) -> None:
        QApplication.instance().setStyleSheet(
            DARK_STYLE if self.settings.theme == "dark" else LIGHT_STYLE
        )

    def choose_file(self) -> None:
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Seleziona file audio o video",
            "",
            "File audio e video (*.mp3 *.wav *.m4a *.mp4 *.mov *.mkv)",
        )
        if path:
            self.set_selected_file(path)

    def set_selected_file(self, path: str) -> None:
        if self.current_worker is not None:
            return
        candidate = Path(path)
        if not is_supported_media(candidate):
            self.show_error(
                "Scegli un file MP3, WAV, M4A, MP4, MOV o MKV supportato."
            )
            return
        self.selected_file = candidate
        self._file_duration = probe_duration(candidate)
        self.hide_error_banner()
        self.set_status("File selezionato", "idle")
        self.progress_bar.setValue(0)
        self.populate_hero()
        self.update_actions()

    def clear_file(self) -> None:
        self.selected_file = None
        self._file_duration = None
        self.transcript_segments = []
        self.translation_segments = []
        self.italian_text.clear()
        self.english_text.clear()
        self.en_pane.hide()
        self.success_banner.hide()
        self.hide_error_banner()
        self.set_status("Pronto", "idle")
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
            if self.selected_file is not None:
                self.populate_hero()
            # refresh theme-dependent inline colours, keeping the current state
            self.set_status(self.status_label.text(), self._status_kind)
            if self._status_kind == "busy":
                self.set_status_dot_busy()
            self.update_actions()

    # --- Workers -------------------------------------------------------------
    def start_transcription(self) -> None:
        if self.selected_file is None:
            return
        if not self.ensure_disk_space(self.selected_file):
            self.show_error(
                "Potrebbe non esserci spazio su disco sufficiente per elaborare "
                "questo file."
            )
            return
        self.hide_error_banner()
        self.set_processing("Preparazione audio…", 0)
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
            self.show_error("Add an OpenAI API key in Settings before translating.")
            return
        self.hide_error_banner()
        self.sync_edited_transcript_to_segments(text)
        if self.settings.confirm_translation and not self.confirm_translation_send(text):
            return
        self.set_processing("Traduzione…", 0)
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
            self.set_status("Annullamento…", "warn")

    def on_transcribed(self, result) -> None:
        self.transcript_segments = result.segments
        self.italian_text.setPlainText(result.text)
        self.set_status("Trascrizione completata", "ok")
        self.progress_bar.setValue(100)
        self.model_dot.setStyleSheet("background: #1f9d55; border-radius: 5px;")
        self.update_actions()
        self.update_stats()

    def on_translated(self, result) -> None:
        self.translation_segments = result.segments
        self.english_text.setPlainText(result.text)
        self.en_pane.show()
        self.work_splitter.setSizes([1, 1])
        self.set_status("Traduzione completata", "ok")
        self.progress_bar.setValue(100)
        self.update_actions()
        self.update_stats()

    def on_worker_finished(self) -> None:
        self.current_worker = None
        self.update_actions()

    # --- Status / progress / errors -----------------------------------------
    def set_status(self, text: str, kind: str) -> None:
        colors = {
            "idle": "#c4cbd9",
            "busy": ACCENT if self.settings.theme == "light" else D_ACCENT,
            "ok": SUCCESS if self.settings.theme == "light" else D_SUCCESS,
            "warn": "#f0a020",
            "error": ERROR if self.settings.theme == "light" else D_ERROR,
        }
        self._status_kind = kind
        self._dot_color = colors.get(kind, "#c4cbd9")
        self.status_label.setText(text)
        self._refresh_dot(self._dot_color)
        # The bar is only useful while something runs: once the job is done
        # the space goes back to the transcript.
        self.progress_bar.setVisible(kind in ("busy", "warn"))

    def set_processing(self, status: str, progress: int) -> None:
        self._status_kind = "busy"
        self.status_label.setText(status)
        self.set_status_dot_busy()
        self.progress_bar.setValue(progress)
        self.progress_bar.show()
        self.update_model_chip_from_status(status)

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

    def update_model_chip_from_status(self, status: str) -> None:
        lowered = status.lower()
        model_name = self.settings.model_name
        downloading = "download" in lowered and "modello" in lowered
        loading = "modello" in lowered and (
            "preparazione" in lowered or "caricamento" in lowered
        )
        if downloading:
            text, color = f"Modello: {model_name} · download in corso…", ACCENT
        elif loading:
            text, color = f"Modello: {model_name} · caricamento…", ACCENT
        else:
            text, color = f"Modello: {model_name}", "#c4cbd9"
        if getattr(self, "_chip_style", None) != (text, color):
            self._chip_style = (text, color)
            self.model_chip_label.setText(text)
            self.model_dot.setStyleSheet(
                f"background: {color}; border-radius: 5px;"
            )

    def show_error(self, message: str) -> None:
        self.set_status("Errore", "error")
        self.progress_bar.setValue(0)
        self.success_banner.hide()
        self.error_label.setText(self.friendly_error(message))
        self.error_banner.setObjectName("bannerError")
        self.error_banner.show()
        self.update_actions()

    def hide_error_banner(self) -> None:
        self.error_banner.hide()

    def friendly_error(self, message: str) -> str:
        lowered = message.lower()
        if "no space" in lowered or "disk" in lowered:
            return "Spazio su disco insufficiente. Libera spazio o scegli un’altra cartella di output."
        if "api key" in lowered:
            return "Aggiungi la tua chiave API OpenAI in Impostazioni prima di tradurre."
        if "cancelled" in lowered:
            return "L’operazione in corso è stata annullata."
        if "model" in lowered and ("download" in lowered or "connection" in lowered):
            return "Il modello Whisper non può essere scaricato. Controlla la connessione e riprova."
        return message.splitlines()[0] if message else "Qualcosa è andato storto. Riprova."

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

    def update_stats(self) -> None:
        it_text = self.italian_text.toPlainText()
        en_text = self.english_text.toPlainText()
        it_words = len(it_text.split())
        en_words = len(en_text.split())
        segments = len(self.transcript_segments)
        self.it_pane_count.setText(f"{it_words} parole")
        self.en_pane_count.setText(f"{en_words} parole")
        if segments:
            self.work_stats.setText("1 frase" if segments == 1 else f"{segments} frasi")
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
        path, _ = QFileDialog.getSaveFileName(self, "Salva file", str(default_path))
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
            self.success_label.setText(
                f"Lavoro completato: salvato “{target.name}” in {target.parent}"
            )
            self.success_banner.setObjectName("bannerOk")
            self.success_banner.show()
            self.hide_error_banner()
            self.set_status(f"Salvato {target.name}", "ok")
        except OSError:
            self.show_error("Impossibile salvare il file. Controlla la cartella e riprova.")

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