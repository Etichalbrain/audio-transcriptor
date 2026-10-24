# Installation and Build Instructions

Release status: the current macOS Apple silicon bundle has been built locally.
The renamed Windows release still needs its build and smoke test. Instructions
below describe the intended published artifacts, not a claim that all downloads
are already available.

## License before installing or distributing

AudioTranscriptor uses **Apache License 2.0 + Commons Clause License Condition
v1.0**: source-available, **not open source** and not vanilla Apache-2.0.
[LICENSE](LICENSE) contains the condition and the full, unmodified Apache text;
[LICENSE-SUPPLEMENT.md](LICENSE-SUPPLEMENT.md) is an explanatory guide, not
additional or prevailing terms. Credits: **Antonio Aversa / aversa.design**.

Personal and professional internal use, including paid work using the app, is
allowed subject to the license, without an automatic royalty. Separate permission
is needed to “Sell”: provide third parties, for a fee or other consideration, a
product or service whose value derives entirely or substantially from the
software's functionality. Fees for hosting and consulting/support related to
the software are included, subject to that same substantial-value test. This is
not a blanket ban on commercial integration; value-added integrations may be
permitted. Contact <https://aversa.design> for permission enquiries. Third-party
licenses remain separate; this summary is not legal advice or a certification
of compliance.

## Install the Windows app

Download `AudioTranscriptorSetup-1.0.1.exe` from the official download channel linked from <https://aversa.design> once published
and run it. It installs for the current user in `%LOCALAPPDATA%\Programs\AudioTranscriptor`,
needs no administrator rights, and adds Start menu and (optional) desktop shortcuts.

`AudioTranscriptor-Portable.zip` contains the same application as a folder: unzip it and run
`AudioTranscriptor\AudioTranscriptor.exe`. Keep the folder intact, the executable needs its
`_internal` directory. This is the option for a PC where you cannot install software; there are no
shortcuts and nothing to uninstall, you just delete the folder.

`SHA256SUMS.txt` lists the SHA-256 of both files. Check it before running the installer, for
example with `Get-FileHash AudioTranscriptorSetup-1.0.1.exe -Algorithm SHA256` in PowerShell.

The installer is not code-signed, so Windows SmartScreen shows "Windows protected your PC";
choose "More info" → "Run anyway".

The setup shows a short privacy note (`installer/LEGGIMI.txt`), then the license, which must
be accepted. The installed folder keeps `LICENSE.txt`, `LICENSE-SUPPLEMENT.md`,
`NOTICE`, `PRIVACY.md`, `TERMS.md`,
`THIRD_PARTY_NOTICES.md` and `licenses/` next to the executable, so the notices survive a copy.

## Install the macOS app

Download `AudioTranscriptor-1.0.1-arm64.dmg` from the official download channel linked from <https://aversa.design> once published,
open it and drag `AudioTranscriptor` into `Applications`. The app is signed ad-hoc, not
notarized: the first launch needs right click → Open. The bundle is arm64 only (Apple silicon).
The legal files are inside `Contents/Resources`.

## Verify the installation

Both platforms ship a self-test that needs no interface and no API key:

```powershell
"C:\Users\<you>\AppData\Local\Programs\AudioTranscriptor\AudioTranscriptor.exe" --self-test
```

```bash
"/Applications/AudioTranscriptor.app/Contents/MacOS/AudioTranscriptor" --self-test
```

It checks the version, every runtime import, the Silero VAD asset, the DOCX template, the
settings folder and the shipped license. Exit code 0 means everything is present; a `FAIL` line
names what is missing, and `self-test.txt` is written next to the executable.

Add `--self-test-engine` instead of `--self-test` to also download the tiny Whisper model (about
75 MB) and run a real transcription through CTranslate2 and ONNX Runtime. The Windows workflow is configured to run this against
the packaged app before creating the installer. This checks basic engine startup,
not every file type, long recording or user workflow; it is not a guarantee of a
bug-free release.

## Development Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m audio_transcriptor
```

Windows PowerShell:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python -m audio_transcriptor
```

## Run the tests

```bash
python -m unittest discover -s tests -t . -v
```

The suite needs no model download and no API key. It also checks that the legal files exist, that
every version string matches, and that each build ships the notices.

## Build macOS `.app`

```bash
./build_macos.sh
```

The script recreates a missing venv, installs the dependencies, builds with
`AudioTranscriptor.spec`, copies the Silero VAD asset and the legal files, ad-hoc signs the bundle
and creates `dist/AudioTranscriptor-1.0.1-arm64.dmg`. The bundle version comes from `audio_transcriptor/__init__.py`.

To regenerate the README screenshot (`docs/app.png`):

```bash
QT_QPA_PLATFORM=offscreen .venv/bin/python scripts/capture_screenshot.py
```

## Build Windows `.exe` and installer

Preferred, no Windows machine needed:

```bash
gh workflow run build-windows.yml
gh run download --name AudioTranscriptor-Windows
```

The workflow runs the test suite first, then builds `dist\AudioTranscriptor\` with
`AudioTranscriptorWindows.spec` (onedir), copies the legal files, checks that the Silero VAD asset
and the python-docx template are present, wraps the folder with Inno Setup 6, writes
`SHA256SUMS.txt` and, for a tag, publishes the release.

Pushing a tag such as `v1.0.1` publishes the release. The tag must match the app version or the
workflow fails.

On a Windows PC, run `build_windows_installer.bat` instead (Python 3.12 + Inno Setup 6). It writes
`installer\Output\AudioTranscriptorSetup-1.0.1.exe`.

## First Launch

The first transcription downloads the selected model (default `small`, about 0.5 GB) and shows a
download status; Cancel stops waiting for it. `medium` and `large-v3` give better quality at the
cost of download size, memory and CPU time.

Translation needs an OpenAI API key in Settings. The key is stored in the per-user settings file
described in [PRIVACY.md](PRIVACY.md).

## Distribution Notes

- Build separately on Windows and macOS.
- Code signing and notarization are not configured: sign the Windows installer and notarize the
  macOS app before broad distribution.
- Keep the version in `audio_transcriptor/__init__.py`, `installer/audio_transcriptor.iss`,
  `installer/windows_version_info.txt` and `pyproject.toml` aligned; the test suite fails otherwise.
- If you redistribute the app, comply with the combined license and keep `LICENSE`,
  `LICENSE-SUPPLEMENT.md`, `NOTICE`, `THIRD_PARTY_NOTICES.md` and `licenses/`,
  including the Commons Clause notice and required attribution.
  Qt/PySide6 is LGPL-3.0: do not statically link it, and keep the Qt libraries replaceable. See
  [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).
