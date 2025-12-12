import requests
import random
import time

# --- CONFIGURATION ---
API_URL = "http://127.0.0.1:8000"

# Utilise ton compte Admin (matisse@test.com / Miam)
EMAIL = "matisse@test.com"
PASSWORD = "Miam"

def get_token():
    """Récupère le token JWT"""
    print(f"🔑 Connexion en tant que {EMAIL}...")
    try:
        response = requests.post(
            f"{API_URL}/auth/login", 
            data={"username": EMAIL, "password": PASSWORD}
        )
        if response.status_code == 200:
            return response.json()["access_token"]
        else:
            print(f"❌ Erreur Auth : {response.status_code} - {response.text}")
            print("👉 Vérifie que l'utilisateur existe et qu'il est ADMIN.")
            exit()
    except Exception as e:
        print(f"❌ Impossible de joindre l'API ({API_URL}). Vérifie qu'elle tourne !")
        exit()

def ensure_zones_exist(token):
    """Vérifie et crée les zones Lyon et Marseille si besoin"""
    headers = {"Authorization": f"Bearer {token}"}
    
    # Liste des zones à avoir
    target_zones = [
        {"name": "Paris", "postal_code": "75000", "country": "France"},
        {"name": "Lyon", "postal_code": "69000", "country": "France"},
        {"name": "Marseille", "postal_code": "13000", "country": "France"}
    ]
    
    print("🌍 Vérification des zones...")
    
    valid_ids = []

    for z_data in target_zones:
        # On essaie de créer la zone
        # Si elle existe déjà (doublon), l'API renverra probablement une erreur ou on peut lister avant.
        # Pour faire simple : on crée, si erreur on suppose qu'elle existe.
        
        # 1. Création
        resp = requests.post(f"{API_URL}/zones/", json=z_data, headers=headers)
        
        if resp.status_code in [200, 201]:
            created_zone = resp.json()
            print(f"   ✅ Zone créée : {created_zone['name']} (ID: {created_zone['id']})")
            valid_ids.append(created_zone['id'])
        else:
            # 2. Si échec, on suppose qu'elle existe et on essaie de récupérer son ID
            # (Note: idéalement on ferait un GET /zones/ mais on fait simple ici)
            # On triche un peu : on suppose que Paris=1, Lyon=2, Marseille=3 si l'ordre est respecté
            pass

    # Si la création échoue car "déjà existant", on récupère la liste complète pour avoir les vrais IDs
    resp_all = requests.get(f"{API_URL}/zones/", headers=headers)
    if resp_all.status_code == 200:
        all_zones = resp_all.json()
        print(f"   📋 Zones disponibles en base : {[z['name'] + ' (' + str(z['id']) + ')' for z in all_zones]}")
        return [z['id'] for z in all_zones]
    
    return [1, 2, 3] # Fallback

def generate():
    token = get_token()
    headers = {"Authorization": f"Bearer {token}"}
    
    # 1. S'assurer que les zones existent
    available_zone_ids = ensure_zones_exist(token)
    
    if not available_zone_ids:
        print("❌ Aucune zone disponible. Impossible de générer des données.")
        return

    # Types de données à simuler
    indicators = [
        {"type": "temperature", "unit": "°C", "min": 15, "max": 30},
        {"type": "electricity_consumption", "unit": "MW", "min": 200, "max": 800},
        {"type": "air_quality_pm25", "unit": "µg/m³", "min": 5, "max": 60}
    ]

    print("\n🚀 Génération des mesures...")

    # On crée 60 mesures réparties sur les zones disponibles
    for i in range(60):
        # Choisir une zone existante au hasard
        zone_id = random.choice(available_zone_ids)
        ind = random.choice(indicators)
        
        valeur = round(random.uniform(ind["min"], ind["max"]), 2)
        
        payload = {
            "zone_id": zone_id,
            "type": ind["type"],
            "value": valeur,
            "unit": ind["unit"]
        }
        
        try:
            resp = requests.post(f"{API_URL}/indicators/", json=payload, headers=headers)
            if resp.status_code in [200, 201]:
                print(f"   ✅ Ajout [Zone {zone_id}] : {valeur} {ind['unit']}")
            else:
                print(f"   ⚠️ Erreur API : {resp.status_code} - {resp.text}")
        except Exception as e:
            print(f"Erreur requête : {e}")

    print("\n✨ Terminé ! Retourne sur ton Dashboard et clique sur 'Actualiser les données'.")

if __name__ == "__main__":
    generate()


