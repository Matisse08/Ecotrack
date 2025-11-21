# Projet API - EcoTrack

Ce projet a été réalisé dans le cadre du cours de développement d'API. L'objectif est de concevoir une API RESTful complète avec FastAPI permettant d'agréger et d'analyser des indicateurs environnementaux locaux.

L'application respecte une architecture modulaire, intègre une base de données relationnelle via SQLAlchemy, une authentification sécurisée par JWT, et consomme des données externes réelles.

## Architecture et Choix Techniques

Le projet est structuré selon les bonnes pratiques d'ingénierie logicielle vues en cours :

* Langage : Python 3.10+
* Framework API : FastAPI
* Base de données : SQLite (pour la portabilité) avec SQLAlchemy (ORM)
* Validation : Pydantic
* Sécurité : Authentification OAuth2 avec Tokens JWT (JSON Web Tokens) et hachage des mots de passe (Bcrypt)
* Tests : Tests d'intégration via Pytest et TestClient

## Documentation des Données (Livrable)

Conformément au cahier des charges, l'application intègre deux sources de données externes distinctes. Le script d'ingestion (`ingest_data.py`) se charge de peupler la base de données initialement.

### Source 1 : Données Météorologiques
* Nom : Open-Meteo API
* URL : https://api.open-meteo.com/v1/forecast
* Type de donnée : Température à 2 mètres du sol.
* Format : JSON.
* Fréquence : Horaire (récupération de l'historique sur 7 jours glissants).
* Limitations et contraintes : L'API est gratuite pour un usage non commercial (< 10 000 requêtes/jour). Elle ne nécessite pas de clé API. Les données dépendent de la latitude/longitude fournie.

### Source 2 : Données Énergétiques
* Nom : ODRÉ (Open Data Réseaux Énergies - RTE)
* URL : https://odre.opendatasoft.com/api/records/1.0/search/
* Dataset : eco2mix-regional-tr (Consommation d'électricité en temps réel).
* Type de donnée : Consommation électrique globale (en MW).
* Format : JSON (Standard OpenDataSoft).
* Fréquence : Temps réel (mise à jour toutes les 15 à 30 minutes).
* Limitations et contraintes : API publique gouvernementale. Le filtrage s'effectue par région administrative ("Île-de-France") et non par coordonnées GPS précises.

## Installation et Configuration

### Clonage du dépôt
Récupérez les sources du projet sur votre machine locale.

### Configuration de l'environnement virtuel
Il est recommandé d'utiliser un environnement virtuel pour isoler les dépendances.

```bash
python -m venv venv
# Activation sous Windows :
venv\Scripts\activate
# Activation sous Mac/Linux :
source venv/bin/activate

Installation des dépendances
Bash

pip install -r requirements.txt
Initialisation de la Base de Données
Un script ETL (Extract, Transform, Load) a été développé pour initialiser la base de données avec des données réelles provenant des deux sources citées plus haut. Exécutez la commande suivante à la racine du projet :

Bash

python ingest_data.py
Si l'exécution est un succès, le script confirmera l'ajout des relevés météorologiques et énergétiques dans le fichier ecotrack.db.

Lancement de l'Application
Pour démarrer le serveur de développement Uvicorn :

Bash

uvicorn app.main:app --reload
L'API sera accessible à l'adresse : http://127.0.0.1:8000

Accès aux fonctionnalités
1. Documentation API (Swagger UI)
Adresse : http://127.0.0.1:8000/docs

Permet de tester tous les endpoints :

Auth : Inscription, Connexion.

Users (Admin) : Liste des utilisateurs, Modification de rôle/statut, Suppression.

Zones (Admin) : Création, Liste, Modification, Suppression de zones géographiques.

Indicators : CRUD complet (Lecture filtrée, Ajout, Modification, Suppression) et Statistiques.

2. Tableau de Bord (Dashboard)
Adresse : http://127.0.0.1:8000/dashboard

Interface graphique permettant de visualiser les données sous forme de tableau et de graphique, de filtrer par zone/type, et pour les administrateurs, d'ajouter ou supprimer des données.

Tests et Qualité
Des tests d'intégration ont été mis en place pour assurer la robustesse des routes principales (authentification, protection des routes, récupération des données).

Pour lancer la suite de tests :

Bash

python -m pytest
Gestion des Rôles
L'application gère deux niveaux de droits :

Utilisateur (user) :

Peut consulter les indicateurs (Lecture seule).

Peut utiliser les filtres (date, zone, type).

Peut consulter les statistiques agrégées.

Administrateur (admin) :

Dispose de tous les droits de l'utilisateur.

Gestion des Indicateurs : Ajout (POST), Modification (PUT) et Suppression (DELETE) de données.

Gestion des Zones : Création et administration des zones géographiques (CRUD).

Gestion des Utilisateurs : Accès à la liste des inscrits, modification des rôles (promotion en admin) et activation/désactivation des comptes.

Note : Lors de l'inscription via l'API, le rôle par défaut est "user".

Auteur : Matisse Marchand
