from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel, EmailStr
from app.core.database import get_db
from app.core.security import verify_password, get_password_hash, create_access_token, create_refresh_token
from app.models.user import User
from datetime import timedelta

router = APIRouter()

class UserRegister(BaseModel):
    email: EmailStr
    username: str
    password: str
    full_name: str | None = None

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

@router.post("/register", response_model=Token, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserRegister, db: AsyncSession = Depends(get_db)):
    # Check if user exists
    result = await db.execute(select(User).where(User.email == user_data.email))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Email already registered")
    
    result = await db.execute(select(User).where(User.username == user_data.username))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Username already taken")
    
    # Create user
    user = User(
        email=user_data.email,
        username=user_data.username,
        hashed_password=get_password_hash(user_data.password),
        full_name=user_data.full_name
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    
    # Create tokens
    access_token = create_access_token({"sub": str(user.id), "email": user.email, "username": user.username})
    refresh_token = create_refresh_token({"sub": str(user.id)})
    
    return {"access_token": access_token, "refresh_token": refresh_token}

@router.post("/login", response_model=Token)
async def login(user_data: UserLogin, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == user_data.email))
    user = result.scalar_one_or_none()
    
    if not user or not verify_password(user_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Incorrect email or password")
    
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    
    access_token = create_access_token({"sub": str(user.id), "email": user.email, "username": user.username})
    refresh_token = create_refresh_token({"sub": str(user.id)})
    
    return {"access_token": access_token, "refresh_token": refresh_token}

@router.post("/oauth/google")
async def google_oauth(token: str, db: AsyncSession = Depends(get_db)):
    # Implement Google OAuth verification
    # This is a placeholder - implement with authlib
    raise HTTPException(status_code=501, detail="Google OAuth not implemented yet")

@router.post("/oauth/github")
async def github_oauth(code: str, db: AsyncSession = Depends(get_db)):
    # Implement GitHub OAuth verification
    # This is a placeholder - implement with authlib
    raise HTTPException(status_code=501, detail="GitHub OAuth not implemented yet")
