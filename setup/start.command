#!/usr/bin/env bash
# Double-click this file in Finder to launch Body Metrics.
# First time only: right-click → Open (to bypass Gatekeeper), then allow in System Settings.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$SCRIPT_DIR/.."
BACKEND="$ROOT/backend"
FRONTEND="$ROOT/frontend"
VENV="$BACKEND/venv"
PYTHON="$VENV/bin/python"
UVICORN="$VENV/bin/uvicorn"

echo "============================================"
echo " Body Metrics — macOS Setup & Launch"
echo "============================================"

# ── 1. Homebrew ───────────────────────────────
echo
echo "[1/5] Checking Homebrew..."
if ! command -v brew &>/dev/null; then
    echo "  Homebrew not found — installing..."
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    # Add Homebrew to PATH for Apple Silicon Macs
    if [[ -f "/opt/homebrew/bin/brew" ]]; then
        eval "$(/opt/homebrew/bin/brew shellenv)"
    fi
fi
echo "  Found: $(brew --version | head -1)"

# ── 2. Python 3 ──────────────────────────────
echo
echo "[2/5] Checking Python 3..."
if ! command -v python3 &>/dev/null; then
    echo "  Python 3 not found — installing via Homebrew..."
    brew install python
fi
echo "  Found: $(python3 --version)"

# ── 3. Node.js ───────────────────────────────
echo
echo "[3/5] Checking Node.js..."
if ! command -v node &>/dev/null; then
    echo "  Node.js not found — installing via Homebrew..."
    brew install node
fi
echo "  Found: Node $(node --version)"

# ── 4. Python venv + backend deps ────────────
echo
echo "[4/5] Setting up Python virtual environment..."
if [[ ! -f "$PYTHON" ]]; then
    echo "  Creating venv..."
    python3 -m venv "$VENV"
fi

if [[ ! -f "$UVICORN" ]]; then
    echo "  Installing Python packages — this may take several minutes on first run."
    echo "  (EasyOCR requires PyTorch, ~2 GB download)"
    echo
    "$PYTHON" -m pip install --upgrade pip --quiet
    "$PYTHON" -m pip install -r "$BACKEND/requirements.txt"
    if [[ ! -f "$UVICORN" ]]; then
        echo "  ERROR: Dependency installation failed."
        read -r -p "  Press Enter to close..."
        exit 1
    fi
fi
echo "  Done."

# ── 5. Frontend deps ──────────────────────────
echo
echo "[5/5] Checking frontend dependencies..."
if [[ ! -d "$FRONTEND/node_modules" ]]; then
    echo "  Installing npm packages..."
    cd "$FRONTEND"
    npm install
    cd "$SCRIPT_DIR"
fi
echo "  Done."

# ── Launch servers ────────────────────────────
echo
echo "  Launching servers..."

osascript <<APPLESCRIPT
tell application "Terminal"
    do script "\"$UVICORN\" main:app --reload --port 8000 --app-dir \"$BACKEND\""
    set custom title of front window to "Body Metrics — Backend"
end tell
APPLESCRIPT

osascript <<APPLESCRIPT
tell application "Terminal"
    do script "cd \"$FRONTEND\" && npm run dev"
    set custom title of front window to "Body Metrics — Frontend"
end tell
APPLESCRIPT

echo "  Waiting for servers to start..."
sleep 6

# Open browser on first available Vite port
for PORT in 5173 5174 5175 5176 5177 5178 5179 5180; do
    if curl -s --max-time 1 "http://localhost:$PORT" >/dev/null 2>&1; then
        echo "  Opening http://localhost:$PORT"
        open "http://localhost:$PORT"
        break
    fi
done

echo
echo "  Both servers are running in separate Terminal windows."
echo "  Close those windows to stop the app."
echo
