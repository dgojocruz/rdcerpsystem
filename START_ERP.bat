@echo off
title RHODECO ERP System v2.0
cls
echo.
echo  Starting RHODECO ERP System v2.0...
echo  Browser will open automatically.
echo  Press Ctrl+C in this window to stop.
echo.
cd /d "%~dp0"

:: Find Python
set PYTHON=
for %%p in (python python3 py) do (
    if not defined PYTHON (
        %%p --version >nul 2>&1 && set PYTHON=%%p
    )
)

:: Fallback: common Python paths on Windows
if not defined PYTHON (
    for %%p in (
        "%LOCALAPPDATA%\Python\pythoncore-3.14-64\python.exe"
        "%LOCALAPPDATA%\Programs\Python\Python312\python.exe"
        "%LOCALAPPDATA%\Programs\Python\Python311\python.exe"
        "%LOCALAPPDATA%\Programs\Python\Python310\python.exe"
        "C:\Python312\python.exe"
        "C:\Python311\python.exe"
        "C:\Python310\python.exe"
    ) do (
        if exist %%p if not defined PYTHON set PYTHON=%%p
    )
)

if not defined PYTHON (
    echo ERROR: Python not found.
    echo Please install Python 3.10+ from https://www.python.org
    pause
    exit /b 1
)

:: Check if client argument given
if "%1"=="" (
    %PYTHON% run.py
) else (
    %PYTHON% run.py --client %1
)

pause
