from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class HealthRecordCreate(BaseModel):
    heart_rate: int
    blood_pressure_systolic: int
    blood_pressure_diastolic: int
    blood_sugar: float
    body_temperature: float

class HealthRecordResponse(HealthRecordCreate):
    id: int
    user_id: int
    risk_score: Optional[float] = None
    risk_assessment: Optional[str] = None
    recorded_at: datetime

    class Config:
        orm_mode = True

class MedicationCreate(BaseModel):
    name: str
    dosage: str
    frequency: str
    time_to_take: str

class MedicationResponse(MedicationCreate):
    id: int
    user_id: int
    is_active: bool
    created_at: datetime

    class Config:
        orm_mode = True
