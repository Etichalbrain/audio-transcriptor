from __future__ import annotations

import shutil
from pathlib import Path

from PySide6.QtCore import QThreadPool, QTimer, Qt, QUrl
from PySide6.QtGui import (
    QDesktopServices,
    QIcon,
    QKeySequence,
    QShortcut,
)
from PySide6.QtWidgets import (
    QApplication,
    QDialog,
    QFileDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QProgressBar,
    QPushButton,
    QSlider,
    QTextEdit,
)

from audio_transcriptor import __version__, i18n
from audio_transcriptor.alignment import align_lines_to_segments
from audio_transcriptor.exporters import write_docx, write_srt, write_txt
from audio_transcriptor.i18n import tr, tr_n
from audio_transcriptor.models import TranscriptSegment, is_supported_media
from audio_transcriptor.services import probe_duration
from audio_transcriptor.settings import SettingsStore
from audio_transcriptor.workers import BaseWorker, TranscriptionWorker, TranslationWorker
from audio_transcriptor.ui.dialogs import (
    AUTHOR,
    AboutDialog,
    ExportDialog,
    SettingsDialog,
    TranslationConfirmDialog,
)
from audio_transcriptor.ui.layout import LayoutMixin
from audio_transcriptor.ui.playback import PlaybackMixin
from audio_transcriptor.ui.theme import (
    ACCENT,
    DARK_STYLE,
    D_ACCENT,
    D_ERROR,
    D_SUCCESS,
    ERROR,
    LIGHT_STYLE,
    SUCCESS,
)
from audio_transcriptor.ui.widgets import (
    _dot_label,
    _logo_pixmap,
    _upload_icon,
    system_ui_languages,
)


class MainWindow(LayoutMixin, PlaybackMixin, QMainWindow):
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
