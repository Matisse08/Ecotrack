from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from .. import database, schemas, crud, deps, models

router = APIRouter(
    prefix="/zones", 
    tags=["Zones"]
)

@router.get("/", response_model=List[schemas.ZoneOut])
def read_zones(skip: int = 0, limit: int = 100, db: Session = Depends(database.get_db)):
    return crud.get_zones(db, skip=skip, limit=limit)

@router.post("/", response_model=schemas.ZoneOut)
def create_zone(
    zone: schemas.ZoneCreate, 
    db: Session = Depends(database.get_db), 
    current_user: models.User = Depends(deps.get_admin_user)
):
    """Créer une nouvelle zone (Admin seulement)."""
    # Vérifier unicité du nom si nécessaire (optionnel)
    return crud.create_zone(db, zone)

@router.put("/{zone_id}", response_model=schemas.ZoneOut)
def update_zone(
    zone_id: int, 
    zone: schemas.ZoneUpdate, 
    db: Session = Depends(database.get_db), 
    current_user: models.User = Depends(deps.get_admin_user)
):
    updated = crud.update_zone(db, zone_id, zone)
    if not updated:
        raise HTTPException(status_code=404, detail="Zone not found")
    return updated

@router.delete("/{zone_id}")
def delete_zone(
    zone_id: int, 
    db: Session = Depends(database.get_db), 
    current_user: models.User = Depends(deps.get_admin_user)
):
    if not crud.delete_zone(db, zone_id):
        raise HTTPException(status_code=404, detail="Zone not found")
    return {"detail": "Zone deleted"}
