# Codex Project Handoff

Last updated: 2026-06-10

This document makes the FasterWhisperGUI continuation work reusable from other
Codex accounts or future sessions.

## What This Project Is

This repository continues the open source project
`CheshireCC/faster-whisper-GUI` from the original `0.8.5` baseline. The current
fork-maintained release is:

- Project name: `FasterWhisperGUI`
- Version label: `0.8.6-dev continuation build`
- Branch: `codex-source-dev-run`
- Tag: `FasterWhisperGUI-0.8.6-dev`
- Fork: `https://github.com/Hooghan/faster-whisper-GUI`
- Release:
  `https://github.com/Hooghan/faster-whisper-GUI/releases/tag/FasterWhisperGUI-0.8.6-dev`

The release is marked as a pre-release because it is a continuation build, not
an official upstream stable release.

## Current Verified State

- Full repository test suite reached `169 passed` during release preparation.
- Source GUI ordinary faster-whisper transcription was manually tested.
- Packaged GUI startup, model autoload, VAD transcription, WhisperX vendored
  routes, and Demucs smoke paths were exercised during the continuation work.
- The published Windows package is split into two ZIP parts plus a SHA256 file.

The most detailed technical status is in `docs/continuation-status.md`.
Release-facing notes are in `docs/release-notes-0.8.6-dev.md`.

## Main Changes Already Done

- Updated ordinary transcription to the verified `faster-whisper==1.2.1`
  source-run baseline.
- Added a forward dependency layout using separate requirement files for core
  source-run, CUDA, WhisperX, upstream WhisperX experiments, Demucs, tests, and
  packaging.
- Added startup model autoload when a saved local model path is readable.
- Moved private runtime settings to ignored `user/*.local.json` files.
- Removed Hugging Face tokens from tracked defaults and packaged seed configs.
- Routed WhisperX alignment and speaker diarization through subprocess runners
  to avoid CUDA DLL crashes in the main GUI process.
- Kept the default WhisperX path on the verified vendored backend, while adding
  an isolated upstream backend experiment path.
- Routed Demucs through a subprocess and fixed nested output directory handling.
- Added PyInstaller Windows onedir packaging with the faster-whisper Silero VAD
  ONNX asset included.
- Added tests for dependency baselines, token hygiene, startup autoload, model
  list behavior, WhisperX/Demucs runners, VAD, packaging, local config, and
  release docs.

## Important Files

- `AGENTS.md`: first-read instructions for Codex.
- `README.md`: user-facing project documentation.
- `docs/continuation-status.md`: technical continuation status.
- `docs/release-notes-0.8.6-dev.md`: release notes, Chinese and English.
- `launch-source-gui.cmd`: source GUI launcher.
- `check-source-run-rc.cmd`: release-candidate check script.
- `package-windows-source.cmd`: Windows package builder.
- `build_tools/FasterWhisperGUI.spec`: PyInstaller spec.
- `faster_whisper_GUI/whisperx_backend.py`: WhisperX backend selection.
- `faster_whisper_GUI/whisperx_alignment_runner.py`: alignment subprocess.
- `faster_whisper_GUI/whisperx_diarization_runner.py`: diarization subprocess.
- `faster_whisper_GUI/demucs_runner.py`: Demucs subprocess.

## How To Resume Work

1. Open the repository root in Codex.
2. Read `AGENTS.md`.
3. Read `docs/continuation-status.md`.
4. Check current Git state:

   ```powershell
   git status
   git log --oneline --decorate -5
   ```

5. If changing code, run focused tests for the touched area first.
6. Before committing, check for token-like strings:

   ```powershell
   git grep --cached -n -E "hf_[A-Za-z0-9]{20,}"
   ```

## Git And Release Notes

The continuation work is pushed to the user's fork remote named `myfork`.
If a new Codex account does not have Git credentials, pushing may fail until the
user authenticates in the browser or configures Git.

Useful commands:

```powershell
git remote -v
git status
git push myfork codex-source-dev-run
git push myfork FasterWhisperGUI-0.8.6-dev
```

If GitHub CLI is available, release assets can be replaced with:

```powershell
.\tools\gh-portable-2.96.0\bin\gh.exe release upload FasterWhisperGUI-0.8.6-dev `
  "dist\release-assets\FasterWhisperGUI-0.8.6-dev-continuation-build.zip.part01" `
  "dist\release-assets\FasterWhisperGUI-0.8.6-dev-continuation-build.zip.part02" `
  "dist\release-assets\FasterWhisperGUI-0.8.6-dev-continuation-build.sha256.txt" `
  --repo Hooghan/faster-whisper-GUI `
  --clobber
```

The release asset naming convention is:

- `FasterWhisperGUI-0.8.6-dev-continuation-build.zip.part01`
- `FasterWhisperGUI-0.8.6-dev-continuation-build.zip.part02`
- `FasterWhisperGUI-0.8.6-dev-continuation-build.sha256.txt`

Users rebuild the ZIP with:

```powershell
cmd /c copy /b FasterWhisperGUI-0.8.6-dev-continuation-build.zip.part01+FasterWhisperGUI-0.8.6-dev-continuation-build.zip.part02 FasterWhisperGUI-0.8.6-dev-continuation-build.zip
```

## Hugging Face Token Policy

Do not include user tokens in commits, package assets, release notes, logs, or
handoff prompts.

Token usage summary:

- Ordinary local faster-whisper transcription: no token required.
- Downloading some gated models: token may be required.
- WhisperX alignment: usually no token required.
- WhisperX speaker diarization: token and accepted pyannote model terms are
  required.
- Demucs: no Hugging Face token required.

## Known Future Work

- Continue evaluating upstream WhisperX replacement before changing the default
  backend.
- Improve diarization accuracy options and documentation as more real files are
  tested.
- Consider a stable `0.8.6` release only after the dev build has broader manual
  validation.
- Keep dependency updates incremental; this app has native CUDA, PyTorch,
  CTranslate2, and Windows packaging interactions, so broad upgrades should be
  tested in small slices.

## Suggested Commit For This Handoff

After reviewing these files, commit them with:

```powershell
git add AGENTS.md docs/codex-project-handoff.md docs/codex-project-prompt.md
git grep --cached -n -E "hf_[A-Za-z0-9]{20,}"
git commit -m "docs: add Codex project handoff"
git push myfork codex-source-dev-run
```
