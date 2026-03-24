from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class ScanCreate(BaseModel):
    profile_name: str
    scan_date: Optional[str] = None
    image_filename: Optional[str] = None
    weight: Optional[float] = None
    skeletal_muscle_mass: Optional[float] = None
    body_fat_mass: Optional[float] = None
    body_fat_percent: Optional[float] = None
    total_body_water: Optional[float] = None
    minerals: Optional[float] = None
    bmi: Optional[float] = None
    visceral_fat_level: Optional[int] = None
    waist_hip_ratio: Optional[float] = None
    inbody_score: Optional[int] = None
    height: Optional[int] = None
    age: Optional[int] = None
    gender: Optional[str] = None


class ScanOut(BaseModel):
    id: int
    profile_name: str
    scan_date: Optional[str] = None
    image_filename: Optional[str] = None
    weight: Optional[float] = None
    skeletal_muscle_mass: Optional[float] = None
    body_fat_mass: Optional[float] = None
    body_fat_percent: Optional[float] = None
    total_body_water: Optional[float] = None
    minerals: Optional[float] = None
    bmi: Optional[float] = None
    visceral_fat_level: Optional[int] = None
    waist_hip_ratio: Optional[float] = None
    inbody_score: Optional[int] = None
    height: Optional[int] = None
    age: Optional[int] = None
    gender: Optional[str] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ScanUpdate(BaseModel):
    profile_name: Optional[str] = None
    scan_date: Optional[str] = None
    weight: Optional[float] = None
    skeletal_muscle_mass: Optional[float] = None
    body_fat_mass: Optional[float] = None
    body_fat_percent: Optional[float] = None
    total_body_water: Optional[float] = None
    minerals: Optional[float] = None
    bmi: Optional[float] = None
    visceral_fat_level: Optional[int] = None
    waist_hip_ratio: Optional[float] = None
    inbody_score: Optional[int] = None
    height: Optional[int] = None
    age: Optional[int] = None
    gender: Optional[str] = None


class ScanListItem(BaseModel):
    id: int
    profile_name: str
    scan_date: Optional[str] = None
    weight: Optional[float] = None
    skeletal_muscle_mass: Optional[float] = None
    body_fat_mass: Optional[float] = None
    body_fat_percent: Optional[float] = None
    bmi: Optional[float] = None
    inbody_score: Optional[int] = None
    visceral_fat_level: Optional[int] = None
    image_filename: Optional[str] = None

    class Config:
        from_attributes = True
