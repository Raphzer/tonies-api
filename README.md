# Tonies API Client

A Python library for interacting with the Tonies API. This library provides an asynchronous client to manage your Tonies, Creative-Tonies, households, and more. It supports both standard data fetching via GraphQL/REST and real-time event monitoring via WebSocket/MQTT.

## Features

-   **Asynchronous Client**: Built on `httpx` and `websockets`.
-   **Authentication**: Full OAuth2 flow via Keycloak.
-   **Data Fetching (GraphQL)**:
    -   User details
    -   Households and Members
    -   Tonieboxes
    -   Creative-Tonies and Content-Tonies
    -   Children profiles
-   **Device Configuration (REST)**:
    -   Volume limits (Speaker & Headphones)
    -   LED & Lightring brightness
    -   Toniebox name
    -   Accelerometer & Tap gestures
    -   Bedtime settings
-   **Real-time Events (WebSocket)**:
    -   Monitor connection state (online/offline)
    -   Battery levels
    -   Tonie placement detection
    -   Headphone connection status
-   **Type Safety**: Comprehensive Pydantic models for all data structures.

## Installation

You can install the library directly from the source:

```bash
git clone https://github.com/your-username/tonies-api.git
cd tonies-api
pip install -r requirements.txt
```

## Usage

First, create a `.env` file in your project root with your Tonies credentials:

```
TONIE_USERNAME=your_email@example.com
TONIE_PASSWORD=your_password
```

### Basic Data & Configuration

```python
import asyncio
import os
from dotenv import load_dotenv
from tonies_api.client import TonieAPIClient

async def main():
    load_dotenv()
    username = os.getenv("TONIE_USERNAME")
    password = os.getenv("TONIE_PASSWORD")

    async with TonieAPIClient(username, password) as client:
        # Get Households
        households = await client.tonies.get_households()
        
        # Get Tonieboxes
        tonieboxes = await client.tonies.get_households_boxes()
        if tonieboxes:
            box = tonieboxes[0]
            print(f"Found box: {box.name} (Battery: {box.mac_address})")

            # Update Volume
            await client.tonies.set_max_volume(box.household_id, box.id, 75)
            print("Volume updated!")

if __name__ == "__main__":
    asyncio.run(main())
```

### Real-time Events (WebSocket)

```python
import asyncio
import os
from dotenv import load_dotenv
from tonies_api.client import TonieAPIClient

async def event_handler(topic, payload):
    print(f"Received event on {topic}: {payload}")

async def main():
    load_dotenv()
    async with TonieAPIClient(os.getenv("TONIE_USERNAME"), os.getenv("TONIE_PASSWORD")) as client:
        # Register callback
        client.ws.register_callback(event_handler)
        
        # Connect and subscribe
        await client.ws.connect()
        
        # Keep alive
        await asyncio.sleep(60)

if __name__ == "__main__":
    asyncio.run(main())
```

## API Reference

The `TonieAPIClient` provides access to `TonieResources` via `client.tonies` and `TonieWebSocket` via `client.ws`.

### Data Methods (`client.tonies`)

-   `get_user_details() -> User`
-   `get_households() -> List[Household]`
-   `get_households_boxes() -> List[Toniebox]`
-   `get_tonies() -> List[HouseholdWithTonies]`
-   `get_children(household_id: str) -> List[Child]`
-   `get_household_members(household_id: str) -> HouseholdMembersResponse`
-   `get_content_tonie_details(household_id: str, tonie_id: str) -> List[ContentTonieDetails]`

### Configuration Methods (`client.tonies`)

-   `set_max_volume(household_id, toniebox_id, volume) -> Toniebox`
-   `set_max_headphone_volume(household_id, toniebox_id, volume) -> Toniebox`
-   `set_led_brightness(household_id, toniebox_id, level) -> Toniebox` (level: 'on', 'off', 'dimmed')
-   `set_toniebox_name(household_id, toniebox_id, name) -> Toniebox`
-   `set_accelerometer(household_id, toniebox_id, enabled) -> Toniebox`
-   `set_tap_direction(household_id, toniebox_id, direction) -> Toniebox` ('left' or 'right')
-   `set_lightring_brightness(household_id, toniebox_id, brightness) -> Toniebox`
-   `set_bedtime_max_volume(household_id, toniebox_id, volume) -> Toniebox`
-   `set_bedtime_headphone_max_volume(household_id, toniebox_id, volume) -> Toniebox`
-   `set_bedtime_lightring_brightness(household_id, toniebox_id, brightness) -> Toniebox`

### WebSocket Methods (`client.ws`)

-   `connect()`: Connects to the real-time server.
-   `subscribe_to_toniebox(mac_address)`: Subscribes to standard events for a box.
-   `register_callback(callback)`: Registers a function `async def callback(topic, payload)` to handle events.

## License

This project is licensed under the Apache 2.0 License - see the [LICENSE](LICENSE) file for details.