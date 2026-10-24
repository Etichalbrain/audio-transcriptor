"""The interface catalog: complete in every language, placeholders consistent."""

from __future__ import annotations

import string
import unittest

from audio_transcriptor import i18n
from audio_transcriptor.settings import AppSettings


def _fields(text: str) -> set[str]:
    return {name for _lit, name, _spec, _conv in string.Formatter().parse(text) if name}


class CatalogTests(unittest.TestCase):
    def tearDown(self) -> None:
        i18n.set_language("en")

    def test_every_key_exists_in_every_language(self) -> None:
        for key, entry in i18n.STRINGS.items():
            for code in i18n.LANGUAGES:
                self.assertTrue(entry.get(code, "").strip(), f"{key} missing in {code}")

    def test_placeholders_match_english(self) -> None:
        for key, entry in i18n.STRINGS.items():
            expected = _fields(entry["en"])
            for code in i18n.LANGUAGES:
                self.assertEqual(_fields(entry[code]), expected, f"{key} [{code}]")

    def test_plurals_come_in_pairs(self) -> None:
        for key in i18n.STRINGS:
            if key.endswith(".one"):
                self.assertIn(key[:-4] + ".other", i18n.STRINGS)

    def test_no_em_dash_in_interface_text(self) -> None:
        for key, entry in i18n.STRINGS.items():
            for code, text in entry.items():
                self.assertNotIn("—", text, f"{key} [{code}]")

    def test_every_language_has_a_self_name(self) -> None:
        self.assertEqual(set(i18n.LANGUAGE_NAMES), set(i18n.LANGUAGES))

    def test_fallbacks(self) -> None:
        self.assertEqual(i18n.set_language("es"), "en")
        self.assertEqual(i18n.tr("does.not.exist"), "does.not.exist")

    def test_plural_and_number_format(self) -> None:
        i18n.set_language("fr")
        self.assertEqual(i18n.tr_n("work.sentences", 1), "1 phrase")
        self.assertEqual(i18n.tr_n("work.sentences", 4), "4 phrases")
        i18n.set_language("it")
        self.assertEqual(i18n.format_int(18342), "18.342")
        i18n.set_language("en")
        self.assertEqual(i18n.format_int(18342), "18,342")


class DetectionTests(unittest.TestCase):
    def test_system_language_is_detected(self) -> None:
        self.assertEqual(i18n.detect_language(["it-IT", "en-US"]), "it")
        self.assertEqual(i18n.detect_language(["de_CH"]), "de")
        self.assertEqual(i18n.detect_language(["fr-CA"]), "fr")

    def test_unsupported_system_language_falls_back_to_english(self) -> None:
        self.assertEqual(i18n.detect_language(["es-ES", "pt-BR"]), "en")
        self.assertEqual(i18n.detect_language([]), "en")

    def test_first_supported_preference_wins(self) -> None:
        self.assertEqual(i18n.detect_language(["es-ES", "fr-FR", "it-IT"]), "fr")

    def test_explicit_setting_beats_system(self) -> None:
        self.assertEqual(i18n.resolve_language("de", ["it-IT"]), "de")
        self.assertEqual(i18n.resolve_language("system", ["it-IT"]), "it")

    def test_settings_default_and_sanitising(self) -> None:
        self.assertEqual(AppSettings().ui_language, "system")
        self.assertEqual(AppSettings(ui_language="klingon").ui_language, "system")


if __name__ == "__main__":
    unittest.main()
