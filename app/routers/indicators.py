from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from .. import database, models, schemas, crud, deps

router = APIRouter(
    prefix="/indicators",
    tags=["Indicators"]
)

# --- Lecture (Tout le monde connecté) ---
@router.get("/", response_model=List[schemas.Indicator]) # CORRECTION : Indicator au lieu de IndicatorOut
def read_indicators(
    skip: int = 0,
    limit: int = 100,
    zone_id: Optional[int] = None,
    type: Optional[str] = None,
    db: Session = Depends(database.get_db),
    # Optionnel : décommente si tu veux que seuls les connectés puissent lire
    # current_user: models.User = Depends(deps.get_current_user)
):
    """
    Récupère la liste des indicateurs.
    Permet de filtrer par zone ou par type.
    """
    return crud.get_indicators(db, skip=skip, limit=limit, zone_id=zone_id, type=type)

# --- Création (Utilisateur connecté) ---
@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.Indicator)
def create_indicator(
    indicator: schemas.IndicatorCreate,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(deps.get_current_user)
):
    """Crée un nouveau relevé (Nécessite d'être connecté)."""
    # Vérification basique que la zone existe (optionnel, géré par FK)
    return crud.create_indicator(db=db, indicator=indicator)

# --- Suppression (Admin seulement) ---
@router.delete("/{indicator_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_indicator(
    indicator_id: int,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(deps.get_admin_user)
):
    """Supprime un relevé (Admin seulement)."""
    success = crud.delete_indicator(db, indicator_id)
    if not success:
        raise HTTPException(status_code=404, detail="Indicator not found")
    return None

