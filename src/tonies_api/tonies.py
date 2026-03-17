import uuid
from typing import Any, Callable, List, Optional
import httpx
import asyncio
import json
import logging
import websockets

from .const import (
    API_BASE_URL,
    CONTENT_TONIE_DETAILS_QUERY,
    GET_CHILDREN_QUERY,
    GET_HOUSEHOLD_MEMBERS_QUERY,
    GET_HOUSEHOLDS_BOXES_QUERY,
    GET_HOUSEHOLDS_QUERY,
    GET_USER_DETAILS_QUERY,
    GRAPHQL_URL,
    USER_TONIES_OVERVIEW_QUERY,
    WEBSOCKET_URL,
)
from .exceptions import TonieConnectionError
from .models import (
    Child,
    ContentTonieDetails,
    Household,
    HouseholdMembersResponse,
    HouseholdWithTonies,
    Toniebox,
    User,
)

log = logging.getLogger(__name__)


class TonieResources:
    """Handles fetching resources from the Tonies API."""

    def __init__(self, session: httpx.AsyncClient) -> None:
        """
        Initialize the resource handler.

        Args:
            session: An httpx.AsyncClient session.
        """
        self._session = session

    async def get_households(self) -> List[Household]:
        """
        Get all households for the current account using GraphQL.

        Returns:
            A list of Household objects.

        Raises:
            TonieConnectionError: If there is a connection error.
        """
        log.debug("Getting households.")
        try:
            response = await self._session.post(GRAPHQL_URL, json=GET_HOUSEHOLDS_QUERY)
            response.raise_for_status()
            data = response.json()
            households_data = data.get("data", {}).get("households", [])
            return [Household(**h) for h in households_data]
        except httpx.HTTPError as exc:
            raise TonieConnectionError from exc
        except Exception as e:
            # Broad exception to catch pydantic validation errors or other issues
            raise TonieConnectionError(f"Failed to parse Household data: {e}")

    async def get_tonies(self) -> List[HouseholdWithTonies]:
        """
        Get an overview of all tonies in all households.

        Returns:
            A list of households with detailed tonie information.

        Raises:
            TonieConnectionError: If there is a connection error.
        """
        log.debug("Getting tonies overview.")
        try:
            response = await self._session.post(
                GRAPHQL_URL, json=USER_TONIES_OVERVIEW_QUERY
            )
            response.raise_for_status()
            data = response.json()
            households_data = data.get("data", {}).get("households", [])
            return [HouseholdWithTonies(**h) for h in households_data]
        except httpx.HTTPError as exc:
            raise TonieConnectionError from exc
        except Exception as e:
            raise TonieConnectionError(f"Failed to parse ToniesOverview data: {e}")

    async def get_households_boxes(self) -> List[Toniebox]:
        """
        Get all Tonieboxes for the current account using GraphQL.

        Returns:
            A list of Toniebox objects.

        Raises:
            TonieConnectionError: If there is a connection error.
        """
        log.debug("Getting household boxes.")
        try:
            response = await self._session.post(
                GRAPHQL_URL, json=GET_HOUSEHOLDS_BOXES_QUERY
            )
            response.raise_for_status()
            data = response.json()

            tonieboxes = []
            for household in data.get("data", {}).get("households", []):
                for box_data in household.get("tonieboxes", []):
                    tonieboxes.append(Toniebox(**box_data))

            return tonieboxes
        except httpx.HTTPError as exc:
            raise TonieConnectionError from exc
        except Exception as e:
            # Broad exception to catch pydantic validation errors or other issues
            raise TonieConnectionError(f"Failed to parse Toniebox data: {e}")

    async def get_user_details(self) -> User:
        """
        Get user details for the current account using GraphQL.

        Returns:
            A User object.

        Raises:
            TonieConnectionError: If there is a connection error.
        """
        log.debug("Getting user details.")
        try:
            response = await self._session.post(
                GRAPHQL_URL, json=GET_USER_DETAILS_QUERY
            )
            response.raise_for_status()
            data = response.json().get("data", {})
            user_data = {**data.get("me", {}), **data.get("flags", {})}
            return User(**user_data)
        except httpx.HTTPError as exc:
            raise TonieConnectionError from exc
        except Exception as e:
            # Broad exception to catch pydantic validation errors or other issues
            raise TonieConnectionError(f"Failed to parse User data: {e}")

    async def get_children(self, household_id: str) -> List[Child]:
        """
        Get all children for a given household using GraphQL.

        Args:
            household_id: The ID of the household.

        Returns:
            A list of Child objects.

        Raises:
            TonieConnectionError: If there is a connection error.
        """
        log.debug(f"Getting children for household {household_id}.")
        try:
            payload = {
                "operationName": "GetChildren",
                "variables": {"id": household_id},
                "query": GET_CHILDREN_QUERY,
            }
            response = await self._session.post(GRAPHQL_URL, json=payload)
            response.raise_for_status()
            data = response.json()
            # The result is nested, so we need to extract it
            households = data.get("data", {}).get("households", [])
            if not households:
                return []
            children_data = households[0].get("children", [])
            return [Child(**c) for c in children_data]
        except httpx.HTTPError as exc:
            raise TonieConnectionError from exc
        except Exception as e:
            raise TonieConnectionError(f"Failed to parse Children data: {e}")

    async def get_household_members(
        self, household_id: str
    ) -> HouseholdMembersResponse:
        """
        Get all members and invitations for a given household using GraphQL.

        Args:
            household_id: The ID of the household.

        Returns:
            A HouseholdMembersResponse object containing members and invitations.

        Raises:
            TonieConnectionError: If there is a connection error.
        """
        log.debug(f"Getting members for household {household_id}.")
        try:
            payload = {
                "operationName": "GetHouseholdMembers",
                "variables": {"householdId": household_id},
                "query": GET_HOUSEHOLD_MEMBERS_QUERY,
            }
            response = await self._session.post(GRAPHQL_URL, json=payload)
            response.raise_for_status()
            data = response.json()
            # The result is nested, so we need to extract it
            households = data.get("data", {}).get("households", [])
            if not households:
                return HouseholdMembersResponse(memberships=[], invitations=[])
            return HouseholdMembersResponse(**households[0])
        except httpx.HTTPError as exc:
            raise TonieConnectionError from exc
        except Exception as e:
            raise TonieConnectionError(f"Failed to parse HouseholdMembers data: {e}")

    async def get_content_tonie_details(
        self, household_id: str, tonie_id: str
    ) -> List[ContentTonieDetails]:
        """
        Get details for a specific content Tonie in a household.

        Args:
            household_id: The ID of the household.
            tonie_id: The ID of the content Tonie.

        Returns:
            A list containing the details of the content Tonie.

        Raises:
            TonieConnectionError: If there is a connection error.
        """
        log.debug(f"Getting details for tonie {tonie_id} in household {household_id}.")
        try:
            payload = {
                "operationName": "ContentTonieDetails",
                "variables": {"householdId": household_id, "tonieId": tonie_id},
                "query": CONTENT_TONIE_DETAILS_QUERY,
            }
            response = await self._session.post(GRAPHQL_URL, json=payload)
            response.raise_for_status()
            data = response.json()
            # The result is nested, so we need to extract it
            households = data.get("data", {}).get("households", [])
            if not households:
                return []
            content_tonies_data = households[0].get("contentTonies", [])
            return [ContentTonieDetails(**ct) for ct in content_tonies_data]
        except httpx.HTTPError as exc:
            raise TonieConnectionError from exc
        except Exception as e:
            raise TonieConnectionError(f"Failed to parse ContentTonieDetails data: {e}")

    async def _get_toniebox(self, toniebox_id: str) -> Toniebox:
        """
        Get a specific Toniebox by its ID.

        Note: This is inefficient as it fetches all tonieboxes.

        Args:
            toniebox_id: The ID of the Toniebox.

        Returns:
            The Toniebox object.

        Raises:
            ValueError: If the Toniebox is not found.
        """
        tonieboxes = await self.get_households_boxes()
        for toniebox in tonieboxes:
            if toniebox.id == toniebox_id:
                return toniebox
        raise ValueError(f"Toniebox with ID {toniebox_id} not found.")

    async def set_max_volume(
        self, household_id: str, toniebox_id: str, max_volume: int
    ) -> Toniebox:
        """
        Set the maximum volume for a specific Toniebox.

        Args:
            household_id: The ID of the household.
            toniebox_id: The ID of the Toniebox.
            max_volume: The desired maximum volume.

        Returns:
            A Toniebox object with the updated information.

        Raises:
            ValueError: If max_volume is not one of the allowed values.
            TonieConnectionError: If there is a connection error.
        """
        toniebox = await self._get_toniebox(toniebox_id)
        if "tngSettings" in toniebox.features:
            if not 25 <= max_volume <= 100:
                raise ValueError("Max volume must be between 25 and 100 for this Toniebox.")
        else:
            if max_volume not in [25, 50, 75, 100]:
                raise ValueError("Max volume must be 25, 50, 75, or 100 for this Toniebox.")

        log.debug(
            f"Setting max volume for toniebox {toniebox_id} in household {household_id} to {max_volume}."
        )
        try:
            url = f"{API_BASE_URL}/households/{household_id}/tonieboxes/{toniebox_id}"
            payload = {"maxVolume": max_volume}
            response = await self._session.patch(url, json=payload)
            response.raise_for_status()
            return Toniebox(**response.json())
        except httpx.HTTPError as exc:
            raise TonieConnectionError from exc
        except Exception as e:
            raise TonieConnectionError(f"Failed to set max volume: {e}")

    async def set_max_headphone_volume(
        self, household_id: str, toniebox_id: str, max_headphone_volume: int
    ) -> Toniebox:
        """
        Set the maximum headphone volume for a specific Toniebox.

        Args:
            household_id: The ID of the household.
            toniebox_id: The ID of the Toniebox.
            max_headphone_volume: The desired maximum volume.

        Returns:
            A Toniebox object with the updated information.

        Raises:
            ValueError: If max_headphone_volume is not one of the allowed values.
            TonieConnectionError: If there is a connection error.
        """
        toniebox = await self._get_toniebox(toniebox_id)
        if "tngSettings" in toniebox.features:
            if not 25 <= max_headphone_volume <= 100:
                raise ValueError("Max headphone volume must be between 25 and 100 for this Toniebox.")
        else:
            if max_headphone_volume not in [25, 50, 75, 100]:
                raise ValueError("Max headphone volume must be 25, 50, 75, or 100 for this Toniebox.")

        log.debug(
            f"Setting max headphone volume for toniebox {toniebox_id} in household {household_id} to {max_headphone_volume}."
        )
        try:
            url = f"{API_BASE_URL}/households/{household_id}/tonieboxes/{toniebox_id}"
            payload = {"maxHeadphoneVolume": max_headphone_volume}
            response = await self._session.patch(url, json=payload)
            response.raise_for_status()
            return Toniebox(**response.json())
        except httpx.HTTPError as exc:
            raise TonieConnectionError from exc
        except Exception as e:
            raise TonieConnectionError(f"Failed to set max headphone volume: {e}")
        
    async def set_led_brightness(
        self, household_id: str, toniebox_id: str, led_level: str
    ) -> Toniebox:
        """
        Set the LED brightness for a specific Toniebox.

        Args:
            household_id: The ID of the household.
            toniebox_id: The ID of the Toniebox.
            led_level: The desired LED level ('on', 'off', 'dimmed').

        Returns:
            A Toniebox object with the updated information.

        Raises:
            ValueError: If led_level is not one of the allowed values.
            TonieConnectionError: If there is a connection error.
        """
        if led_level not in ["on", "off", "dimmed"]:
            raise ValueError("LED level must be 'on', 'off', or 'dimmed'.")

        log.debug(
            f"Setting LED level for toniebox {toniebox_id} in household {household_id} to {led_level}."
        )
        try:
            url = f"{API_BASE_URL}/households/{household_id}/tonieboxes/{toniebox_id}"
            payload = {"ledLevel": led_level}
            response = await self._session.patch(url, json=payload)
            response.raise_for_status()
            return Toniebox(**response.json())
        except httpx.HTTPError as exc:
            raise TonieConnectionError from exc
        except Exception as e:
            raise TonieConnectionError(f"Failed to set LED brightness: {e}")

    async def set_toniebox_name(
        self, household_id: str, toniebox_id: str, name: str
    ) -> Toniebox:
        """
        Set the name for a specific Toniebox.

        Args:
            household_id: The ID of the household.
            toniebox_id: The ID of the Toniebox.
            name: The desired name for the Toniebox.

        Returns:
            A Toniebox object with the updated information.

        Raises:
            TonieConnectionError: If there is a connection error.
        """
        if not isinstance(name, str) or not name:
            raise ValueError("Toniebox name must be a non-empty string.")

        log.debug(
            f"Setting name for toniebox {toniebox_id} in household {household_id} to {name}."
        )
        try:
            url = f"{API_BASE_URL}/households/{household_id}/tonieboxes/{toniebox_id}"
            payload = {"name": name}
            response = await self._session.patch(url, json=payload)
            response.raise_for_status()
            return Toniebox(**response.json())
        except httpx.HTTPError as exc:
            raise TonieConnectionError from exc
        except Exception as e:
            raise TonieConnectionError(f"Failed to set Toniebox name: {e}")

    async def set_accelerometer(
        self, household_id: str, toniebox_id: str, enabled: bool
    ) -> Toniebox:
        """
        Enable or disable the accelerometer for a specific Toniebox.

        Args:
            household_id: The ID of the household.
            toniebox_id: The ID of the Toniebox.
            enabled: True to enable, False to disable.

        Returns:
            A Toniebox object with the updated information.

        Raises:
            ValueError: If enabled is not a boolean.
            TonieConnectionError: If there is a connection error.
        """
        if not isinstance(enabled, bool):
            raise ValueError("Enabled must be a boolean.")

        log.debug(
            f"Setting accelerometer for toniebox {toniebox_id} in household {household_id} to {enabled}."
        )
        try:
            url = f"{API_BASE_URL}/households/{household_id}/tonieboxes/{toniebox_id}"
            payload = {"accelerometerEnabled": enabled}
            response = await self._session.patch(url, json=payload)
            response.raise_for_status()
            return Toniebox(**response.json())
        except httpx.HTTPError as exc:
            raise TonieConnectionError from exc
        except Exception as e:
            raise TonieConnectionError(f"Failed to set accelerometer: {e}")

    async def set_tap_direction(
        self, household_id: str, toniebox_id: str, direction: str
    ) -> Toniebox:
        """
        Set the tap direction for a specific Toniebox.

        Args:
            household_id: The ID of the household.
            toniebox_id: The ID of the Toniebox.
            direction: The desired tap direction ('left' or 'right').

        Returns:
            A Toniebox object with the updated information.

        Raises:
            ValueError: If direction is not 'left' or 'right'.
            TonieConnectionError: If there is a connection error.
        """
        if direction not in ["left", "right"]:
            raise ValueError("Direction must be 'left' or 'right'.")

        log.debug(
            f"Setting tap direction for toniebox {toniebox_id} in household {household_id} to {direction}."
        )
        try:
            url = f"{API_BASE_URL}/households/{household_id}/tonieboxes/{toniebox_id}"
            payload = {"tapDirection": direction}
            response = await self._session.patch(url, json=payload)
            response.raise_for_status()
            return Toniebox(**response.json())
        except httpx.HTTPError as exc:
            raise TonieConnectionError from exc
        except Exception as e:
            raise TonieConnectionError(f"Failed to set tap direction: {e}")

    async def set_lightring_brightness(
        self, household_id: str, toniebox_id: str, brightness: int
    ) -> Toniebox:
        """
        Set the lightring brightness for a specific Toniebox.
        This feature is only available for Tonieboxes with 'tngSettings'.

        Args:
            household_id: The ID of the household.
            toniebox_id: The ID of the Toniebox.
            brightness: The desired brightness (0-100).

        Returns:
            A Toniebox object with the updated information.

        Raises:
            ValueError: If the Toniebox does not support this feature or the value is invalid.
            TonieConnectionError: If there is a connection error.
        """
        toniebox = await self._get_toniebox(toniebox_id)
        if "tngSettings" not in toniebox.features:
            raise ValueError("This Toniebox does not support setting lightring brightness.")
        if not 0 <= brightness <= 100:
            raise ValueError("Brightness must be between 0 and 100.")

        log.debug(
            f"Setting lightring brightness for toniebox {toniebox_id} to {brightness}."
        )
        try:
            url = f"{API_BASE_URL}/households/{household_id}/tonieboxes/{toniebox_id}"
            payload = {"lightringBrightness": brightness}
            response = await self._session.patch(url, json=payload)
            response.raise_for_status()
            return Toniebox(**response.json())
        except httpx.HTTPError as exc:
            raise TonieConnectionError from exc
        except Exception as e:
            raise TonieConnectionError(f"Failed to set lightring brightness: {e}")

    async def set_bedtime_max_volume(
        self, household_id: str, toniebox_id: str, volume: int
    ) -> Toniebox:
        """
        Set the bedtime max volume for a specific Toniebox.
        This feature is only available for Tonieboxes with 'tngSettings'.

        Args:
            household_id: The ID of the household.
            toniebox_id: The ID of the Toniebox.
            volume: The desired bedtime max volume (0-100).

        Returns:
            A Toniebox object with the updated information.

        Raises:
            ValueError: If the Toniebox does not support this feature or the value is invalid.
            TonieConnectionError: If there is a connection error.
        """
        toniebox = await self._get_toniebox(toniebox_id)
        if "tngSettings" not in toniebox.features:
            raise ValueError("This Toniebox does not support setting bedtime max volume.")
        if not 0 <= volume <= 100:
            raise ValueError("Bedtime max volume must be between 0 and 100.")

        log.debug(
            f"Setting bedtime max volume for toniebox {toniebox_id} to {volume}."
        )
        try:
            url = f"{API_BASE_URL}/households/{household_id}/tonieboxes/{toniebox_id}"
            payload = {"bedtimeMaxVolume": volume}
            response = await self._session.patch(url, json=payload)
            response.raise_for_status()
            return Toniebox(**response.json())
        except httpx.HTTPError as exc:
            raise TonieConnectionError from exc
        except Exception as e:
            raise TonieConnectionError(f"Failed to set bedtime max volume: {e}")

    async def set_bedtime_headphone_max_volume(
        self, household_id: str, toniebox_id: str, volume: int
    ) -> Toniebox:
        """
        Set the bedtime headphone volume for a specific Toniebox.
        This feature is only available for Tonieboxes with 'tngSettings'.

        Args:
            household_id: The ID of the household.
            toniebox_id: The ID of the Toniebox.
            volume: The desired bedtime headphone volume (25-100).

        Returns:
            A Toniebox object with the updated information.

        Raises:
            ValueError: If the Toniebox does not support this feature or the value is invalid.
            TonieConnectionError: If there is a connection error.
        """
        toniebox = await self._get_toniebox(toniebox_id)
        if "tngSettings" not in toniebox.features:
            raise ValueError("This Toniebox does not support setting bedtime headphone volume.")
        if not 25 <= volume <= 100:
            raise ValueError("Bedtime headphone volume must be between 25 and 100.")

        log.debug(
            f"Setting bedtime headphone volume for toniebox {toniebox_id} to {volume}."
        )
        try:
            url = f"{API_BASE_URL}/households/{household_id}/tonieboxes/{toniebox_id}"
            payload = {"bedtimeMaxHeadphoneVolume": volume}
            response = await self._session.patch(url, json=payload)
            response.raise_for_status()
            return Toniebox(**response.json())
        except httpx.HTTPError as exc:
            raise TonieConnectionError from exc
        except Exception as e:
            raise TonieConnectionError(f"Failed to set bedtime headphone volume: {e}")

    async def set_bedtime_lightring_brightness(
        self, household_id: str, toniebox_id: str, brightness: int
    ) -> Toniebox:
        """
        Set the bedtime lightring brightness for a specific Toniebox.
        This feature is only available for Tonieboxes with 'tngSettings'.

        Args:
            household_id: The ID of the household.
            toniebox_id: The ID of the Toniebox.
            brightness: The desired bedtime lightring brightness (0-100).

        Returns:
            A Toniebox object with the updated information.

        Raises:
            ValueError: If the Toniebox does not support this feature or the value is invalid.
            TonieConnectionError: If there is a connection error.
        """
        toniebox = await self._get_toniebox(toniebox_id)
        if "tngSettings" not in toniebox.features:
            raise ValueError("This Toniebox does not support setting bedtime lightring brightness.")
        if not 0 <= brightness <= 100:
            raise ValueError("Bedtime lightring brightness must be between 0 and 100.")

        log.debug(
            f"Setting bedtime lightring brightness for toniebox {toniebox_id} to {brightness}."
        )
        try:
            url = f"{API_BASE_URL}/households/{household_id}/tonieboxes/{toniebox_id}"
            payload = {"bedtimeLightringBrightness": brightness}
            response = await self._session.patch(url, json=payload)
            response.raise_for_status()
            return Toniebox(**response.json())
        except httpx.HTTPError as exc:
            raise TonieConnectionError from exc
        except Exception as e:
            raise TonieConnectionError(f"Failed to set bedtime lightring brightness: {e}")

    async def is_tng_toniebox(self, toniebox) -> bool:
        if "tngSettings" in toniebox.features:
            return True
        else:
            return False





# ---------------------------------------------------------------------------
# Reconnection constants — tweak to taste
# ---------------------------------------------------------------------------
_RECONNECT_BASE_DELAY  = 2.0    # seconds before first retry
_RECONNECT_MAX_DELAY   = 120.0  # ceiling for exponential backoff
_RECONNECT_MAX_RETRIES = 0      # 0 = retry forever


class TonieWebSocket:
    """Handles the WebSocket connection to the Tonies server.

    Automatic reconnection
    ----------------------
    When the connection is lost unexpectedly the client enters a reconnection
    loop with exponential backoff (starting at ``_RECONNECT_BASE_DELAY`` s,
    capped at ``_RECONNECT_MAX_DELAY`` s).  All topics that were subscribed
    before the drop are re-subscribed automatically on each successful
    reconnection.

    A voluntary ``disconnect()`` cancels the loop immediately.
    """

    def __init__(self, client: Any) -> None:
        """
        Initialize the WebSocket handler.

        Args:
            client: The TonieAPIClient instance.
        """
        self._client = client
        self._session = client._session
        self._ws: Optional[websockets.WebSocketClientProtocol] = None  # type: ignore
        self._listen_task: Optional[asyncio.Task] = None
        self._ping_task: Optional[asyncio.Task] = None
        self._reconnect_task: Optional[asyncio.Task] = None
        self._is_running = False
        self._disconnecting = False          # True only during a voluntary disconnect
        self._packet_id = 0
        self._callbacks: list[Callable[[str, dict], Any]] = []
        self._subscribed_topics: list[str] = []   # persisted for auto re-subscribe

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    async def connect(self) -> None:
        """
        Establish the WebSocket connection, perform the MQTT handshake, and
        start the background reconnection supervisor.

        Raises:
            TonieConnectionError: If the initial connection or handshake fails.
        """
        self._disconnecting = False
        await self._do_connect()

        # Supervisor: watches _listen_task and reconnects on unexpected drops.
        self._reconnect_task = asyncio.create_task(self._reconnect_loop())

    async def disconnect(self) -> None:
        """Close the connection and stop the reconnection supervisor."""
        self._disconnecting = True
        self._is_running = False

        if self._reconnect_task:
            self._reconnect_task.cancel()
            try:
                await self._reconnect_task
            except asyncio.CancelledError:
                pass
            self._reconnect_task = None

        await self._teardown()
        log.info("WebSocket disconnected.")

    async def subscribe_to_toniebox(self, box: "Toniebox") -> bool:
        """
        Subscribe to all relevant topics for a specific Toniebox.

        Boxes without the ``tngSettings`` feature (older generation) do not
        expose a WebSocket interface. They are skipped with a warning so that
        a mixed fleet (some compatible, some not) does not interrupt the
        subscription loop.

        Args:
            box: Toniebox object.

        Returns:
            True if the subscription was sent, False if the box is not compatible.
        """
        if "tngSettings" not in box.features:
            log.warning(
                "Skipping WebSocket subscription for '%s' (%s): "
                "box does not support real-time events.",
                box.name,
                box.mac_address,
            )
            return False
        topics = [f"external/toniebox/{box.mac_address}/#"]
        await self.subscribe(topics)
        return True

    async def subscribe(self, topics: list[str]) -> None:
        """Send an MQTT SUBSCRIBE packet and persist topics for reconnection."""
        for t in topics:
            if t not in self._subscribed_topics:
                self._subscribed_topics.append(t)

        if self._ws and self._is_running:
            packet = self._create_subscribe_packet(topics)
            await self._ws.send(packet)
            log.debug(f"MQTT SUBSCRIBE sent: {topics}")
        else:
            log.warning(
                "WebSocket not connected — topics queued and will be sent on (re)connect: %s",
                topics,
            )

    def register_callback(self, callback: Callable[[str, dict], Any]) -> Callable[[], None]:
        """Register a callback to be notified of new events.

        Returns a no-arg function that unregisters the callback when called.
        """
        self._callbacks.append(callback)
        return lambda: self._callbacks.remove(callback)

    async def send_toniebox_command(
        self,
        mac_address: str,
        command_type: str,
        payload: Optional[dict] = None,
    ) -> None:
        """
        Send a command to a specific Toniebox via MQTT Publish (QoS 1).

        Args:
            mac_address: The MAC address of the Toniebox.
            command_type: The command endpoint (e.g., 'stl', 'sleep', 'sync').
            payload: Optional dictionary containing command parameters.
        """
        if not self._ws or not self._is_running:
            log.error("Cannot send command: WebSocket not connected")
            return

        if payload is None:
            payload = {}

        clean_mac = mac_address.lower().replace(":", "")
        topic = f"external/toniebox/{clean_mac}/app-control/{command_type}"
        packet = self._create_publish_packet(topic, payload)
        await self._ws.send(packet)  # type: ignore
        log.debug(f"MQTT PUBLISH (Command) sent to {topic}: {payload}")

    async def sleep_now(self, mac_address: str) -> None:
        clean_mac = mac_address.lower().replace(":", "")
        await self.send_toniebox_command(clean_mac, "stl", {"state": "on", "duration": 300})
        await self.send_toniebox_command(clean_mac, "sleep")

    # ------------------------------------------------------------------
    # Internal connection lifecycle
    # ------------------------------------------------------------------

    async def _do_connect(self) -> None:
        """
        Open the WebSocket, perform the MQTT handshake, and start I/O tasks.

        This is called both on the initial ``connect()`` and after each
        reconnection attempt.

        Raises:
            TonieConnectionError: On any connection or handshake failure.
        """
        auth_header = self._session.headers.get("Authorization")
        if not auth_header:
            raise TonieConnectionError("Missing Authorization header in session.")

        token = auth_header.replace("Bearer ", "")
        user = await self._client.tonies.get_user_details()
        client_id = f"{user.uuid}_com.tonies.app_2.153.2_{uuid.uuid4()}"

        log.debug(f"Connecting to {WEBSOCKET_URL} with subprotocol 'mqtt'")
        try:
            self._ws = await websockets.connect(
                str(WEBSOCKET_URL),
                additional_headers={"Authorization": auth_header},
                subprotocols=["mqtt"],  # type: ignore
            )
        except Exception as exc:
            raise TonieConnectionError(f"WebSocket handshake failed: {exc}") from exc

        # MQTT CONNECT
        connect_packet = self._create_connect_packet(client_id, user.uuid, token)
        await self._ws.send(connect_packet)  # type: ignore

        # MQTT CONNACK
        try:
            connack = await asyncio.wait_for(self._ws.recv(), timeout=10.0)  # type: ignore
        except asyncio.TimeoutError as exc:
            raise TonieConnectionError("Timeout waiting for MQTT CONNACK") from exc

        if not isinstance(connack, bytes) or connack[0] != 0x20 or connack[3] != 0x00:
            rc = connack[3] if isinstance(connack, bytes) and len(connack) > 3 else "unknown"
            raise TonieConnectionError(f"MQTT CONNACK rejected. Return code: {rc}")

        self._is_running = True
        log.info("Connected and authenticated to Tonies ICI server")

        # Re-subscribe to all previously known topics (no-op on first connect)
        if self._subscribed_topics:
            packet = self._create_subscribe_packet(self._subscribed_topics)
            await self._ws.send(packet)
            log.debug(f"Re-subscribed to {len(self._subscribed_topics)} topic(s) after (re)connect")

        # Start I/O background tasks
        self._listen_task = asyncio.create_task(self._listen_loop())
        self._ping_task = asyncio.create_task(self._ping_loop())

    async def _teardown(self) -> None:
        """Cancel I/O tasks and close the WebSocket cleanly."""
        self._is_running = False

        if self._ping_task and not self._ping_task.done():
            self._ping_task.cancel()
            try:
                await self._ping_task
            except asyncio.CancelledError:
                pass
        self._ping_task = None

        if self._listen_task and not self._listen_task.done():
            self._listen_task.cancel()
            try:
                await self._listen_task
            except asyncio.CancelledError:
                pass
        self._listen_task = None

        if self._ws:
            try:
                await self._ws.close()
            except Exception:
                pass
            self._ws = None

    async def _reconnect_loop(self) -> None:
        """
        Supervisor task: waits for the listen task to finish, then reconnects
        with exponential backoff — unless ``_disconnecting`` is True.
        """
        attempt = 0
        while not self._disconnecting:
            # Wait until the current listen task exits (connection dropped)
            if self._listen_task:
                try:
                    await self._listen_task
                except asyncio.CancelledError:
                    break

            if self._disconnecting:
                break

            # Compute delay: 2 s, 4 s, 8 s … up to 120 s
            delay = min(_RECONNECT_BASE_DELAY * (2 ** attempt), _RECONNECT_MAX_DELAY)
            attempt += 1

            if _RECONNECT_MAX_RETRIES and attempt > _RECONNECT_MAX_RETRIES:
                log.error(
                    "WebSocket: maximum reconnection attempts (%d) reached. Giving up.",
                    _RECONNECT_MAX_RETRIES,
                )
                break

            log.warning(
                "WebSocket connection lost. Reconnecting in %.0f s (attempt %d)…",
                delay,
                attempt,
            )
            await asyncio.sleep(delay)

            if self._disconnecting:
                break

            await self._teardown()

            try:
                # Refresh the access token before reconnecting — the previous
                # one may have expired while we were disconnected.
                await self._client.auth.refresh()
                new_token = self._client.auth.access_token
                self._session.headers["Authorization"] = f"Bearer {new_token}"

                await self._do_connect()
                log.info("WebSocket reconnected successfully (attempt %d).", attempt)
                attempt = 0   # reset backoff counter on success
            except Exception as exc:
                log.error("Reconnection attempt %d failed: %s", attempt, exc)
                # Loop continues — next iteration will wait longer

    # ------------------------------------------------------------------
    # I/O loops
    # ------------------------------------------------------------------

    async def _listen_loop(self) -> None:
        """Receive MQTT messages until the connection closes."""
        try:
            while self._is_running and self._ws:
                message = await self._ws.recv()
                if isinstance(message, bytes):
                    self._handle_binary_message(message)
                else:
                    self._handle_event({"topic": "raw/text", "payload": json.loads(message)})
        except websockets.exceptions.ConnectionClosed as exc:
            log.warning("WebSocket connection closed: %s", exc)
        except asyncio.CancelledError:
            raise   # let asyncio handle task cancellation normally
        except Exception as exc:
            log.error("Unexpected error in WebSocket listener: %s", exc)
        finally:
            self._is_running = False

    async def _ping_loop(self) -> None:
        """Send periodic MQTT PINGREQ every 60 s."""
        try:
            while self._is_running and self._ws:
                await asyncio.sleep(60)
                if self._ws and self._is_running:
                    await self._ws.send(b"\xc0\x00")
        except asyncio.CancelledError:
            raise
        except Exception:
            pass

    # ------------------------------------------------------------------
    # Event dispatch
    # ------------------------------------------------------------------

    def _handle_binary_message(self, message: bytes) -> None:
        """Dispatch an incoming binary MQTT packet."""
        packet_type = message[0] & 0xF0
        if packet_type == 0x30:  # PUBLISH
            self._parse_publish_packet(message)
        elif packet_type == 0xD0:  # PINGRESP
            log.debug("MQTT PINGRESP received")

    def _parse_publish_packet(self, packet: bytes) -> None:
        """Parse an MQTT PUBLISH packet and dispatch the payload."""
        try:
            pos = 1
            while packet[pos] & 0x80:
                pos += 1
            pos += 1
            topic_len = int.from_bytes(packet[pos:pos + 2], byteorder="big")
            pos += 2
            topic = packet[pos:pos + topic_len].decode("utf-8")
            pos += topic_len
            payload_raw = packet[pos:]
            json_start = payload_raw.find(b"{")
            if json_start != -1:
                data = json.loads(payload_raw[json_start:].decode("utf-8"))
                self._handle_event({"topic": topic, "payload": data})
        except Exception as exc:
            log.error("Failed to parse PUBLISH packet: %s", exc)

    def _handle_event(self, data: dict) -> None:
        """Dispatch an event dict to all registered callbacks."""
        topic = data.get("topic", "unknown")
        payload = data.get("payload", data)
        for callback in self._callbacks:
            if asyncio.iscoroutinefunction(callback):
                asyncio.create_task(callback(topic, payload))
            else:
                callback(topic, payload)

    # ------------------------------------------------------------------
    # MQTT packet builders
    # ------------------------------------------------------------------

    def _create_connect_packet(self, client_id: str, username: str, token: str) -> bytes:
        """Build a binary MQTT 3.1 CONNECT packet."""
        def encode_str(s: str) -> bytes:
            b = s.encode("utf-8")
            return len(b).to_bytes(2, "big") + b

        var_header = encode_str("MQIsdp") + b"\x03\xc2" + (60).to_bytes(2, "big")
        payload = encode_str(client_id) + encode_str(username) + encode_str(token)
        packet = b"\x10"
        rem_len = len(var_header) + len(payload)
        while True:
            digit = rem_len % 128
            rem_len //= 128
            if rem_len > 0:
                digit |= 128
            packet += digit.to_bytes(1, "big")
            if rem_len <= 0:
                break
        return packet + var_header + payload

    def _create_subscribe_packet(self, topics: list[str]) -> bytes:
        """Build a binary MQTT SUBSCRIBE packet."""
        self._packet_id = (self._packet_id + 1) % 65535
        var_header = self._packet_id.to_bytes(2, "big")
        payload = b""
        for topic in topics:
            b = topic.encode("utf-8")
            payload += len(b).to_bytes(2, "big") + b + b"\x00"
        packet = b"\x82"
        rem_len = len(var_header) + len(payload)
        temp_len = rem_len
        while True:
            digit = temp_len % 128
            temp_len //= 128
            if temp_len > 0:
                digit |= 128
            packet += digit.to_bytes(1, "big")
            if temp_len <= 0:
                break
        return packet + var_header + payload

    def _create_publish_packet(self, topic: str, payload_dict: dict) -> bytes:
        """Build a binary MQTT 3.1 PUBLISH packet with QoS 1."""
        self._packet_id = (self._packet_id + 1) % 65535
        topic_bytes = topic.encode("utf-8")
        variable_header = len(topic_bytes).to_bytes(2, "big") + topic_bytes
        variable_header += self._packet_id.to_bytes(2, "big")
        payload_bytes = json.dumps(payload_dict, separators=(",", ":")).encode("utf-8")
        remaining_length = len(variable_header) + len(payload_bytes)
        packet = bytearray([0x32])  # PUBLISH, QoS 1
        temp_len = remaining_length
        while True:
            digit = temp_len % 128
            temp_len //= 128
            if temp_len > 0:
                digit |= 128
            packet.append(digit)
            if temp_len <= 0:
                break
        return bytes(packet) + variable_header + payload_bytes