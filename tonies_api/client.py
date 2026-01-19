from types import TracebackType
from typing import Self

import httpx

from .auth import TonieAuth
from .tonies import TonieResources, TonieWebSocket


class TonieAPIClient:
    """A client for the Tonies API."""

    def __init__(self, username: str, password: str) -> None:
        """
        Initialize the client.

        Args:
            username: The Tonies account username.
            password: The Tonies account password.
        """
        self._session = httpx.AsyncClient()
        self.auth = TonieAuth(username, password, self._session)
        self.tonies = TonieResources(self._session)
        self.ws = TonieWebSocket(self)

    async def __aenter__(self) -> Self:
        """Enter the async context manager."""
        await self.auth.login()
        self._session.headers["Authorization"] = f"Bearer {self.auth.access_token}"
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        """Exit the async context manager."""
        await self._session.aclose()
