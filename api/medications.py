from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List
from core.database import get_db
from models.health import Medication
from models.user import User
from schemas.health import MedicationCreate, MedicationResponse
from api.deps import get_current_active_user

router = APIRouter()

@router.post("/", response_model=MedicationResponse)
async def create_medication(
    medication_in: MedicationCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    db_meds = Medication(
        user_id=current_user.id,
        name=medication_in.name,
        dosage=medication_in.dosage,
        frequency=medication_in.frequency,
        time_to_take=medication_in.time_to_take,
    )
    db.add(db_meds)
    await db.commit()
    await db.refresh(db_meds)
    return db_meds

@router.get("/", response_model=List[MedicationResponse])
async def read_medications(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    result = await db.execute(
        select(Medication)
        .where(Medication.user_id == current_user.id, Medication.is_active == True)
        .order_by(Medication.created_at.desc())
        .offset(skip).limit(limit)
    )
    medications = result.scalars().all()
    return medications

@router.delete("/{medication_id}")
async def delete_medication(
    medication_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    result = await db.execute(
        select(Medication)
        .where(Medication.id == medication_id, Medication.user_id == current_user.id)
    )
    medication = result.scalars().first()
    if not medication:
        raise HTTPException(status_code=404, detail="Medication not found")
    
    medication.is_active = False
    await db.commit()
    return {"msg": "Medication soft-deleted"}
