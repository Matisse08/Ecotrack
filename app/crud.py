from sqlalchemy.orm import Session
from . import models, schemas, utils

def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

def create_user(db: Session, user: schemas.UserCreate):
    hashed_password = utils.get_password_hash(user.password)
    # Par défaut, le premier user n'est pas admin, on le force ici à "user"
    db_user = models.User(
        email=user.email, 
        password_hash=hashed_password,
        role="user" 
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user