from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime

# --- SCHÉMAS UTILISATEURS & AUTH ---

class UserBase(BaseModel):
    email: EmailStr

class UserCreate(UserBase):
    password: str

class UserOut(UserBase):
    id: int
    role: str
    is_active: bool

    class Config:
        from_attributes = True 

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None

# --- SCHÉMAS INDICATEURS & STATS ---

class IndicatorBase(BaseModel):
    type: str
    value: float
    unit: str
    zone_id: int
    timestamp: Optional[datetime] = None

class IndicatorCreate(IndicatorBase):
    pass

class IndicatorOut(IndicatorBase):
    id: int
    timestamp: datetime

    class Config:
        from_attributes = True

class StatResult(BaseModel):
    zone: str
    type: str
    average: float
    unit: str

class UserUpdate(BaseModel):
    role: Optional[str] = None
    is_active: Optional[bool] = None
