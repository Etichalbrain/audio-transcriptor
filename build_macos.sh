#!/usr/bin/env sh
set -eu

cd "$(dirname "$0")"

# Recreate the venv if it is missing or was moved from another folder
# (a moved venv keeps stale absolute paths in its scripts).
if [ ! -x .venv/bin/python ]; then
  python3 -m venv .venv
fi

# Call the venv interpreter by path instead of activating it: on macOS there is
# no plain `python` on PATH, and a moved venv keeps stale paths in its scripts.
PYTHON=.venv/bin/python
"$PYTHON" -m pip install --upgrade pip setuptools wheel
"$PYTHON" -m pip install -r requirements.txt
"$PYTHON" -m pip install pyinstaller
# `python -m PyInstaller` instead of the `pyinstaller` script: it keeps working
# even when the venv console scripts still point at an old absolute path.
PYINSTALLER_CONFIG_DIR=.pyinstaller-cache "$PYTHON" -m PyInstaller --noconfirm AudioTranscriptor.spec

# Copy the Silero VAD asset next to the bundled package. The path is resolved at
# runtime so the script no longer depends on the venv's Python version.
"$PYTHON" - <<'PY'
import shutil
import sys
from pathlib import Path

import faster_whisper

app = Path("dist/AudioTranscriptor.app")
if not app.exists():
    sys.exit(0)

source = Path(faster_whisper.__file__).parent / "assets" / "silero_vad_v6.onnx"
for target_dir in (
    app / "Contents/Frameworks/faster_whisper/assets",
    app / "Contents/Resources/faster_whisper/assets",
):
    target_dir.mkdir(parents=True, exist_ok=True)
    if not (target_dir / source.name).exists():
        shutil.copy2(source, target_dir / source.name)
PY

# Ship the legal files inside the bundle so the notice travels with the app.
if [ -d "dist/AudioTranscriptor.app" ]; then
  resources="dist/AudioTranscriptor.app/Contents/Resources"
  mkdir -p "$resources/licenses"
  cp LICENSE "$resources/LICENSE.txt"
  cp NOTICE LICENSE-SUPPLEMENT.md PRIVACY.md TERMS.md THIRD_PARTY_NOTICES.md "$resources/"
  cp licenses/*.txt "$resources/licenses/"
fi

# Name the DMG with the app version so a download is self-explanatory.
VERSION=$("$PYTHON" -c "from audio_transcriptor import __version__; print(__version__)")
DMG="dist/AudioTranscriptor-$VERSION-arm64.dmg"
rm -f "dist/AudioTranscriptor.dmg" "$DMG"

codesign --force --deep --sign - "dist/AudioTranscriptor.app"

# Build the image from a staging folder. `hdiutil create -srcfolder` is the
# usual path, but on some macOS and sandboxed environments it fails with the
# misleading "Directory not empty" even on a trivial folder; `makehybrid`
# handles the same input, so fall back to it and compress to UDZO afterwards.
# Any image left over from a previous run must be removed: both commands refuse
# to overwrite and report the same confusing error.
STAGE=".dmgstage-audio-transcriptor"
rm -rf "$STAGE"
rm -f "$DMG"
mkdir -p "$STAGE"
ditto --norsrc --noextattr --noacl "dist/AudioTranscriptor.app" "$STAGE/AudioTranscriptor.app"
xattr -cr "$STAGE/AudioTranscriptor.app"
if ! hdiutil create -srcfolder "$STAGE" -fs APFS -format UDZO -volname "AudioTranscriptor" "$DMG"; then
  echo "hdiutil create failed; retrying with makehybrid"
  rm -f "$DMG"
  RAW="$(mktemp -t audio_transcriptor_dmg).dmg"
  # Point at the staging folder, not the .app itself: makehybrid copies the
  # contents of the path it is given, so the bundle must stay one level down.
  hdiutil makehybrid -o "$RAW" -hfs -hfs-volume-name "AudioTranscriptor" "$STAGE"
  hdiutil convert "$RAW" -format UDZO -o "$DMG.tmp" >/dev/null
  mv -f "$DMG.tmp.dmg" "$DMG"
  rm -f "$RAW"
fi
rm -rf "$STAGE"

# Ship the checksum the docs tell people to verify against, so it can never
# describe a DMG other than the one in this folder.
(cd dist && shasum -a 256 "$(basename "$DMG")" > SHA256SUMS.txt)

echo "Build complete. Check: dist/AudioTranscriptor.app and $DMG"
