"""Self-test for a packaged build.

Run the executable with ``--self-test`` to prove that the frozen bundle can
import every runtime dependency, find its data files and write its settings.
The same command works on Windows, macOS and from a source checkout, which is
what makes an installed build verifiable without opening the interface.
"""

from __future__ import annotations

import math
import struct
import sys
import tempfile
import wave
from pathlib import Path

from audio_transcriptor import __version__

# Small model used by the optional engine check: fast to download, enough to
# prove that CTranslate2 and ONNX Runtime really run inside the package.
ENGINE_PROBE_MODEL = "tiny"

CHECKS_IMPORTS = (
    "PySide6.QtWidgets",
    "av",
    "faster_whisper",
    "ctranslate2",
    "openai",
    "docx",
    "platformdirs",
    "onnxruntime",
    "huggingface_hub",
)


def _bundle_root() -> Path | None:
    """PyInstaller extraction folder, when running from a frozen build."""
    candidate = getattr(sys, "_MEIPASS", None)
    return Path(candidate) if candidate else None


def _bundle_contents() -> Path | None:
    """The .app bundle root on macOS, for a build launched from Contents/MacOS."""
    executable = Path(sys.executable).resolve()
    for parent in executable.parents:
        if parent.suffix == ".app":
            return parent
    return None


def _legal_roots() -> list[Path]:
    """Find shipped documents, never masking a missing bundle file with cwd."""
    if not getattr(sys, "frozen", False):
        return [Path(__file__).resolve().parents[1]]
    app_bundle = _bundle_contents()
    if app_bundle is not None:
        return [app_bundle / "Contents" / "Resources"]
    roots = [Path(sys.executable).resolve().parent]
    bundle = _bundle_root()
    if bundle is not None:
        roots.extend([bundle, bundle.parent])
    return roots


def legal_document_path(name: str) -> Path | None:
    """Resolve a bundled legal document, or its source-checkout counterpart."""
    allowed = {
        "LICENSE", "LICENSE-SUPPLEMENT.md", "NOTICE", "PRIVACY.md",
        "TERMS.md", "THIRD_PARTY_NOTICES.md",
    }
    if name not in allowed:
        return None
    names = ("LICENSE.txt", "LICENSE") if name == "LICENSE" else (name,)
    return next(
        (root / filename for root in _legal_roots() for filename in names
         if (root / filename).is_file()),
        None,
    )


def _report_path() -> Path:
    """Write the report outside the signed bundle: a new file there breaks the signature."""
    app_bundle = _bundle_contents()
    if app_bundle is not None:
        return app_bundle.parent / "self-test.txt"
    return Path(sys.executable).resolve().parent / "self-test.txt"


def _write_probe_wav(path: Path, seconds: float = 2.0, rate: int = 16000) -> None:
    """Write a small tone so the engine has a real file to decode."""
    frames = int(rate * seconds)
    samples = b"".join(
        struct.pack("<h", int(3000 * math.sin(2 * math.pi * 440 * index / rate)))
        for index in range(frames)
    )
    with wave.open(str(path), "wb") as handle:
        handle.setnchannels(1)
        handle.setsampwidth(2)
        handle.setframerate(rate)
        handle.writeframes(samples)


def run_engine_check(model_name: str = ENGINE_PROBE_MODEL) -> tuple[bool, str]:
    """Load Whisper and transcribe a generated file, to prove inference works.

    This downloads the tiny model (about 75 MB) the first time, so it is opt-in.
    """
    try:
        from faster_whisper import WhisperModel

        with tempfile.TemporaryDirectory() as folder:
            probe = Path(folder) / "probe.wav"
            _write_probe_wav(probe)
            model = WhisperModel(model_name, device="cpu", compute_type="int8")
            segments, info = model.transcribe(str(probe), vad_filter=True)
            count = sum(1 for _segment in segments)
        return True, f"model {model_name} ran, {count} segment(s), language {info.language}"
    except Exception as exc:
        return False, f"{type(exc).__name__}: {exc}"


def run_self_test(include_engine: bool = False) -> list[tuple[str, bool, str]]:
    """Return (check, passed, detail) for every verification."""
    results: list[tuple[str, bool, str]] = [
        ("version", bool(__version__), __version__),
        ("frozen", True, "packaged" if getattr(sys, "frozen", False) else "source checkout"),
    ]

    for module_name in CHECKS_IMPORTS:
        try:
            module = __import__(module_name, fromlist=["*"])
        except Exception as exc:  # a missing import is exactly what this test hunts
            results.append((f"import {module_name}", False, f"{type(exc).__name__}: {exc}"))
        else:
            version = getattr(module, "__version__", "") or ""
            results.append((f"import {module_name}", True, str(version)))

    try:
        import docx
        import faster_whisper

        vad = Path(faster_whisper.__file__).parent / "assets" / "silero_vad_v6.onnx"
        results.append(("silero VAD asset", vad.is_file(), str(vad)))
        template = Path(docx.__file__).parent / "templates" / "default.docx"
        results.append(("docx template", template.is_file(), str(template)))
    except Exception as exc:
        results.append(("data files", False, f"{type(exc).__name__}: {exc}"))

    try:
        from audio_transcriptor.settings import SettingsStore

        store = SettingsStore()
        store.config_dir.mkdir(parents=True, exist_ok=True)
        with tempfile.NamedTemporaryFile(dir=store.config_dir, prefix="self-test-", delete=True):
            pass
        results.append(("settings folder writable", True, str(store.config_dir)))
    except Exception as exc:
        results.append(("settings folder writable", False, f"{type(exc).__name__}: {exc}"))

    legal = legal_document_path("LICENSE")
    results.append(
        (
            "license shipped with the app",
            legal is not None,
            str(legal) if legal else "not found in the app resources",
        )
    )
    for name in ("NOTICE", "LICENSE-SUPPLEMENT.md", "PRIVACY.md", "TERMS.md", "THIRD_PARTY_NOTICES.md"):
        document = legal_document_path(name)
        results.append((f"legal document {name}", document is not None,
                        str(document) if document else "not found in the app resources"))

    if include_engine:
        passed, detail = run_engine_check()
        results.append((f"transcription engine ({ENGINE_PROBE_MODEL})", passed, detail))
    return results


def format_report(results: list[tuple[str, bool, str]]) -> str:
    lines = [f"AudioTranscriptor {__version__} self-test", ""]
    for name, passed, detail in results:
        lines.append(f"[{'OK  ' if passed else 'FAIL'}] {name}: {detail}")
    failures = sum(1 for _name, passed, _detail in results if not passed)
    lines.extend(["", f"{len(results) - failures} passed, {failures} failed"])
    return "\n".join(lines)


def run_self_test_cli(include_engine: bool = False) -> int:
    results = run_self_test(include_engine=include_engine)
    report = format_report(results)
    print(report)

    # With console=False on Windows stdout is hidden, so keep a file next to the
    # executable when the app is packaged.
    if getattr(sys, "frozen", False):
        try:
            target = _report_path()
            target.write_text(report + "\n", encoding="utf-8")
            print(f"Report written to {target}")
        except OSError as exc:
            print(f"Could not write self-test.txt: {exc}")

    return 0 if all(passed for _name, passed, _detail in results) else 1
