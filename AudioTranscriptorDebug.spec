# -*- mode: python ; coding: utf-8 -*-

from PyInstaller.utils.hooks import collect_data_files
from pathlib import Path

import faster_whisper

silero_vad_asset = str(Path(faster_whisper.__file__).parent / "assets" / "silero_vad_v6.onnx")

a = Analysis(
    ["audio_transcriptor/__main__.py"],
    pathex=[],
    binaries=[(silero_vad_asset, "faster_whisper/assets")],
    datas=collect_data_files("faster_whisper"),
    hiddenimports=[
        "faster_whisper",
        # Imported lazily by the player, so name it for the Qt multimedia hook.
        "PySide6.QtMultimedia",
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
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name="AudioTranscriptor Debug",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    icon="assets/AudioTranscriptor.ico",
)
