from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QSplitter,
    QVBoxLayout,
    QWidget,
)

from audio_transcriptor.i18n import tr
from audio_transcriptor.ui.theme import (
    SUCCESS,
)
from audio_transcriptor.ui.widgets import (
    DropZone,
    _card,
    _fmt_size,
    _fmt_time,
    _logo_pixmap,
)


class LayoutMixin:
    """Widget construction for MainWindow (moved verbatim from main_window.py)."""

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
