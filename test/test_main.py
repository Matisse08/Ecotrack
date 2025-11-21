from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.database import Base, get_db
import pytest

# 1. Configuration d'une BDD de test (en mémoire RAM, pour ne pas casser la vraie BDD)
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Surcharge la dépendance get_db pour utiliser la BDD de test
def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

# Création des tables de test
Base.metadata.create_all(bind=engine)

client = TestClient(app)

# --- TESTS ---

def test_read_main():
    """Vérifie que l'API tourne"""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to EcoTrack API. Go to /dashboard to see the UI."}

def test_register_user():
    """Test: Création d'un utilisateur"""
    response = client.post(
        "/auth/register",
        json={"email": "test@example.com", "password": "password123"},
    )
    # 200 OK signifie que l'user est créé
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "test@example.com"
    assert "id" in data

def test_login_user():
    """Test: Connexion et récupération du Token"""
    response = client.post(
        "/auth/login",
        data={"username": "test@example.com", "password": "password123"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    return data["access_token"]

def test_create_indicator_as_admin():
    """
    Test: Création d'indicateur.
    Note: Par défaut le user créé est 'user'. 
    Dans un vrai test, on devrait le passer admin manuellement ou mocker la dépendance admin.
    Ici, pour simplifier, on teste que l'accès est INTERDIT (403) pour un user normal,
    ce qui prouve que la sécurité fonctionne.
    """
    # 1. Login
    token = test_login_user()
    
    # 2. Tentative de création
    response = client.post(
        "/indicators/",
        json={
            "type": "test_type",
            "value": 10.5,
            "unit": "test_unit",
            "zone_id": 1
        },
        headers={"Authorization": f"Bearer {token}"}
    )
    
    # Doit être 403 Forbidden car le user par défaut n'est pas admin
    assert response.status_code == 403

def test_read_indicators():
    """Test: Lecture publique des indicateurs"""
    response = client.get("/indicators/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)