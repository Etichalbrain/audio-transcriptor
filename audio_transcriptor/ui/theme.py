from __future__ import annotations

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
