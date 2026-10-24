from __future__ import annotations

import json
import os
import tempfile
import unittest
from pathlib import Path

from audio_transcriptor.settings import AppSettings, SettingsStore


class DefaultTests(unittest.TestCase):
    def test_default_model_is_small(self) -> None:
        self.assertEqual(AppSettings().model_name, "small")

    def test_default_translation_mode_is_openai(self) -> None:
        self.assertEqual(AppSettings().translation_mode, "openai")

    def test_unknown_model_falls_back(self) -> None:
        self.assertEqual(AppSettings(model_name="huge-v9").model_name, "small")

    def test_legacy_local_mode_falls_back(self) -> None:
        self.assertEqual(AppSettings(translation_mode="local").translation_mode, "openai")

    def test_unknown_theme_falls_back(self) -> None:
        self.assertEqual(AppSettings(theme="solarized").theme, "light")


class StoreTests(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.store = SettingsStore()
        self.store.config_dir = Path(self._tmp.name)
        self.store.config_path = self.store.config_dir / "settings.json"

    def test_missing_file_returns_defaults(self) -> None:
        self.assertEqual(self.store.load().model_name, "small")

    def test_corrupt_file_returns_defaults(self) -> None:
        self.store.config_path.write_text("{not json", encoding="utf-8")
        self.assertEqual(self.store.load().model_name, "small")

    def test_non_object_file_returns_defaults(self) -> None:
        self.store.config_path.write_text('["a", "b"]', encoding="utf-8")
        self.assertEqual(self.store.load().model_name, "small")

    def test_round_trip(self) -> None:
        settings = AppSettings(
            model_name="medium",
            language="auto",
            output_folder="/tmp/out",
            openai_api_key="sk-test",
            openai_model="gpt-5",
            theme="dark",
        )
        self.store.save(settings)
        loaded = self.store.load()
        self.assertEqual(loaded, settings)

    @unittest.skipUnless(os.name == "posix", "POSIX permissions are not enforced on Windows")
    def test_settings_file_is_owner_only(self) -> None:
        # The file holds the OpenAI API key in plain text: never world readable.
        self.store.save(AppSettings(openai_api_key="sk-test"))
        self.assertEqual(self.store.config_path.stat().st_mode & 0o777, 0o600)

    def test_old_shipped_file_is_migrated(self) -> None:
        self.store.config_path.write_text(
            json.dumps(
                {
                    "model_name": "large-v3",
                    "language": "it",
                    "output_folder": "",
                    "openai_api_key": "",
                    "openai_model": "gpt-5",
                    "translation_mode": "local",
                    "theme": "dark",
                    "unknown_key": "ignored",
                }
            ),
            encoding="utf-8",
        )
        loaded = self.store.load()
        self.assertEqual(loaded.translation_mode, "openai")
        self.assertEqual(loaded.model_name, "large-v3")
        self.assertEqual(loaded.theme, "dark")


if __name__ == "__main__":
    unittest.main()
