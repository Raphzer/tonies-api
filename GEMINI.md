# Project: ToniesBox Python API

## Context
Développement d'une bibliothèque Python pour interroger l'API REST et GraphQL de Tonies (my.tonies.com). 
L'objectif est de permettre aux utilisateurs de gérer leurs Tonies, leurs Creative-Tonies, et de consulter les informations de leur foyer (household) et de leur compte.

## Architecture Implémentée
- **Authentification**: Flux OAuth2 complet via Keycloak, avec récupération des cookies de session, soumission de formulaire, et échange de code d'autorisation contre des jetons (JWT).
- **API de Données**: Client GraphQL asynchrone pour l'interrogation des données.
- **Modélisation des Données**: Utilisation de Pydantic pour la validation et la sérialisation des réponses de l'API.

## Tech Stack
- **Language:** Python 3.10+
- **HTTP/GraphQL Client:** `httpx` (async)
- **HTML Parsing:** `beautifulsoup4` (pour le flux d'authentification)
- **Data Models:** `pydantic`
- **Dependency Management:** `requirements.txt` (`httpx`, `websockets`, `python-dotenv`, `beautifulsoup4`, `pydantic`)

## Project Structure
```text
tonies_api/
├── .vscode/
│   └── settings.json
├── tonies_api/
│   ├── __init__.py
│   ├── client.py           # Client principal et orchestrateur
│   ├── auth.py             # Gestion de l'authentification OAuth2
│   ├── tonies.py           # Méthodes pour les requêtes API (GraphQL)
│   ├── const.py            # Constantes (URLs, requêtes GraphQL)
│   ├── exceptions.py       # Exceptions personnalisées
│   └── models.py           # Modèles de données Pydantic
├── examples/
│   └── demo_full.py        # Exemple d'utilisation complet
├── .env.example
├── .gitignore
├── README.md
└── requirements.txt
```

## API & Models

### Méthodes Implémentées (`TonieResources`)
- `get_user_details()`: Récupère les informations détaillées de l'utilisateur.
- `get_households()`: Récupère la liste des foyers de l'utilisateur.
- `get_households_boxes()`: Récupère les Tonieboxes associées au compte.
- `get_tonies()`: Récupère une vue d'ensemble de tous les Tonies (Content et Creative) dans tous les foyers.
- `get_children(household_id)`: Récupère les enfants d'un foyer spécifique.
- `get_household_members(household_id)`: Récupère les membres et invitations d'un foyer.
- `get_content_tonie_details(household_id, tonie_id)`: Récupère les détails d'un Content-Tonie spécifique.

### Modèles Pydantic (`models.py`)
Le fichier `models.py` contient une série de modèles Pydantic qui structurent les réponses des requêtes GraphQL, incluant :
- `User`: Informations complètes sur l'utilisateur.
- `Household`, `HouseholdWithTonies`: Données sur les foyers, avec ou sans les listes détaillées de Tonies.
- `Toniebox`, `TonieboxInChild`: Représentations des appareils Toniebox.
- `ContentTonie`, `CreativeTonie`, `ContentTonieDetails`: Modèles pour les différents types de Tonies.
- `Child`: Informations sur les enfants du foyer.
- `Member`, `Invitation`, `HouseholdMembersResponse`: Données sur les membres du foyer.
- De nombreux autres modèles de support pour les structures de données imbriquées (`Tune`, `Series`, `Chapter`, etc.).