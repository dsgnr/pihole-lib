"""Pi-hole API client."""

from typing import Any

import requests

from .constants import API_AUTH, DEFAULT_TIMEOUT, HEADER_SESSION_ID
from .exceptions import PiHoleAuthenticationError
from .utils import make_pihole_request

# Dynamic API client configuration
# Maps property names to their corresponding module and class information
API_CLIENTS = {
    "info": {
        "module": "info",
        "class": "PiHoleInfo",
        "description": "system information operations",
    },
    "actions": {
        "module": "actions",
        "class": "PiHoleActions",
        "description": "system actions",
    },
    "backup": {
        "module": "backup",
        "class": "PiHoleBackup",
        "description": "backup operations",
    },
    "config": {
        "module": "config",
        "class": "PiHoleConfig",
        "description": "configuration management",
    },
    "dhcp": {
        "module": "dhcp",
        "class": "PiHoleDHCP",
        "description": "DHCP operations",
    },
    "dns": {
        "module": "dns",
        "class": "PiHoleDNS",
        "description": "DNS operations",
    },
    "lists": {
        "module": "lists",
        "class": "PiHoleLists",
        "description": "domain list operations",
    },
    "groups": {
        "module": "groups",
        "class": "PiHoleGroups",
        "description": "group management operations",
    },
    "padd": {
        "module": "padd",
        "class": "PiHolePADD",
        "description": "PADD dashboard operations",
    },
}


def _create_api_property(property_name: str, config: dict[str, str]) -> property:
    """Create a dynamic property for an API client.

    Args:
        property_name: Name of the property (e.g., 'info', 'actions')
        config: Configuration dict with 'module', 'class', and 'description'

    Returns:
        Property object that lazy-loads the API client
    """
    cache_attr = f"_{property_name}"
    module_name = config["module"]
    class_name = config["class"]
    description = config["description"]

    def getter(self: "PiHoleClient") -> Any:
        # Check if already cached
        if not hasattr(self, cache_attr) or getattr(self, cache_attr) is None:
            # Dynamic import and instantiation
            module = __import__(f"pihole_lib.{module_name}", fromlist=[class_name])
            api_class = getattr(module, class_name)
            setattr(self, cache_attr, api_class(self))
        return getattr(self, cache_attr)

    getter.__doc__ = f"""Get Pi-hole {property_name} API client.

        Returns:
            {class_name} instance for {description}.
        """

    return property(getter)


class PiHoleClient:
    """Pi-hole API client.

    Handles authentication and session management for Pi-hole API interactions.
    Can be used as a context manager for automatic cleanup.

    Examples:
        ```python
        # Basic usage with property access
        with PiHoleClient("http://192.168.1.100", password="secret") as client:
            # Get system information
            login_info = client.info.get_login_info()

            # Perform actions
            for line in client.actions.update_gravity():
                print(line.strip())

            # Manage lists
            all_lists = client.lists.get_lists()

            # Configuration management
            current_config = client.config.get_config()

        # Alternative usage with explicit class imports
        from pihole_lib import PiHoleInfo, PiHoleActions

        with PiHoleClient("http://192.168.1.100", password="secret") as client:
            info = PiHoleInfo(client)
            actions = PiHoleActions(client)
        ```
    """

    def __init__(
        self,
        base_url: str,
        password: str,
        timeout: int = DEFAULT_TIMEOUT,
        verify_ssl: bool = True,
    ) -> None:
        """Initialize a Pi-hole client.

        Args:
            base_url: Pi-hole base URL (e.g., "http://192.168.1.100").
            password: Pi-hole admin password.
            timeout: Request timeout in seconds. Defaults to 30.
            verify_ssl: Whether to verify SSL certificates. Defaults to True.
        """
        self.base_url = base_url.rstrip("/")  # Remove trailing slash for consistency
        self._password = password
        self._session_id: str | None = None
        self.timeout = timeout
        self.verify_ssl = verify_ssl
        self._session: requests.Session | None = None

        # Initialize cache attributes for all API clients
        for property_name in API_CLIENTS:
            setattr(self, f"_{property_name}", None)

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

        # Update session headers with authentication if available
        if self._session_id and self._session:
            self._session.headers.update({HEADER_SESSION_ID: self._session_id})

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

        # First attempt
        response = make_pihole_request(
            self,
            "POST",
            API_AUTH,
            json={"password": self._password},
        )

        # Handle rate limiting with retry
        if response.status_code == 429:
            import time

            time.sleep(1)
            response = make_pihole_request(
                self,
                "POST",
                API_AUTH,
                json={"password": self._password},
            )

        data = response.json()
        session = data.get("session", {})

        if not session.get("valid"):
            raise PiHoleAuthenticationError("Login failed")

        self._session_id = session.get("sid")

        if not self._session_id:
            raise PiHoleAuthenticationError("No session ID received")

        # Update session headers with the new authentication
        self._ensure_session()

    def _delete_session(self) -> None:
        """Delete Pi-hole session."""
        if not self._session_id or not self._session:
            return

        try:
            auth_url = f"{self.base_url}{API_AUTH}"
            self._session.delete(
                auth_url,
                headers={HEADER_SESSION_ID: self._session_id},
                timeout=self.timeout,
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

    def get_session_id(self) -> str | None:
        """Get current session ID.

        Returns:
            Session ID if authenticated, None otherwise.
        """
        return self._session_id


# Dynamically create properties for all API clients
for prop_name, prop_config in API_CLIENTS.items():
    setattr(PiHoleClient, prop_name, _create_api_property(prop_name, prop_config))
