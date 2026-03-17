# Tonies API Client

An asynchronous Python SDK for interacting with the Tonies cloud and your Toniebox devices. Supports data fetching via GraphQL/REST, device configuration, and real-time event monitoring via WebSocket/MQTT.

## Features

- **Asynchronous** — built on `httpx` and `websockets`
- **Authentication** — full OAuth2 flow via Keycloak, with automatic token refresh
- **GraphQL** — fetch users, households, Tonieboxes, Tonies, children, members
- **REST** — configure volume, LED, name, accelerometer, tap direction, bedtime settings
- **WebSocket / MQTT** — real-time events with automatic reconnection and topic re-subscription
- **Type-safe** — comprehensive Pydantic v2 models for all data structures

## Requirements

- Python ≥ 3.14

## Installation

```bash
git clone https://github.com/Raphzer/tonies-api.git
cd tonies-api
pip install .
```

For development (editable mode):

```bash
pip install -e .
```

## Quick start

Create a `.env` file with your Tonies credentials:

```
TONIE_USERNAME=your_email@example.com
TONIE_PASSWORD=your_password
```

### Fetch data and configure a Toniebox

```python
import asyncio
import os
from dotenv import load_dotenv
from tonies_api import TonieAPIClient

async def main():
    load_dotenv()
    async with TonieAPIClient(os.getenv("TONIE_USERNAME"), os.getenv("TONIE_PASSWORD")) as client:

        # User details
        user = await client.tonies.get_user_details()
        print(f"Logged in as {user.first_name} {user.last_name}")

        # List all Tonieboxes
        boxes = await client.tonies.get_households_boxes()
        for box in boxes:
            print(f"  {box.name} — TNG: {box.is_tng}, MAC: {box.mac_address}")

        # Configure the first box
        if boxes:
            box = boxes[0]
            await client.tonies.set_max_volume(box.household_id, box.id, 75)
            await client.tonies.set_toniebox_name(box.household_id, box.id, "Living room")

if __name__ == "__main__":
    asyncio.run(main())
```

### Real-time events (WebSocket)

```python
import asyncio
import os
from dotenv import load_dotenv
from tonies_api import TonieAPIClient

async def on_event(topic: str, payload: dict):
    print(f"[{topic}] {payload}")
    if "online-state" in topic:
        print(f"  → Box is {'online' if payload.get('onlineState') else 'offline'}")
    elif "metrics/battery" in topic:
        print(f"  → Battery: {payload.get('percent')}%")
    elif "playback/state" in topic:
        print(f"  → Tonie placed: {payload.get('tonie')}")

async def main():
    load_dotenv()
    async with TonieAPIClient(os.getenv("TONIE_USERNAME"), os.getenv("TONIE_PASSWORD")) as client:
        client.ws.register_callback(on_event)
        await client.ws.connect()

        boxes = await client.tonies.get_households_boxes()
        for box in boxes:
            subscribed = await client.ws.subscribe_to_toniebox(box)
            if subscribed:
                print(f"Subscribed to {box.name}")

        await asyncio.sleep(300)  # listen for 5 minutes

if __name__ == "__main__":
    asyncio.run(main())
```

`subscribe_to_toniebox` returns `True` if the subscription was sent, `False` if the box does not support WebSocket events (older generation). Incompatible boxes are skipped with a warning — they do not interrupt the loop.

The connection is supervised: if it drops, the client reconnects automatically with exponential backoff and re-subscribes to all previously registered topics.

## API Reference

### `TonieAPIClient`

Main entry point. Use as an async context manager — authentication and session cleanup are handled automatically.

```python
async with TonieAPIClient(username, password) as client:
    ...
```

| Attribute | Type | Description |
|---|---|---|
| `client.tonies` | `TonieResources` | Data fetching and device configuration |
| `client.ws` | `TonieWebSocket` | Real-time WebSocket/MQTT client |
| `client.auth` | `TonieAuth` | Authentication handler (OAuth2 / Keycloak) |

---

### `client.tonies` — `TonieResources`

#### Data methods

| Method | Returns | Description |
|---|---|---|
| `get_user_details()` | `User` | Authenticated user profile and flags |
| `get_households()` | `List[Household]` | All households for the account |
| `get_households_boxes()` | `List[Toniebox]` | All Tonieboxes across all households |
| `get_tonies()` | `List[HouseholdWithTonies]` | Full Tonies overview per household |
| `get_children(household_id)` | `List[Child]` | Children profiles for a household |
| `get_household_members(household_id)` | `HouseholdMembersResponse` | Members and pending invitations |
| `get_content_tonie_details(household_id, tonie_id)` | `List[ContentTonieDetails]` | Detailed info for a content Tonie |

#### Configuration methods

All configuration methods return an updated `Toniebox` object. They require `household_id` and `toniebox_id`.

Toniebox data is cached for 30 seconds to avoid redundant GraphQL requests when multiple settings are applied in sequence.

| Method | Parameter | Constraints |
|---|---|---|
| `set_max_volume(…, volume)` | `int` | TNG: 25–100 · Classic: 25, 50, 75, 100 |
| `set_max_headphone_volume(…, volume)` | `int` | TNG: 25–100 · Classic: 25, 50, 75, 100 |
| `set_led_brightness(…, level)` | `str` | `'on'`, `'off'`, `'dimmed'` |
| `set_toniebox_name(…, name)` | `str` | Non-empty string |
| `set_accelerometer(…, enabled)` | `bool` | |
| `set_tap_direction(…, direction)` | `str` | `'left'` or `'right'` |
| `set_lightring_brightness(…, brightness)` | `int` | TNG only · 0–100 |
| `set_bedtime_max_volume(…, volume)` | `int` | TNG only · 0–100 |
| `set_bedtime_headphone_max_volume(…, volume)` | `int` | TNG only · 25–100 |
| `set_bedtime_lightring_brightness(…, brightness)` | `int` | TNG only · 0–100 |

---

### `client.ws` — `TonieWebSocket`

#### Methods

| Method | Returns | Description |
|---|---|---|
| `connect()` | `None` | Connect, perform MQTT handshake, start reconnection supervisor |
| `disconnect()` | `None` | Gracefully close connection and stop the supervisor |
| `subscribe_to_toniebox(box)` | `bool` | Subscribe to all events for a box (`False` if not TNG-compatible) |
| `subscribe(topics)` | `None` | Manually subscribe to a list of MQTT topic strings |
| `register_callback(fn)` | `Callable` | Register `async def fn(topic, payload)` — returns an unregister function |
| `send_toniebox_command(mac, cmd, payload)` | `None` | Send a raw MQTT command to a box |
| `sleep_now(mac)` | `None` | Immediately put a Toniebox to sleep |

#### MQTT topics

Subscribing to a Toniebox with `subscribe_to_toniebox(box)` registers the wildcard topic `external/toniebox/{mac_address}/#`. Common events:

| Topic suffix | Description |
|---|---|
| `.../online-state` | Box went online or offline |
| `.../metrics/battery` | Battery level update |
| `.../metrics/headphones` | Headphone connection status |
| `.../playback/state` | Tonie placed on or removed from the box |
| `.../app-reply/bedtime-state` | Bedtime mode status |
| `.../changed-properties` | General property change notification |
| `.../settings-applied` | Confirmation that settings were applied |
| `.../setup/status` | Setup status update |

#### Automatic reconnection

When the connection drops unexpectedly, the client enters a reconnection loop with exponential backoff (starting at 2 s, capped at 120 s). All previously subscribed topics are re-subscribed automatically on reconnect. The access token is refreshed before each attempt. A voluntary `disconnect()` cancels the loop immediately.

---

### Models

| Class | Description |
|---|---|
| `Toniebox` | Device — includes `is_tng` property and `bedtime_schedules` |
| `BedtimeSchedules` | Bedtime schedule entry (alarm, sleep/wakeup times, days) |
| `User` | Authenticated user profile and feature flags |
| `Household` | Household container |
| `HouseholdWithTonies` | Household with nested content/creative Tonies and discs |
| `Child` | Child profile with associated Tonieboxes |
| `HouseholdMembersResponse` | Memberships and pending invitations |
| `ContentTonieDetails` | Detailed content Tonie data including owned tunes |

All models are Pydantic v2 `BaseModel` subclasses and accept camelCase aliases from the API responses.

#### `Toniebox.is_tng`

```python
if box.is_tng:
    await client.tonies.set_lightring_brightness(box.household_id, box.id, 80)
```

Returns `True` if the box has the `tngSettings` feature (Toniebox Go / next-gen). Several configuration methods and all WebSocket subscriptions require `is_tng == True`.

---

### Exceptions

| Exception | Description |
|---|---|
| `ToniesApiError` | Base exception for all library errors |
| `TonieAuthError` | Authentication failure (login, token refresh) |
| `TonieConnectionError` | Network or API error during a request |

---

## Changelog

See [CHANGELOG.md](CHANGELOG.md).

## License

Apache 2.0 — see [LICENSE](LICENSE).