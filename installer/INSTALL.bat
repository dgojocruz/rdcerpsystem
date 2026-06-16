@echo off
setlocal enabledelayedexpansion
title RHODECO ERP v2.0 — Installer
color 0A
cls
echo.
echo  ╔══════════════════════════════════════════════════════╗
echo  ║         RHODECO ERP System v2.0 — Installer         ║
echo  ║     Philippine HR, Payroll and Timekeeping System    ║
echo  ╚══════════════════════════════════════════════════════╝
echo.

:: ── Step 1: Find Python ──────────────────────────────────────
echo  [1/5] Checking Python installation...
set PYTHON=
for %%p in (python python3 py) do (
    if not defined PYTHON (
        %%p --version >nul 2>&1 && set PYTHON=%%p
    )
)
if not defined PYTHON (
    echo.
    echo  ERROR: Python 3.10 or higher is required.
    echo  Please download and install Python from: https://www.python.org/downloads/
    echo  IMPORTANT: Check "Add Python to PATH" during installation.
    echo.
    pause
    exit /b 1
)
for /f "tokens=2" %%v in ('!PYTHON! --version 2^>^&1') do set PY_VER=%%v
echo  Found Python !PY_VER! ^(!PYTHON!^)
echo.

:: ── Step 2: Choose install location ──────────────────────────
echo  [2/5] Install location
echo.
set INSTALL_DIR=C:\RHODECO_ERP
set /p INSTALL_DIR="  Install to [%INSTALL_DIR%]: "
if "%INSTALL_DIR%"=="" set INSTALL_DIR=C:\RHODECO_ERP
echo.
echo  Installing to: %INSTALL_DIR%
echo.

:: ── Step 3: Copy files ───────────────────────────────────────
echo  [3/5] Copying application files...
if not exist "%INSTALL_DIR%" mkdir "%INSTALL_DIR%"
xcopy /E /I /Y /Q "%~dp0..\*" "%INSTALL_DIR%\" >nul
echo  Files copied.
echo.

:: ── Step 4: Install Python packages ──────────────────────────
echo  [4/5] Installing Python dependencies...
!PYTHON! -m pip install flask werkzeug openpyxl --upgrade --quiet 2>nul
if errorlevel 1 (
    echo  WARNING: Some packages may not have installed. Trying with --user flag...
    !PYTHON! -m pip install flask werkzeug openpyxl --upgrade --quiet --user 2>nul
)
echo  Dependencies installed.
echo.

:: ── Step 5: Create shortcuts ──────────────────────────────────
echo  [5/5] Creating shortcuts...

:: Create launcher script in install dir
(
echo @echo off
echo title RHODECO ERP System
echo cd /d "%INSTALL_DIR%"
echo echo Starting ERP System...
echo !PYTHON! run.py
echo pause
) > "%INSTALL_DIR%\START_ERP.bat"

:: Desktop shortcut via PowerShell
powershell -Command "$s=(New-Object -COM WScript.Shell).CreateShortcut([Environment]::GetFolderPath('Desktop')+'\RHODECO ERP.lnk');$s.TargetPath='%INSTALL_DIR%\START_ERP.bat';$s.WorkingDirectory='%INSTALL_DIR%';$s.IconLocation='%INSTALL_DIR%\installer\assets\icon.ico,0';$s.Description='RHODECO ERP System v2.0';$s.Save()" 2>nul

:: Start Menu shortcut
set SM_DIR=%APPDATA%\Microsoft\Windows\Start Menu\Programs\RHODECO ERP
if not exist "%SM_DIR%" mkdir "%SM_DIR%"
powershell -Command "$s=(New-Object -COM WScript.Shell).CreateShortcut('%SM_DIR%\RHODECO ERP.lnk');$s.TargetPath='%INSTALL_DIR%\START_ERP.bat';$s.WorkingDirectory='%INSTALL_DIR%';$s.Description='RHODECO ERP System v2.0';$s.Save()" 2>nul

echo  Shortcuts created on Desktop and Start Menu.
echo.

:: ── Done ──────────────────────────────────────────────────────
echo  ╔══════════════════════════════════════════════════════╗
echo  ║                Installation Complete!                ║
echo  ╠══════════════════════════════════════════════════════╣
echo  ║  Location : %INSTALL_DIR%
echo  ║  Shortcut : Desktop → RHODECO ERP                   ║
echo  ║  Login    : admin / admin123                         ║
echo  ║                                                      ║
echo  ║  To start : Double-click "RHODECO ERP" on desktop   ║
echo  ║  Or run   : START_ERP.bat in install folder         ║
echo  ╚══════════════════════════════════════════════════════╝
echo.
set /p LAUNCH="  Launch ERP now? [Y/N]: "
if /i "!LAUNCH!"=="Y" (
    start "" "!PYTHON!" "%INSTALL_DIR%\run.py"
    timeout /t 2 /nobreak >nul
    start "" "http://127.0.0.1:5000"
)
echo.
pause
