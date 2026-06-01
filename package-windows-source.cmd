@echo off
cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" (
    echo Missing .venv\Scripts\python.exe
    echo Install the source-run environment first.
    pause
    exit /b 1
)

".venv\Scripts\python.exe" -m PyInstaller --version >nul 2>nul
if errorlevel 1 (
    echo PyInstaller is not installed in this environment.
    echo Run:
    echo   .\.venv\Scripts\python.exe -m pip install -r requirements-dev-package.txt
    pause
    exit /b 1
)

echo Running source-run tests before packaging...
".venv\Scripts\python.exe" -m pytest tests -q -p no:cacheprovider
if errorlevel 1 (
    echo Tests failed. Packaging stopped.
    pause
    exit /b 1
)

echo Building Windows onedir package...
".venv\Scripts\python.exe" -m PyInstaller --noconfirm --clean "build_tools\FasterWhisperGUI.spec"
if errorlevel 1 (
    echo PyInstaller packaging failed.
    pause
    exit /b 1
)

echo Seeding packaged local config without private tokens...
".venv\Scripts\python.exe" -m tools.seed_packaged_local_config
if errorlevel 1 (
    echo Packaged local config seeding failed.
    pause
    exit /b 1
)

echo.
echo Package created:
echo   dist\FasterWhisperGUI-0.8.6-dev-source\FasterWhisperGUI.exe
echo.
echo This package seeds a local user config for smoke testing, but strips
echo private Hugging Face tokens. Source user\*.local.json files are not
echo included directly.
pause
