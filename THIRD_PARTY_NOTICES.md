# Third-party notices

AudioTranscriptor bundles and links third-party software. Each component stays
under its own license; this project's Apache License 2.0 + Commons Clause
License Condition v1.0 does not replace them or apply the Commons Clause to
those separately licensed components. The application as a whole is described
as source-available, not open source. Project credits: Antonio Aversa / aversa.design.
This file lists every component that ships inside the installers, with the
license it is distributed under.

## Runtime components

Versions are the ones resolved by `requirements.txt` at build time. The exact
version of every package that ships in a given installer is listed in its
`_internal\*.dist-info` folder (or `Contents/Frameworks/*.dist-info` on macOS).

| Component | License | Copyright |
| --- | --- | --- |
| Qt for Python (PySide6, PySide6-Essentials, PySide6-Addons, shiboken6) | LGPL-3.0-only (also offered under GPL-2.0 / GPL-3.0) | The Qt Company Ltd. and contributors |
| faster-whisper | MIT | SYSTRAN and contributors |
| CTranslate2 | MIT | OpenNMT / SYSTRAN |
| ONNX Runtime | MIT | Microsoft Corporation |
| OpenAI Python SDK | Apache-2.0 | OpenAI |
| python-docx | MIT | Steve Canny and contributors |
| platformdirs | MIT | Platformdirs contributors |
| NumPy | BSD-3-Clause | NumPy Developers |
| tokenizers | Apache-2.0 | Hugging Face |
| huggingface-hub | Apache-2.0 | Hugging Face |
| hf-xet | Apache-2.0 | Hugging Face |
| PyAV (av) | BSD-3-Clause | PyAV contributors |
| protobuf | BSD-3-Clause | Google Inc. |
| flatbuffers | Apache-2.0 | Google Inc. |
| SymPy | BSD-3-Clause | SymPy Development Team |
| mpmath | BSD-3-Clause | Fredrik Johansson and contributors |
| coloredlogs | MIT | xolox |
| humanfriendly | MIT | xolox |
| tqdm | MPL-2.0 AND MIT | tqdm developers |
| anyio | MIT | Alex Grönholm |
| httpx | BSD-3-Clause | Tom Christie |
| h11 | MIT | Nathaniel J. Smith |
| httpcore | BSD-3-Clause | Tom Christie |
| pydantic / pydantic-core | MIT | Samuel Colvin and contributors |
| typing-extensions | PSF-2.0 | Python Software Foundation |
| typing-inspection | MIT | Pydantic Services Inc. |
| annotated-types / annotated-doc | MIT | Adrian Garcia Badaracco, Pydantic |
| filelock | Unlicense | Thomas Kemmer |
| fsspec | BSD-3-Clause | fsspec developers |
| PyYAML | MIT | Kirill Simonov and contributors |
| packaging | Apache-2.0 OR BSD-2-Clause | PyPA |
| idna | BSD-3-Clause | Kim Davies |
| sniffio | MIT OR Apache-2.0 | Nathaniel J. Smith |
| distro | Apache-2.0 | Nir Cohen |
| jiter | MIT | David Montague |
| certifi | MPL-2.0 | Kenneth Reitz and contributors |
| lxml | BSD-3-Clause | lxml contributors |
| rich / markdown-it-py / mdurl | MIT | Will McGugan and contributors |
| Pygments | BSD-2-Clause | Georg Brandl and contributors |
| click | BSD-3-Clause | Pallets |
| typer | MIT | Sebastián Ramírez |
| shellingham | ISC | Tzu-ping Chung |
| exceptiongroup | MIT | Alex Grönholm |
| importlib-metadata | Apache-2.0 | Jason R. Coombs |
| setuptools | MIT | Python Packaging Authority |

The Whisper model weights are downloaded at run time from Hugging Face under the
terms of the model repository you select; they are not distributed with this
application.

The Silero VAD model (`silero_vad_v6.onnx`), shipped inside `faster_whisper`, is
distributed under the MIT License by the Silero team.

## Qt and the LGPL

Qt is used unmodified, under LGPL-3.0. In the packaged application the Qt
libraries are separate dynamic libraries inside the application folder
(`_internal/PySide6` and `_internal/shiboken6` on Windows,
`Contents/Frameworks` on macOS), not statically linked. That keeps the LGPL
requirement that a user can replace them:

1. Download the matching Qt 6 / PySide6 minor release from
   <https://download.qt.io/official_releases/QtForPython/> or build Qt from
   <https://code.qt.io/>.
2. Replace the corresponding `.dll` / `.dylib` files in the application folder.
3. Keep the folder layout unchanged and start the app again.

Qt and PySide6 source code: <https://code.qt.io/cgit/pyside/pyside-setup.git/>

The full texts of the GNU Lesser General Public License v3 and the GNU General
Public License v3 are in [`licenses/`](licenses).

If you redistribute a modified build of this application, comply with the
combined application license and keep `LICENSE`, `LICENSE-SUPPLEMENT.md`,
`NOTICE`, this file and the `licenses/` folder next to the executable. The
supplement is an explanatory guide, not terms overriding those licenses.
Keep the Commons Clause notice with the application's required license notices;
this does not relicense the third-party components. This list and the Qt
replacement instructions are not a certification of legal compliance.

## Attribution

The MIT and BSD licenses require the copyright notices above to travel with the
software. Keep this file in every copy you distribute. See also
[NOTICE](NOTICE).
