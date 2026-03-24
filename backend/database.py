from sqlalchemy import create_engine, Column, Integer, Float, String, DateTime
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
os.makedirs(DATA_DIR, exist_ok=True)
DATABASE_URL = f"sqlite:///{os.path.join(DATA_DIR, 'body_metrics.db')}"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class Scan(Base):
    __tablename__ = "scans"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    profile_name = Column(String, nullable=False, index=True)
    scan_date = Column(String, nullable=True)
    image_filename = Column(String, nullable=True)
    weight = Column(Float, nullable=True)
    skeletal_muscle_mass = Column(Float, nullable=True)
    body_fat_mass = Column(Float, nullable=True)
    body_fat_percent = Column(Float, nullable=True)
    total_body_water = Column(Float, nullable=True)
    minerals = Column(Float, nullable=True)
    bmi = Column(Float, nullable=True)
    visceral_fat_level = Column(Integer, nullable=True)
    waist_hip_ratio = Column(Float, nullable=True)
    inbody_score = Column(Integer, nullable=True)
    height = Column(Integer, nullable=True)
    age = Column(Integer, nullable=True)
    gender = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


def init_db():
    Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
