# -*- mode: python ; coding: utf-8 -*-
"""Windows build: onedir layout, bundled into an installer by installer/audio_transcriptor.iss.

Onedir instead of onefile: the app already ships Qt + CTranslate2 + ONNX Runtime
(~200 MB), so a onefile exe would unpack everything into %TEMP% on every launch.
"""

from pathlib import Path

import faster_whisper
from PyInstaller.utils.hooks import collect_data_files

silero_vad_asset = str(Path(faster_whisper.__file__).parent / "assets" / "silero_vad_v6.onnx")

a = Analysis(
    ["audio_transcriptor/__main__.py"],
    pathex=[],
    binaries=[(silero_vad_asset, "faster_whisper/assets")],
    datas=collect_data_files("faster_whisper"),
    hiddenimports=[
        "faster_whisper",
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
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="AudioTranscriptor",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,
    icon="assets/AudioTranscriptor.ico",
    version="installer/windows_version_info.txt",
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name="AudioTranscriptor",
)
