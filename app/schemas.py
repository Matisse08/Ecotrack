from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime

# --- TOKENS ---
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None

# --- USERS ---
class UserBase(BaseModel):
    email: EmailStr
    is_active: Optional[bool] = True

class UserCreate(UserBase):
    password: str
    # On ajoute le champ role, par défaut "user"
    role: str = "user" 

class UserUpdate(BaseModel):
    role: Optional[str] = None
    is_active: Optional[bool] = None

class UserOut(UserBase):
    id: int
    role: str
    
    class Config:
        from_attributes = True

class User(UserBase):
    id: int
    role: str
    items: List["Indicator"] = []

    class Config:
        from_attributes = True

# --- ZONES ---
class ZoneBase(BaseModel):
    name: str
    postal_code: str
    country: str

class ZoneCreate(ZoneBase):
    pass

class ZoneUpdate(BaseModel):
    name: Optional[str] = None
    postal_code: Optional[str] = None
    country: Optional[str] = None

class Zone(ZoneBase):
    id: int

    class Config:
        from_attributes = True

# --- INDICATORS ---
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

class Indicator(IndicatorBase):
    id: int
    timestamp: datetime

    class Config:
        from_attributes = True

class StatResult(BaseModel):
    zone: str
    type: str
    average: float
    unit: str