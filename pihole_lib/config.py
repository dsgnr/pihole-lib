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

    def get_config(self) -> dict[str, Any]:
        """Get current Pi-hole configuration.

        Retrieves the complete configuration of your Pi-hole instance,
        including DNS settings, DHCP configuration, web server settings,
        and various other options.

        Returns:
            Dictionary containing the complete Pi-hole configuration.
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

            # Access DNS settings
            dns_config = config_data['dns']
            print(f"Upstream DNS servers: {dns_config['upstreams']}")
            print(f"Query logging: {dns_config['queryLogging']}")

            # Access DHCP settings
            dhcp_config = config_data['dhcp']
            print(f"DHCP enabled: {dhcp_config['active']}")

            # Access web server settings
            web_config = config_data['webserver']
            print(f"Web domain: {web_config['domain']}")
            ```
        """
        response = make_pihole_request(
            self._client,
            "GET",
            API_CONFIG,
        )

        result: dict[str, Any] = response.json()
        config_data: dict[str, Any] = result["config"]
        return config_data
