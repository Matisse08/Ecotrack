from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# URL de la base de données SQLite (fichier local ecotrack.db)
SQLALCHEMY_DATABASE_URL = "sqlite:///./ecotrack.db"

# Création du moteur de base de données
# check_same_thread=False est nécessaire uniquement pour SQLite avec FastAPI
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

# SessionLocal : fabrique de sessions pour chaque requête
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base : classe parente pour tous nos modèles
Base = declarative_base()

# Dépendance pour récupérer la DB dans les routes
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()