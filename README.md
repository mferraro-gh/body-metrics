# Body Metrics

A local web app for tracking body composition over time using InBody reports. Upload PNG scans, extract metrics automatically via OCR, compare progress across profiles and time periods.

---

## Quick Start

See the setup guide for your operating system:

- [Windows instructions](documentation/windows-instructions.md)
- [Mac instructions](documentation/mac-instructions.md)

---

## Architecture

```
body-metrics/
├── start.bat               ← Launch script (double-click to run)
├── backend/
│   ├── main.py             ← FastAPI app + all API endpoints
│   ├── parser.py           ← OCR engine (EasyOCR) + metric extraction logic
│   ├── database.py         ← SQLite setup via SQLAlchemy
│   ├── models.py           ← Pydantic request/response schemas
│   ├── requirements.txt    ← Python dependencies
│   ├── venv/               ← Python virtual environment (auto-created)
│   └── data/
│       ├── body_metrics.db ← SQLite database (auto-created on first run)
│       └── *.jpg / *.png   ← Uploaded InBody images
└── frontend/
    ├── index.html
    ├── package.json
    ├── vite.config.js      ← Dev server + proxy to backend
    └── src/
        ├── main.js
        ├── App.vue          ← Shell: navbar, dark/light theme toggle
        ├── router/
        │   └── index.js     ← Client-side routes
        ├── views/
        │   ├── DashboardView.vue  ← Metric cards, progress chart, scan history
        │   ├── UploadView.vue     ← Upload form + review/edit extracted metrics
        │   ├── CompareView.vue    ← Side-by-side profile comparison
        │   └── SettingsView.vue   ← Data info + reset button
        └── components/
            ├── MetricCard.vue         ← Read-only metric display card
            ├── EditableMetricCard.vue ← Metric card with inline pen-click editing
            └── ProgressChart.vue      ← Line chart (Chart.js) for trends over time
```

---

## How Data Flows

### 1. Upload

```
User drops PNG → UploadView
  → POST /api/scans/upload  (multipart: file + profile_name)
      → image saved to backend/data/
      → parser.py runs EasyOCR on the image
      → extracted metrics returned as JSON + saved to body_metrics.db
  → Review screen shows editable metric cards
  → User corrects any wrong values (pen icon on hover)
  → PATCH /api/scans/{id}  (saves corrections to DB)
  → Redirect to Dashboard
```

### 2. Dashboard

```
onMounted → GET /api/profiles
              → SELECT DISTINCT profile_name FROM scans

User selects profile → GET /api/scans?profile=Marco
                          → SELECT * FROM scans WHERE profile_name='Marco'
                            ORDER BY scan_date DESC

Vue renders:
  latestScan  = scans[0]          → metric cards at top
  sortedScans = oldest→newest     → progress line chart
  filteredScans = date-filtered   → scan history list
```

### 3. Compare

```
User picks profiles → GET /api/compare?profiles=Marco,Ana
  → returns latest scan per profile as a dict
  → side-by-side table + bar chart rendered in CompareView
```

---

## OCR Parser

InBody reports are in Spanish. `parser.py` uses **EasyOCR** (offline, no API key needed) with two strategies:

| Strategy | Used for |
|---|---|
| **Right-of-label** — find label token, return first number to its right on the same line | Peso, Agua Corporal, Minerales, Masa Grasa, Masa Muscular |
| **Below-label (sparse rows)** — find label, scan lines below it, skip dense axis rows (>3 numbers), return nearest by Euclidean distance | IMC, Grasa Visceral, Cintura-Cadera, Edad |
| **Token regex** | InBody Score (`70/100`), Height (`183cm`), Date (`2026.02.14`), Gender |

EasyOCR initializes once at module load (~5 s). Subsequent uploads on the same session are fast.

---

## API Reference

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/scans/upload` | Upload image, run OCR, save scan |
| `GET` | `/api/scans` | List scans (optional `?profile=name`) |
| `GET` | `/api/scans/{id}` | Get single scan |
| `PATCH` | `/api/scans/{id}` | Update scan fields (corrections after OCR) |
| `DELETE` | `/api/scans/{id}` | Delete scan + image file |
| `GET` | `/api/profiles` | List distinct profile names |
| `GET` | `/api/compare?profiles=a,b` | Latest scan per profile for comparison |
| `DELETE` | `/api/reset` | Delete all scans and images |
| `GET` | `/data/{filename}` | Serve uploaded image files (static) |

---

## Tech Stack

| Layer | Tech |
|---|---|
| Backend | Python 3, FastAPI, Uvicorn |
| OCR | EasyOCR (PyTorch-based, runs fully offline) |
| Database | SQLite via SQLAlchemy (single file, no server) |
| Frontend | Vue 3, Vite, Vue Router |
| Charts | Chart.js + vue-chartjs |
| HTTP client | Axios |
| Styling | CSS custom properties, dark/light theme |

---

## Database

Single file: `backend/data/body_metrics.db`

**`scans` table** — one row per uploaded report:

| Column | Type | Description |
|---|---|---|
| `id` | INTEGER PK | Auto-increment |
| `profile_name` | TEXT | Person's name |
| `scan_date` | TEXT | ISO date from report (`YYYY-MM-DD`) |
| `image_filename` | TEXT | Filename in `data/` |
| `weight` | REAL | kg |
| `skeletal_muscle_mass` | REAL | kg |
| `body_fat_mass` | REAL | kg |
| `body_fat_percent` | REAL | % |
| `total_body_water` | REAL | L |
| `minerals` | REAL | kg |
| `bmi` | REAL | |
| `visceral_fat_level` | INTEGER | 1–20+ |
| `waist_hip_ratio` | REAL | |
| `inbody_score` | INTEGER | 0–100 |
| `height` | INTEGER | cm |
| `age` | INTEGER | years |
| `gender` | TEXT | `M` or `F` |
| `created_at` | DATETIME | Row insert time |

To reset everything: **Settings → Reset Everything** (deletes all rows and image files, keeps the `.db` file intact).

---

## Notes

- **First run is slow** — EasyOCR downloads ~100 MB of language models on first use, then caches them locally. All subsequent runs are offline.
- **PDF support** — not yet implemented. Planned: convert PDF pages to images via `pymupdf`, then run through the same OCR pipeline.
- **Port** — backend runs on `8000`, frontend on `5173` (or next available). The Vite dev server proxies `/api` and `/data` to the backend automatically.
