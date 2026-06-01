@echo off
setlocal
cd /d "%~dp0"

echo Running source-run tests...
".venv\Scripts\python.exe" -m pytest tests -q -p no:cacheprovider
if errorlevel 1 goto :failed

echo.
echo Source-run verification passed.
echo.
echo Current status:
git status --short
echo.
echo Important dependency entrypoints:
echo   requirements-dev-faster-whisper.txt
echo   requirements-dev-cuda-cu124.txt
echo   requirements-dev-whisperx.txt
echo   requirements-dev-whisperx-next.txt
echo   requirements-dev-demucs.txt
echo   requirements-dev-package.txt
echo   requirements-dev-test.txt
echo   requirements.txt
echo.
echo Source-run release-candidate handoff:
echo   1. Optionally run check-source-run-rc.cmd
echo   2. Run launch-source-gui.cmd
echo   3. Confirm the saved model autoloads
echo   4. Run one ordinary faster-whisper transcription
echo   5. Run package-windows-source.cmd for the separate Windows package smoke
echo.
echo This script does not commit or merge. Commit later after Git identity and
echo destination branch are intentionally chosen.
pause
exit /b 0

:failed
echo.
echo The verification script stopped because one step failed.
echo Current status:
git status --short
pause
exit /b 1
