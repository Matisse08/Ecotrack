from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel

# Imports internes
from .. import database, models, schemas, crud, deps

router = APIRouter(
    prefix="/users",
    tags=["Users Management"]
)

# --- MODELES SPECIFIQUES ---
class RoleChangeRequest(BaseModel):
    target_role: str

# --- 1. ROUTES UTILISATEUR CONNECTÉ (Nouveau) ---

@router.get("/me", response_model=schemas.UserOut)
def read_user_me(
    current_user: models.User = Depends(deps.get_current_user)
):
    """Renvoie les infos de l'utilisateur connecté (dont son rôle)."""
    return current_user

@router.post("/me/switch-role")
def switch_role(
    request: RoleChangeRequest,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(deps.get_current_user)
):
    """
    Permet de changer de rôle dynamiquement.
    Autorisé SEULEMENT si :
    - L'utilisateur est Admin
    - OU l'utilisateur est "matisse@test.com" (Backdoor dev)
    """
    is_super_dev = (current_user.email == "matisse@test.com")
    is_admin = (current_user.role == "admin")

    # Sécurité : Si pas admin et pas le compte dev, on refuse
    if not is_super_dev and not is_admin:
        raise HTTPException(
            status_code=403, 
            detail="Action non autorisée. Vous n'êtes pas administrateur."
        )

    # --- CORRECTION DU BUG ---
    # On récupère l'utilisateur dans la session actuelle (db) via son ID
    # pour éviter l'erreur "not persistent within this Session"
    user_in_db = db.query(models.User).filter(models.User.id == current_user.id).first()
    
    if not user_in_db:
        raise HTTPException(status_code=404, detail="Utilisateur introuvable.")

    # Mise à jour du rôle sur l'objet attaché à la session
    user_in_db.role = request.target_role
    db.commit()
    db.refresh(user_in_db)
    
    return {
        "message": f"Rôle changé en {request.target_role}", 
        "new_role": user_in_db.role
    }

@router.post("/me/request-admin")
def request_admin_access(
    current_user: models.User = Depends(deps.get_current_user)
):
    """Permet à un utilisateur lambda de demander les droits."""
    # Simulation d'envoi de demande
    return {"message": "Votre demande a été envoyée aux administrateurs."}


# --- 2. ROUTES CRUD ADMIN (Classique) ---

@router.get("/", response_model=List[schemas.UserOut])
def read_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(deps.get_admin_user)
):
    """Récupère la liste de tous les utilisateurs (Admin seulement)."""
    return crud.get_users(db, skip=skip, limit=limit)

@router.put("/{user_id}", response_model=schemas.UserOut)
def update_user(
    user_id: int,
    user_update: schemas.UserUpdate,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(deps.get_admin_user)
):
    """Met à jour le rôle ou le statut d'un utilisateur (Admin seulement)."""
    db_user = crud.get_user(db, user_id=user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return crud.update_user(db, db_user=db_user, updates=user_update)

@router.delete("/{user_id}")
def delete_user(
    user_id: int,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(deps.get_admin_user)
):
    """Supprime un utilisateur (Admin seulement)."""
    db_user = crud.get_user(db, user_id=user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    crud.delete_user(db, db_user)
    return {"detail": "User deleted successfully"}

# --- 3. CREATION COMPTE (Inscription) ---
@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.UserOut)
def create_user(user: schemas.UserCreate, db: Session = Depends(database.get_db)):
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return crud.create_user(db=db, user=user)


