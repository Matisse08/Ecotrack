from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from .. import database, models, schemas, crud, deps

router = APIRouter(
    prefix="/zones",
    tags=["Zones"]
)

# --- Lecture (Accessible à tous) ---
# CORRECTION ICI : schemas.Zone au lieu de schemas.ZoneOut
@router.get("/", response_model=List[schemas.Zone])
def read_zones(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(database.get_db)
):
    """Récupère la liste des zones géographiques."""
    return crud.get_zones(db, skip=skip, limit=limit)

# --- Création (Admin seulement) ---
@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.Zone)
def create_zone(
    zone: schemas.ZoneCreate, 
    db: Session = Depends(database.get_db),
    # Sécurité : Seul un admin peut créer une zone (pour éviter le spam)
    current_user: models.User = Depends(deps.get_admin_user)
):
    """Crée une nouvelle zone (Admin seulement)."""
    return crud.create_zone(db=db, zone=zone)

# --- Mise à jour (Admin seulement) ---
@router.put("/{zone_id}", response_model=schemas.Zone)
def update_zone(
    zone_id: int, 
    zone_update: schemas.ZoneUpdate, 
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(deps.get_admin_user)
):
    """Met à jour une zone (Admin seulement)."""
    updated_zone = crud.update_zone(db, zone_id=zone_id, updates=zone_update)
    if not updated_zone:
        raise HTTPException(status_code=404, detail="Zone introuvable")
    return updated_zone

# --- Suppression (Admin seulement) ---
@router.delete("/{zone_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_zone(
    zone_id: int, 
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(deps.get_admin_user)
):
    """Supprime une zone (Admin seulement)."""
    success = crud.delete_zone(db, zone_id=zone_id)
    if not success:
        raise HTTPException(status_code=404, detail="Zone introuvable")
    return None

