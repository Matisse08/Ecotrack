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
        from_attributes = True # Remplace orm_mode dans Pydantic V2

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None