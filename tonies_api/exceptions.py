class ToniesApiError(Exception):
    """Base exception for the Tonies API client."""


class TonieAuthError(ToniesApiError):
    """Exception for authentication errors."""


class TonieConnectionError(ToniesApiError):
    """Exception for connection errors."""