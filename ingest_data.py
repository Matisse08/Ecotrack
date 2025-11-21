import requests
from datetime import datetime
from sqlalchemy.orm import Session
from app.database import SessionLocal, engine
from app import models

# Initialisation de la BDD (crée les tables si elles n'existent pas encore)
models.Base.metadata.create_all(bind=engine)

# DOCUMENTATION DES SOURCES (Livrable PDF)

# Source 1 : Open-Meteo
# - URL : https://api.open-meteo.com/v1/forecast
# - Type : Météo (Température)
# - Format : JSON
# - Fréquence : Horaire (Historique 7 jours)
# - Limitation : Pas de clé API requise, mais limite de requêtes par minute.

# Source 2 : ODRÉ (Open Data Réseaux Énergies - RTE)
# - URL : https://odre.opendatasoft.com/api/records/1.0/search/
# - Dataset : eco2mix-regional-tr
# - Type : Consommation Énergétique (MW)
# - Format : JSON (OpenDataSoft)
# - Fréquence : Temps réel (toutes les 15-30 min)
# - Limitation : API publique, nécessite un filtrage précis par région.


def get_or_create_zone(db: Session, name: str):
    """Récupère une zone par son nom ou la crée si elle n'existe pas."""
    zone = db.query(models.Zone).filter(models.Zone.name == name).first()
    if not zone:
        print(f"ℹ️ Création de la zone : {name}")
        # Code postal fixe pour l'exemple
        zone = models.Zone(name=name, postal_code="75000", country="France")
        db.add(zone)
        db.commit()
        db.refresh(zone)
    return zone

def ingest_weather_data(db: Session, zone_id: int, lat: float, lon: float):
    """
    SOURCE 1: Open-Meteo
    Récupère l'historique température sur 7 jours.
    """
    print("☁️ Récupération Météo (Source: Open-Meteo)...")
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat,
        "longitude": lon,
        "hourly": "temperature_2m",
        "past_days": 7
    }
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        
        hourly = data.get("hourly", {})
        times = hourly.get("time", [])
        values = hourly.get("temperature_2m", [])
        
        count = 0
        for t_str, val in zip(times, values):
            if val is None: continue
            
            # Format OpenMeteo : "2023-11-21T00:00"
            t_obj = datetime.fromisoformat(t_str)
            
            # Vérification doublon pour ne pas insérer deux fois la même donnée
            exists = db.query(models.Indicator).filter(
                models.Indicator.zone_id == zone_id,
                models.Indicator.type == "temperature",
                models.Indicator.timestamp == t_obj
            ).first()
            
            if not exists:
                indicator = models.Indicator(
                    type="temperature",
                    value=val,
                    unit="°C",
                    timestamp=t_obj,
                    zone_id=zone_id
                )
                db.add(indicator)
                count += 1
        
        db.commit()
        print(f"Succès Météo : {count} relevés ajoutés.")
        
    except Exception as e:
        print(f"Erreur Météo : {e}")

def ingest_energy_data(db: Session, zone_id: int):
    """
    SOURCE 2: ODRÉ (Eco2Mix Régional)
    Récupère la consommation électrique en temps réel pour l'Île-de-France.
    """
    print("⚡ Récupération Énergie (Source: ODRÉ / RTE)...")
    url = "https://odre.opendatasoft.com/api/records/1.0/search/"
    
    # On filtre sur "Île-de-France" pour correspondre à notre zone Paris
    params = {
        "dataset": "eco2mix-regional-tr",
        "q": "",
        "rows": 50,  # On récupère les 50 derniers points
        "sort": "-date_heure",
        "refine.libelle_region": "Île-de-France"
    }
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        records = data.get("records", [])
        
        count = 0
        for record in records:
            fields = record.get("fields", {})
            consommation = fields.get("consommation") # En MW
            date_str = fields.get("date_heure") # Format ISO 8601
            
            if consommation is None or date_str is None:
                continue
                
            # Conversion date (Gère le format ISO complet avec timezone)
            try:
                t_obj = datetime.fromisoformat(date_str)
            except ValueError:
                continue

            # Vérification doublon
            exists = db.query(models.Indicator).filter(
                models.Indicator.zone_id == zone_id,
                models.Indicator.type == "electricity_consumption",
                models.Indicator.timestamp == t_obj
            ).first()

            if not exists:
                indicator = models.Indicator(
                    type="electricity_consumption",
                    value=consommation,
                    unit="MW",
                    timestamp=t_obj,
                    zone_id=zone_id
                )
                db.add(indicator)
                count += 1
        
        db.commit()
        print(f"Succès Énergie : {count} relevés ajoutés.")

    except Exception as e:
        print(f"Erreur Énergie : {e}")

def main():
    db = SessionLocal()
    try:
        # 1. On définit Paris (Latitude: 48.8566, Longitude: 2.3522)
        paris = get_or_create_zone(db, "Paris")
        
        # 2. Source 1 : Météo (Nécessite Lat/Lon)
        ingest_weather_data(db, paris.id, 48.8566, 2.3522)
        
        # 3. Source 2 : Énergie (Nécessite juste l'ID de la zone pour lier les données)
        ingest_energy_data(db, paris.id)
        
    finally:
        db.close()

if __name__ == "__main__":
    main()