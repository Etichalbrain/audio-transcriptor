# Security policy

No security guarantee is given. The application is not certified or audited, and
it is provided "as is" (see [TERMS.md](TERMS.md)): nothing here promises that it
is free of defects or vulnerabilities. This document describes how the app
handles data today and how to report a problem — it is not a warranty.

Reports are handled on a best-effort basis; there is no bug bounty and no
committed fix deadline.

## Reporting a vulnerability

Do not open a public issue for a security problem. Use the contact options on
<https://aversa.design> to request a private reporting channel before sending
sensitive details. GitHub private vulnerability reporting must be enabled on the
actual repository before it is advertised as an available channel.

Please include the version, the operating system and non-sensitive steps to
reproduce. Never post API keys, recordings, transcripts or personal information
in public issues. Reports are best-effort; no response time is guaranteed.

## Scope

The application runs locally and has no server component. Relevant reports
include, for example:

- a way to make the app send files or transcript content somewhere other than
  `api.openai.com`
- a way to leak the stored OpenAI API key
- a malicious media file that executes code while being decoded
- a build or installer that ships something other than this source tree

## What the app already does

- No telemetry, no analytics, no remote code loading, no auto-update.
- The settings file is written with owner-only permissions where supported.
- The API key is only sent to `api.openai.com`.
- The Windows installer needs no administrator rights and installs per user.
- The Windows GitHub Actions workflow runs tests before packaging and can
  publish a release from a version tag. macOS builds are currently made locally.

## Known limitations that are not vulnerabilities

- The Windows installer is unsigned. The macOS bundle is signed ad-hoc, not
  Developer ID-signed or notarized; operating systems may warn on first launch.
  Verify the SHA-256 obtained from the trusted release channel.
- The API key is stored in plain text in the settings file, as documented in
  [PRIVACY.md](PRIVACY.md).
