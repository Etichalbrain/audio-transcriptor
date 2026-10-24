# AudioTranscriptor User Guide

## Basic Workflow

1. Open AudioTranscriptor.
2. Click `Scegli file` or drag a media file into the upload area.
3. Click `Trascrivi in italiano`.
4. Review and edit the Italian transcript.
5. Click `Traduci in inglese`. A confirmation shows how many sentences and characters will be
   sent to OpenAI; tick `Non chiedere più` to skip it next time (re-enable it in Settings).
6. Review and edit the English translation.
7. Export the files you need.

## Supported Files

- MP3
- WAV
- M4A
- MP4
- MOV
- MKV

## Settings

Open `Impostazioni` to configure:

- Whisper model: `small` (default, about 0.5 GB), `medium` (about 1.5 GB), or `large-v3` (about 3 GB)
- Language: `Italian` or `Auto`
- Output folder
- OpenAI API key
- OpenAI model
- Light or dark mode

The model file is downloaded on first use. While it downloads the status line says so, and
`Annulla operazione` stops the wait.

Translation always uses the OpenAI API: a key is required in Settings. There is no offline
translation mode.

## Export Files

Available exports:

- Italian TXT
- English TXT
- Italian SRT subtitles
- English SRT subtitles
- Italian DOCX
- English DOCX

Default filenames use the uploaded file name:

```text
intervista_it.txt
intervista_en.txt
intervista_it.srt
intervista_en.srt
intervista_it.docx
intervista_en.docx
```

## Editing and Subtitles

The text you see is the text that gets exported. If you edit a transcript and keep one line per
subtitle, each line goes back to its own cue. If you add or remove lines, the export distributes
the lines over the cues according to their timing, keeping your order and wording instead of
silently using the old text. Merged lines become a single cue text.

## License, credits and privacy

The `Informazioni` button in the top right shows the version, the author, the license and a short
summary of what leaves the computer. The same information, in full, is in the application folder:
`LICENSE.txt`, `LICENSE-SUPPLEMENT.md`, `NOTICE`, `PRIVACY.md`, `TERMS.md`,
`THIRD_PARTY_NOTICES.md` and `LEGGIMI.txt`.

Credits: **Antonio Aversa / aversa.design**. The app uses **Apache License 2.0 +
Commons Clause License Condition v1.0**, not vanilla Apache-2.0: it is
**source-available, not open source**. The license file contains the condition
and full, unmodified Apache text; [LICENSE-SUPPLEMENT.md](LICENSE-SUPPLEMENT.md)
is an explanatory guide, not custom or prevailing terms.

Personal and professional internal use, including paid work using the app, is
allowed subject to the license, without an automatic royalty. Separate permission
is required to “Sell”: provide third parties, for a fee or other consideration,
a product or service whose value derives entirely or substantially from the
software's functionality. This includes fees for hosting and consulting/support
related to the software, subject to the same substantial-value test. It is not a
blanket ban on commercial integrations: value-added integrations may be permitted.
For permission enquiries use <https://aversa.design>. Third-party components keep
their own licenses. This is a summary, not legal advice or a legal certification.

In short: the audio never leaves the computer, the transcript is sent to OpenAI only when you
translate, no usage data is collected. Settings and the OpenAI key are stored in
`%LOCALAPPDATA%\AudioTranscriptor\settings.json` on Windows or
`~/Library/Application Support/AudioTranscriptor/settings.json` on macOS.

## Troubleshooting

If the app does not start, run it with `--self-test` from a terminal (see
[INSTALLATION.md](INSTALLATION.md#verify-the-installation)): it names the missing component and
writes `self-test.txt` next to the executable.

If transcription fails, check that the file is valid and that enough disk space is available.

If translation fails, check that the OpenAI API key is saved in Settings.

If the first transcription is slow, the Whisper model is still downloading; `small` downloads
fastest.

Support is not guaranteed: this is a free project, not a service. There is no obligation to
answer, fix a bug or ship an update, and the app is provided without warranty of security or
accuracy. See [TERMS.md](TERMS.md) for the full disclaimer.
