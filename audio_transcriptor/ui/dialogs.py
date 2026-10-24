from __future__ import annotations

from html import escape
from pathlib import Path

from PySide6.QtCore import Qt, QUrl
from PySide6.QtGui import (
    QDesktopServices,
)
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDialog,
    QFileDialog,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from audio_transcriptor import __version__, i18n
from audio_transcriptor.diagnostics import legal_document_path
from audio_transcriptor.i18n import tr, tr_n
from audio_transcriptor.settings import AppSettings
from audio_transcriptor.ui.widgets import _card, _logo_pixmap


AUTHOR = "Antonio Aversa"
PROJECT_URL = "https://aversa.design"

LICENSE_NAME = "Apache License 2.0 + Commons Clause v1.0"

# Whisper models offered in Settings; their labels live in i18n ("model.<name>").
MODEL_CHOICES = ("small", "medium", "large-v3")


class SettingsDialog(QDialog):
    """Settings: transcription model, translation, interface language, output and theme."""

    def __init__(self, settings: AppSettings, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle(tr("header.settings"))
        self.setMinimumWidth(540)

        self.model_combo = QComboBox()
        for value in MODEL_CHOICES:
            self.model_combo.addItem(tr(f"model.{value}"), value)
        self.model_combo.setCurrentIndex(max(0, self.model_combo.findData(settings.model_name)))

        self.language_combo = QComboBox()
        self.language_combo.addItem(tr("settings.audio_italian"), "it")
        self.language_combo.addItem(tr("settings.audio_auto"), "auto")
        self.language_combo.setCurrentIndex(0 if settings.language == "it" else 1)

        self.ui_language_combo = QComboBox()
        self.ui_language_combo.addItem(tr("settings.interface_system"), "system")
        for code in i18n.LANGUAGES:
            # Each language is shown in itself, so it can be found from any language.
            self.ui_language_combo.addItem(i18n.LANGUAGE_NAMES[code], code)
        self.ui_language_combo.setCurrentIndex(
            max(0, self.ui_language_combo.findData(settings.ui_language))
        )

        self.output_edit = QLineEdit(settings.output_folder)
        output_button = QPushButton(tr("action.browse"))
        output_button.setObjectName("secondary")
        output_button.clicked.connect(self.choose_output_folder)
        output_row = QHBoxLayout()
        output_row.addWidget(self.output_edit, stretch=1)
        output_row.addWidget(output_button)

        self.api_key_edit = QLineEdit(settings.openai_api_key)
        self.api_key_edit.setEchoMode(QLineEdit.EchoMode.Password)
        self.openai_model_edit = QLineEdit(settings.openai_model)
        self.confirm_translation_check = QCheckBox(tr("settings.confirm_translation"))
        self.confirm_translation_check.setChecked(settings.confirm_translation)

        self.theme_combo = QComboBox()
        self.theme_combo.addItem(tr("settings.theme_light"), "light")
        self.theme_combo.addItem(tr("settings.theme_dark"), "dark")
        self.theme_combo.setCurrentIndex(0 if settings.theme == "light" else 1)

        root = QVBoxLayout(self)
        root.setContentsMargins(18, 16, 18, 16)
        root.setSpacing(12)

        model_card, model_layout = _card(tr("settings.section_model"))
        grid = QGridLayout()
        grid.setHorizontalSpacing(10)
        grid.setVerticalSpacing(8)
        grid.addWidget(QLabel(tr("settings.whisper_model")), 0, 0)
        grid.addWidget(self.model_combo, 0, 1)
        grid.addWidget(QLabel(tr("settings.audio_language")), 1, 0)
        grid.addWidget(self.language_combo, 1, 1)
        model_layout.addLayout(grid)
        root.addWidget(model_card)

        trans_card, trans_layout = _card(tr("settings.section_translation"))
        hint = QLabel(tr("settings.translation_hint"))
        hint.setObjectName("muted")
        trans_layout.addWidget(hint)
        tgrid = QGridLayout()
        tgrid.setHorizontalSpacing(10)
        tgrid.setVerticalSpacing(8)
        tgrid.addWidget(QLabel(tr("settings.api_key")), 0, 0)
        tgrid.addWidget(self.api_key_edit, 0, 1)
        tgrid.addWidget(QLabel(tr("settings.openai_model")), 1, 0)
        tgrid.addWidget(self.openai_model_edit, 1, 1)
        trans_layout.addLayout(tgrid)
        trans_layout.addWidget(self.confirm_translation_check)
        root.addWidget(trans_card)

        gen_card, gen_layout = _card(tr("settings.section_general"))
        ggrid = QGridLayout()
        ggrid.setHorizontalSpacing(10)
        ggrid.setVerticalSpacing(8)
        ggrid.addWidget(QLabel(tr("settings.interface_language")), 0, 0)
        ggrid.addWidget(self.ui_language_combo, 0, 1)
        ggrid.addWidget(QLabel(tr("settings.output_folder")), 1, 0)
        ggrid.addLayout(output_row, 1, 1)
        ggrid.addWidget(QLabel(tr("settings.theme")), 2, 0)
        ggrid.addWidget(self.theme_combo, 2, 1)
        gen_layout.addLayout(ggrid)
        root.addWidget(gen_card)

        save_button = QPushButton(tr("action.save"))
        cancel_button = QPushButton(tr("action.cancel"))
        cancel_button.setObjectName("secondary")
        save_button.clicked.connect(self.accept)
        cancel_button.clicked.connect(self.reject)
        buttons = QHBoxLayout()
        buttons.addStretch()
        buttons.addWidget(cancel_button)
        buttons.addWidget(save_button)
        root.addLayout(buttons)

    def choose_output_folder(self) -> None:
        folder = QFileDialog.getExistingDirectory(
            self, tr("settings.choose_folder"), self.output_edit.text()
        )
        if folder:
            self.output_edit.setText(folder)

    def updated_settings(self) -> AppSettings:
        return AppSettings(
            model_name=self.model_combo.currentData(),
            language=self.language_combo.currentData(),
            output_folder=self.output_edit.text().strip(),
            openai_api_key=self.api_key_edit.text().strip(),
            openai_model=self.openai_model_edit.text().strip() or "gpt-5",
            translation_mode="openai",
            theme="dark" if self.theme_combo.currentData() == "dark" else "light",
            confirm_translation=self.confirm_translation_check.isChecked(),
            ui_language=self.ui_language_combo.currentData(),
        )


class ExportDialog(QDialog):
    """Export panel: TXT / SRT / DOCX for the Italian text and the English translation."""

    def __init__(
        self,
        parent: QWidget | None,
        flags: dict[str, bool],
        output_folder: str,
    ) -> None:
        super().__init__(parent)
        self.setWindowTitle(tr("export.window"))
        self.setMinimumWidth(560)
        self.flags = flags
        self.output_folder = output_folder

        root = QVBoxLayout(self)
        root.setContentsMargins(18, 16, 18, 16)
        root.setSpacing(12)

        title = QLabel(tr("export.title"))
        title.setStyleSheet("font-size: 17px; font-weight: 700;")
        root.addWidget(title)

        intro = QLabel(tr("export.intro"))
        intro.setObjectName("muted")
        intro.setWordWrap(True)
        root.addWidget(intro)

        grid = QGridLayout()
        grid.setHorizontalSpacing(10)
        grid.setVerticalSpacing(10)
        grid.addWidget(QLabel(""), 0, 0)
        grid.addWidget(QLabel(tr("pane.italian")), 0, 1)
        grid.addWidget(QLabel(tr("pane.english")), 0, 2)
        for row, kind in enumerate(("txt", "srt", "docx"), start=1):
            grid.addWidget(QLabel(kind.upper()), row, 0)
            for col, lang in ((1, "it"), (2, "en")):
                key = f"{lang}_{kind}"
                button = QPushButton(tr("export.button", fmt=kind.upper()))
                button.setObjectName("secondary")
                button.setEnabled(flags.get(key, False))
                button.clicked.connect(
                    lambda checked=False, k=key: self.request_export(k)
                )
                grid.addWidget(button, row, col)
        root.addLayout(grid)

        folder_row = QHBoxLayout()
        folder_label = QLabel(tr("export.folder"))
        folder_label.setObjectName("muted")
        self.folder_label = QLabel(output_folder or tr("export.folder_default"))
        self.folder_label.setObjectName("muted")
        self.folder_label.setWordWrap(True)
        open_button = QPushButton(tr("action.open_folder"))
        open_button.setObjectName("ghost")
        open_button.clicked.connect(self.open_folder)
        folder_row.addWidget(folder_label)
        folder_row.addWidget(self.folder_label, stretch=1)
        folder_row.addWidget(open_button)
        root.addLayout(folder_row)

        close_button = QPushButton(tr("action.close"))
        close_button.setObjectName("secondary")
        close_button.clicked.connect(self.accept)
        buttons = QHBoxLayout()
        buttons.addStretch()
        buttons.addWidget(close_button)
        root.addLayout(buttons)

        self._export_requested: str | None = None

    def open_folder(self) -> None:
        folder = self.output_folder or str(Path.home())
        QDesktopServices.openUrl(QUrl.fromLocalFile(folder))

    def request_export(self, kind: str) -> None:
        self._export_requested = kind
        self.accept()

    def requested_export(self) -> str | None:
        return self._export_requested


class TranslationConfirmDialog(QDialog):
    """Confirms what is sent to OpenAI: the text only, never the audio."""

    def __init__(
        self, parent: QWidget | None, sentences: int, characters: int, model: str
    ) -> None:
        super().__init__(parent)
        self.setWindowTitle(tr("action.translate"))
        self.setMinimumWidth(480)

        root = QVBoxLayout(self)
        root.setContentsMargins(20, 18, 20, 18)
        root.setSpacing(12)

        title = QLabel(tr("confirm.title"))
        title.setStyleSheet("font-size: 17px; font-weight: 700;")
        root.addWidget(title)

        body = QLabel(
            tr(
                "confirm.body",
                sentences=tr_n("work.sentences", sentences),
                chars=i18n.format_int(characters),
                model=escape(model),
            )
        )
        body.setWordWrap(True)
        root.addWidget(body)

        self.dont_ask = QCheckBox(tr("confirm.dont_ask"))
        root.addWidget(self.dont_ask)

        send_button = QPushButton(tr("confirm.send"))
        cancel_button = QPushButton(tr("action.cancel"))
        cancel_button.setObjectName("secondary")
        send_button.clicked.connect(self.accept)
        cancel_button.clicked.connect(self.reject)
        send_button.setDefault(True)
        buttons = QHBoxLayout()
        buttons.addStretch()
        buttons.addWidget(cancel_button)
        buttons.addWidget(send_button)
        root.addLayout(buttons)

    def dont_ask_again(self) -> bool:
        return self.dont_ask.isChecked()


class AboutDialog(QDialog):
    """Credit, privacy, accuracy and license summary, reachable from the main window."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle(tr("header.about"))
        self.setMinimumWidth(560)

        root = QVBoxLayout(self)
        root.setContentsMargins(20, 18, 20, 18)
        root.setSpacing(12)

        head = QHBoxLayout()
        logo = QLabel()
        logo.setPixmap(_logo_pixmap(56))
        head.addWidget(logo)
        title_box = QVBoxLayout()
        title = QLabel(f"AudioTranscriptor {__version__}")
        title.setStyleSheet("font-size: 19px; font-weight: 700;")
        author = QLabel(
            f'{escape(tr("about.made_by", author=AUTHOR))} · '
            f'<a href="{PROJECT_URL}">{PROJECT_URL.replace("https://", "")}</a>'
        )
        author.setObjectName("muted")
        author.setOpenExternalLinks(True)
        title_box.addWidget(title)
        title_box.addWidget(author)
        head.addLayout(title_box, stretch=1)
        root.addLayout(head)

        # Read legal texts shipped with the app, not unverified website routes.
        # The legal documents themselves are in English, whatever the interface.
        urls = {}
        for name in ("LICENSE", "PRIVACY.md", "TERMS.md", "THIRD_PARTY_NOTICES.md"):
            path = legal_document_path(name)
            urls[name] = escape(path.as_uri() if path else PROJECT_URL, quote=True)

        def link(name: str, key: str) -> str:
            return f'<a href="{urls[name]}">{escape(tr(key))}</a>'

        body = QLabel(
            f"<p><b>{tr('about.privacy_title')}</b> "
            f"{tr('about.privacy_body', translate=escape(tr('action.translate')))} "
            f"{link('PRIVACY.md', 'about.privacy_link')}.</p>"
            f"<p><b>{tr('about.accuracy_title')}</b> {tr('about.accuracy_body')} "
            f"{link('TERMS.md', 'about.terms_link')}.</p>"
            f"<p><b>{tr('about.license_title')}</b> "
            f"{tr('about.license_body', license=LICENSE_NAME)} "
            f"{link('LICENSE', 'about.license_link')} · "
            f"{link('THIRD_PARTY_NOTICES.md', 'about.third_party_link')} "
            f"{tr('about.third_party_list')} · {tr('about.permissions')} "
            f'<a href="{PROJECT_URL}">aversa.design</a>.</p>'
        )
        body.setWordWrap(True)
        body.setOpenExternalLinks(True)
        body.setTextInteractionFlags(Qt.TextInteractionFlag.TextBrowserInteraction)
        root.addWidget(body, stretch=1)

        close_button = QPushButton(tr("action.close"))
        close_button.clicked.connect(self.accept)
        buttons = QHBoxLayout()
        buttons.addStretch()
        buttons.addWidget(close_button)
        root.addLayout(buttons)
