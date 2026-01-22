# Project: ToniesBox Python API

## Context
Développement d'une bibliothèque Python pour interroger l'API REST, GraphQL et WebSocket de Tonies (my.tonies.com).
L'objectif est de permettre aux utilisateurs de gérer leurs Tonies, leurs Creative-Tonies, de consulter les informations de leur foyer (household), de leur compte, et de recevoir des événements en temps réel depuis les Tonieboxes.

## Architecture Implémentée
- **Authentification**: Flux OAuth2 complet via Keycloak, avec récupération des cookies de session, soumission de formulaire, et échange de code d'autorisation contre des jetons (JWT).
- **API de Données**: Client GraphQL asynchrone pour l'interrogation des données et API REST pour certaines modifications de configuration.
- **Temps Réel**: Client WebSocket implémentant une couche MQTT légère pour recevoir les événements en temps réel (état en ligne, lecture, batterie, etc.) et s'abonner aux topics des Tonieboxes.
- **Modélisation des Données**: Utilisation de Pydantic pour la validation et la sérialisation des réponses de l'API.

## Tech Stack
- **Language:** Python 3.14+
- **HTTP/GraphQL Client:** `httpx` (async)
- **WebSocket Client:** `websockets`
- **HTML Parsing:** `beautifulsoup4` (pour le flux d'authentification)
- **Data Models:** `pydantic`
- **Dependency Management:** `requirements.txt` (`httpx`, `websockets`, `python-dotenv`, `beautifulsoup4`, `pydantic`)

## Project Structure
```text
tonies_api/
├── .vscode/
│   └── settings.json
├── src/
│   └── tonies_api/
│       ├── __init__.py
│       ├── client.py           # Client principal et orchestrateur
│       ├── auth.py             # Gestion de l'authentification OAuth2
│       ├── tonies.py           # Méthodes pour les requêtes API (GraphQL) et WebSocket
│       ├── const.py            # Constantes (URLs, requêtes GraphQL)
│       ├── exceptions.py       # Exceptions personnalisées
│       └── models.py           # Modèles de données Pydantic
├── example/
│   ├── demo_full.py            # Exemple d'utilisation complet (API REST/GraphQL)
│   └── test_ws.py              # Exemple d'utilisation du WebSocket
├── .env.example
├── .gitignore
├── README.md
├── pyproject.toml
└── requirements.txt
```

## API & Models

### Méthodes Implémentées (`TonieResources`)
**Lecture (GraphQL)**
- `get_user_details()`: Récupère les informations détaillées de l'utilisateur.
- `get_households()`: Récupère la liste des foyers de l'utilisateur.
- `get_households_boxes()`: Récupère les Tonieboxes associées au compte.
- `get_tonies()`: Récupère une vue d'ensemble de tous les Tonies (Content et Creative) dans tous les foyers.
- `get_children(household_id)`: Récupère les enfants d'un foyer spécifique.
- `get_household_members(household_id)`: Récupère les membres et invitations d'un foyer.
- `get_content_tonie_details(household_id, tonie_id)`: Récupère les détails d'un Content-Tonie spécifique.

**Écriture / Configuration (REST)**
- `set_max_volume(...)`: Définit le volume maximum.
- `set_max_headphone_volume(...)`: Définit le volume maximum du casque.
- `set_led_brightness(...)`: Règle la luminosité de la LED (on, off, dimmed).
- `set_toniebox_name(...)`: Renomme une Toniebox.
- `set_accelerometer(...)`: Active/Désactive l'accéléromètre (tap).
- `set_tap_direction(...)`: Configure la direction du tap (left/right).
- `set_lightring_brightness(...)`: Règle la luminosité de l'anneau lumineux (modèles récents).
- `set_bedtime_max_volume(...)`: Définit le volume max pour le mode coucher.
- `set_bedtime_headphone_max_volume(...)`: Définit le volume casque pour le mode coucher.
- `set_bedtime_lightring_brightness(...)`: Règle la luminosité de l'anneau pour le mode coucher.

### WebSocket (`TonieWebSocket`)
- `connect()`: Établit la connexion WebSocket et effectue le handshake MQTT.
- `subscribe_to_toniebox(mac_address)`: S'abonne automatiquement aux topics pertinents d'une Toniebox.
- `subscribe(topics)`: S'abonne à une liste de topics MQTT arbitraires.
- `register_callback(callback)`: Enregistre une fonction de rappel pour traiter les messages entrants.
- `disconnect()`: Ferme proprement la connexion.

### Modèles Pydantic (`models.py`)
Le fichier `models.py` contient une série de modèles Pydantic qui structurent les réponses, incluant :
- `User`: Informations complètes sur l'utilisateur.
- `Household`, `HouseholdWithTonies`: Données sur les foyers.
- `Toniebox`, `TonieboxInChild`: Représentations des appareils Toniebox (incluant les nouvelles propriétés de configuration).
- `ContentTonie`, `CreativeTonie`, `ContentTonieDetails`: Modèles pour les différents types de Tonies.
- `Child`: Informations sur les enfants.
- `Member`, `Invitation`: Données sur les membres du foyer.
- Structures pour les planifications (`BetTimeSchedules`), chapitres, séries, etc.
