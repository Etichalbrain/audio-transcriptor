from __future__ import annotations

from PySide6.QtCore import QUrl
from PySide6.QtGui import (
    QColor,
    QTextCursor,
    QTextFormat,
)
from PySide6.QtWidgets import (
    QTextEdit,
)

from audio_transcriptor.alignment import line_at_time, line_time_spans
from audio_transcriptor.i18n import tr
from audio_transcriptor.ui.theme import (
    ACCENT_TINT,
    D_ACCENT_TINT,
)
from audio_transcriptor.ui.widgets import (
    _fmt_time,
)


class PlaybackMixin:
    """Media playback and transcript highlighting for MainWindow (moved verbatim from main_window.py)."""

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
