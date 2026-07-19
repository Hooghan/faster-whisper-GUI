# Windows Installer

This project can be distributed either as the existing portable onedir package
or as a clickable Windows installer built with Inno Setup.

## Prerequisites

1. Build the packaged app first:

   ```powershell
   .\package-windows-source.cmd
   ```

2. Install Inno Setup 6:

   ```text
   https://jrsoftware.org/isdl.php
   ```

## Build The Installer

Run:

```powershell
.\build-installer.cmd
```

The installer output is:

```text
dist\installer\FasterWhisperGUI-0.8.6-dev-Setup.exe
```

## Installer Behavior

- Installs per user by default under:

  ```text
  %LOCALAPPDATA%\Programs\FasterWhisperGUI
  ```

- Creates Start Menu and optional Desktop shortcuts.
- Keeps the `_internal` folder beside `FasterWhisperGUI.exe`.
- Seeds `user\fasterWhisperGUIConfig.local.json` only when it does not already
  exist.
- Does not include private Hugging Face tokens.
- Leaves the `user` folder behind during uninstall so local settings are not
  accidentally removed.

## Notes

The installer is not code-signed. Windows may show an unknown publisher warning
unless a signing certificate is added in a future release process.
