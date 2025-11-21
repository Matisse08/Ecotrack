from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

# --- SCHÉMAS UTILISATEURS & AUTH ---

class UserBase(BaseModel):
    email: EmailStr

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    role: Optional[str] = None
    is_active: Optional[bool] = None

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

# --- SCHÉMAS ZONES ---

class ZoneBase(BaseModel):
    name: str
    postal_code: Optional[str] = None
    country: str = "France"

class ZoneCreate(ZoneBase):
    pass

class ZoneUpdate(BaseModel):
    name: Optional[str] = None
    postal_code: Optional[str] = None
    country: Optional[str] = None

class ZoneOut(ZoneBase):
    id: int
    class Config:
        from_attributes = True

# --- SCHÉMAS INDICATEURS & STATS ---

class IndicatorBase(BaseModel):
    type: str
    value: float
    unit: str
    zone_id: int
    timestamp: Optional[datetime] = None

class IndicatorCreate(IndicatorBase):
    pass

class IndicatorUpdate(BaseModel):
    type: Optional[str] = None
    value: Optional[float] = None
    unit: Optional[str] = None
    zone_id: Optional[int] = None

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
