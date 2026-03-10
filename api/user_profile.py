from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List, Dict, Any
from core.database import get_db
from models.user import User
from models.health import Disease, EmergencyContact, Allergy, Surgery, Vaccination, FamilyHistory, UserSetting
from api.deps import get_current_active_user
from pydantic import BaseModel

router = APIRouter()

# Simple request schemas
class ItemCreate(BaseModel):
    name: str

class ContactCreate(BaseModel):
    name: str
    phone: str
    relation: str

class SettingsUpdate(BaseModel):
    language: str = "English"
    theme: str = "dark"
    units: str = "metric"
    voice: str = "Off"

@router.get("/")
async def get_profile(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    # Fetch all data
    settings_q = await db.execute(select(UserSetting).where(UserSetting.user_id == current_user.id))
    settings = settings_q.scalars().first()
    
    diseases_q = await db.execute(select(Disease).where(Disease.user_id == current_user.id))
    diseases = [{"id": d.id, "disease_name": d.disease_name} for d in diseases_q.scalars().all()]
    
    contacts_q = await db.execute(select(EmergencyContact).where(EmergencyContact.user_id == current_user.id))
    contact = contacts_q.scalars().first()
    ec_dict = {"name": contact.name, "phone": contact.phone, "relation": contact.relation} if contact else {"name": "", "phone": "", "relation": ""}
    
    allergies_q = await db.execute(select(Allergy).where(Allergy.user_id == current_user.id))
    allergies = [a.allergy_name for a in allergies_q.scalars().all()]
    
    surgeries_q = await db.execute(select(Surgery).where(Surgery.user_id == current_user.id))
    surgeries = [s.surgery_name for s in surgeries_q.scalars().all()]
    
    vaccinations_q = await db.execute(select(Vaccination).where(Vaccination.user_id == current_user.id))
    vaccinations = [v.vaccination_name for v in vaccinations_q.scalars().all()]
    
    fam_hist_q = await db.execute(select(FamilyHistory).where(FamilyHistory.user_id == current_user.id))
    family_history = [f.history_name for f in fam_hist_q.scalars().all()]

    return {
        "user": {
            "name": current_user.name,
            "email": current_user.email,
            "phone": current_user.phone,
            "age": current_user.age,
            "gender": current_user.gender,
            "blood_group": current_user.blood_group
        },
        "settings": {
            "language": settings.language if settings else "English",
            "theme": settings.theme if settings else "dark",
            "units": settings.units if settings else "metric",
            "voice": settings.voice if settings else "Off",
        },
        "diseases": diseases,
        "medInfo": {
            "emergencyContact": ec_dict,
            "allergies": allergies,
            "surgeries": surgeries,
            "vaccinations": vaccinations,
            "familyHistory": family_history
        }
    }

@router.put("/settings")
async def update_settings(
    data: SettingsUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    settings_q = await db.execute(select(UserSetting).where(UserSetting.user_id == current_user.id))
    settings = settings_q.scalars().first()
    if not settings:
        settings = UserSetting(user_id=current_user.id)
        db.add(settings)
    settings.language = data.language
    settings.theme = data.theme
    settings.units = data.units
    settings.voice = data.voice
    await db.commit()
    return {"msg": "Settings updated"}

@router.post("/disease")
async def add_disease(
    data: ItemCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    item = Disease(user_id=current_user.id, disease_name=data.name)
    db.add(item)
    await db.commit()
    return {"msg": "Disease added", "id": item.id}

@router.post("/emergency_contact")
async def update_emergency_contact(
    data: ContactCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    contacts_q = await db.execute(select(EmergencyContact).where(EmergencyContact.user_id == current_user.id))
    contact = contacts_q.scalars().first()
    if not contact:
        contact = EmergencyContact(user_id=current_user.id)
        db.add(contact)
    contact.name = data.name
    contact.phone = data.phone
    contact.relation = data.relation
    await db.commit()
    return {"msg": "Emergency contact updated"}

@router.post("/allergy")
async def add_allergy(
    data: ItemCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    item = Allergy(user_id=current_user.id, allergy_name=data.name)
    db.add(item)
    await db.commit()
    return {"msg": "Allergy added"}

@router.post("/surgery")
async def add_surgery(
    data: ItemCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    item = Surgery(user_id=current_user.id, surgery_name=data.name)
    db.add(item)
    await db.commit()
    return {"msg": "Surgery added"}

@router.post("/vaccination")
async def add_vaccination(
    data: ItemCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    item = Vaccination(user_id=current_user.id, vaccination_name=data.name)
    db.add(item)
    await db.commit()
    return {"msg": "Vaccination added"}

@router.post("/family_history")
async def add_family_history(
    data: ItemCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    item = FamilyHistory(user_id=current_user.id, history_name=data.name)
    db.add(item)
    await db.commit()
    return {"msg": "Family history added"}
