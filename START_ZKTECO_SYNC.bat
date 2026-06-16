@echo off
title RHODECO ZKTeco Sync Service
echo ================================================
echo   RHODECO ZKTeco Biometric Sync Service
echo ================================================
echo.
echo Installing required packages...
pip install pyzk requests -q
echo.
echo Starting sync service...
echo Press Ctrl+C to stop.
echo.
python zkteco_sync.py
pause
