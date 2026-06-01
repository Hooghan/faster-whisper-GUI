# FasterWhisperGUI 0.8.6-dev continuation build

This is an unofficial continuation build based on
`CheshireCC/faster-whisper-GUI` `0.8.5`. It keeps the original application name
while marking this release as a fork-maintained development build, not an
official upstream stable release.

## Highlights

- Updates ordinary faster-whisper transcription to the verified
  `faster-whisper==1.2.1` source-run baseline.
- Keeps `large-v3` and `large-v3-turbo`, adds `distil-large-v3.5`, and omits
  duplicate aliases such as `large` and `turbo` from the GUI model list.
- Enables startup model autoload when a saved local model path exists.
- Separates local private settings from tracked defaults and strips Hugging
  Face tokens from packaged seed configs.
- Runs WhisperX alignment and speaker diarization through subprocesses to avoid
  CUDA DLL conflicts with the main faster-whisper process.
- Keeps the default WhisperX route on the verified vendored backend, with an
  isolated upstream WhisperX experiment path available for testing.
- Runs Demucs audio separation through a subprocess and fixes nested output
  directory handling.
- Adds Windows onedir packaging with PyInstaller and includes the
  faster-whisper Silero VAD ONNX asset required for VAD-enabled transcription.
- Adds a focused test suite covering dependency baselines, token hygiene,
  startup autoload, model names, WhisperX/Demucs runners, packaging, and VAD.

## Verification

- Repository test suite: `169 passed`.
- Source GUI: ordinary faster-whisper transcription manually tested.
- Packaged GUI: startup, model autoload, VAD-enabled ordinary transcription,
  WhisperX vendored paths, and Demucs smoke tests were exercised during the
  continuation work.

## Windows Package Assets

The packaged Windows build is large, so the release asset is split into parts
for GitHub Releases:

- `FasterWhisperGUI-0.8.6-dev-continuation-build.zip.part01`
- `FasterWhisperGUI-0.8.6-dev-continuation-build.zip.part02`
- `FasterWhisperGUI-0.8.6-dev-continuation-build.sha256.txt`

After downloading both parts, rebuild the ZIP from PowerShell:

```powershell
cmd /c copy /b FasterWhisperGUI-0.8.6-dev-continuation-build.zip.part01+FasterWhisperGUI-0.8.6-dev-continuation-build.zip.part02 FasterWhisperGUI-0.8.6-dev-continuation-build.zip
```

Then extract `FasterWhisperGUI-0.8.6-dev-continuation-build.zip` and run
`FasterWhisperGUI.exe`.

## Notes

- The package does not include user Hugging Face tokens.
- WhisperX speaker diarization still requires the user to accept the relevant
  pyannote model terms on Hugging Face and enter their own token.
- The upstream WhisperX backend remains experimental; the default release path
  uses the vendored WhisperX backend.
