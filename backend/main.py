import os
import shutil
from typing import List, Optional

from fastapi import FastAPI, File, Form, UploadFile, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session

from database import Scan, get_db, init_db
from models import ScanOut, ScanListItem, ScanUpdate
from parser import extract_metrics, parse_filename_date

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
os.makedirs(DATA_DIR, exist_ok=True)

# ---------------------------------------------------------------------------
# App setup
# ---------------------------------------------------------------------------
app = FastAPI(title="Body Metrics API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # local-only app, all origins fine
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/data", StaticFiles(directory=DATA_DIR), name="data")

# Initialise DB tables on startup
init_db()


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@app.post("/api/scans/upload", response_model=ScanOut)
async def upload_scan(
    file: UploadFile = File(...),
    profile_name: str = Form(...),
    db: Session = Depends(get_db),
):
    # Validate file type
    if not file.filename.lower().endswith((".png", ".jpg", ".jpeg")):
        raise HTTPException(
            status_code=400, detail="Only PNG/JPG images are accepted.")

    # Save image to data/
    dest_path = os.path.join(DATA_DIR, file.filename)
    with open(dest_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    # Extract metrics via OCR
    try:
        metrics = extract_metrics(dest_path)
    except Exception as exc:
        # Remove saved file on failure
        if os.path.exists(dest_path):
            os.remove(dest_path)
        raise HTTPException(
            status_code=500, detail=f"OCR extraction failed: {exc}")

    # Fall back to filename date if OCR couldn't find one
    if not metrics.get("scan_date"):
        metrics["scan_date"] = parse_filename_date(file.filename)

    # Persist to DB
    scan = Scan(
        profile_name=profile_name,
        image_filename=file.filename,
        **metrics,
    )
    db.add(scan)
    db.commit()
    db.refresh(scan)
    return scan


@app.get("/api/scans", response_model=List[ScanOut])
def list_scans(profile: Optional[str] = None, db: Session = Depends(get_db)):
    q = db.query(Scan)
    if profile:
        q = q.filter(Scan.profile_name == profile)
    return q.order_by(Scan.scan_date.desc()).all()


@app.get("/api/profiles")
def list_profiles(db: Session = Depends(get_db)):
    rows = db.query(Scan.profile_name).distinct().all()
    return [r[0] for r in rows]


@app.get("/api/scans/{scan_id}", response_model=ScanOut)
def get_scan(scan_id: int, db: Session = Depends(get_db)):
    scan = db.query(Scan).filter(Scan.id == scan_id).first()
    if not scan:
        raise HTTPException(status_code=404, detail="Scan not found.")
    return scan


@app.patch("/api/scans/{scan_id}", response_model=ScanOut)
def update_scan(scan_id: int, data: ScanUpdate, db: Session = Depends(get_db)):
    scan = db.query(Scan).filter(Scan.id == scan_id).first()
    if not scan:
        raise HTTPException(status_code=404, detail="Scan not found.")
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(scan, field, value)
    db.commit()
    db.refresh(scan)
    return scan


@app.delete("/api/scans/{scan_id}")
def delete_scan(scan_id: int, db: Session = Depends(get_db)):
    scan = db.query(Scan).filter(Scan.id == scan_id).first()
    if not scan:
        raise HTTPException(status_code=404, detail="Scan not found.")

    # Remove image file
    if scan.image_filename:
        img_path = os.path.join(DATA_DIR, scan.image_filename)
        if os.path.exists(img_path):
            os.remove(img_path)

    db.delete(scan)
    db.commit()
    return {"detail": "Scan deleted."}


@app.delete("/api/reset")
def reset_all(db: Session = Depends(get_db)):
    """Delete all scans from the DB and all image files from data/."""
    db.query(Scan).delete()
    db.commit()

    image_extensions = {".png", ".jpg", ".jpeg", ".gif", ".webp"}
    for filename in os.listdir(DATA_DIR):
        if os.path.splitext(filename)[1].lower() in image_extensions:
            os.remove(os.path.join(DATA_DIR, filename))

    return {"detail": "All data cleared."}


@app.delete("/api/profiles/{profile_name}")
def delete_profile(profile_name: str, db: Session = Depends(get_db)):
    """Delete all scans and image files for a specific profile."""
    scans = db.query(Scan).filter(Scan.profile_name == profile_name).all()
    if not scans:
        raise HTTPException(status_code=404, detail="Profile not found.")

    for scan in scans:
        if scan.image_filename:
            img_path = os.path.join(DATA_DIR, scan.image_filename)
            if os.path.exists(img_path):
                os.remove(img_path)
        db.delete(scan)

    db.commit()
    return {"detail": f"Profile '{profile_name}' and all its data deleted."}


@app.get("/api/compare")
def compare_profiles(profiles: str, db: Session = Depends(get_db)):
    """
    ?profiles=alice,bob  — returns latest scan per profile grouped in a dict.
    """
    names = [n.strip() for n in profiles.split(",") if n.strip()]
    result = {}
    for name in names:
        scan = (
            db.query(Scan)
            .filter(Scan.profile_name == name)
            .order_by(Scan.scan_date.desc())
            .first()
        )
        if scan:
            result[name] = ScanOut.model_validate(scan).model_dump()
    return result
