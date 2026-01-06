"""Pi-hole API client."""

from typing import Any, Optional

import requests

from .exceptions import (
    PiHoleAuthenticationError,
)
from .utils import make_pihole_request


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

        # First attempt
        response = make_pihole_request(
            self._session,
            "POST",
            auth_url,
            endpoint_name="authentication",
            json={"password": self._password},
            timeout=self.timeout,
        )

        # Handle rate limiting with retry
        if response.status_code == 429:
            import time

            time.sleep(1)
            response = make_pihole_request(
                self._session,
                "POST",
                auth_url,
                endpoint_name="authentication",
                json={"password": self._password},
                timeout=self.timeout,
            )

        data = response.json()
        session = data.get("session", {})

        if not session.get("valid"):
            raise PiHoleAuthenticationError("Login failed")

        self._session_id = session.get("sid")

        if not self._session_id:
            raise PiHoleAuthenticationError("No session ID received")

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
