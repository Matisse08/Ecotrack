from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional, List
from datetime import datetime
from . import models, schemas, utils

# --- USERS ---

def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

def create_user(db: Session, user: schemas.UserCreate):
    hashed_password = utils.get_password_hash(user.password)
    db_user = models.User(
        email=user.email, 
        password_hash=hashed_password,
        role="user" 
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

# --- INDICATORS ---

def get_indicators(
    db: Session, 
    skip: int = 0, 
    limit: int = 100, 
    zone_id: Optional[int] = None, 
    type: Optional[str] = None,
    from_date: Optional[datetime] = None,
    to_date: Optional[datetime] = None
):
    query = db.query(models.Indicator)
    
    if zone_id:
        query = query.filter(models.Indicator.zone_id == zone_id)
    if type:
        query = query.filter(models.Indicator.type == type)
    if from_date:
        query = query.filter(models.Indicator.timestamp >= from_date)
    if to_date:
        query = query.filter(models.Indicator.timestamp <= to_date)
        
    return query.offset(skip).limit(limit).all()

def get_indicator_stats(db: Session, zone_id: int, type: str):
    # Calcul de la moyenne
    avg_value = db.query(func.avg(models.Indicator.value))\
        .filter(models.Indicator.zone_id == zone_id, models.Indicator.type == type)\
        .scalar()

    if avg_value is None:
        return None

    # Récupération des métadonnées pour la réponse (Nom de zone, Unité)
    zone = db.query(models.Zone).filter(models.Zone.id == zone_id).first()
    # On prend l'unité du premier enregistrement correspondant
    unit_entry = db.query(models.Indicator.unit)\
        .filter(models.Indicator.zone_id == zone_id, models.Indicator.type == type)\
        .first()
    
    return schemas.StatResult(
        zone=zone.name if zone else f"Zone {zone_id}",
        type=type,
        average=avg_value,
        unit=unit_entry[0] if unit_entry else ""
    )

def create_indicator(db: Session, indicator: schemas.IndicatorCreate):
    db_indicator = models.Indicator(
        type=indicator.type,
        value=indicator.value,
        unit=indicator.unit,
        zone_id=indicator.zone_id,
        timestamp=indicator.timestamp or datetime.utcnow()
    )
    db.add(db_indicator)
    db.commit()
    db.refresh(db_indicator)
    return db_indicator

def delete_indicator(db: Session, indicator_id: int):
    db_indicator = db.query(models.Indicator).filter(models.Indicator.id == indicator_id).first()
    if db_indicator:
        db.delete(db_indicator)
        db.commit()
        return True
    return False

class UserUpdate(BaseModel):
    role: Optional[str] = None
    is_active: Optional[bool] = None
