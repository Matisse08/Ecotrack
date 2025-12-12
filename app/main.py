from fastapi import FastAPI
from . import models, database
# Ajout de users et zones dans les imports
from .routers import auth, indicators, dashboard, users, zones 

# Création des tables dans la BDD au démarrage
models.Base.metadata.create_all(bind=database.engine)

app = FastAPI(title="EcoTrack API")

# Inclusion des routeurs
app.include_router(auth.router)
app.include_router(users.router)       # <-- Nouveau routeur
app.include_router(zones.router)       # <-- Nouveau routeur
app.include_router(indicators.router)
app.include_router(dashboard.router)

@app.get("/")
def read_root():
    return {"message": "Welcome to EcoTrack API. Go to /dashboard to see the UI."}
