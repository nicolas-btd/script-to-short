#!/usr/bin/env bash
# Start Google Chrome with remote debugging port 9222 and isolated profile.

set -e

DIR="$(cd "$(dirname "$0")" && pwd)"
PROFILE_DIR="$DIR/profile"
mkdir -p "$PROFILE_DIR"

if [[ "$OSTYPE" == "darwin"* ]]; then
    CHROME_BIN="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
elif [[ "$OSTYPE" == "linux"* ]]; then
    CHROME_BIN=$(which google-chrome 2>/dev/null || which chromium-browser 2>/dev/null || which chromium 2>/dev/null || echo "google-chrome")
else
    CHROME_BIN="chrome"
fi

if [ ! -f "$CHROME_BIN" ] && ! command -v "$CHROME_BIN" &> /dev/null; then
    echo "[CHROME] Error: Chrome binary not found: $CHROME_BIN" >&2
    exit 1
fi

echo "[CHROME] Starting Chrome on port 9222 (profile: $PROFILE_DIR)..."
"$CHROME_BIN" --remote-debugging-port=9222 --user-data-dir="$PROFILE_DIR" >/dev/null 2>&1 &
