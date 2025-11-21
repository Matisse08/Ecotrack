from sqlalchemy import Column, Integer, String, Boolean, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    role = Column(String, default="user")  # "user" ou "admin"
    is_active = Column(Boolean, default=True)

class Zone(Base):
    __tablename__ = "zones"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    postal_code = Column(String, index=True)
    country = Column(String, default="France")

    # Une zone a plusieurs indicateurs
    indicators = relationship("Indicator", back_populates="zone")

class Indicator(Base):
    __tablename__ = "indicators"

    id = Column(Integer, primary_key=True, index=True)
    type = Column(String, index=True)  # ex: "air_quality", "temperature"
    value = Column(Float, nullable=False)
    unit = Column(String)              # ex: "µg/m³", "°C"
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    # Lien vers la zone
    zone_id = Column(Integer, ForeignKey("zones.id"))
    zone = relationship("Zone", back_populates="indicators")