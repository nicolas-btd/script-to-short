@echo off
REM Start Google Chrome with remote debugging port 9222 and isolated profile on Windows.

set "SCRIPT_DIR=%~dp0"
set "PROFILE_DIR=%SCRIPT_DIR%profile"

if not exist "%PROFILE_DIR%" mkdir "%PROFILE_DIR%"

set "CHROME_BIN="
if exist "%ProgramFiles%\Google\Chrome\Application\chrome.exe" set "CHROME_BIN=%ProgramFiles%\Google\Chrome\Application\chrome.exe"
if exist "%ProgramFiles(x86)%\Google\Chrome\Application\chrome.exe" set "CHROME_BIN=%ProgramFiles(x86)%\Google\Chrome\Application\chrome.exe"
if exist "%LocalAppData%\Google\Chrome\Application\chrome.exe" set "CHROME_BIN=%LocalAppData%\Google\Chrome\Application\chrome.exe"

if "%CHROME_BIN%"=="" (
    echo [CHROME] Error: Google Chrome not found in standard installation paths.
    echo Please ensure Google Chrome is installed on your computer.
    pause
    exit /b 1
)

echo [CHROME] Starting Chrome on port 9222 with isolated profile...
start "" "%CHROME_BIN%" --remote-debugging-port=9222 --user-data-dir="%PROFILE_DIR%"
