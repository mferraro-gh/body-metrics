# Body Metrics — Windows Setup Guide

Track your body composition over time. Upload InBody PNG scans, extract metrics automatically, and compare progress across profiles.

---

## Requirements

Before running the app, make sure the following are installed on your machine:

| Requirement | Version | Download |
|---|---|---|
| **Python** | 3.10 or higher | https://python.org/downloads — check **"Add Python to PATH"** during install |
| **Node.js** | 18 or higher | https://nodejs.org |

> **First run only:** EasyOCR (the OCR engine) will download ~2 GB of PyTorch and language model files. This happens automatically — just let it finish. All subsequent runs are instant and fully offline.

---

## How to Launch

1. Open the `setup\` folder inside the project
2. Double-click **`start.bat`**

That's it. The script will:

- Create a Python virtual environment (first run only)
- Install all backend Python packages including EasyOCR and PyTorch (first run only, ~5–15 min)
- Install frontend npm packages (first run only)
- Open the backend and frontend in separate terminal windows
- Open your browser automatically

---

## What Runs Where

| Service | Address | Window title |
|---|---|---|
| Backend API | `http://localhost:8000` | Body Metrics — Backend |
| Frontend UI | `http://localhost:5173` | Body Metrics — Frontend |

To stop the app, close both terminal windows.

---

## Troubleshooting

**"Python not found" error**
Install Python from https://python.org/downloads and make sure to check **"Add Python to PATH"** during setup. Then restart and try again.

**"Node not found" error**
Install Node.js from https://nodejs.org, restart your terminal, and try again.

**Dependency install failed**
Open a terminal in the `backend\` folder and run:
```
venv\Scripts\python.exe -m pip install -r requirements.txt
```

**Browser opens but the page is blank**
The frontend may still be starting. Wait a few seconds and refresh.

**Port 8000 already in use**
Another process is using that port. End it via Task Manager or restart your machine.

---

## Data & Privacy

All data stays on your machine:

- Uploaded images are saved to `backend\data\`
- The database is a single file at `backend\data\body_metrics.db`
- No data is ever sent to any server or cloud service

To reset everything: open the app → **Settings → Reset Everything**.
To delete a specific profile: **Settings → Delete Profile**.
