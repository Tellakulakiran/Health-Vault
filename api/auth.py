from fastapi import APIRouter, Depends, HTTPException, status, Response
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from datetime import timedelta
from core.database import get_db
from core.security import verify_password, create_access_token, get_password_hash
from core.config import settings
from models.user import User

from pydantic import BaseModel
from typing import Optional

router = APIRouter()

class RegisterRequest(BaseModel):
    name: str
    email: Optional[str] = ""
    phone: str
    password: str
    age: int
    gender: str
    blood_group: str

@router.post("/register")
async def register_user(
    data: RegisterRequest,
    db: AsyncSession = Depends(get_db)
):
    from sqlalchemy import or_
    existing_user = await db.execute(
        select(User).where(or_(User.username == data.phone, User.phone == data.phone))
    )
    if existing_user.scalars().first():
        raise HTTPException(status_code=400, detail="Phone number already registered")

    new_user = User(
        username=data.phone,
        phone=data.phone,
        email=data.email,
        name=data.name,
        age=data.age,
        gender=data.gender,
        blood_group=data.blood_group,
        hashed_password=get_password_hash(data.password)
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    
    # Capture the ID before the next commit expires the new_user object
    user_id = new_user.id
    
    # Initialize basic settings
    from models.health import UserSetting
    db.add(UserSetting(user_id=user_id))
    await db.commit()
    
    return {"msg": "Registration successful", "user_id": user_id}

@router.post("/token")
async def login_for_access_token(
    response: Response,
    form_data: OAuth2PasswordRequestForm = Depends(), 
    db: AsyncSession = Depends(get_db)
):
    from sqlalchemy import or_
    result = await db.execute(
        select(User).where(or_(User.username == form_data.username, User.phone == form_data.username, User.email == form_data.username))
    )
    user = result.scalars().first()
    
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    
    # Also set as HTTP-only cookie for the frontend
    response.set_cookie(
        key="access_token",
        value=f"Bearer {access_token}",
        httponly=True,
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        expires=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        samesite="lax",
        secure=False # Set to True in production with HTTPS
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/logout")
async def logout(response: Response):
    response.delete_cookie(key="access_token")
    return {"msg": "Logged out successfully"}
