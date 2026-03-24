# Body Metrics — macOS Setup Guide

Track your body composition over time. Upload InBody PNG scans, extract metrics automatically, and compare progress across profiles.

---

## Requirements

The launch script installs everything automatically, but here's what it needs and what it will do:

| Requirement | How it's handled |
|---|---|
| **Homebrew** | Installed automatically if missing |
| **Python 3** | Installed via Homebrew if missing |
| **Node.js 18+** | Installed via Homebrew if missing |
| **Python packages** | Installed into a local `venv` on first run |
| **npm packages** | Installed into `frontend/node_modules` on first run |

> **First run only:** EasyOCR (the OCR engine) will download ~2 GB of PyTorch and language model files. This happens automatically — just let it finish. All subsequent runs are instant and fully offline.

---

## One-Time Setup (first time only)

Before you can double-click the launcher, you need to make it executable. Open **Terminal** and run:

```bash
chmod +x /path/to/body-metrics/setup/start.command
```

Replace `/path/to/body-metrics` with the actual location of the project folder. For example, if it's on your Desktop:

```bash
chmod +x ~/Desktop/body-metrics/setup/start.command
```

You only need to do this once.

---

## How to Launch

1. Open the `setup/` folder inside the project
2. Double-click **`start.command`**

> **First launch only:** macOS may block the file with a Gatekeeper warning. If that happens:
> Right-click `start.command` → **Open** → click **Open** in the dialog.
> After that, double-clicking works normally every time.

The script will:

- Check and install Homebrew, Python 3, and Node.js if missing
- Create a Python virtual environment (first run only)
- Install all backend Python packages including EasyOCR and PyTorch (first run only, ~5–15 min)
- Install frontend npm packages (first run only)
- Open the backend and frontend in separate Terminal windows
- Open your browser automatically

---

## What Runs Where

| Service | Address | Window title |
|---|---|---|
| Backend API | `http://localhost:8000` | Body Metrics — Backend |
| Frontend UI | `http://localhost:5173` | Body Metrics — Frontend |

To stop the app, close both Terminal windows.

---

## Running from Terminal (alternative)

If you prefer the command line:

```bash
cd /path/to/body-metrics/setup
bash start.command
```

---

## Troubleshooting

**Gatekeeper blocks the file**
Right-click `start.command` → **Open** → click **Open**. You only need to do this once.

**"brew: command not found" after Homebrew install**
On Apple Silicon Macs, Homebrew installs to `/opt/homebrew`. Add it to your PATH:
```bash
echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> ~/.zprofile
source ~/.zprofile
```
Then try again.

**"python3: command not found"**
Run `brew install python` in Terminal, then try again.

**Dependency install failed**
Open Terminal in the `backend/` folder and run:
```bash
venv/bin/python -m pip install -r requirements.txt
```

**Browser opens but the page is blank**
The frontend may still be starting. Wait a few seconds and refresh.

**Port 8000 already in use**
Run this to find and stop the process:
```bash
lsof -ti:8000 | xargs kill
```

---

## Data & Privacy

All data stays on your machine:

- Uploaded images are saved to `backend/data/`
- The database is a single file at `backend/data/body_metrics.db`
- No data is ever sent to any server or cloud service

To reset everything: open the app → **Settings → Reset Everything**.
To delete a specific profile: **Settings → Delete Profile**.
