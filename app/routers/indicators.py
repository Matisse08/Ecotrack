from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from .. import database, schemas, crud, models, deps

router = APIRouter(
    prefix="/indicators",
    tags=["Indicators"]
)

@router.get("/", response_model=List[schemas.IndicatorOut])
def read_indicators(
    skip: int = 0,
    limit: int = 100,
    zone_id: Optional[int] = None,
    type: Optional[str] = None,
    from_date: Optional[datetime] = None,
    to_date: Optional[datetime] = None,
    db: Session = Depends(database.get_db)
):
    """
    Récupère la liste des indicateurs avec filtres optionnels.
    """
    indicators = crud.get_indicators(
        db, skip=skip, limit=limit, 
        zone_id=zone_id, type=type, 
        from_date=from_date, to_date=to_date
    )
    return indicators

@router.get("/stats", response_model=schemas.StatResult)
def read_indicator_stats(
    zone_id: int,
    type: str,
    db: Session = Depends(database.get_db)
):
    """
    Retourne la moyenne d'un type d'indicateur pour une zone donnée.
    """
    stats = crud.get_indicator_stats(db, zone_id=zone_id, type=type)
    if not stats:
        raise HTTPException(status_code=404, detail="No data found for this zone and type")
    return stats

@router.post("/", response_model=schemas.IndicatorOut)
def create_indicator(
    indicator: schemas.IndicatorCreate,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(deps.get_admin_user)
):
    """
    Crée un nouvel indicateur (Admin seulement).
    """
    # Vérification existence zone (optionnel mais recommandé)
    zone = db.query(models.Zone).filter(models.Zone.id == indicator.zone_id).first()
    if not zone:
        raise HTTPException(status_code=404, detail="Zone not found")
        
    return crud.create_indicator(db=db, indicator=indicator)

@router.delete("/{indicator_id}")
def delete_indicator(
    indicator_id: int,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(deps.get_admin_user)
):
    """
    Supprime un indicateur par son ID (Admin seulement).
    """
    success = crud.delete_indicator(db, indicator_id)
    if not success:
        raise HTTPException(status_code=404, detail="Indicator not found")
    return {"detail": "Indicator deleted successfully"}