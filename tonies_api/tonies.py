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
            raise TonieConnectionError(f"Failed to parse UserDetails data: {e}")

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
                return HouseholdMembersResponse(memberships=[], invitations=[], typename="")
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