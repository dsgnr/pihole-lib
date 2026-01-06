"""Pi-hole API client."""

from typing import Any, Optional

import requests

from .exceptions import (
    PiHoleAPIError,
    PiHoleAuthenticationError,
    PiHoleConnectionError,
    PiHoleServerError,
)


class PiHoleClient:
    """Pi-hole API client.

    Handles authentication and session management for Pi-hole API interactions.
    Can be used as a context manager for automatic cleanup.

    Examples:
        ```python
        with PiHoleClient("http://192.168.1.100", password="secret") as client:
            # Perform operations
            pass
        ```
    """

    def __init__(
        self,
        base_url: str,
        password: str,
        timeout: int = 30,
        verify_ssl: bool = True,
    ) -> None:
        """Initialize a Pi-hole client.

        Args:
            base_url: Pi-hole base URL (e.g., "http://192.168.1.100").
            password: Pi-hole admin password.
            timeout: Request timeout in seconds. Defaults to 30.
            verify_ssl: Whether to verify SSL certificates. Defaults to True.
        """
        self.base_url = base_url
        self._password = password
        self._session_id: Optional[str] = None
        self.timeout = timeout
        self.verify_ssl = verify_ssl
        self._session: Optional[requests.Session] = None

    def __enter__(self) -> "PiHoleClient":
        """Enter context manager and authenticate.

        Returns:
            The authenticated client instance.
        """
        self._ensure_session()
        self._authenticate()
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Exit context manager and clean up resources."""
        self.close()

    def _ensure_session(self) -> None:
        """Ensure HTTP session exists."""
        if self._session is None:
            self._session = requests.Session()
            self._session.verify = self.verify_ssl

    def close(self) -> None:
        """Close session and clean up resources."""
        if self._session_id:
            self._delete_session()
        if self._session:
            self._session.close()
            self._session = None

    def _authenticate(self) -> None:
        """Authenticate with Pi-hole.

        Raises:
            PiHoleAuthenticationError: Authentication failed.
            PiHoleConnectionError: Connection failed.
            PiHoleServerError: Server error.
            PiHoleAPIError: Other API errors.
        """
        self._ensure_session()
        assert self._session is not None

        auth_url = f"{self.base_url}/api/auth"

        try:
            response = self._session.post(
                auth_url, json={"password": self._password}, timeout=self.timeout
            )

            # Handle different error responses from Pi-hole
            status_errors = {
                400: PiHoleAPIError("Bad request - missing parameter"),
                401: PiHoleAuthenticationError("Invalid credentials"),
                402: PiHoleAPIError("Request failed"),
                403: PiHoleAuthenticationError("Access denied"),
                404: PiHoleAPIError("Endpoint not found"),
            }

            if response.status_code in status_errors:
                raise status_errors[response.status_code]
            elif response.status_code == 429:
                # Pi-hole is rate limiting requests - attempt retry after brief delay
                import time

                time.sleep(1)
                response = self._session.post(
                    auth_url, json={"password": self._password}, timeout=self.timeout
                )
                if response.status_code == 429:
                    raise PiHoleAPIError("Too many requests")
            elif response.status_code >= 500:
                raise PiHoleServerError(f"Server error: {response.status_code}")
            elif response.status_code != 200:
                response.raise_for_status()

            data = response.json()
            session = data.get("session", {})

            if not session.get("valid"):
                raise PiHoleAuthenticationError("Login failed")

            self._session_id = session.get("sid")

            if not self._session_id:
                raise PiHoleAuthenticationError("No session ID received")

        except requests.RequestException as e:
            raise PiHoleConnectionError(f"Connection failed: {e}") from e

    def _delete_session(self) -> None:
        """Delete Pi-hole session."""
        if not self._session_id or not self._session:
            return

        try:
            auth_url = f"{self.base_url}/api/auth"
            self._session.delete(
                auth_url, headers={"X-FTL-SID": self._session_id}, timeout=self.timeout
            )
        except Exception:
            # If logout fails, that's acceptable - cleanup continues regardless
            pass
        finally:
            self._session_id = None

    def is_authenticated(self) -> bool:
        """Check if client is authenticated.

        Returns:
            True if authenticated, False otherwise.
        """
        return self._session_id is not None

    def get_session_id(self) -> Optional[str]:
        """Get current session ID.

        Returns:
            Session ID if authenticated, None otherwise.
        """
        return self._session_id
