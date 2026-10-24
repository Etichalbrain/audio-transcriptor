# Changelog

All notable changes to AudioTranscriptor. Versions follow the app version in
`audio_transcriptor/__init__.py`.

## Unreleased

### Listen while correcting

- A player above the transcript: play/pause, 5 seconds back and forward, a
  position slider and "Play from cursor", which starts at the sentence under
  the text cursor. The sentence being spoken is highlighted in the Italian and
  English text and scrolled into view while playing.
- Keyboard first: Esc plays/pauses, Ctrl+J (Cmd+J on macOS) plays from the
  cursor line, Ctrl+[ and Ctrl+] move 5 seconds.
- Edits are respected: after merging, adding or deleting lines the timing
  follows the same rule as the subtitle export, so playback and SRT agree.
- Without an audio output device the app says so; transcription and export
  are unaffected. Qt Multimedia is loaded only on the first play.

### Interface languages

- The interface is available in **English, Italian, German and French**. On
  first launch it follows the system language (English when the system uses
  another language); Settings → General → Interface language changes it
  immediately, without restarting and without losing the open transcript.
- All interface text lives in one catalog, `audio_transcriptor/i18n.py`, with
  plural forms and per-language number formatting. The services report
  progress as catalog keys, so no user-facing text is hard-coded outside it.
- Only the interface changes: the audio language (Italian or automatic) and
  the translation target (English) are unaffected. Legal documents remain in
  English.

### Interface

- Progress shows measured values: minutes of audio processed during
  transcription, sentences translated during translation.
- The progress bar appears only while a job runs and no longer draws a
  low-contrast percentage; the finished state leaves the space to the text.
- The transcript counter counts sentences, consistent with the rest of the app.
- The file row no longer shows a stray separator when size is unavailable,
  and shows the media duration as soon as a file is selected.
- The remove-file button inside the model chip now renders its × and has a
  tooltip and accessible name.
- Before translating, a confirmation states how many sentences and characters
  go to OpenAI and with which model; it can be disabled from the dialog or in
  Settings. A missing API key is reported before anything is prepared.
- About dialog reordered: privacy first, then accuracy and warranty, license
  last and shorter. The footer carries the author credit and the local-audio
  promise instead of the license name.
- DOCX headings follow the content language: "Trascrizione" for Italian
  exports, "English translation" for English ones.

### Tests

- Catalog tests: every key in every language, matching placeholders, plural
  pairs, system-language detection and fallback.
- Offscreen UI tests for counters, progress visibility, file metadata, model
  chip, translation confirmation and live language switching.

## 1.0.1 — 2026-10-22

First release of **AudioTranscriptor** (rename of the previous working name).
Local faster-whisper transcription of Italian audio and video, optional OpenAI
translation to English, and TXT/SRT/DOCX export remain the core workflow;
transcription progress reporting has been corrected as described below.

### Interface

- New interface aligned with the design mockup: warm paper-grey background,
  white rounded cards, blue accent, state-driven layout (empty upload state,
  file selected with model chip, transcribing, editor, Italian/English side by
  side, exported). The app is fully in Italian.
- The new monogram logo is embedded in the header and used as the window icon.
- Export moved to a dedicated panel dialog (TXT/SRT/DOCX for Italian and
  English), settings split into Model/Translation sections, About redesigned
  with credits, privacy, license and AI-transparency notes.

### Behavior fixes

- Transcription progress is now time-based, so long files (e.g. one-hour
  recordings) advance smoothly instead of parking at 95%.
- Export ready states are gated on real segments (no more empty SRT files).
- Clearing the selected file fully resets the workspace; dropping a file while
  a job is running is ignored; error/success banners never overlap.

### Legal and distribution

- **License changed to Apache License 2.0 + Commons Clause License Condition
  v1.0**: source-available, not open source and not vanilla Apache-2.0.
  `LICENSE` contains the condition and full, unmodified Apache text;
  `LICENSE-SUPPLEMENT.md` is retained as an explanatory guide, not additional
  or prevailing terms. Credits: Antonio Aversa / aversa.design.
- Licensing documentation now distinguishes permitted personal/professional
  internal use (including paid work using the app, without an automatic royalty)
  from “Sell”: providing third parties, for a fee or other consideration, a
  product or service whose value derives entirely or substantially from the
  software's functionality. Hosting and related consulting/support fees are
  included under that same substantial-value test. Such offerings require
  separate permission; value-added commercial integrations may be permitted.
  Third-party licenses remain separate. AI-output and responsibility disclaimers
  are retained.
- Windows: intended per-user Inno Setup installer (no administrator rights) and
  portable zip via GitHub Actions from the release tag. This renamed version
  still needs a Windows build and smoke test. The artifacts are unsigned;
  SmartScreen may warn on first launch.
- macOS: ad-hoc signed `.app` and `AudioTranscriptor-<version>-arm64.dmg` for
  Apple silicon.
- `SHA256SUMS.txt` is published with every release.