@echo off
setlocal
title Instagram Public Downloader - Local

cd /d "%~dp0"

echo.
echo ==========================================
echo   Instagram Public Downloader - Windows
echo ==========================================
echo.

where py >nul 2>nul
if %errorlevel% neq 0 (
    echo Python was not found.
    echo.
    echo Install Python 3.11 or newer from:
    echo https://www.python.org/downloads/windows/
    echo.
    echo IMPORTANT: enable "Add python.exe to PATH" during installation.
    pause
    exit /b 1
)

if not exist ".venv\Scripts\python.exe" (
    echo Creating Python virtual environment...
    py -m venv .venv
    if %errorlevel% neq 0 (
        echo Failed to create the virtual environment.
        pause
        exit /b 1
    )
)

echo Installing/updating required packages...
".venv\Scripts\python.exe" -m pip install --upgrade pip
".venv\Scripts\python.exe" -m pip install -r requirements-windows.txt

if %errorlevel% neq 0 (
    echo.
    echo Package installation failed.
    pause
    exit /b 1
)

echo.
echo.
echo Instagram session fallback:
echo If public Instagram URLs still show "could not be resolved",
echo set INSTAGRAM_COOKIES_FROM_BROWSER=chrome below and restart.
echo This reads your local browser session only; it is not uploaded.
echo.
rem set INSTAGRAM_COOKIES_FROM_BROWSER=chrome
echo Starting local server...
echo.
echo Open this address in your browser:
echo http://127.0.0.1:8000
echo.
echo Keep this window open while using the site.
echo Press Ctrl+C to stop the server.
echo.

start "" http://127.0.0.1:8000

".venv\Scripts\python.exe" -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000

pause
