# -*- mode: python ; coding: utf-8 -*-

import re
import sys
from pathlib import Path

import faster_whisper
from PyInstaller.utils.hooks import collect_data_files

block_cipher = None
silero_vad_asset = str(Path(faster_whisper.__file__).parent / "assets" / "silero_vad_v6.onnx")

# Keep the bundle version in sync with audio_transcriptor/__init__.py instead of
# letting macOS report 0.0.0.
match = re.search(
    r'__version__\s*=\s*"([^"]+)"',
    Path("audio_transcriptor/__init__.py").read_text(encoding="utf-8"),
)
app_version = match.group(1) if match else "0.0.0"

a = Analysis(
    ["audio_transcriptor/__main__.py"],
    pathex=[],
    binaries=[(silero_vad_asset, "faster_whisper/assets")],
    datas=collect_data_files("faster_whisper"),
    hiddenimports=[
        "faster_whisper",
        # Imported lazily by the player, so name it for the Qt multimedia hook.
        "PySide6.QtMultimedia",
        # `import ctranslate2` re-exports these subpackages, so PyInstaller's
        # static analysis misses them and the frozen app fails to transcribe.
        "ctranslate2",
        "ctranslate2.converters",
        "ctranslate2.models",
        "ctranslate2.specs",
        "openai",
        "docx",
        "platformdirs",
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

if sys.platform == "darwin":
    exe = EXE(
        pyz,
        a.scripts,
        [],
        exclude_binaries=True,
        name="AudioTranscriptor",
        debug=False,
        bootloader_ignore_signals=False,
        strip=False,
        upx=True,
        console=False,
    )

    coll = COLLECT(
        exe,
        a.binaries,
        a.zipfiles,
        a.datas,
        strip=False,
        upx=True,
        upx_exclude=[],
        name="AudioTranscriptor",
    )

    app = BUNDLE(
        coll,
        name="AudioTranscriptor.app",
        icon="assets/AudioTranscriptor.icns",
        bundle_identifier="com.aversadesign.audiotranscriptor",
        info_plist={
            "CFBundleShortVersionString": app_version,
            "CFBundleVersion": app_version,
            "NSHighResolutionCapable": True,
        },
    )
else:
    exe = EXE(
        pyz,
        a.scripts,
        a.binaries,
        a.zipfiles,
        a.datas,
        [],
        name="AudioTranscriptor",
        debug=False,
        bootloader_ignore_signals=False,
        strip=False,
        upx=True,
        upx_exclude=[],
        runtime_tmpdir=None,
        console=False,
    )
