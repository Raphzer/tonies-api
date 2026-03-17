import logging
import time
from typing import Self
from urllib.parse import parse_qs, urlparse

import httpx
from bs4 import BeautifulSoup

from .const import CLIENT_ID, OAUTH_URL, REDIRECT_URI, SCOPE, TOKEN_PATH, AUTH_BASE_URL
from .exceptions import TonieAuthError

log = logging.getLogger(__name__)

# Renew the token this many seconds before it actually expires, to avoid
# race conditions on slow networks.
_TOKEN_EXPIRY_MARGIN = 30


class TonieAuth:
    """Handles authentication for the Tonies API using Keycloak."""

    def __init__(self, username: str, password: str, session: httpx.AsyncClient):
        """
        Initialize the authentication handler.

        Args:
            username: The Tonies account username.
            password: The Tonies account password.
            session: An httpx.AsyncClient session.
        """
        self.username = username
        self.password = password
        self._session = session
        self.access_token: str | None = None
        self.refresh_token: str | None = None
        self.id_token: str | None = None
        self._access_token_expires_at: float = 0.0
        self._refresh_token_expires_at: float = 0.0

    async def login(self) -> Self:
        """
        Log in to the Tonies API and retrieve tokens.

        Returns:
            The authenticated TonieAuth instance.

        Raises:
            TonieAuthError: If login fails.
        """
        log.debug("Starting authentication flow.")
        try:
            response = await self._session.get(OAUTH_URL)
            response.raise_for_status()
        except httpx.HTTPError as exc:
            raise TonieAuthError("Failed to get login page") from exc

        soup = BeautifulSoup(response.text, "html.parser")
        form = soup.find("form", id="kc-form-login")
        if not form or not form.has_attr("action"):
            raise TonieAuthError("Could not find login form or action URL")

        action_url = form["action"]
        log.debug(f"Found login form action URL: {action_url}")

        data = {
            "username": self.username,
            "password": self.password,
        }
        try:
            response = await self._session.post(
                str(action_url),
                data=data,
            )
            # Don't raise for status here, as a 302 is expected on success
        except httpx.HTTPError as exc:
            raise TonieAuthError("Failed to submit login form") from exc

        if response.status_code == 302:
            redirect_url = response.headers.get("Location")
            if not redirect_url:
                raise TonieAuthError("Login failed, no redirect URL found after form submission")
            log.debug(f"Redirected to: {redirect_url}")

            parsed_redirect_url = urlparse(redirect_url)
            query_params = parse_qs(parsed_redirect_url.query)
            code = query_params.get("code", [None])[0]

            if not code:
                raise TonieAuthError(f"Login failed, no authorization code found in redirect URL: {redirect_url}")
            log.debug(f"Extracted authorization code: {code[:10]}...")

            token_url = f"{AUTH_BASE_URL}{TOKEN_PATH}"
            token_data = {
                "grant_type": "authorization_code",
                "client_id": CLIENT_ID,
                "scope": SCOPE,
                "redirect_uri": REDIRECT_URI,
                "code": code,
            }
            try:
                token_response = await self._session.post(token_url, data=token_data)
                token_response.raise_for_status()
                tokens = token_response.json()

                self._save_tokens(tokens)

                if not self.access_token:
                    raise TonieAuthError("Failed to retrieve access token from token endpoint")

                log.debug("Successfully retrieved access token.")
                return self

            except httpx.HTTPError as exc:
                raise TonieAuthError("Failed to exchange authorization code for tokens") from exc

        else:
            soup = BeautifulSoup(response.text, "html.parser")
            error_element = soup.find("span", id="kc-feedback-text")
            if error_element:
                error_message = error_element.text.strip()
                log.error(f"Login failed with message: {error_message}")
                raise TonieAuthError(f"Login failed: {error_message}")
            else:
                log.error("Login failed for an unknown reason.")
                raise TonieAuthError("Login failed for an unknown reason")

    def _save_tokens(self, tokens: dict) -> None:
        """
        Persist tokens and compute their expiry timestamps.

        Args:
            tokens: Raw JSON response from the token endpoint.
        """
        now = time.monotonic()
        self.access_token = tokens.get("access_token")
        self.refresh_token = tokens.get("refresh_token")
        self.id_token = tokens.get("id_token")

        expires_in: int = tokens.get("expires_in", 300)
        refresh_expires_in: int = tokens.get("refresh_expires_in", 1800)

        self._access_token_expires_at = now + expires_in - _TOKEN_EXPIRY_MARGIN
        # A refresh_expires_in of 0 means the refresh token never expires
        # (offline_access scope). Treat it as effectively infinite.
        if refresh_expires_in > 0:
            self._refresh_token_expires_at = now + refresh_expires_in - _TOKEN_EXPIRY_MARGIN
        else:
            self._refresh_token_expires_at = float("inf")

    @property
    def is_access_token_expired(self) -> bool:
        """Return True if the access token is missing or past its expiry margin."""
        return self.access_token is None or time.monotonic() >= self._access_token_expires_at

    @property
    def is_refresh_token_expired(self) -> bool:
        """Return True if the refresh token is missing or past its expiry margin."""
        return self.refresh_token is None or time.monotonic() >= self._refresh_token_expires_at

    async def refresh(self) -> None:
        """
        Obtain a new access token.

        Tries the refresh token flow first. Falls back to a full re-login when
        the refresh token is itself expired or rejected by the server.

        Raises:
            TonieAuthError: If both the refresh and the re-login fail.
        """
        if not self.is_refresh_token_expired:
            log.debug("Attempting token refresh.")
            try:
                await self._do_refresh()
                return
            except TonieAuthError as exc:
                log.warning(f"Token refresh failed ({exc}), falling back to full re-login.")

        log.debug("Refresh token expired or unusable — performing full re-login.")
        await self.login()

    async def _do_refresh(self) -> None:
        """
        Exchange the refresh token for a new access token.

        Raises:
            TonieAuthError: If the token endpoint rejects the refresh token.
        """
        token_url = f"{AUTH_BASE_URL}{TOKEN_PATH}"
        token_data = {
            "grant_type": "refresh_token",
            "client_id": CLIENT_ID,
            "refresh_token": self.refresh_token,
        }
        try:
            response = await self._session.post(token_url, data=token_data)
            response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            # 400 Bad Request typically means the refresh token is invalid/expired.
            raise TonieAuthError(
                f"Refresh token rejected by server (HTTP {exc.response.status_code})"
            ) from exc
        except httpx.HTTPError as exc:
            raise TonieAuthError("Network error during token refresh") from exc

        tokens = response.json()
        self._save_tokens(tokens)

        if not self.access_token:
            raise TonieAuthError("Token endpoint returned no access token during refresh")

        log.debug("Token refreshed successfully.")