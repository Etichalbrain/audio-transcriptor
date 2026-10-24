"""Interface states that were wrong in 1.0.1, checked without a display."""

from __future__ import annotations

import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication, QDialog  # noqa: E402

from audio_transcriptor import app as app_module, i18n  # noqa: E402
from audio_transcriptor.models import TranscriptSegment  # noqa: E402
from audio_transcriptor.settings import AppSettings, SettingsStore  # noqa: E402

_APP = QApplication.instance() or QApplication([])


class UiStateTests(unittest.TestCase):
    def tearDown(self) -> None:
        i18n.set_language("en")

    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        with patch.object(SettingsStore, "load", return_value=AppSettings(ui_language="it")):
            self.window = app_module.MainWindow()
        self.window.settings_store.config_dir = Path(self._tmp.name)
        self.window.settings_store.config_path = Path(self._tmp.name) / "settings.json"
        self.addCleanup(self.window.close)

    def _segments(self, count: int) -> list[TranscriptSegment]:
        return [TranscriptSegment(i + 1, i * 2.0, i * 2.0 + 1.5, f"frase {i}") for i in range(count)]

    def test_counter_says_frasi_not_segmenti(self) -> None:
        self.window.transcript_segments = self._segments(5)
        self.window.update_stats()
        self.assertEqual(self.window.work_stats.text(), "5 frasi")
        self.window.transcript_segments = self._segments(1)
        self.window.update_stats()
        self.assertEqual(self.window.work_stats.text(), "1 frase")

    def test_progress_bar_only_while_busy(self) -> None:
        self.window.show()
        self.window.set_processing("Trascrizione in corso…", 40)
        self.assertTrue(self.window.progress_bar.isVisible())
        self.window.set_status("Trascrizione completata", "ok")
        self.assertFalse(self.window.progress_bar.isVisible())

    def test_missing_file_has_no_dangling_separator(self) -> None:
        self.window.show()
        self.window.set_selected_file(str(Path(self._tmp.name) / "non_esiste.mp4"))
        self.assertEqual(self.window.file_meta_label.text(), "")
        self.assertFalse(self.window.file_meta_label.isVisible())

    def test_model_chip_reacts_to_download_progress(self) -> None:
        self.window.update_model_chip_from_status("progress.downloading_model")
        self.assertIn("download in corso", self.window.model_chip_label.text())

    def test_progress_params_are_rendered(self) -> None:
        self.window.set_processing("progress.transcribing_time", 50, {"done": "1:00", "total": "2:00"})
        self.assertEqual(self.window.status_label.text(), "Trascrizione in corso: 1:00 di 2:00")

    def test_language_switch_keeps_state_and_redraws(self) -> None:
        self.window.transcript_segments = self._segments(3)
        self.window.italian_text.setPlainText("uno\ndue\ntre")
        self.window.set_status("progress.transcribed", "ok")
        self.window.show_error_key("error.save_failed")

        self.window.settings.ui_language = "de"
        self.window.apply_language()
        self.window.retranslate_ui()

        self.assertEqual(self.window.translate_button.text(), "Ins Englische übersetzen")
        self.assertEqual(self.window.work_stats.text(), "3 Sätze")
        self.assertEqual(self.window.status_label.text(), "Fehler")
        self.assertIn("nicht gespeichert", self.window.error_label.text())
        self.assertEqual(self.window.italian_text.toPlainText(), "uno\ndue\ntre")

    def test_unknown_worker_error_keeps_raw_text(self) -> None:
        self.window.show_error("Rate limit reached for gpt-5\ndetails")
        self.assertEqual(self.window.error_label.text(), "Rate limit reached for gpt-5")

    def test_translation_without_key_stops_before_sending(self) -> None:
        self.window.italian_text.setPlainText("ciao")
        with patch.object(app_module, "TranslationWorker") as worker:
            self.window.start_translation()
        worker.assert_not_called()
        self.assertIn("chiave API", self.window.error_label.text())

    def test_declined_confirmation_sends_nothing(self) -> None:
        self.window.settings.openai_api_key = "sk-test"
        self.window.italian_text.setPlainText("ciao")
        with patch.object(
            app_module.TranslationConfirmDialog, "exec", return_value=QDialog.DialogCode.Rejected
        ), patch.object(app_module, "TranslationWorker") as worker:
            self.window.start_translation()
        worker.assert_not_called()

    def test_dont_ask_again_is_remembered(self) -> None:
        self.window.settings.openai_api_key = "sk-test"
        self.window.italian_text.setPlainText("ciao")
        with patch.object(
            app_module.TranslationConfirmDialog, "exec", return_value=QDialog.DialogCode.Accepted
        ), patch.object(
            app_module.TranslationConfirmDialog, "dont_ask_again", return_value=True
        ), patch.object(app_module, "TranslationWorker"), patch.object(
            self.window.thread_pool, "start"
        ):
            self.window.start_translation()
        self.assertFalse(self.window.settings.confirm_translation)
        self.assertFalse(self.window.settings_store.load().confirm_translation)



class PlayerTests(unittest.TestCase):
    """Player logic without real audio: seek_to is patched, nothing is played."""

    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        media = Path(self._tmp.name) / "intervista.mp3"
        media.write_bytes(b"not really audio")
        with patch.object(SettingsStore, "load", return_value=AppSettings(ui_language="en")):
            self.window = app_module.MainWindow()
        self.addCleanup(self.window.close)
        self.window.show()
        self.window.set_selected_file(str(media))

    def _transcribe(self, lines: list[str]) -> None:
        self.window.transcript_segments = [
            TranscriptSegment(i + 1, i * 10.0, i * 10.0 + 8.0, line) for i, line in enumerate(lines)
        ]
        self.window.italian_text.setPlainText("\n".join(lines))
        self.window.update_actions()

    def _put_cursor_on_line(self, line: int) -> None:
        cursor = self.window.italian_text.textCursor()
        block = self.window.italian_text.document().findBlockByNumber(line)
        cursor.setPosition(block.position())
        self.window.italian_text.setTextCursor(cursor)

    def test_player_appears_only_with_timings(self) -> None:
        self.assertFalse(self.window.player_bar.isVisible())
        self._transcribe(["uno", "due"])
        self.assertTrue(self.window.player_bar.isVisible())
        self.window.clear_file()
        self.assertFalse(self.window.player_bar.isVisible())

    def test_play_from_cursor_starts_at_that_sentence(self) -> None:
        self._transcribe(["uno", "due", "tre"])
        self._put_cursor_on_line(2)
        with patch.object(self.window, "seek_to") as seek:
            self.window.play_from_cursor()
        seek.assert_called_once_with(20.0, play=True)

    def test_play_from_blank_line_uses_previous_sentence(self) -> None:
        self._transcribe(["uno", "due", "tre"])
        self.window.italian_text.setPlainText("uno\ndue\n\ntre")
        self._put_cursor_on_line(2)
        with patch.object(self.window, "seek_to") as seek:
            self.window.play_from_cursor()
        self.assertEqual(seek.call_args.args[0], 10.0)

    def test_tick_highlights_the_spoken_line(self) -> None:
        self._transcribe(["uno", "due", "tre"])
        self.window._on_player_tick(12.0)
        selections = self.window.italian_text.extraSelections()
        self.assertEqual(len(selections), 1)
        self.assertEqual(selections[0].cursor.block().text(), "due")
        self.assertEqual(self.window.time_label.text().split(" / ")[0], "0:12")

    def test_editing_text_moves_highlight_with_it(self) -> None:
        self._transcribe(["uno", "due", "tre"])
        self.window._on_player_tick(25.0)
        self.window.italian_text.setPlainText("titolo aggiunto\nuno\ndue\ntre")
        self.window._on_player_tick(25.0)
        selections = self.window.italian_text.extraSelections()
        line = selections[0].cursor.blockNumber()
        self.assertGreaterEqual(line, 2)

    def test_shortcuts_hint_is_translated(self) -> None:
        self._transcribe(["uno"])
        self.assertIn("play/pause", self.window.shortcut_hint.text())
        self.window.settings.ui_language = "it"
        self.window.apply_language()
        self.window.retranslate_ui()
        self.assertIn("riproduci/pausa", self.window.shortcut_hint.text())
        self.assertEqual(self.window.from_cursor_button.text(), "Ascolta da qui")

    def tearDown(self) -> None:
        i18n.set_language("en")


if __name__ == "__main__":
    unittest.main()
