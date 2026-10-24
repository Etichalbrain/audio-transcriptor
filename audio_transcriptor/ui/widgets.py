from __future__ import annotations

from PySide6.QtCore import QByteArray, QLocale, QPointF, Qt, Signal
from PySide6.QtGui import (
    QColor,
    QDragEnterEvent,
    QDropEvent,
    QPainter,
    QPen,
    QPixmap,
    QPolygonF,
)
from PySide6.QtWidgets import (
    QFrame,
    QLabel,
    QSizePolicy,
    QVBoxLayout,
)

from audio_transcriptor.ui.theme import ACCENT, ACCENT_TINT


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
