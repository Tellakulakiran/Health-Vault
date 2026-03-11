from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List
from core.database import get_db
from models.health import HealthRecord
from models.user import User
from schemas.health import HealthRecordCreate, HealthRecordResponse
from api.deps import get_current_active_user
# import sys
# import os
# sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# from ai.engine import risk_analyzer

router = APIRouter()

@router.post("/", response_model=HealthRecordResponse)
async def create_health_record(
    record_in: HealthRecordCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    # 1. Analyze vitals using AI Engine (Disabled due to Vercel module pathing bug)
    # score, assessment = risk_analyzer.analyze_vitals(...)
    score, assessment = 0, "AI Analysis offline"

    # 2. Save record
    db_record = HealthRecord(
        user_id=current_user.id,
        heart_rate=record_in.heart_rate,
        blood_pressure_systolic=record_in.blood_pressure_systolic,
        blood_pressure_diastolic=record_in.blood_pressure_diastolic,
        blood_sugar=record_in.blood_sugar,
        body_temperature=record_in.body_temperature,
        risk_score=score,
        risk_assessment=assessment
    )

    db.add(db_record)
    await db.commit()
    await db.refresh(db_record)
    
    return db_record

@router.get("/", response_model=List[HealthRecordResponse])
async def read_health_records(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    result = await db.execute(
        select(HealthRecord)
        .where(HealthRecord.user_id == current_user.id)
        .order_by(HealthRecord.recorded_at.desc())
        .offset(skip).limit(limit)
    )
    records = result.scalars().all()
    return records
