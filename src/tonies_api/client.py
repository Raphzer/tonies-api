from types import TracebackType
from typing import Self

import httpx

from .auth import TonieAuth
from .tonies import TonieResources, TonieWebSocket

# Sentinel extension key used to prevent infinite retry loops.
_RETRIED_KEY = "token_refreshed"


class TonieAPIClient:
    """A client for the Tonies API."""

    def __init__(self, username: str, password: str) -> None:
        """
        Initialize the client.

        Args:
            username: The Tonies account username.
            password: The Tonies account password.
        """
        self._session = httpx.AsyncClient(event_hooks={"response": [self._on_response]})
        self.auth = TonieAuth(username, password, self._session)
        self.tonies = TonieResources(self._session)
        self.ws = TonieWebSocket(self)

    async def _on_response(self, response: httpx.Response) -> None:
        """
        httpx response hook: transparently refresh the access token on 401.

        The hook is called for every response before it is returned to the
        caller. When a 401 is received and this is not already a retry attempt,
        the token is refreshed, the session Authorization header is updated,
        and the original request is resent once with the new token.

        The retried response replaces the original in-place so the caller
        always receives the final result without any special handling.
        """
        if response.status_code != 401:
            return

        request = response.request
        if request.extensions.get(_RETRIED_KEY):
            # Already retried once — don't loop. Let the 401 propagate.
            return

        await response.aread()  # drain the response body before sending a new request

        await self.auth.refresh()
        new_token = self.auth.access_token
        self._session.headers["Authorization"] = f"Bearer {new_token}"

        # Build a copy of the original request with the updated Authorization
        # header and mark it as a retry to prevent infinite recursion.
        retried_request = request.copy(
            headers={**dict(request.headers), "Authorization": f"Bearer {new_token}"},
            extensions={**dict(request.extensions), _RETRIED_KEY: True},
        )
        retried_response = await self._session.send(retried_request)

        # Mutate the response object in-place so the caller sees the new result.
        response.__dict__.update(retried_response.__dict__)

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
        