@echo off
setlocal
cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" (
    echo Source-run Python environment was not found.
    echo Run launch-source-gui.cmd for setup guidance.
    pause
    exit /b 1
)

".venv\Scripts\python.exe" -m tools.source_run_rc_check
if errorlevel 1 (
    echo.
    echo Source-run RC check failed.
    pause
    exit /b 1
)

echo.
echo Source-run RC check passed.
pause
