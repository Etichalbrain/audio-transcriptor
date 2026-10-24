"""Interface strings in English, Italian, German and French.

One table, one entry per key, every language side by side: a missing
translation is visible at a glance and caught by tests/test_i18n.py.
Placeholders use str.format names ({name}) and must match across languages.
Plurals use two keys, ``<key>.one`` and ``<key>.other``.

Only the interface is translated. The transcription language (Italian or
automatic) and the translation target (English) do not depend on it.
"""

from __future__ import annotations

from typing import Iterable

LANGUAGES = ("en", "it", "de", "fr")
DEFAULT_LANGUAGE = "en"

# Each language named in itself, as it appears in the language picker.
LANGUAGE_NAMES = {
    "en": "English",
    "it": "Italiano",
    "de": "Deutsch",
    "fr": "Français",
}

_current = DEFAULT_LANGUAGE

STRINGS: dict[str, dict[str, str]] = {
    # --- Header and main actions -------------------------------------------
    "header.about": {
        "en": "About", "it": "Informazioni", "de": "Info", "fr": "À propos",
    },
    "header.settings": {
        "en": "Settings", "it": "Impostazioni", "de": "Einstellungen", "fr": "Réglages",
    },
    "hero.title": {
        "en": "Drop an audio or video file here",
        "it": "Trascina qui un file audio o video",
        "de": "Audio- oder Videodatei hierher ziehen",
        "fr": "Déposez un fichier audio ou vidéo ici",
    },
    "hero.choose": {
        "en": "Choose file", "it": "Scegli file", "de": "Datei wählen", "fr": "Choisir un fichier",
    },
    "file.none": {
        "en": "No file selected", "it": "Nessun file selezionato",
        "de": "Keine Datei ausgewählt", "fr": "Aucun fichier sélectionné",
    },
    "file.duration": {
        "en": "duration {time}", "it": "durata {time}", "de": "Dauer {time}", "fr": "durée {time}",
    },
    "file.remove": {
        "en": "Remove file", "it": "Rimuovi file", "de": "Datei entfernen", "fr": "Retirer le fichier",
    },
    "file.change": {
        "en": "Change file", "it": "Cambia file", "de": "Datei wechseln", "fr": "Changer de fichier",
    },
    "chip.model": {
        "en": "Model: {name}", "it": "Modello: {name}", "de": "Modell: {name}", "fr": "Modèle : {name}",
    },
    "chip.downloading": {
        "en": "Model: {name} · downloading…",
        "it": "Modello: {name} · download in corso…",
        "de": "Modell: {name} · wird heruntergeladen…",
        "fr": "Modèle : {name} · téléchargement…",
    },
    "chip.loading": {
        "en": "Model: {name} · loading…",
        "it": "Modello: {name} · caricamento…",
        "de": "Modell: {name} · wird geladen…",
        "fr": "Modèle : {name} · chargement…",
    },
    "action.transcribe": {
        "en": "Transcribe Italian audio", "it": "Trascrivi in italiano",
        "de": "Italienisch transkribieren", "fr": "Transcrire l’italien",
    },
    "action.translate": {
        "en": "Translate to English", "it": "Traduci in inglese",
        "de": "Ins Englische übersetzen", "fr": "Traduire en anglais",
    },
    "action.export": {
        "en": "Export…", "it": "Esporta…", "de": "Exportieren…", "fr": "Exporter…",
    },
    "action.cancel_job": {
        "en": "Cancel", "it": "Annulla operazione", "de": "Abbrechen", "fr": "Annuler l’opération",
    },
    "action.close": {
        "en": "Close", "it": "Chiudi", "de": "Schließen", "fr": "Fermer",
    },
    "action.cancel": {
        "en": "Cancel", "it": "Annulla", "de": "Abbrechen", "fr": "Annuler",
    },
    "action.save": {
        "en": "Save", "it": "Salva", "de": "Speichern", "fr": "Enregistrer",
    },
    "action.open_folder": {
        "en": "Open folder", "it": "Apri cartella", "de": "Ordner öffnen", "fr": "Ouvrir le dossier",
    },
    "action.browse": {
        "en": "Browse…", "it": "Sfoglia…", "de": "Durchsuchen…", "fr": "Parcourir…",
    },

    # --- Work area ---------------------------------------------------------
    "work.title": {
        "en": "Transcript", "it": "Trascrizione", "de": "Transkript", "fr": "Transcription",
    },
    "work.sentences.one": {
        "en": "{n} sentence", "it": "{n} frase", "de": "{n} Satz", "fr": "{n} phrase",
    },
    "work.sentences.other": {
        "en": "{n} sentences", "it": "{n} frasi", "de": "{n} Sätze", "fr": "{n} phrases",
    },
    "work.words.one": {
        "en": "{n} word", "it": "{n} parola", "de": "{n} Wort", "fr": "{n} mot",
    },
    "work.words.other": {
        "en": "{n} words", "it": "{n} parole", "de": "{n} Wörter", "fr": "{n} mots",
    },
    "pane.italian": {
        "en": "Italian", "it": "Italiano", "de": "Italienisch", "fr": "Italien",
    },
    "pane.english": {
        "en": "English", "it": "Inglese", "de": "Englisch", "fr": "Anglais",
    },
    "placeholder.italian": {
        "en": "The Italian transcript will appear here. You can fix the text before "
              "translating or exporting it.",
        "it": "La trascrizione in italiano apparirà qui. Puoi correggere il testo prima "
              "di tradurlo o esportarlo.",
        "de": "Hier erscheint das italienische Transkript. Sie können den Text vor dem "
              "Übersetzen oder Exportieren korrigieren.",
        "fr": "La transcription italienne apparaîtra ici. Vous pouvez corriger le texte "
              "avant de le traduire ou de l’exporter.",
    },
    "placeholder.english": {
        "en": "The English translation will appear here, next to the Italian.",
        "it": "La traduzione in inglese apparirà qui, accanto all’italiano.",
        "de": "Hier erscheint die englische Übersetzung, neben dem Italienischen.",
        "fr": "La traduction anglaise apparaîtra ici, à côté de l’italien.",
    },
    "footer": {
        "en": "AudioTranscriptor by {author} · aversa.design · the audio stays on this computer",
        "it": "AudioTranscriptor di {author} · aversa.design · l’audio resta su questo computer",
        "de": "AudioTranscriptor von {author} · aversa.design · das Audio bleibt auf diesem Computer",
        "fr": "AudioTranscriptor par {author} · aversa.design · l’audio reste sur cet ordinateur",
    },

    # --- Player ------------------------------------------------------------
    "player.play": {
        "en": "Play", "it": "Riproduci", "de": "Abspielen", "fr": "Lire",
    },
    "player.pause": {
        "en": "Pause", "it": "Pausa", "de": "Pause", "fr": "Pause",
    },
    "player.from_cursor": {
        "en": "Play from cursor", "it": "Ascolta da qui", "de": "Ab Cursor abspielen",
        "fr": "Écouter d’ici",
    },
    "player.back": {
        "en": "Back 5 seconds", "it": "Indietro di 5 secondi", "de": "5 Sekunden zurück",
        "fr": "Reculer de 5 secondes",
    },
    "player.forward": {
        "en": "Forward 5 seconds", "it": "Avanti di 5 secondi", "de": "5 Sekunden vor",
        "fr": "Avancer de 5 secondes",
    },
    "player.position": {
        "en": "Playback position", "it": "Posizione di ascolto", "de": "Wiedergabeposition",
        "fr": "Position de lecture",
    },
    "player.shortcuts": {
        "en": "{play} play/pause · {jump} play from the cursor line · {back} / {fwd} 5 s back / forward",
        "it": "{play} riproduci/pausa · {jump} ascolta dalla riga del cursore · {back} / {fwd} 5 s indietro / avanti",
        "de": "{play} Abspielen/Pause · {jump} ab der Cursorzeile abspielen · {back} / {fwd} 5 s zurück / vor",
        "fr": "{play} lecture/pause · {jump} écouter depuis la ligne du curseur · {back} / {fwd} 5 s en arrière / en avant",
    },
    "player.unavailable": {
        "en": "Audio playback is not available on this computer. Transcription and export still work.",
        "it": "La riproduzione audio non è disponibile su questo computer. Trascrizione ed esportazione funzionano comunque.",
        "de": "Die Audiowiedergabe ist auf diesem Computer nicht verfügbar. Transkription und Export funktionieren weiterhin.",
        "fr": "La lecture audio n’est pas disponible sur cet ordinateur. La transcription et l’export fonctionnent toujours.",
    },

    # --- Status ------------------------------------------------------------
    "status.title": {
        "en": "Status", "it": "Stato", "de": "Status", "fr": "État",
    },
    "status.ready": {
        "en": "Ready", "it": "Pronto", "de": "Bereit", "fr": "Prêt",
    },
    "status.file_selected": {
        "en": "File selected", "it": "File selezionato", "de": "Datei ausgewählt",
        "fr": "Fichier sélectionné",
    },
    "status.preparing_audio": {
        "en": "Preparing audio…", "it": "Preparazione audio…", "de": "Audio wird vorbereitet…",
        "fr": "Préparation de l’audio…",
    },
    "status.cancelling": {
        "en": "Cancelling…", "it": "Annullamento…", "de": "Wird abgebrochen…", "fr": "Annulation…",
    },
    "status.error": {
        "en": "Error", "it": "Errore", "de": "Fehler", "fr": "Erreur",
    },
    "status.saved": {
        "en": "Saved {name}", "it": "Salvato {name}", "de": "{name} gespeichert",
        "fr": "{name} enregistré",
    },
    "success.saved": {
        "en": "Done: saved “{name}” in {folder}",
        "it": "Lavoro completato: salvato “{name}” in {folder}",
        "de": "Fertig: „{name}“ in {folder} gespeichert",
        "fr": "Terminé : « {name} » enregistré dans {folder}",
    },

    # --- Progress reported by the services ---------------------------------
    "progress.preparing_model": {
        "en": "Preparing the Whisper model…", "it": "Preparazione del modello Whisper…",
        "de": "Whisper-Modell wird vorbereitet…", "fr": "Préparation du modèle Whisper…",
    },
    "progress.downloading_model": {
        "en": "Downloading the Whisper model (first use only)…",
        "it": "Download del modello Whisper (solo al primo utilizzo)…",
        "de": "Whisper-Modell wird heruntergeladen (nur beim ersten Mal)…",
        "fr": "Téléchargement du modèle Whisper (première utilisation uniquement)…",
    },
    "progress.loading_model": {
        "en": "Loading the Whisper model…", "it": "Caricamento del modello Whisper…",
        "de": "Whisper-Modell wird geladen…", "fr": "Chargement du modèle Whisper…",
    },
    "progress.transcribing": {
        "en": "Transcribing…", "it": "Trascrizione in corso…", "de": "Wird transkribiert…",
        "fr": "Transcription en cours…",
    },
    "progress.transcribing_time": {
        "en": "Transcribing: {done} of {total}",
        "it": "Trascrizione in corso: {done} di {total}",
        "de": "Wird transkribiert: {done} von {total}",
        "fr": "Transcription en cours : {done} sur {total}",
    },
    "progress.transcribed": {
        "en": "Transcription complete", "it": "Trascrizione completata",
        "de": "Transkription abgeschlossen", "fr": "Transcription terminée",
    },
    "progress.translating": {
        "en": "Translating…", "it": "Traduzione in corso…", "de": "Wird übersetzt…",
        "fr": "Traduction en cours…",
    },
    "progress.translating_count": {
        "en": "Translating: {done} of {total} sentences",
        "it": "Traduzione in corso: {done} di {total} frasi",
        "de": "Wird übersetzt: {done} von {total} Sätzen",
        "fr": "Traduction en cours : {done} phrases sur {total}",
    },
    "progress.translated": {
        "en": "Translation complete", "it": "Traduzione completata",
        "de": "Übersetzung abgeschlossen", "fr": "Traduction terminée",
    },

    # --- Errors ------------------------------------------------------------
    "error.unsupported": {
        "en": "Choose a supported MP3, WAV, M4A, MP4, MOV or MKV file.",
        "it": "Scegli un file MP3, WAV, M4A, MP4, MOV o MKV supportato.",
        "de": "Wählen Sie eine unterstützte MP3-, WAV-, M4A-, MP4-, MOV- oder MKV-Datei.",
        "fr": "Choisissez un fichier MP3, WAV, M4A, MP4, MOV ou MKV pris en charge.",
    },
    "error.disk_precheck": {
        "en": "There may not be enough disk space to process this file.",
        "it": "Potrebbe non esserci spazio su disco sufficiente per elaborare questo file.",
        "de": "Möglicherweise ist nicht genug Speicherplatz für diese Datei frei.",
        "fr": "L’espace disque risque d’être insuffisant pour traiter ce fichier.",
    },
    "error.disk": {
        "en": "Not enough disk space. Free some space or choose another output folder.",
        "it": "Spazio su disco insufficiente. Libera spazio o scegli un’altra cartella di output.",
        "de": "Nicht genug Speicherplatz. Geben Sie Speicher frei oder wählen Sie einen "
              "anderen Ausgabeordner.",
        "fr": "Espace disque insuffisant. Libérez de l’espace ou choisissez un autre dossier "
              "de sortie.",
    },
    "error.api_key": {
        "en": "Add your OpenAI API key in Settings before translating.",
        "it": "Aggiungi la tua chiave API OpenAI in Impostazioni prima di tradurre.",
        "de": "Fügen Sie vor dem Übersetzen Ihren OpenAI-API-Schlüssel in den Einstellungen hinzu.",
        "fr": "Ajoutez votre clé API OpenAI dans les Réglages avant de traduire.",
    },
    "error.cancelled": {
        "en": "The operation was cancelled.",
        "it": "L’operazione in corso è stata annullata.",
        "de": "Der Vorgang wurde abgebrochen.",
        "fr": "L’opération a été annulée.",
    },
    "error.model_download": {
        "en": "The Whisper model could not be downloaded. Check your connection and try again.",
        "it": "Il modello Whisper non può essere scaricato. Controlla la connessione e riprova.",
        "de": "Das Whisper-Modell konnte nicht heruntergeladen werden. Prüfen Sie die "
              "Verbindung und versuchen Sie es erneut.",
        "fr": "Le modèle Whisper n’a pas pu être téléchargé. Vérifiez votre connexion et "
              "réessayez.",
    },
    "error.generic": {
        "en": "Something went wrong. Try again.",
        "it": "Qualcosa è andato storto. Riprova.",
        "de": "Etwas ist schiefgelaufen. Bitte erneut versuchen.",
        "fr": "Un problème est survenu. Réessayez.",
    },
    "error.save_failed": {
        "en": "The file could not be saved. Check the folder and try again.",
        "it": "Impossibile salvare il file. Controlla la cartella e riprova.",
        "de": "Die Datei konnte nicht gespeichert werden. Prüfen Sie den Ordner und "
              "versuchen Sie es erneut.",
        "fr": "Impossible d’enregistrer le fichier. Vérifiez le dossier et réessayez.",
    },

    # --- File dialogs --------------------------------------------------------
    "dialog.open_media": {
        "en": "Select an audio or video file", "it": "Seleziona file audio o video",
        "de": "Audio- oder Videodatei auswählen", "fr": "Sélectionner un fichier audio ou vidéo",
    },
    "dialog.media_filter": {
        "en": "Audio and video files", "it": "File audio e video",
        "de": "Audio- und Videodateien", "fr": "Fichiers audio et vidéo",
    },
    "dialog.save_file": {
        "en": "Save file", "it": "Salva file", "de": "Datei speichern", "fr": "Enregistrer le fichier",
    },

    # --- Settings ----------------------------------------------------------
    "settings.section_model": {
        "en": "Transcription model", "it": "Modello di trascrizione",
        "de": "Transkriptionsmodell", "fr": "Modèle de transcription",
    },
    "settings.whisper_model": {
        "en": "Whisper model", "it": "Modello Whisper", "de": "Whisper-Modell",
        "fr": "Modèle Whisper",
    },
    "settings.audio_language": {
        "en": "Audio language", "it": "Lingua dell’audio", "de": "Sprache des Audios",
        "fr": "Langue de l’audio",
    },
    "settings.audio_italian": {
        "en": "Italian", "it": "Italiano", "de": "Italienisch", "fr": "Italien",
    },
    "settings.audio_auto": {
        "en": "Automatic", "it": "Automatica", "de": "Automatisch", "fr": "Automatique",
    },
    "settings.section_translation": {
        "en": "Translation", "it": "Traduzione", "de": "Übersetzung", "fr": "Traduction",
    },
    "settings.translation_hint": {
        "en": "Translation uses the OpenAI API with your own key.",
        "it": "La traduzione usa l’API OpenAI con la tua chiave.",
        "de": "Die Übersetzung nutzt die OpenAI-API mit Ihrem eigenen Schlüssel.",
        "fr": "La traduction utilise l’API OpenAI avec votre propre clé.",
    },
    "settings.api_key": {
        "en": "API key", "it": "Chiave API", "de": "API-Schlüssel", "fr": "Clé API",
    },
    "settings.openai_model": {
        "en": "OpenAI model", "it": "Modello OpenAI", "de": "OpenAI-Modell", "fr": "Modèle OpenAI",
    },
    "settings.confirm_translation": {
        "en": "Ask before sending text to OpenAI",
        "it": "Chiedi conferma prima di inviare il testo a OpenAI",
        "de": "Vor dem Senden von Text an OpenAI nachfragen",
        "fr": "Demander avant d’envoyer le texte à OpenAI",
    },
    "settings.section_general": {
        "en": "General", "it": "Generale", "de": "Allgemein", "fr": "Général",
    },
    "settings.interface_language": {
        "en": "Interface language", "it": "Lingua dell’interfaccia",
        "de": "Sprache der Oberfläche", "fr": "Langue de l’interface",
    },
    "settings.interface_system": {
        "en": "Same as system", "it": "Come il sistema", "de": "Wie das System",
        "fr": "Comme le système",
    },
    "settings.output_folder": {
        "en": "Output folder", "it": "Cartella di output", "de": "Ausgabeordner",
        "fr": "Dossier de sortie",
    },
    "settings.choose_folder": {
        "en": "Choose the output folder", "it": "Scegli la cartella di output",
        "de": "Ausgabeordner wählen", "fr": "Choisir le dossier de sortie",
    },
    "settings.theme": {
        "en": "Theme", "it": "Tema", "de": "Design", "fr": "Thème",
    },
    "settings.theme_light": {
        "en": "Light", "it": "Chiaro", "de": "Hell", "fr": "Clair",
    },
    "settings.theme_dark": {
        "en": "Dark", "it": "Scuro", "de": "Dunkel", "fr": "Sombre",
    },
    "model.small": {
        "en": "small (fast, about 0.5 GB to download)",
        "it": "small (veloce, circa 0,5 GB da scaricare)",
        "de": "small (schnell, etwa 0,5 GB Download)",
        "fr": "small (rapide, environ 0,5 Go à télécharger)",
    },
    "model.medium": {
        "en": "medium (balanced, about 1.5 GB)",
        "it": "medium (equilibrato, circa 1,5 GB)",
        "de": "medium (ausgewogen, etwa 1,5 GB)",
        "fr": "medium (équilibré, environ 1,5 Go)",
    },
    "model.large-v3": {
        "en": "large-v3 (best quality, about 3 GB)",
        "it": "large-v3 (qualità migliore, circa 3 GB)",
        "de": "large-v3 (beste Qualität, etwa 3 GB)",
        "fr": "large-v3 (meilleure qualité, environ 3 Go)",
    },

    # --- Export ------------------------------------------------------------
    "export.window": {
        "en": "Export", "it": "Esporta", "de": "Exportieren", "fr": "Exporter",
    },
    "export.title": {
        "en": "Export transcript", "it": "Esporta trascrizione", "de": "Transkript exportieren",
        "fr": "Exporter la transcription",
    },
    "export.intro": {
        "en": "Choose a format: files are saved in the output folder.",
        "it": "Scegli il formato: i file vengono salvati nella cartella di output.",
        "de": "Wählen Sie ein Format: Die Dateien werden im Ausgabeordner gespeichert.",
        "fr": "Choisissez un format : les fichiers sont enregistrés dans le dossier de sortie.",
    },
    "export.button": {
        "en": "Export {fmt}", "it": "Esporta {fmt}", "de": "{fmt} exportieren", "fr": "Exporter {fmt}",
    },
    "export.folder": {
        "en": "Folder:", "it": "Cartella:", "de": "Ordner:", "fr": "Dossier :",
    },
    "export.folder_default": {
        "en": "(next to the selected file)", "it": "(accanto al file selezionato)",
        "de": "(neben der ausgewählten Datei)", "fr": "(à côté du fichier sélectionné)",
    },

    # --- Translation confirmation -------------------------------------------
    "confirm.title": {
        "en": "The text will be sent to OpenAI", "it": "Il testo verrà inviato a OpenAI",
        "de": "Der Text wird an OpenAI gesendet", "fr": "Le texte sera envoyé à OpenAI",
    },
    "confirm.body": {
        "en": "You will send <b>{sentences}</b> ({chars} characters) to the <b>{model}</b> "
              "model with your API key. The audio stays on this computer.<br><br>The cost "
              "depends on the model and is charged to your OpenAI account.",
        "it": "Invierai <b>{sentences}</b> ({chars} caratteri) al modello <b>{model}</b> "
              "con la tua chiave API. L’audio resta su questo computer.<br><br>Il costo "
              "dipende dal modello scelto e viene addebitato sul tuo account OpenAI.",
        "de": "Sie senden <b>{sentences}</b> ({chars} Zeichen) mit Ihrem API-Schlüssel an "
              "das Modell <b>{model}</b>. Das Audio bleibt auf diesem Computer.<br><br>Die "
              "Kosten hängen vom Modell ab und werden Ihrem OpenAI-Konto belastet.",
        "fr": "Vous allez envoyer <b>{sentences}</b> ({chars} caractères) au modèle "
              "<b>{model}</b> avec votre clé API. L’audio reste sur cet ordinateur.<br><br>"
              "Le coût dépend du modèle et est facturé sur votre compte OpenAI.",
    },
    "confirm.dont_ask": {
        "en": "Don’t ask again (you can change this in Settings)",
        "it": "Non chiedere più (modificabile in Impostazioni)",
        "de": "Nicht mehr fragen (in den Einstellungen änderbar)",
        "fr": "Ne plus demander (modifiable dans les Réglages)",
    },
    "confirm.send": {
        "en": "Translate", "it": "Traduci", "de": "Übersetzen", "fr": "Traduire",
    },

    # --- About -------------------------------------------------------------
    "about.made_by": {
        "en": "Made by {author}", "it": "Realizzato da {author}", "de": "Erstellt von {author}",
        "fr": "Conçu par {author}",
    },
    "about.privacy_title": {
        "en": "The audio stays on this computer.", "it": "L’audio resta su questo computer.",
        "de": "Das Audio bleibt auf diesem Computer.", "fr": "L’audio reste sur cet ordinateur.",
    },
    "about.privacy_body": {
        "en": "Transcription runs locally and no usage data is collected. Only when you press "
              "<i>{translate}</i> is the text (never the audio) sent to the OpenAI API with "
              "your key.",
        "it": "La trascrizione gira in locale e non vengono raccolti dati di utilizzo. Solo "
              "quando premi <i>{translate}</i> il testo (mai l’audio) viene inviato all’API "
              "OpenAI con la tua chiave.",
        "de": "Die Transkription läuft lokal, Nutzungsdaten werden nicht erhoben. Nur wenn "
              "Sie <i>{translate}</i> drücken, wird der Text (nie das Audio) mit Ihrem "
              "Schlüssel an die OpenAI-API gesendet.",
        "fr": "La transcription s’exécute en local et aucune donnée d’utilisation n’est "
              "collectée. Le texte (jamais l’audio) n’est envoyé à l’API OpenAI avec votre "
              "clé que lorsque vous appuyez sur <i>{translate}</i>.",
    },
    "about.privacy_link": {
        "en": "Privacy details", "it": "Dettagli sulla privacy", "de": "Details zum Datenschutz",
        "fr": "Détails sur la confidentialité",
    },
    "about.accuracy_title": {
        "en": "Always check the text.", "it": "Verifica sempre il testo.",
        "de": "Prüfen Sie den Text immer.", "fr": "Vérifiez toujours le texte.",
    },
    "about.accuracy_body": {
        "en": "Transcripts and translations are generated by AI models and can contain "
              "errors, especially in names and numbers. The app is provided as is, with no "
              "warranty and no obligation of support; consent to record is your "
              "responsibility.",
        "it": "Trascrizioni e traduzioni sono generate da modelli di IA e possono contenere "
              "errori, soprattutto su nomi e cifre. L’app è fornita così com’è, senza "
              "garanzia né obbligo di assistenza; il consenso alla registrazione è tua "
              "responsabilità.",
        "de": "Transkripte und Übersetzungen werden von KI-Modellen erzeugt und können "
              "Fehler enthalten, besonders bei Namen und Zahlen. Die App wird ohne Gewähr "
              "und ohne Supportpflicht bereitgestellt; die Einwilligung zur Aufnahme liegt "
              "in Ihrer Verantwortung.",
        "fr": "Les transcriptions et traductions sont générées par des modèles d’IA et "
              "peuvent contenir des erreurs, notamment sur les noms et les chiffres. "
              "L’application est fournie en l’état, sans garantie ni obligation "
              "d’assistance ; le consentement à l’enregistrement relève de votre "
              "responsabilité.",
    },
    "about.terms_link": {
        "en": "Terms of use", "it": "Termini di utilizzo", "de": "Nutzungsbedingungen",
        "fr": "Conditions d’utilisation",
    },
    "about.license_title": {
        "en": "License.", "it": "Licenza.", "de": "Lizenz.", "fr": "Licence.",
    },
    "about.license_body": {
        "en": "Free for personal and professional use, including paid work. {license}: "
              "source-available, not open source; selling a product or service based "
              "substantially on this app is not permitted.",
        "it": "Uso personale e professionale gratuito, anche per lavoro retribuito. "
              "{license}: source-available, non open source; non è consentito vendere un "
              "prodotto o servizio basato sostanzialmente su questa app.",
        "de": "Kostenlos für private und berufliche Nutzung, auch für bezahlte Arbeit. "
              "{license}: Source-available, nicht Open Source; der Verkauf eines Produkts "
              "oder Dienstes, der im Wesentlichen auf dieser App beruht, ist nicht erlaubt.",
        "fr": "Gratuit pour un usage personnel et professionnel, y compris rémunéré. "
              "{license} : source-available, pas open source ; il n’est pas permis de vendre "
              "un produit ou un service reposant substantiellement sur cette application.",
    },
    "about.license_link": {
        "en": "Full license", "it": "Licenza completa", "de": "Vollständige Lizenz",
        "fr": "Licence complète",
    },
    "about.third_party_link": {
        "en": "third-party components", "it": "componenti di terze parti",
        "de": "Komponenten von Drittanbietern", "fr": "composants tiers",
    },
    "about.third_party_list": {
        "en": "(Qt, Whisper and others)", "it": "(Qt, Whisper e altri)",
        "de": "(Qt, Whisper und weitere)", "fr": "(Qt, Whisper et autres)",
    },
    "about.permissions": {
        "en": "separate permissions at", "it": "permessi separati su",
        "de": "gesonderte Genehmigungen über", "fr": "autorisations distinctes sur",
    },
}


def set_language(code: str) -> str:
    """Switch the interface language; unknown codes fall back to English."""
    global _current
    _current = code if code in LANGUAGES else DEFAULT_LANGUAGE
    return _current


def current_language() -> str:
    return _current


def tr(key: str, **params: object) -> str:
    """Translate ``key`` into the current language, falling back to English, then the key."""
    entry = STRINGS.get(key)
    if entry is None:
        return key
    text = entry.get(_current) or entry.get(DEFAULT_LANGUAGE) or key
    return text.format(**params) if params else text


def tr_n(key: str, n: int, **params: object) -> str:
    """Plural form: ``<key>.one`` for 1, ``<key>.other`` otherwise."""
    return tr(f"{key}.{'one' if n == 1 else 'other'}", n=n, **params)


def format_int(value: int) -> str:
    """Thousands separator as each language writes it: 18,342 / 18.342 / 18 342."""
    text = f"{value:,}"
    separator = {"en": ",", "it": ".", "de": ".", "fr": "\u202f"}.get(_current, ",")
    return text.replace(",", separator)


def detect_language(preferred: Iterable[str]) -> str:
    """First supported language among the system's preferred ones ("it-IT", "de_CH"…)."""
    for name in preferred:
        code = str(name).replace("_", "-").split("-")[0].lower()
        if code in LANGUAGES:
            return code
    return DEFAULT_LANGUAGE


def resolve_language(setting: str, system_preferred: Iterable[str]) -> str:
    """The language to use for a ``ui_language`` setting ("system" or a code)."""
    if setting in LANGUAGES:
        return setting
    return detect_language(system_preferred)
