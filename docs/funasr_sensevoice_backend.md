# SenseVoice / FunASR backend adapter

This branch adds a small adapter layer for wiring FunASR or SenseVoice into the
existing FasterWhisperGUI transcription pipeline.

The GUI currently expects loaded models to provide a faster-whisper-like
`transcribe(...)` method returning `(segments, info)`. The new
`FunASRWhisperCompatibleModel` keeps FunASR optional, lazily loads
`funasr.AutoModel`, calls `AutoModel.generate(...)`, and converts common FunASR
result shapes into the `start`, `end`, `text`, `words` and `language` attributes
used by the current subtitle/export flow.

Suggested UI follow-up:

1. Add an ASR backend selector with `faster-whisper` and `funasr`.
2. When `funasr` is selected, load `FunASRWhisperCompatibleModel` instead of
   `WhisperModel`.
3. Default the FunASR model id to `iic/SenseVoiceSmall`.
4. Quote the optional install command in the release notes:

```bash
python -m pip install -U "funasr>=1.3.19"
```

Language notes:

- `Auto`, empty language, or `None` map to FunASR auto-detection.
- `zhs`, `zht`, and `zh-CN` map to `zh`.
- `yue`, `ja`, `ko`, and `en` are passed through as compact language hints.
