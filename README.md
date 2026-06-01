# faster-whisper-GUI

    faster-whisper、whisperX，GUI with PySide6

- ## model download

  - https://huggingface.co/models?sort=trending&search=faster-whisper
  
  - you can also download and convert models in software

  - The GUI model selector follows the short model names supported by the
    installed `faster-whisper` package. With the current continuation baseline
    (`faster-whisper==1.2.1`), the selector omits duplicate aliases such as
    `large` and `turbo`, keeps explicit names such as `large-v3` and
    `large-v3-turbo`, and lists `distil-large-v3.5` before `distil-large-v3`.

  - large-v3 model float32 :
  
    - [Huggingface](https://huggingface.co/CheshireCC/faster-whisper-large-v3-float32)
    
    - [百度云网盘链接](https://pan.baidu.com/s/1qltCehSq3pWMlIJ06sWLCQ?pwd=5xq8)
    
        
  
- ### Links

  - [pyside6-fluent-widgets](https://github.com/zhiyiYo/PyQt-Fluent-Widgets)
  - [faster-whisper](https://github.com/guillaumekln/faster-whisper)
  - [whisperX](https://github.com/m-bain/whisperX)
  - [HuggingFace models download](https://huggingface.co/models)
  - [Demucs](https://github.com/facebookresearch/demucs)
  - more and better AVE ：

    - [UVR](https://github.com/Anjok07/ultimatevocalremovergui#installation)
    - [Demucs-Gui](https://github.com/CarlGao4/Demucs-Gui)
  
- ## What's this

  - this is a GUI software of faster-whisper , you can:
    - Transcrib audio or video files to srt/txt/smi/vtt/lrc file
    - provide all paraments of VAD-model and whisper-model
    - now, it support whisperX
    - Demucs model support
    - whisper large-v3 model support

---

## Windows source run for ordinary faster-whisper transcription

The continuation baseline starts with the ordinary `faster-whisper` GUI flow.
The source continuation build displays `0.8.6-dev` and the focused ordinary
transcription baseline currently pins `faster-whisper` 1.2.1.
Startup model autoload is enabled by default: when a saved model target exists,
the GUI loads it automatically after the window finishes initializing.
The autoload switch is independent from automatic config saving, so turning off
automatic config saving does not silently clear the startup autoload preference.
Create a virtual environment, install the first source-run dependency slice,
and start the app from the repository root:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements-dev-faster-whisper.txt
.\.venv\Scripts\python.exe FasterWhisperGUI.py
```

For the repository test suite, install the test-only dependency slice after the
ordinary source-run requirements:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements-dev-test.txt
.\.venv\Scripts\python.exe -m pytest tests -q -p no:cacheprovider
```

For final source-run handoff verification, run:

```powershell
.\finish-source-run-merge.cmd
```

This verifies the source-run test suite and prints the remaining manual
release-candidate checks. It does not commit or merge.
To check whether the local startup config is ready to autoload a saved model
before opening the GUI, run:

```powershell
.\check-source-run-rc.cmd
```

For a Windows onedir package build after the source-run flow is verified,
install the package-build dependency slice and run the package script:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements-dev-package.txt
.\package-windows-source.cmd
```

The package script runs the test suite before invoking PyInstaller and writes
the build to `dist\FasterWhisperGUI-0.8.6-dev-source\FasterWhisperGUI.exe`.
Local user config files and Hugging Face tokens under `user\*.local.json` are
not included in the package.

For the CUDA 12.4 development path used by the `0.8.5` portable release,
install the optional Torch CUDA runtime before running GPU transcription:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements-dev-cuda-cu124.txt
```

For the experimental WhisperX alignment and speaker diarization path, install
the WhisperX add-on after the ordinary and CUDA dependency slices:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements-dev-whisperx.txt
```

For Demucs audio separation, install the Demucs add-on after the ordinary and
CUDA dependency slices:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements-dev-demucs.txt
```

WhisperX alignment is smoke-tested through a CUDA subprocess. WhisperX speaker
diarization is also smoke-tested through a CUDA subprocess and fills the table's
speaker column with `SPEAKER_00` / `SPEAKER_01` labels. Demucs audio separation
is smoke-tested through a CUDA subprocess. Windows executable packaging now has
a PyInstaller onedir build entrypoint and a basic packaged-executable startup
smoke pass. Packaged ordinary transcription with VAD enabled was manually
smoke-tested after adding the bundled faster-whisper VAD asset.

The source build currently uses the repository's vendored `whisperx/` package,
so the title bar displays `WhisperX-vendored` rather than a pip package version.

`requirements-dev-whisperx-next.txt` is an isolated experimental entrypoint for
testing upstream `whisperx==3.8.6`. Do not install it over the verified GUI
baseline until command-line alignment and speaker diarization smoke tests pass
in a separate environment. On 2026-05-26, import, audio loading, CPU alignment,
and CPU diarization smoke tests passed after accepting access for the upstream
default `pyannote/speaker-diarization-community-1` model.

Example upstream WhisperX smoke-test flow:

```powershell
py -3.12 -m venv .venv-whisperx-next
.\.venv-whisperx-next\Scripts\python.exe -m pip install --upgrade pip
.\.venv-whisperx-next\Scripts\python.exe -m pip install -r requirements-dev-whisperx-next.txt
.\.venv-whisperx-next\Scripts\python.exe tools\whisperx_next_smoke.py --audio path\to\sample.wav --language zh --min-speakers 2 --max-speakers 2
```

The upstream WhisperX smoke script requires `ffmpeg.exe` on `PATH` for audio
loading. The script can use `imageio-ffmpeg` from the isolated environment to
provide FFmpeg without changing the Windows system PATH.
It also writes Hugging Face, Transformers, and pyannote cache files under
`cache/whisperx-next` instead of the user-global cache. The upstream
requirements include `hf_xet` so Hugging Face downloads do not fall back to the
slower Xet path when that helper is missing.

After the isolated smoke tests pass, the GUI can be launched with the upstream
WhisperX backend for manual testing:

```powershell
$env:FASTER_WHISPER_GUI_WHISPERX_BACKEND = "upstream"
.\.venv\Scripts\python.exe FasterWhisperGUI.py
Remove-Item Env:\FASTER_WHISPER_GUI_WHISPERX_BACKEND
```

The upstream GUI path runs WhisperX subprocesses through
`.venv-whisperx-next\Scripts\python.exe` when that environment exists. Without
the environment variable, the GUI keeps using the verified vendored WhisperX
backend.

The same switch is available in the WhisperX parameter panel as
`WhisperX 后端`. Keep `vendored` for the verified route, or choose `upstream` to
test the isolated WhisperX 3.8.6 backend.

For speaker diarization comparison tests, the runner prints the selected model,
speaker count limits, and assignment mode. Optional environment variables:

```powershell
$env:FASTER_WHISPER_GUI_WHISPERX_DIARIZATION_MODEL = "pyannote/speaker-diarization-community-1"
$env:FASTER_WHISPER_GUI_WHISPERX_ASSIGN_FILL_NEAREST = "1"
```

Leave these unset for the verified default. `ASSIGN_FILL_NEAREST=1` can reduce
empty speaker assignments around small timing gaps, but it may also assign a
nearby speaker to ambiguous silence or overlap.

The WhisperX parameter panel includes a `短回应修正` switch. It is enabled by
default and helps two-person dialogue where short interjections are otherwise
attached to the surrounding main speaker.

### Hugging Face token and gated model access

Most ordinary transcription work does not need a Hugging Face token after the
selected faster-whisper model is already available locally. A token is only
needed when a feature has to download or use a Hugging Face repository that is
private, rate-limited, or gated by model access terms.

Do not distribute the original author's Hugging Face token or any other shared
token with a build. Each user should create their own Hugging Face access token
and accept the required model terms with their own account. The GUI stores a
user-entered token only in the local private config under `user/*.local.json`;
tracked default configs and packaged seed configs keep the token blank.

Feature access summary:

| Feature | Hugging Face token needed? | Required model access |
| --- | --- | --- |
| Ordinary faster-whisper transcription with a local model path | No | None beyond having the local model files |
| Downloading faster-whisper models from Hugging Face | Sometimes | Depends on the selected model repository |
| WhisperX time alignment | Usually no | Alignment models are normally public for common languages |
| WhisperX speaker diarization / speaker labels | Yes | Accept the pyannote speaker diarization model terms before use |
| Vendored WhisperX diarization default | Yes | `pyannote/speaker-diarization@2.1` |
| Upstream WhisperX 3.8.6 diarization experiment | Yes | `pyannote/speaker-diarization-community-1` |
| Demucs audio separation | No | Uses the Demucs model asset, not the Hugging Face token |

To use speaker diarization, sign in to Hugging Face, open the required pyannote
model page, accept its access terms, then create a personal access token and
paste it into the settings page. If the token is empty or the account has not
accepted the model terms, WhisperX speaker diarization can fail. In that case,
ordinary transcription and alignment still work.

A pure import check can be run without loading audio:

```powershell
.\.venv-whisperx-next\Scripts\python.exe tools\whisperx_next_smoke.py --audio temp\source-run-smoke.wav --skip-alignment --skip-diarization
```

An audio-loading check can be run without downloading alignment or diarization
models:

```powershell
.\.venv-whisperx-next\Scripts\python.exe tools\whisperx_next_smoke.py --audio temp\source-run-smoke.wav --check-audio --skip-alignment --skip-diarization
```

For diarization, upstream WhisperX 3.8.6 defaults to
`pyannote/speaker-diarization-community-1`, which is separately gated on
Hugging Face. Accept that model's access terms before running the default
diarization smoke test. The older model route is kept only as compatibility
context and still needs extra revision handling under pyannote 4:

```powershell
.\.venv-whisperx-next\Scripts\python.exe tools\whisperx_next_smoke.py --audio temp\source-run-smoke.wav --skip-alignment --diarization-model "pyannote/speaker-diarization@2.1"
```

The current verified continuation state is summarized in
[`docs/continuation-status.md`](docs/continuation-status.md).

### Dependency entrypoints

- `requirements-dev-faster-whisper.txt` is the current verified source-run
  dependency file for ordinary `faster-whisper` transcription. It currently
  uses `faster-whisper` 1.2.1 and the PySide6 6.10.x GUI baseline.
- `requirements-dev-cuda-cu124.txt` is the optional NVIDIA CUDA 12.4 add-on used
  with the verified Windows development path.
- `requirements-dev-whisperx.txt` is the experimental WhisperX add-on for
  alignment and speaker diarization dependency work.
- `requirements-dev-whisperx-next.txt` is the isolated upstream WhisperX
  upgrade experiment. It is not part of the verified GUI baseline yet.
- `requirements-dev-demucs.txt` is the experimental Demucs add-on for audio
  separation dependency work.
- `requirements-dev-test.txt` is the test-only dependency file for the
  repository test suite. `pytest.ini` filters known third-party warning noise
  from vendored WhisperX dependencies so new warnings stay visible.
- `requirements.txt` is legacy full-feature dependency context from the original
  project. It has not been modernized or verified for the continuation baseline,
  and it is not the current ordinary source-run install path.

---

- ## Best wishes to the world that received this message

  - ### Agreement

    - By using this software, you have read and agreed to the following user agreement:
      - You agree to use this software in compliance with the laws of your country or region.
      - You may not perform, including, but not limited to, the following acts, nor facilitate any violation of the law:
        - those who oppose the basic principles laid down in the Constitution.
        - endangering national security, divulging state secrets, subverting state power and undermining national unity.
        - harming the honor and interests of the country.
        - inciting ethnic hatred and racial discrimination.
        - those who sabotage the country's religious policy and promote cults.
        - spreading rumors, disturbing social order and undermining social stability.
        - spreading pornography, gambling, violence, murder, terrorism or abetting crime.
        - insulting or slandering others and infringing upon the legitimate rights and interests of others.
        - containing other contents prohibited by laws or administrative regulations.
      - All consequences and responsibilities caused by violations of laws and regulations in any related matters such as the generation, collection, processing and use of your data shall be borne by you.

---

## Star History

[![Star History Chart](https://api.star-history.com/svg?repos=CheshireCC/faster-whisper-GUI&type=Timeline)](https://star-history.com/#CheshireCC/faster-whisper-GUI&Timeline)

- ### UI Language ###

    ![屏幕截图 2024-03-11 183130](./README.assets/183130.png)

- ### Theme Color ###

    ![屏幕截图 2024-03-11 184459](./README.assets/184459.png)

    ![image-20240311184818398](./README.assets/image-20240311184818398.png)

- ### Load Model / Download Model / Convert Model

![image-20231118155123131](./README.assets/image-20231118155123131.png)

- ### Large-v3 模型支持

  ![image-20231118155209847](./README.assets/image-20231118155209847.png)
- ### Demucs AVE

  ![DemucsFunction](./README.assets/DemucsFunction.png)
- ### batch process

![image-20231008150849827](./README.assets/image-20231008150849827.png)

- ### File List

  ![0.3.0_newFIleSystem](./README.assets/0.3.0_newFIleSystem.png)
- ### FileFilter

  ![fileFilter](./README.assets/fileFilter.png)
- ### WhisperX function

![0.3.0_whisperx](./README.assets/0.3.0_whisperx.png)

- ### paraments of faster-whisper model

![image-20231113020210745](./README.assets/image-20231113020210745.png)

- ### Silero VAD

  ![image-20231113020407272](./README.assets/image-20231113020407272.png)
- ### setting

  ![image-20231118155300816](./README.assets/image-20231118155300816.png)
- ### Show result and edit timestample

  ![0.3.0_result](./README.assets/0.3.0_result.png)![image-20231007191942864](./README.assets/image-20231007191942864.png)
- ### words-level timestamps —— karaoka lyric (work in `VTT`/`LRC`/`SMI` format)


  - play with foobar2000 , ESLyric plugin, `lrc` format lyric

  ![image-20230811130449688](./README.assets/image-20230811130449688.png)
