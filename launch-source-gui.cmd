@echo off
setlocal
cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" (
    echo Source-run Python environment was not found.
    echo.
    echo Create it from this directory with:
    echo   python -m venv .venv
    echo   .\.venv\Scripts\python.exe -m pip install --upgrade pip
    echo   .\.venv\Scripts\python.exe -m pip install -r requirements-dev-faster-whisper.txt
    echo.
    pause
    exit /b 1
)

".venv\Scripts\python.exe" "FasterWhisperGUI.py"
if errorlevel 1 (
    echo.
    echo FasterWhisperGUI.py stopped with an error.
    echo Check the messages above, then install or repair the source-run dependencies:
    echo   .\.venv\Scripts\python.exe -m pip install -r requirements-dev-faster-whisper.txt
    echo.
    pause
    exit /b 1
)
