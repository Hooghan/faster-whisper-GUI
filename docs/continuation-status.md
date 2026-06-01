# Continuation Status

Last updated: 2026-06-01

## Verified Baseline

The current continuation baseline verifies ordinary faster-whisper transcription
from source on Windows. The source-run dependency entrypoint is
`requirements-dev-faster-whisper.txt`.

The continuation build displays app version `0.8.6-dev` in the title bar. This
marks the source continuation work as newer than the original `0.8.5` release
without claiming a packaged stable release yet.

Startup model autoload is enabled by default. The GUI waits until startup is
settled, then loads the saved model only when the saved model target is
non-empty, so a fresh empty local-model path does not show a startup error.
The autoload switch is kept independent from the automatic config-save switch,
so disabling automatic config saving does not silently clear the startup
autoload preference.

Key verified dependency ranges:

- `faster-whisper==1.2.1`
- `PySide6>=6.10,<6.11`
- `PySide6-Fluent-Widgets>=1.11,<1.12`
- `ctranslate2>=4.7.2,<4.8`
- `onnxruntime>=1.26,<1.27`
- `numpy>=2,<3`

The GUI model selector has been refreshed against the installed
`faster-whisper==1.2.1` short-name list. It intentionally omits duplicate
aliases such as `large` and `turbo`, because they map to the explicit
`large-v3` and `large-v3-turbo` entries already shown in the GUI. The newer
`distil-large-v3.5` entry is listed before `distil-large-v3`, while existing
saved `modelName` indices before that point continue to resolve to the same
model. In particular, `large-v3-turbo` at index `11` is unchanged.

Core dependency update check:

- `onnxruntime 1.26.0` is the newest installable line seen by pip in this
  environment.
- `huggingface-hub 1.16.1` is the newest installable line seen by pip in this
  environment.
- `tokenizers 0.23.1` is the newest standalone installable line seen by pip in
  this environment, but the shared source-run range is `tokenizers>=0.22,<0.24`
  so the WhisperX add-on can coexist with `transformers==5.9.0`.
- The optional CUDA 12.4 add-on uses `torch==2.6.0`, which is the forward
  PyTorch baseline documented for CUDA 12.4 wheels.

## WhisperX Add-on

`requirements-dev-whisperx.txt` is the experimental add-on for WhisperX
alignment and speaker diarization dependency work.

The GUI title bar reports WhisperX as `vendored` because the app uses the
repository's local `whisperx/` package instead of a pip-installed `whisperx`
distribution. The verified diarization backend package in this baseline is
`pyannote.audio==3.1.1`.

Current import-tested package pins:

- `torchaudio==2.6.0`
- `transformers==5.9.0`
- `pyannote.audio==3.1.1`
- `nltk==3.9.4`
- `pandas>=3.0,<3.1`
- `matplotlib>=3.10,<3.11`

Vendored WhisperX import is verified with the add-on installed. The local
package includes small NumPy 2 compatibility shims for pyannote's legacy
`np.NaN` and `np.NAN` usage.

WhisperX alignment runs in a subprocess and defaults to CUDA when CUDA is
available. This avoids a native crash observed when CTranslate2's CUDA/cuDNN
DLLs and PyTorch CUDA alignment models are loaded in the same Python process.
The alignment path has been manually smoke-tested from the GUI.

WhisperX speaker diarization runs in a subprocess and defaults to CUDA through
the same `FASTER_WHISPER_GUI_WHISPERX_DEVICE` switch. Set
`FASTER_WHISPER_GUI_WHISPERX_DEVICE=cpu` before launch to force WhisperX
subprocess work back to CPU. The speaker diarization path has unit coverage and
was GUI smoke-tested on 2026-05-26 with `SPEAKER_00` / `SPEAKER_01` labels
filled in the table.

The WhisperX speaker diarization runner now logs summary counts such as
`speaker diarization produced ... speaker turns across ... speakers` and
`assigned speakers to .../... transcript segments`. Use those lines to
distinguish model output issues from GUI table refresh issues during future
testing.

On 2026-05-27, a vendored WhisperX compatibility bug was fixed: the upstream
backend compatibility layer must not pass `model_name=None` into the vendored
`DiarizationPipeline`, because that overrides the vendored default
`pyannote/speaker-diarization@2.1` model. The fix was verified against the
sample file
`D:\20260408台北菩提禪堂禪修健身班推廣-失眠改善篇\台北菩提禪堂禪修健身班推廣-失眠改善篇 2026.04.08 V1_CLEAN.mp4`;
speaker diarization assigned speakers to `12/12` transcript segments.

`requirements-dev-whisperx-next.txt` is reserved for a future upstream
WhisperX upgrade experiment. It currently points at `whisperx==3.8.6`, but it
must be tested in an isolated environment before replacing the verified
vendored WhisperX GUI path.

The GUI has a reversible backend toggle for the gradual replacement work. By
default, `FASTER_WHISPER_GUI_WHISPERX_BACKEND` is unset and WhisperX
subprocesses use the verified vendored backend. Set
`FASTER_WHISPER_GUI_WHISPERX_BACKEND=upstream` before launch to route WhisperX
alignment and speaker diarization subprocesses through the isolated
`.venv-whisperx-next` Python environment. The upstream runner removes the repo
root from `sys.path` and refuses to import the vendored `whisperx/` package by
mistake.

The WhisperX parameter panel now also exposes this as a `WhisperX 后端` selector
with `vendored` and `upstream` options. The saved default remains `vendored`,
and selecting `upstream` routes only WhisperX subprocesses through the isolated
`.venv-whisperx-next` Python environment without changing the main GUI Python
runtime.

WhisperX worker and subprocess logs now print `WhisperX backend: vendored` or
`WhisperX backend: upstream` so manual tests can confirm which backend actually
ran.

The upstream backend runner path was smoke-tested on 2026-05-26 outside the GUI:
alignment completed through `faster_whisper_GUI.whisperx_alignment_runner`, and
speaker diarization completed through
`faster_whisper_GUI.whisperx_diarization_runner` with `SPEAKER_00` assigned to
the sample transcript segment. The GUI default remains vendored until manual GUI
testing confirms the upstream backend on real files.

On 2026-05-27, the upstream backend speaker diarization runner was also
verified against the insomnia sample MP4 with `min=max=2` speakers and
`refine_short_responses=true`. The upstream route assigned speakers to `12/12`
transcript segments and refined `3` short response speaker assignments,
including the repeated `真的假的` lines.

The upstream backend alignment runner was verified against the same insomnia
sample MP4 on 2026-05-27. It loaded audio, loaded the alignment model, and
returned aligned timestamps for all `12/12` transcript segments.

Speaker diarization accuracy is model- and audio-dependent. The runner now logs
the selected diarization model, speaker count limits, and whether nearest
speaker filling is enabled. For comparison testing, set
`FASTER_WHISPER_GUI_WHISPERX_DIARIZATION_MODEL` before launch to try a specific
pyannote model, and set `FASTER_WHISPER_GUI_WHISPERX_ASSIGN_FILL_NEAREST=1` to
let WhisperX fill transcript segments/words with the nearest diarization turn
when there is no direct overlap. Leave both variables unset for the verified
default behavior.

The GUI also exposes a `短回应修正` switch in the WhisperX parameter panel. It is
enabled by default and corrects short two-person interjections such as
`真的假的` when they are surrounded by the other speaker's turns. The runner logs
`refined ... short response speaker assignments` when this post-processing
changes any speaker labels.

The repository test configuration filters known third-party warning noise from
vendored WhisperX dependencies, including SWIG, torchaudio backend, SpeechBrain
compatibility, and `AudioMetaData` deprecation messages. This keeps future test
runs focused on new warnings from the continuation code.

Use `tools/whisperx_next_smoke.py` from a separate virtual environment to test
the upstream route. The script removes the repository root from `sys.path` and
refuses to run if it imports the local vendored `whisperx/` package by mistake.
On this machine, the upstream import check reached
`.venv-whisperx-next/Lib/site-packages/whisperx`. The experiment uses
`imageio-ffmpeg` to provide FFmpeg inside the isolated environment without
changing the Windows system PATH. It also redirects Hugging Face, Transformers,
NLTK, and pyannote caches to `cache/whisperx-next` to avoid the user-global
cache permission issues seen during the first alignment smoke attempts.

WhisperX 3.8.6 upstream smoke status on 2026-05-26:

- Import smoke passed from `.venv-whisperx-next/Lib/site-packages/whisperx`.
- Audio loading smoke passed with the `imageio-ffmpeg` shim.
- Alignment smoke passed on CPU for the sample audio.
- After accepting access for the upstream default
  `pyannote/speaker-diarization-community-1`, diarization smoke passed on CPU
  and assigned speakers to `1/1` transcript segments.
- The diarization smoke path preloads audio with WhisperX before calling
  pyannote, which avoids the non-fatal torchcodec DLL warning seen while
  pyannote initializes.
- The upstream requirements include `hf_xet` to avoid Hugging Face Xet fallback
  warnings, and the GUI/subprocess backend filters the known non-fatal
  torchcodec DLL warning because audio is preloaded before pyannote runs.
  Direct command-line experiments may still print non-fatal warnings about
  `TRANSFORMERS_CACHE` deprecation or short-audio statistics. These did not
  block the successful smoke result.
- The older `pyannote/speaker-diarization` route remains lower priority under
  pyannote 4.0.4 because legacy `@revision` model references need explicit
  `revision=` handling.

## Demucs Audio Separation

`requirements-dev-demucs.txt` is the experimental add-on for Demucs audio
separation dependency work.

Current import-tested package pins:

- `torchaudio==2.6.0`
- `soundfile>=0.13,<0.14`

Demucs audio separation runs in a subprocess and defaults to CUDA when CUDA is
available. This keeps PyTorch CUDA model loading outside the main GUI process,
which avoids the same native CUDA DLL conflict class observed with WhisperX.
Demucs output folder creation now supports nested custom output directories.

The Demucs model is cached at `cache/hdemucs_high_trained.pt` using the official
torchaudio asset key `models/hdemucs_high_trained.pt`. The GUI smoke test on
2026-05-25 produced the expected vocals/background two-track WAV outputs from
the Demucs page.

Local user settings are written under `user/*.local.json` and are ignored by
Git. The tracked default config files should not contain machine-specific model
paths, cache paths, or Hugging Face access tokens.

Temporary subtitle cleanup now uses the internal `clear_temp_srt_files()` helper
instead of shelling out to `del`, and only removes `.srt` files from the temp
directory.
Transcription and audio-capture temp directory creation now use the shared
`ensure_directory()` helper instead of direct `os.mkdir` calls.

Settings-page shortcuts now create the temp directory or log files before
opening them, so first-run installs do not fail when those paths do not exist
yet.

Translator startup config loading now uses a small `load_language_config()`
helper with explicit fallback to automatic language selection when the config is
missing or invalid.

Speaker audio splitting now writes `00_list.csv` with a context manager and
uses idempotent output directory creation.

## Windows Packaging

`requirements-dev-package.txt` pins `pyinstaller==6.20.0` for the
Windows executable packaging source build path. `package-windows-source.cmd`
runs the repository test suite, then invokes the PyInstaller spec at
`build_tools/FasterWhisperGUI.spec`.

The packaging spec builds a Windows onedir package named
`FasterWhisperGUI-0.8.6-dev-source`. It includes the tracked default configs,
resource modules, the main GUI package, faster-whisper package data such as the
Silero VAD ONNX asset, and the vendored WhisperX package, but does not include
`user/*.local.json`, Hugging Face tokens, user cache directories, or virtual
environments.

On 2026-06-01, the package build completed and created
`dist/FasterWhisperGUI-0.8.6-dev-source/FasterWhisperGUI.exe`. A basic startup
smoke pass launched the packaged executable, confirmed the process stayed alive,
and confirmed `fasterwhispergui.log` was created with the expected
`0.8.6-dev` startup line.

After manual packaged startup exposed a `FileNotFoundError` for
`fasterWhisperGUIConfig.json`, packaged config path handling was fixed. In a
PyInstaller build, the tracked default config is read from PyInstaller's
`_internal` directory, while private user config files are still created next
to the executable under `user/`.

`package-windows-source.cmd` now seeds the packaged `user/` config from the
current source-run local config after each build. This lets the packaged app
reuse the verified saved model path for manual smoke tests, while
`huggingface_user_token` is stripped before the config is copied.

The settings-page Hugging Face token help text now explicitly tells users to
use their own Hugging Face token and accept pyannote model access terms. The GUI
does not include or distribute another person's token. User-entered tokens are
saved only in local private config files, while tracked defaults and packaged
seed configs keep the token blank.

The README now documents which features need Hugging Face credentials. Ordinary local faster-whisper transcription and Demucs do not require a token. WhisperX speaker diarization requires the user to accept the relevant pyannote model terms (`pyannote/speaker-diarization@2.1` for the verified vendored path or `pyannote/speaker-diarization-community-1` for the upstream experiment) and use their own Hugging Face token.

On 2026-06-01, packaged ordinary transcription initially failed with VAD enabled
because `faster_whisper/assets/silero_vad_v6.onnx` was missing from the
PyInstaller output. The packaging spec now collects faster-whisper package data,
and the rebuilt packaged executable completed the user's ordinary transcription
smoke test.

## Source-Run Release Candidate

The current source-run continuation is a release candidate for Windows source
execution, not for a packaged portable executable. The verified source-run
scope includes ordinary faster-whisper transcription, model autoload, local
config separation, WhisperX vendored alignment/diarization, upstream WhisperX
runner smoke coverage, Demucs subprocess separation, dependency entrypoints,
and the repository test suite.

Final source-run handoff checks:

- Run `finish-source-run-merge.cmd` from the repository root.
- Optionally run `check-source-run-rc.cmd` to confirm the local startup config
  has autoload enabled and a readable saved model target before opening the GUI.
- Launch `launch-source-gui.cmd` and confirm the saved model autoloads.
- Run one ordinary faster-whisper transcription.
- Optionally smoke-test WhisperX alignment, WhisperX speaker diarization, and
  Demucs from their GUI pages when their add-on dependency slices are installed.
- Build the Windows onedir package with `package-windows-source.cmd`, then run
  a packaged ordinary-transcription smoke pass before treating it as a packaged
  release.

## Verification

Run the current test suite from the repository root:

```powershell
.\.venv\Scripts\python.exe -m pytest tests -q -p no:cacheprovider
```

The current verified result is `168 passed`.

For a manual smoke test, launch `launch-source-gui.cmd`, confirm the saved model
autoloads, and run one ordinary faster-whisper transcription. If no saved model
target exists, choose the verified model path once and let the local user config
persist it for the next launch. WhisperX alignment, WhisperX speaker
diarization, and Demucs audio separation should then be tested from their GUI
pages when their add-on dependency slices are installed.

On 2026-06-01, `check-source-run-rc.cmd` passed with
`autoLoadModel=True`, `hasModelTarget=True`, and
`modelTargetAccessible=True`. The most recent GUI launch after this RC check
autoloaded the saved model and logged `Load over`.

The ordinary faster-whisper source-run smoke was also verified on
`temp/source-run-smoke.wav` with the same readable saved model path. The smoke
returned one English transcript segment.
