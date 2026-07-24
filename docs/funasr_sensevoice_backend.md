# FunASR / SenseVoice backend

FasterWhisperGUI can load SenseVoice through an optional FunASR backend without
changing the default faster-whisper installation.

## Install

Install the normal application requirements first, then add the optional
backend:

```bash
python -m pip install -r requirements.txt
python -m pip install -r requirements-funasr.txt
```

Packaged executables do not gain Python packages at runtime. A release that
offers the selector must therefore be built in an environment where
`requirements-funasr.txt` is installed and FunASR is included in the package.
The normal build can continue to omit it.

## Use

1. Open **Model parameters**.
2. Set **ASR backend** to **FunASR / SenseVoice**.
3. Keep `iic/SenseVoiceSmall` or enter another compatible FunASR model id.
4. Select `cpu` or a CUDA device and click **Load model**.
5. Run transcription through the existing files and subtitle workflow.

The load action imports and initializes FunASR immediately, so a missing
optional dependency or model download error is shown before transcription.

## Behavior

The adapter calls `AutoModel.generate(...)`, requests sentence timestamps, and
converts FunASR's millisecond timestamps to the seconds expected by the current
subtitle and table pipeline. SenseVoice rich-transcription tags are removed
from visible text while the language tag is retained as transcription metadata.
FunASR 1.3.29 and newer return SenseVoice text for each VAD speech region in
`sentence_info`, so long recordings retain real segment boundaries even when
the ASR model does not provide token timestamps. Compatible custom models that
return neither sentence nor token timing fall back to one cue using the media
duration instead of producing a zero-length subtitle.

Language mapping:

- `Auto`, empty language, or `None` map to FunASR auto-detection.
- `zhs`, `zht`, and `zh-CN` map to `zh`.
- `yue`, `ja`, `ko`, and `en` are passed through as compact language hints.

Decoding options that only exist in faster-whisper are accepted and ignored by
the adapter, which keeps the shared transcription worker backward compatible.
SenseVoice does not provide speech translation through this adapter, so the
`translate` task raises a clear error instead of silently transcribing.
