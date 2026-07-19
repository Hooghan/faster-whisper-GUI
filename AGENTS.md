# Codex Project Guide

This repository is a continuation workspace for `CheshireCC/faster-whisper-GUI`.
Read this file first when opening the project from another Codex account.

## Project Status

- Current continuation branch: `codex-source-dev-run`
- Current release tag: `FasterWhisperGUI-0.8.6-dev`
- Public fork: `https://github.com/Hooghan/faster-whisper-GUI`
- Release page:
  `https://github.com/Hooghan/faster-whisper-GUI/releases/tag/FasterWhisperGUI-0.8.6-dev`
- This is an unofficial continuation build based on upstream `0.8.5`.

Detailed status lives in:

- `docs/continuation-status.md`
- `docs/release-notes-0.8.6-dev.md`
- `docs/codex-project-handoff.md`

## Communication

- Use Traditional Chinese with the project owner unless they ask otherwise.
- Keep explanations practical and step-by-step.
- Avoid exposing private tokens, local user paths, or machine-specific settings
  in public docs, commits, logs, release notes, or screenshots.

## Safety Rules

- Never commit Hugging Face tokens. Search for token-like strings before any
  commit or release:

  ```powershell
  git grep --cached -n -E "hf_[A-Za-z0-9]{20,}"
  ```

- Tracked default config files must keep token fields blank.
- Local/private runtime settings belong under `user/*.local.json`; these files
  are ignored by Git.
- Do not commit build outputs, release ZIP parts, logs, caches, virtual
  environments, or local temp files.
- The Codex sandbox may be unable to write `.git`. If committing or pushing
  fails from Codex, ask the user to run the shown Git commands in PowerShell.

## Common Commands

Install and run the source GUI from the verified source-run environment:

```powershell
.\launch-source-gui.cmd
```

Run the release-candidate checks:

```powershell
.\check-source-run-rc.cmd
```

Build the Windows onedir package:

```powershell
.\package-windows-source.cmd
```

Run tests directly:

```powershell
.\.venv\Scripts\python.exe -m pytest
```

## Implementation Notes

- Ordinary transcription uses `faster-whisper==1.2.1`.
- WhisperX alignment and speaker diarization run in subprocesses to avoid CUDA
  DLL conflicts with the main faster-whisper process.
- WhisperX defaults to the verified vendored backend. The isolated upstream
  backend remains experimental.
- Demucs audio separation also runs in a subprocess.
- Startup model autoload is enabled when a saved local model path is readable.
- The GUI model list intentionally omits duplicate aliases such as `large` and
  `turbo`; keep explicit entries such as `large-v3`, `large-v3-turbo`, and
  `distil-large-v3.5`.

## Before Claiming Completion

For docs-only changes, check status and token hygiene. For code or packaging
changes, run the focused tests first, then the full test suite when practical.
For release-affecting changes, update `docs/continuation-status.md`,
`docs/release-notes-0.8.6-dev.md`, and the GitHub release notes if needed.
