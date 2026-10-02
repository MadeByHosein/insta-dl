@echo off
taskkill /FI "WINDOWTITLE eq Instagram Public Downloader - Local*" /T /F >nul 2>nul
echo Server stopped (if it was running).
pause
