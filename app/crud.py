from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional, List
from datetime import datetime
from . import models, schemas, utils

# --- USERS ---

def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()

def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()

def create_user(db: Session, user: schemas.UserCreate):
    hashed_password = utils.get_password_hash(user.password)
    # MODIFICATION ICI : on utilise user.role au lieu de "user" en dur
    db_user = models.User(
        email=user.email, 
        password_hash=hashed_password,
        role=user.role  
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def update_user(db: Session, db_user: models.User, updates: schemas.UserUpdate):
    if updates.role is not None:
        db_user.role = updates.role
    if updates.is_active is not None:
        db_user.is_active = updates.is_active
    db.commit()
    db.refresh(db_user)
    return db_user

def delete_user(db: Session, db_user: models.User):
    db.delete(db_user)
    db.commit()

# --- ZONES ---

def get_zones(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Zone).offset(skip).limit(limit).all()

def create_zone(db: Session, zone: schemas.ZoneCreate):
    db_zone = models.Zone(
        name=zone.name,
        postal_code=zone.postal_code,
        country=zone.country
    )
    db.add(db_zone)
    db.commit()
    db.refresh(db_zone)
    return db_zone

def update_zone(db: Session, zone_id: int, updates: schemas.ZoneUpdate):
    db_zone = db.query(models.Zone).filter(models.Zone.id == zone_id).first()
    if db_zone:
        if updates.name is not None: db_zone.name = updates.name
        if updates.postal_code is not None: db_zone.postal_code = updates.postal_code
        if updates.country is not None: db_zone.country = updates.country
        db.commit()
        db.refresh(db_zone)
    return db_zone

def delete_zone(db: Session, zone_id: int):
    db_zone = db.query(models.Zone).filter(models.Zone.id == zone_id).first()
    if db_zone:
        db.delete(db_zone)
        db.commit()
        return True
    return False

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
    avg_value = db.query(func.avg(models.Indicator.value))\
        .filter(models.Indicator.zone_id == zone_id, models.Indicator.type == type)\
        .scalar()

    if avg_value is None:
        return None

    zone = db.query(models.Zone).filter(models.Zone.id == zone_id).first()
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

def update_indicator(db: Session, indicator_id: int, updates: schemas.IndicatorUpdate):
    db_indicator = db.query(models.Indicator).filter(models.Indicator.id == indicator_id).first()
    if not db_indicator:
        return None
    
    if updates.type is not None: db_indicator.type = updates.type
    if updates.value is not None: db_indicator.value = updates.value
    if updates.unit is not None: db_indicator.unit = updates.unit
    if updates.zone_id is not None: db_indicator.zone_id = updates.zone_id
    
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