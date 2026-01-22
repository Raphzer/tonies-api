import logging
from typing import Self
from urllib.parse import parse_qs, urlparse

import httpx
from bs4 import BeautifulSoup

from .const import CLIENT_ID, OAUTH_URL, REDIRECT_URI, SCOPE, TOKEN_PATH, AUTH_BASE_URL
from .exceptions import TonieAuthError

log = logging.getLogger(__name__)


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

                self.access_token = tokens.get("access_token")
                self.refresh_token = tokens.get("refresh_token")
                self.id_token = tokens.get("id_token")

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