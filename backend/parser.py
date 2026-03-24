"""
InBody report OCR parser — Spanish language reports.
EasyOCR reader is lazy-initialised on first use.
"""

import re
import math
import os
from typing import Optional

import easyocr

# ---------------------------------------------------------------------------
# Lazy singleton
# ---------------------------------------------------------------------------
_reader = None


def _get_reader():
    global _reader
    if _reader is None:
        print("[parser] Initialising EasyOCR reader (es + en) …")
        _reader = easyocr.Reader(["es", "en"], gpu=False, verbose=False)
        print("[parser] EasyOCR ready.")
    return _reader


# ---------------------------------------------------------------------------
# Line grouping helpers
# ---------------------------------------------------------------------------

def _build_lines(results, y_tolerance=18):
    """
    Group OCR tokens into horizontal lines.
    Returns list of lines sorted by y, each line = list of tokens sorted by x.
    token = {'text': str, 'cx': float, 'cy': float}
    """
    lines = []
    for (bbox, text, conf) in results:
        xs = [p[0] for p in bbox]
        ys = [p[1] for p in bbox]
        cx = sum(xs) / len(xs)
        cy = sum(ys) / len(ys)

        placed = False
        for line in lines:
            if abs(line["cy"] - cy) <= y_tolerance:
                line["tokens"].append({"text": text, "cx": cx, "cy": cy})
                placed = True
                break
        if not placed:
            lines.append({"cy": cy, "tokens": [{"text": text, "cx": cx, "cy": cy}]})

    for line in lines:
        line["tokens"].sort(key=lambda t: t["cx"])

    return sorted(lines, key=lambda l: l["cy"])


def _is_plain_number(text: str) -> bool:
    """True if text (comma→period) parses as a float."""
    try:
        float(text.replace(",", ".").strip())
        return True
    except ValueError:
        return False


# ---------------------------------------------------------------------------
# Search strategies
# ---------------------------------------------------------------------------

def _right_of_label(lines, label_pattern, value_min=None, value_max=None):
    """
    Find label token in lines (first match by y), return first numeric token
    to its right on the same grouped line.
    Skips lines that are dense with numbers (chart axes have 10+ numbers).
    """
    label_re = re.compile(label_pattern, re.IGNORECASE)

    for line in lines:
        tokens = line["tokens"]
        label_x = None

        for tok in tokens:
            if label_re.search(tok["text"]):
                label_x = tok["cx"]
                break

        if label_x is None:
            continue

        for tok in tokens:
            if tok["cx"] <= label_x + 10:
                continue
            if _is_plain_number(tok["text"]):
                val = _to_float(tok["text"])
                if val is None:
                    continue
                if value_min is not None and val < value_min:
                    continue
                if value_max is not None and val > value_max:
                    continue
                return tok["text"]

    return None


def _below_label_sparse(lines, label_pattern, y_range=80,
                        value_min=None, value_max=None,
                        label_y_min=None, max_nums_in_row=3):
    """
    Find label (optionally after label_y_min), then collect all valid numeric
    candidates in lines below it within y_range (skipping dense axis rows).
    Returns the candidate nearest to the label by Euclidean distance.
    """
    label_re = re.compile(label_pattern, re.IGNORECASE)

    # Find label position
    label_cx, label_cy = None, None
    for line in lines:
        if label_y_min is not None and line["cy"] < label_y_min:
            continue
        for tok in line["tokens"]:
            if label_re.search(tok["text"]):
                label_cx = tok["cx"]
                label_cy = line["cy"]
                break
        if label_cy is not None:
            break

    if label_cy is None:
        return None

    # Collect all candidates from lines below
    candidates = []
    for line in lines:
        if line["cy"] <= label_cy:
            continue
        if line["cy"] > label_cy + y_range:
            break

        nums = [(t["text"], t["cx"], line["cy"]) for t in line["tokens"] if _is_plain_number(t["text"])]
        if len(nums) > max_nums_in_row:
            continue  # dense axis row — skip

        for text, cx, cy in nums:
            val = _to_float(text)
            if val is None:
                continue
            if value_min is not None and val < value_min:
                continue
            if value_max is not None and val > value_max:
                continue
            dist = math.sqrt((cx - label_cx) ** 2 + (cy - label_cy) ** 2)
            candidates.append((dist, text))

    if candidates:
        return min(candidates, key=lambda c: c[0])[1]

    return None


# ---------------------------------------------------------------------------
# Type converters
# ---------------------------------------------------------------------------

def _to_float(s: Optional[str]) -> Optional[float]:
    if s is None:
        return None
    try:
        return float(s.replace(",", ".").strip().rstrip("."))
    except ValueError:
        return None


def _to_int(s: Optional[str]) -> Optional[int]:
    v = _to_float(s)
    return int(round(v)) if v is not None else None


# ---------------------------------------------------------------------------
# Filename date extraction
# ---------------------------------------------------------------------------

def parse_filename_date(filename: str) -> Optional[str]:
    """
    117820876_20260214132635_InBody.jpg  →  "2026-02-14"
    """
    basename = os.path.basename(filename)
    m = re.search(r"_(\d{4})(\d{2})(\d{2})\d{6}_", basename)
    if m:
        return f"{m.group(1)}-{m.group(2)}-{m.group(3)}"
    m = re.search(r"(\d{4})(\d{2})(\d{2})", basename)
    if m:
        return f"{m.group(1)}-{m.group(2)}-{m.group(3)}"
    return None


# ---------------------------------------------------------------------------
# Main extraction
# ---------------------------------------------------------------------------

def extract_metrics(image_path: str) -> dict:
    """
    Run EasyOCR on image_path and return a dict with all InBody metrics.
    Missing fields are None.
    """
    results = _get_reader().readtext(image_path, detail=1)
    lines = _build_lines(results, y_tolerance=18)

    full_text = " ".join(t for (_, t, _) in results)

    # ── Date ────────────────────────────────────────────────────────────────
    scan_date: Optional[str] = None
    dm = re.search(r"(\d{4})[.\-/](\d{2})[.\-/](\d{2})", full_text)
    if dm:
        scan_date = f"{dm.group(1)}-{dm.group(2)}-{dm.group(3)}"

    # ── Gender ───────────────────────────────────────────────────────────────
    gender: Optional[str] = None
    if re.search(r"\bmujer\b|\bfemenino\b|\bfemale\b", full_text, re.IGNORECASE):
        gender = "F"
    elif re.search(r"\bhombre\b|\bmasculino\b|\bmale\b", full_text, re.IGNORECASE):
        gender = "M"

    # ── Height — token looks like "183cm" ────────────────────────────────────
    height_s: Optional[str] = None
    for (_, text, _) in results:
        m = re.match(r"^(\d{2,3})cm$", text, re.IGNORECASE)
        if m:
            height_s = m.group(1)
            break

    # ── Age — below "Edad" label ─────────────────────────────────────────────
    age_s = _below_label_sparse(lines, r"^Edad$", y_range=60,
                                value_min=1, value_max=120)
    # age must be a whole number — reject floats like "1,5"
    if age_s and "," in age_s:
        age_s = None

    # ── InBody Score — "70/100" is ONE token ─────────────────────────────────
    inbody_score_s: Optional[str] = None
    for (_, text, _) in results:
        m = re.match(r"^(\d{2,3})/100$", text)
        if m:
            inbody_score_s = m.group(1)
            break

    # ── Composition table (top section): look RIGHT of label ────────────────
    # Weight: label is standalone "Peso", value "102,3" is to its right
    weight_s = _right_of_label(lines, r"^Peso$", value_min=30, value_max=300)

    # Total Body Water: "52," is split from "0" so plain-number check still
    # catches "52," because float("52.") == 52.0
    tbw_s = _right_of_label(lines, r"Agua Corporal Total", value_min=10, value_max=100)

    # Minerals
    minerals_s = _right_of_label(lines, r"^Minerales$", value_min=1, value_max=15)

    # Body Fat Mass
    bfm_s = _right_of_label(lines, r"Masa Grasa Corporal", value_min=1, value_max=100)

    # ── Bar-chart metrics: value is below the label in a sparse row ──────────
    # Skeletal Muscle Mass — "40,5" lands on the same grouped line as the label
    smm_s = _right_of_label(lines, r"musculoesquel", value_min=10, value_max=80)

    # BMI — use second "IMC" occurrence (in Parámetros section, y > 1000)
    bmi_s = _below_label_sparse(lines, r"^IMC$", y_range=40,
                                value_min=10, value_max=50, label_y_min=1000)

    # Body Fat % — "Porcentaje de" label is ~29px above the value row
    bfp_s = _below_label_sparse(lines, r"Porcentaje de", y_range=50,
                                value_min=1, value_max=70)

    # Visceral Fat Level — "grasa visceral" is ~60px above "14"
    visceral_s = _below_label_sparse(lines, r"grasa visceral", y_range=80,
                                     value_min=1, value_max=30)

    # Waist-Hip Ratio — label then "1,04" ~59px below
    whr_s = _below_label_sparse(lines, r"Cintura.Cadera", y_range=80,
                                value_min=0.5, value_max=1.5)

    return {
        "scan_date":            scan_date,
        "weight":               _to_float(weight_s),
        "skeletal_muscle_mass": _to_float(smm_s),
        "body_fat_mass":        _to_float(bfm_s),
        "body_fat_percent":     _to_float(bfp_s),
        "total_body_water":     _to_float(tbw_s),
        "minerals":             _to_float(minerals_s),
        "bmi":                  _to_float(bmi_s),
        "visceral_fat_level":   _to_int(visceral_s),
        "waist_hip_ratio":      _to_float(whr_s),
        "inbody_score":         _to_int(inbody_score_s),
        "height":               _to_int(height_s),
        "age":                  _to_int(age_s),
        "gender":               gender,
    }
