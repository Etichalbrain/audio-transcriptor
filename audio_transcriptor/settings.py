from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path

from platformdirs import user_config_dir


APP_NAME = "AudioTranscriptor"

WHISPER_MODELS = ("small", "medium", "large-v3")
DEFAULT_MODEL = "small"
TRANSLATION_MODES = ("openai",)
LANGUAGES = ("it", "auto")
THEMES = ("light", "dark")


@dataclass
class AppSettings:
    model_name: str = DEFAULT_MODEL
    language: str = "it"
    output_folder: str = ""
    openai_api_key: str = ""
    openai_model: str = "gpt-5"
    translation_mode: str = "openai"
    theme: str = "light"
    confirm_translation: bool = True

    def __post_init__(self) -> None:
        # Sanitise values that may come from an older settings file, so the app
        # never offers a mode or a model it cannot run.
        if self.model_name not in WHISPER_MODELS:
            self.model_name = DEFAULT_MODEL
        if self.language not in LANGUAGES:
            self.language = "it"
        if self.translation_mode not in TRANSLATION_MODES:
            self.translation_mode = "openai"
        if self.theme not in THEMES:
            self.theme = "light"


class SettingsStore:
    def __init__(self) -> None:
        self.config_dir = Path(user_config_dir(APP_NAME, appauthor=False))
        self.config_path = self.config_dir / "settings.json"

    def load(self) -> AppSettings:
        if not self.config_path.exists():
            return AppSettings()
        try:
            data = json.loads(self.config_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return AppSettings()
        if not isinstance(data, dict):
            return AppSettings()
        defaults = asdict(AppSettings())
        defaults.update({key: value for key, value in data.items() if key in defaults})
        return AppSettings(**defaults)

    def save(self, settings: AppSettings) -> None:
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.config_path.write_text(
            json.dumps(asdict(settings), indent=2),
            encoding="utf-8",
        )
        # The file holds the OpenAI API key in plain text (see PRIVACY.md), so it
        # is kept readable by the owner only. On Windows this only clears the
        # read-only flag; the per-user profile already protects the folder.
        for target, mode in ((self.config_dir, 0o700), (self.config_path, 0o600)):
            try:
                target.chmod(mode)
            except OSError:
                pass
