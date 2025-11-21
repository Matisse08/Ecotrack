EcoTrack API 🌱

EcoTrack est une application backend complète développée avec FastAPI. Elle permet de collecter, stocker, analyser et visualiser des indicateurs environnementaux (Météo et Consommation Énergétique) pour la zone de Paris / Île-de-France.

Ce projet a été réalisé dans le cadre du cours de développement API.

🚀 Fonctionnalités Clés

API RESTful performante avec FastAPI.

Base de Données SQLite gérée via l'ORM SQLAlchemy.

Authentification Sécurisée par tokens JWT (JSON Web Tokens).

Gestion des Rôles : Distinction entre user (lecture seule) et admin (écriture/suppression).

Ingestion Automatisée (ETL) : Script Python récupérant des données réelles depuis des APIs externes.

Dashboard Interactif : Interface web (HTML/JS/Chart.js) pour visualiser les données sous forme de courbes et tableaux.

📂 Structure du Projet

ecotrack/
├── ingest_data.py          # Script ETL (Extraction & Chargement des données externes)
├── ecotrack.db             # Base de données SQLite (générée automatiquement)
├── requirements.txt        # Liste des dépendances Python
├── app/
│   ├── main.py             # Point d'entrée de l'application
│   ├── models.py           # Modèles de Base de Données (User, Zone, Indicator)
│   ├── schemas.py          # Schémas de validation Pydantic
│   ├── crud.py             # Logique métier (Lecture/Écriture BDD)
│   ├── utils.py            # Utilitaires de sécurité (Hashage, JWT)
│   └── routers/
│       ├── auth.py         # Routes d'inscription et connexion
│       ├── indicators.py   # Routes API pour les données (Filtres, Stats)
│       └── dashboard.py    # Route servant l'interface graphique


📊 Sources de Données Externes

Conformément au cahier des charges, ce projet intègre deux sources de données distinctes et fiables :

Source

Type de Donnée

Format

Fréquence

Description

1. Open-Meteo

Météo (Température)

JSON

Horaire

Historique des températures sur les 7 derniers jours pour Paris.

2. ODRÉ (RTE)

Énergie (Consommation)

JSON

Temps réel (15-30 min)

Données du Réseau de Transport d'Électricité (RTE) filtrées sur la région Île-de-France.

🛠️ Installation et Démarrage

1. Prérequis

Python 3.10 ou supérieur.

Git.

2. Installation

Clonez le projet et installez les dépendances :

# Cloner le dépôt
git clone [https://github.com/VOTRE_NOM/ecotrack.git](https://github.com/VOTRE_NOM/ecotrack.git)
cd ecotrack

# Créer un environnement virtuel
python -m venv venv

# Activer l'environnement (Windows)
.\venv\Scripts\Activate
# OU Activer l'environnement (Mac/Linux)
source venv/bin/activate

# Installer les librairies
pip install -r requirements.txt


3. Initialisation des Données (ETL)

Lancez le script d'ingestion pour créer la base de données et la remplir avec les données réelles :

python ingest_data.py


Vous devriez voir des messages de succès indiquant l'ajout des relevés Météo et Énergie.

4. Lancer le Serveur

uvicorn app.main:app --reload


Le serveur est accessible sur : http://127.0.0.1:8000

🖥️ Utilisation

Interface Graphique (Dashboard)

Accédez à http://127.0.0.1:8000/dashboard.

Connectez-vous (ou créez un compte via l'API).

Visualisez les courbes de température et de consommation.

Filtrez par type de donnée.

Documentation API (Swagger UI)

Accédez à http://127.0.0.1:8000/docs.

Testez tous les endpoints directement depuis le navigateur.

Utilisez /auth/register pour créer un utilisateur.

Utilisez le bouton "Authorize" (cadenas vert) pour vous authentifier avec le token reçu.

Gestion des Rôles

User : Peut consulter le Dashboard, lister les indicateurs et voir les statistiques.

Admin : Peut ajouter manuellement des données et supprimer des indicateurs erronés via le Dashboard ou l'API.

Note : Pour passer un utilisateur en Admin, modifiez la colonne role directement en base de données pour ce TP.

Auteur

Projet réalisé par Matisse Marchand.