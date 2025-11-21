from fastapi import FastAPI
from . import models, database
from .routers import auth

# Création des tables dans la BDD au démarrage
models.Base.metadata.create_all(bind=database.engine)

app = FastAPI(title="EcoTrack API")

# Inclusion des routeurs
app.include_router(auth.router)

@app.get("/")
def read_root():
    return {"message": "Welcome to EcoTrack API"}