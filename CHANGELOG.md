# Changelog

All notable changes to AudioTranscriptor. Versions follow the app version in
`audio_transcriptor/__init__.py`.

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