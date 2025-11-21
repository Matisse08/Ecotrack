from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from .. import database, models, schemas, crud, deps

router = APIRouter(
    prefix="/users",
    tags=["Users Management"]
)

# --- 1. Liste paginée des utilisateurs (Admin) ---
@router.get("/", response_model=List[schemas.UserOut])
def read_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(deps.get_admin_user)
):
    """
    Récupère la liste de tous les utilisateurs (Admin seulement).
    Supporte la pagination (skip, limit).
    """
    users = crud.get_users(db, skip=skip, limit=limit)
    return users

# --- 2. Modification d'un utilisateur (Rôle / Activation) ---
@router.put("/{user_id}", response_model=schemas.UserOut)
def update_user(
    user_id: int,
    user_update: schemas.UserUpdate,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(deps.get_admin_user)
):
    """
    Met à jour le rôle ou le statut d'activation d'un utilisateur.
    (Admin seulement).
    """
    db_user = crud.get_user(db, user_id=user_id)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    updated_user = crud.update_user(db, db_user=db_user, updates=user_update)
    return updated_user

# --- 3. Suppression (Optionnel mais recommandé pour CRUD complet) ---
@router.delete("/{user_id}")
def delete_user(
    user_id: int,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(deps.get_admin_user)
):
    """
    Supprime définitivement un utilisateur.
    """
    db_user = crud.get_user(db, user_id=user_id)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    crud.delete_user(db, db_user)
    return {"detail": "User deleted successfully"}
