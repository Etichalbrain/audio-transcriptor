from __future__ import annotations

import re
import unittest
from pathlib import Path

from audio_transcriptor import __version__
from audio_transcriptor.settings import TRANSLATION_MODES, WHISPER_MODELS


ROOT = Path(__file__).resolve().parents[1]

# Installer language -> pre-install notice shown by that language.
INSTALLER_NOTICES = {
    "english": Path("README-INSTALL-en.txt"),
    "italian": Path("LEGGIMI.txt"),
    "german": Path("README-INSTALL-de.txt"),
    "french": Path("README-INSTALL-fr.txt"),
}


def read(relative: str) -> str:
    return (ROOT / relative).read_text(encoding="utf-8")


class VersionConsistencyTests(unittest.TestCase):
    def test_installer_uses_package_version(self) -> None:
        match = re.search(r'#define MyAppVersion "([^"]+)"', read("installer/audio_transcriptor.iss"))
        self.assertIsNotNone(match)
        self.assertEqual(match.group(1), __version__)

    def test_windows_version_resource_matches(self) -> None:
        major, minor, patch = __version__.split(".")
        content = read("installer/windows_version_info.txt")
        self.assertIn(f"filevers=({major}, {minor}, {patch}, 0)", content)
        self.assertIn(f"prodvers=({major}, {minor}, {patch}, 0)", content)
        self.assertIn(f'StringStruct("FileVersion", "{__version__}")', content)
        self.assertIn(f'StringStruct("ProductVersion", "{__version__}")', content)

    def test_pyproject_version_matches(self) -> None:
        match = re.search(r'^version = "([^"]+)"', read("pyproject.toml"), flags=re.MULTILINE)
        self.assertIsNotNone(match)
        self.assertEqual(match.group(1), __version__)

    def test_macos_spec_reads_version_from_package(self) -> None:
        content = read("AudioTranscriptor.spec")
        self.assertIn("audio_transcriptor/__init__.py", content)
        self.assertIn("CFBundleShortVersionString", content)

    def test_docs_mention_current_installer_name(self) -> None:
        expected = f"AudioTranscriptorSetup-{__version__}.exe"
        for document in ("README.md", "INSTALLATION.md", "build_windows_installer.bat"):
            self.assertIn(expected, read(document), f"{document} is out of date")

    def test_docs_mention_current_macos_dmg(self) -> None:
        expected = f"AudioTranscriptor-{__version__}-arm64.dmg"
        for document in ("README.md", "INSTALLATION.md"):
            self.assertIn(expected, read(document), f"{document} is out of date")
        self.assertIn("AudioTranscriptor-$VERSION-arm64.dmg", read("build_macos.sh"))

    def test_self_test_is_wired_into_the_entry_point_and_the_build(self) -> None:
        self.assertIn("--self-test", read("audio_transcriptor/__main__.py"))
        self.assertIn("--self-test", read(".github/workflows/build-windows.yml"))

    def test_requirements_keep_pyav_compatible_with_faster_whisper(self) -> None:
        # PyAV 19 dropped av.open(metadata_errors=...), which faster-whisper uses.
        content = read("requirements.txt")
        self.assertRegex(content, r"(?m)^av>=[\d.]+,<19$")

    def test_license_contains_commons_clause_and_full_apache_text(self) -> None:
        content = read("LICENSE")
        self.assertIn('“Commons Clause” License Condition v1.0', content)
        self.assertIn("entirely or substantially", content)
        self.assertIn("Software: AudioTranscriptor", content)
        self.assertIn("License: Apache License, Version 2.0", content)
        self.assertIn("Licensor: Antonio Aversa", content)
        self.assertTrue(content.endswith(read("licenses/Apache-2.0.txt")))
        guide = read("LICENSE-SUPPLEMENT.md")
        self.assertIn("does **not** add, replace or override", guide)
        self.assertIn("no automatic", guide.lower())
        self.assertIn("https://aversa.design", guide)

    def test_license_summaries_do_not_claim_noncommercial_only(self) -> None:
        for name in (
            "README.md", "LICENSE-SUPPLEMENT.md", "NOTICE", "TERMS.md",
            "audio_transcriptor/app.py", "installer/LEGGIMI.txt",
            "installer/windows_version_info.txt", ".github/workflows/build-windows.yml",
            "docs/cover.html",
        ):
            content = read(name)
            self.assertNotIn("PolyForm", content, name)
            self.assertIn("Commons Clause", content, name)
        self.assertIn("source-available", read("README.md"))
        self.assertIn("Apache 2.0 + Commons Clause", read("installer/windows_version_info.txt"))

    def test_notice_requires_credit(self) -> None:
        content = read("NOTICE")
        self.assertIn("Antonio Aversa", content)
        self.assertIn("credit", content.lower())
        self.assertIn("Commons Clause", content)
        self.assertIn("does not add to or", content)
        self.assertIn("LICENSE", content)

    def test_legal_documents_exist_and_say_what_they_promise(self) -> None:
        privacy = read("PRIVACY.md")
        self.assertIn("api.openai.com", privacy)
        self.assertIn("No audio ever leaves the computer", privacy)
        self.assertIn("settings.json", privacy)

        terms = read("TERMS.md")
        self.assertIn('"as is"', terms)
        self.assertIn("consent", terms.lower())
        self.assertIn("liability", terms.lower())
        self.assertIn("Commons Clause", terms)

        third_party = read("THIRD_PARTY_NOTICES.md")
        self.assertIn("LGPL-3.0", third_party)
        self.assertIn("Qt", third_party)
        self.assertIn("replace", third_party.lower())

        for notice in ("SECURITY.md", "licenses/LGPL-3.0.txt", "licenses/GPL-3.0.txt"):
            self.assertTrue((ROOT / notice).is_file(), f"missing {notice}")

    def test_terms_cover_security_support_and_correct_use(self) -> None:
        terms = read("TERMS.md").lower()
        for clause in (
            "no guarantee of security",
            "no support, maintenance or updates",
            "correct use",
            "indemn",
            "gross negligence",
            "backups",
        ):
            self.assertIn(clause, terms, f"TERMS.md no longer states {clause!r}")

        installer_note = read("installer/LEGGIMI.txt").lower()
        for promise in ("sicurezza", "assistenza", "indenne"):
            self.assertIn(promise, installer_note, f"LEGGIMI.txt no longer mentions {promise}")

        translated = {
            "installer/README-INSTALL-en.txt": ("no guarantee of security", "support or updates", "hold the author harmless"),
            "installer/README-INSTALL-de.txt": ("keine sicherheitsgarantie", "support oder updates", "stellen den autor frei"),
            "installer/README-INSTALL-fr.txt": ("aucune garantie de sécurité", "assistance ou de mises à jour", "garantissez l'auteur"),
        }
        for name, phrases in translated.items():
            note = read(name).lower()
            for phrase in phrases:
                self.assertIn(phrase, note, f"{name} no longer mentions {phrase!r}")

        self.assertIn("no obligation of support", read("README.md").lower())
        self.assertIn("TERMS.md", read("audio_transcriptor/app.py"))

    def test_installer_notices_exist_and_every_build_ships_them(self) -> None:
        installer = read("installer/audio_transcriptor.iss")
        self.assertRegex(installer, r'(?m)^Name: "english";.*Default\.isl')
        self.assertLess(installer.index('Name: "english"'), installer.index('Name: "italian"'))
        for language, note in INSTALLER_NOTICES.items():
            self.assertTrue((ROOT / "installer" / note.name).is_file(), f"missing installer/{note.name}")
            raw = (ROOT / "installer" / note.name).read_bytes()
            if not raw.isascii():
                self.assertTrue(raw.startswith(b"\xef\xbb\xbf"), f"{note.name} needs a UTF-8 BOM for Inno Setup")
            self.assertIn(f"Languages\\{language.capitalize()}.isl" if language != "english" else "Default.isl", installer)
        for build in (".github/workflows/build-windows.yml", "build_windows_installer.bat"):
            content = read(build)
            for note in INSTALLER_NOTICES.values():
                self.assertIn(note.name, content, f"{build} does not ship {note.name}")

    def test_every_build_ships_the_legal_files(self) -> None:
        for build in (
            ".github/workflows/build-windows.yml",
            "build_windows_installer.bat",
            "build_macos.sh",
        ):
            content = read(build)
            for name in ("LICENSE", "LICENSE-SUPPLEMENT.md", "NOTICE", "PRIVACY.md", "TERMS.md", "THIRD_PARTY_NOTICES.md"):
                self.assertIn(name, content, f"{build} does not ship {name}")
            self.assertIn("licenses", content, f"{build} does not ship the license texts")

    def test_installer_and_readme_mention_the_license(self) -> None:
        installer = read("installer/audio_transcriptor.iss")
        self.assertIn(r"LicenseFile=..\LICENSE", installer)
        self.assertNotIn("InfoBeforeFile=", installer, "InfoBeforeFile must be set per language")
        for language, note in INSTALLER_NOTICES.items():
            self.assertRegex(
                installer,
                rf'(?m)^Name: "{language}";.*InfoBeforeFile: "{re.escape(note.name)}"',
            )
        self.assertIn("Commons Clause", read("README.md"))
        self.assertIn("Commons Clause", read("audio_transcriptor/app.py"))

    def test_app_credits_the_author_and_explains_privacy(self) -> None:
        content = read("audio_transcriptor/app.py")
        self.assertIn("class AboutDialog", content)
        self.assertIn("Antonio Aversa", content)
        self.assertIn("PRIVACY.md", content)
        self.assertIn("THIRD_PARTY_NOTICES.md", content)
        self.assertIn("https://aversa.design", content)

    def test_repo_branding_is_only_audio_transcriptor_and_aversa(self) -> None:
        # The retired project name and the retired personal handle must not
        # reappear in published files. Spell them here so this test contains
        # no literal of either one.
        retired = ("Transcript " + "Studio", "yak" + "kyo")
        for name in (
            "audio_transcriptor/app.py",
            "README.md",
            "NOTICE",
            "TERMS.md",
            "pyproject.toml",
        ):
            content = read(name)
            for word in retired:
                self.assertNotIn(word, content, name)

    def test_changelog_documents_only_the_current_version(self) -> None:
        content = read("CHANGELOG.md")
        self.assertIn(f"## {__version__}", content)
        self.assertEqual(re.findall(r"^## (\d+\.\d+\.\d+)", content, flags=re.MULTILINE), [__version__])

    def test_workflow_publishes_release_on_tag(self) -> None:
        content = read(".github/workflows/build-windows.yml")
        self.assertIn("tags:", content)
        self.assertIn("action-gh-release", content)
        self.assertIn("contents: write", content)


class CapabilityTests(unittest.TestCase):
    def test_no_fake_local_translation_mode(self) -> None:
        self.assertEqual(TRANSLATION_MODES, ("openai",))
        self.assertNotIn("placeholder", read("audio_transcriptor/services.py").lower())

    def test_default_model_is_offered_in_settings_ui(self) -> None:
        from audio_transcriptor import app  # noqa: F401  (imported for the constant only)

        from audio_transcriptor.i18n import STRINGS

        self.assertIn("small", app.MODEL_CHOICES)
        self.assertIn("0.5 GB", STRINGS["model.small"]["en"])
        for value in app.MODEL_CHOICES:
            self.assertIn(value, WHISPER_MODELS)
            self.assertIn(f"model.{value}", STRINGS)


if __name__ == "__main__":
    unittest.main()