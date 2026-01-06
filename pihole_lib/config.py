"""Pi-hole Config API client."""

from typing import TYPE_CHECKING, Any

from .base import BasePiHoleAPIClient
from .constants import API_CONFIG
from .utils import make_pihole_request

if TYPE_CHECKING:
    pass


class PiHoleConfig(BasePiHoleAPIClient):
    """Pi-hole Config API client.

    Handles configuration endpoints for Pi-hole settings.
    Uses a PiHoleClient instance for making authenticated requests.

    Examples:
        ```python
        from pihole_lib import PiHoleClient, PiHoleConfig

        with PiHoleClient("http://192.168.1.100", password="secret") as client:
            config = PiHoleConfig(client)

            # Get current configuration
            current_config = config.get_config()
            print(f"DNS upstreams: {current_config['dns']['upstreams']}")
            print(f"DHCP active: {current_config['dhcp']['active']}")
        ```
    """

    def get_config(self, element: str | None = None) -> dict[str, Any]:
        """Get Pi-hole configuration.

        Retrieves the complete configuration or a specific subset of your Pi-hole instance.

        Args:
            element: Optional configuration element path (e.g., 'dns', 'dns/upstreams', 'dhcp').
                    If None, returns the complete configuration.

        Returns:
            Dictionary containing the Pi-hole configuration.
            If element is specified, returns only that subset.
            The structure includes sections like 'dns', 'dhcp', 'webserver',
            'files', 'misc', and 'debug'.

        Raises:
            PiHoleConnectionError: Connection failed.
            PiHoleAuthenticationError: Authentication failed.
            PiHoleServerError: Server error.
            PiHoleAPIError: Other API errors.

        Examples:
            ```python
            # Get full configuration
            config_data = config.get_config()
            dns_config = config_data['dns']
            print(f"Upstream DNS servers: {dns_config['upstreams']}")

            # Get only DNS configuration
            dns_config = config.get_config('dns')
            print(f"DNS settings: {dns_config['dns']}")

            # Get only upstream DNS servers
            upstreams = config.get_config('dns/upstreams')
            print(f"Upstream servers: {upstreams['dns']['upstreams']}")

            # Get DHCP configuration
            dhcp_config = config.get_config('dhcp')
            print(f"DHCP active: {dhcp_config['dhcp']['active']}")

            # Get web server configuration
            web_config = config.get_config('webserver')
            print(f"Web domain: {web_config['webserver']['domain']}")
            ```
        """
        # Build the endpoint URL
        endpoint = API_CONFIG if element is None else f"{API_CONFIG}/{element}"

        response = make_pihole_request(
            self._client,
            "GET",
            endpoint,
        )

        result: dict[str, Any] = response.json()
        config_data: dict[str, Any] = result["config"]
        return config_data
