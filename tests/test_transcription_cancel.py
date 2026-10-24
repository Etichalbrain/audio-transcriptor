from __future__ import annotations

import time
import unittest

import faster_whisper.utils as whisper_utils

from audio_transcriptor.services import TranscriptionService


class ModelLoadCancelTests(unittest.TestCase):
    def test_cancel_interrupts_a_running_download(self) -> None:
        original = whisper_utils.download_model

        def slow_download(size_or_id: str, **kwargs) -> str:
            time.sleep(5)
            return size_or_id

        whisper_utils.download_model = slow_download
        self.addCleanup(setattr, whisper_utils, "download_model", original)

        started = time.monotonic()
        with self.assertRaises(RuntimeError):
            TranscriptionService()._load_model(
                "small",
                progress_callback=lambda status, value, *_: None,
                cancel_checker=lambda: True,
            )
        self.assertLess(time.monotonic() - started, 2, "cancel should not wait for the download")


if __name__ == "__main__":
    unittest.main()
