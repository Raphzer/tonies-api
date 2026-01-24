import asyncio
import os
import logging
import uuid
from dotenv import load_dotenv

# Import de ton SDK
from tonies_api import TonieAPIClient
from tonies_api import TonieConnectionError, TonieAuthError

# Configuration du logging pour voir le détail du handshake MQTT et des trames
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
log = logging.getLogger(__name__)

# --- CALLBACK ---
async def event_callback(topic: str, data: dict):
    """
    Fonction appelée automatiquement à chaque réception de message MQTT.
    """
    print(f"\n [NOUVEL ÉVÉNEMENT]")
    print(f" Topic : {topic}")
    print(f" Data  : {data}")
    
    # Exemple de traitement spécifique
    if "online-state" in topic:
        print(f"ℹ État de la box : {data.get('onlineState')}")
    elif "placed_tonie" in topic:
        print(f" Tonie détecté ! ID : {data.get('tonieId')}")
    elif "battery" in topic:
        print(f" Batterie : {data.get('battery')} %")

# --- MAIN ---
async def main():
    # Chargement des variables d'environnement (.env)
    load_dotenv()
    
    username = os.getenv("TONIE_USERNAME")
    password = os.getenv("TONIE_PASSWORD")
    
    if not username or not password:
        log.error("Veuillez configurer TONIE_USERNAME et TONIE_PASSWORD dans votre fichier .env")
        return

    log.info(f"Tentative de connexion pour l'utilisateur : {username}")
    
    async with TonieAPIClient(username, password) as client:
        try:
            # 1. Authentification (REST / OAuth2)
            # Normalement géré automatiquement par le 'async with' si implémenté, 
            # sinon on s'assure d'être loggé.
            
            # 2. Enregistrement du callback avant la connexion
            # Cela permet de capturer les messages "retained" envoyés par le serveur dès le début.
            client.ws.register_callback(event_callback)
            
            # 3. Connexion au WebSocket (ICI) et Handshake MQTT
            log.info("Connexion au serveur temps-réel (WebSocket/MQTT)...")
            await client.ws.connect()
            log.info("Handshake MQTT réussi !")

            # 4. Récupération des Tonieboxes pour abonnement
            # On utilise la Mac Address car les topics ICI sont basés dessus.
            log.info("Récupération de la liste des Tonieboxes...")
            boxes = await client.tonies.get_households_boxes()
            for box in boxes:
                await client.ws.subscribe_to_toniebox(box)

            log.info("--- ÉCOUTE ACTIVE (60 secondes) ---")
            
            # On maintient le script en vie. Le ping_loop en arrière-plan gère le Keep-Alive.
            await asyncio.sleep(60)
            
        except TonieAuthError as e:
            log.error(f"Erreur d'authentification : {e}")
        except TonieConnectionError as e:
            log.error(f"Erreur de connexion : {e}")
        except Exception as e:
            log.error(f"Une erreur inattendue est survenue : {e}")
            import traceback
            traceback.print_exc()
        finally:
            log.info("Fermeture de la connexion WebSocket...")
            await client.ws.disconnect()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        log.info("Arrêt du script par l'utilisateur.")