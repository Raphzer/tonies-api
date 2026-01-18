import logging
from typing import List
import httpx

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
