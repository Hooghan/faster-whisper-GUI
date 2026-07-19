@echo off
setlocal
cd /d "%~dp0"

set "APP_DIR=dist\FasterWhisperGUI-0.8.6-dev-source"
set "APP_EXE=%APP_DIR%\FasterWhisperGUI.exe"
set "ISS_FILE=build_tools\FasterWhisperGUI-Setup.iss"

if not exist "%APP_EXE%" (
    echo Packaged app was not found:
    echo   %APP_EXE%
    echo.
    echo Build it first with:
    echo   package-windows-source.cmd
    echo.
    pause
    exit /b 1
)

set "ISCC_EXE="
if exist "tools\InnoSetup6\ISCC.exe" set "ISCC_EXE=%CD%\tools\InnoSetup6\ISCC.exe"
if exist "%ProgramFiles(x86)%\Inno Setup 6\ISCC.exe" set "ISCC_EXE=%ProgramFiles(x86)%\Inno Setup 6\ISCC.exe"
if not defined ISCC_EXE if exist "%ProgramFiles%\Inno Setup 6\ISCC.exe" set "ISCC_EXE=%ProgramFiles%\Inno Setup 6\ISCC.exe"

if not defined ISCC_EXE (
    for %%I in (ISCC.exe) do (
        if not "%%~$PATH:I"=="" set "ISCC_EXE=%%~$PATH:I"
    )
)

if not defined ISCC_EXE (
    echo Inno Setup compiler was not found.
    echo.
    echo Install Inno Setup 6, then run this script again:
    echo   https://jrsoftware.org/isdl.php
    echo.
    echo Expected compiler:
    echo   ISCC.exe
    echo.
    pause
    exit /b 1
)

if not exist "dist\installer" mkdir "dist\installer"

echo Building installer with:
echo   %ISCC_EXE%
echo.
"%ISCC_EXE%" "%ISS_FILE%"
if errorlevel 1 (
    echo.
    echo Installer build failed.
    pause
    exit /b 1
)

echo.
echo Installer created:
echo   dist\installer\FasterWhisperGUI-0.8.6-dev-Setup.exe
echo.
pause
