from __future__ import annotations

import tempfile
import unittest
import wave
from pathlib import Path
from unittest.mock import patch

from audio_transcriptor import __version__
from audio_transcriptor.diagnostics import (
    CHECKS_IMPORTS,
    _write_probe_wav,
    format_report,
    legal_document_path,
    run_self_test,
)


class SelfTestTests(unittest.TestCase):
    def setUp(self) -> None:
        # Exercise the real writable-folder check without touching a user's
        # profile or depending on permissions outside the test workspace.
        folder = tempfile.TemporaryDirectory()
        self.addCleanup(folder.cleanup)
        config = patch("audio_transcriptor.settings.user_config_dir", return_value=folder.name)
        config.start()
        self.addCleanup(config.stop)

    def test_every_check_passes_in_a_source_checkout(self) -> None:
        results = run_self_test()
        failures = [
            f"{name}: {detail}"
            for name, passed, detail in results
            if not passed
        ]
        self.assertEqual(failures, [], "self-test failures: " + "; ".join(failures))

    def test_checks_cover_the_runtime_dependencies(self) -> None:
        checked = {name for name, _passed, _detail in run_self_test()}
        for module_name in CHECKS_IMPORTS:
            self.assertIn(f"import {module_name}", checked)
        self.assertIn("silero VAD asset", checked)
        self.assertIn("docx template", checked)
        self.assertIn("settings folder writable", checked)
        self.assertIn("license shipped with the app", checked)

    def test_packaged_legal_files_cannot_be_masked_by_checkout(self) -> None:
        with tempfile.TemporaryDirectory() as folder:
            app = Path(folder) / "Example.app"
            resources = app / "Contents" / "Resources"
            resources.mkdir(parents=True)
            with patch("audio_transcriptor.diagnostics.sys.frozen", True, create=True), \
                 patch("audio_transcriptor.diagnostics._bundle_contents", return_value=app):
                self.assertIsNone(legal_document_path("LICENSE"))
                license_file = resources / "LICENSE.txt"
                license_file.write_text("combined license", encoding="utf-8")
                self.assertEqual(legal_document_path("LICENSE"), license_file)
                self.assertIsNone(legal_document_path("NOTICE"))
                self.assertIsNone(legal_document_path("../LICENSE"))

    def test_checks_cover_all_shipped_legal_documents(self) -> None:
        checked = {name for name, _passed, _detail in run_self_test()}
        for name in ("NOTICE", "LICENSE-SUPPLEMENT.md", "PRIVACY.md", "TERMS.md", "THIRD_PARTY_NOTICES.md"):
            self.assertIn(f"legal document {name}", checked)

    def test_engine_check_is_opt_in(self) -> None:
        names = [name for name, _passed, _detail in run_self_test()]
        self.assertFalse(any(name.startswith("transcription engine") for name in names))

    def test_probe_wav_is_a_playable_mono_file(self) -> None:
        with tempfile.TemporaryDirectory() as folder:
            probe = Path(folder) / "probe.wav"
            _write_probe_wav(probe)
            with wave.open(str(probe)) as handle:
                self.assertEqual(handle.getnchannels(), 1)
                self.assertEqual(handle.getframerate(), 16000)
                self.assertEqual(handle.getnframes(), 32000)

    def test_report_shows_version_and_outcome(self) -> None:
        report = format_report([("version", True, __version__), ("broken", False, "nope")])
        self.assertIn(f"AudioTranscriptor {__version__} self-test", report)
        self.assertIn("[OK  ] version", report)
        self.assertIn("[FAIL] broken", report)
        self.assertIn("1 passed, 1 failed", report)


if __name__ == "__main__":
    unittest.main()
