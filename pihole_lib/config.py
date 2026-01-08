"""Pi-hole Config API client."""

from typing import Any
from urllib.parse import quote

from .base import BasePiHoleAPIClient
from .utils import make_pihole_request


class PiHoleConfig(BasePiHoleAPIClient):
    """Pi-hole Config API client.

    Handles configuration endpoints for Pi-hole settings.
    Uses a PiHoleClient instance for making authenticated requests.

    Examples::

        from pihole_lib import PiHoleClient, PiHoleConfig

        with PiHoleClient("http://192.168.1.100", password="secret") as client:
            config = PiHoleConfig(client)

            # Get current configuration
            current_config = config.get_config()
            print(f"DNS upstreams: {current_config['dns']['upstreams']}")
            print(f"DHCP active: {current_config['dhcp']['active']}")

            # Update configuration
            new_config = {
                "dns": {
                    "upstreams": ["1.1.1.1", "1.0.0.1"],
                    "queryLogging": True
                }
            }
            updated_config = config.update_config(new_config)

            # Add upstream DNS server
            config.add_config_item("dns/upstreams", "8.8.8.8")

            # Remove upstream DNS server
            config.remove_config_item("dns/upstreams", "8.8.8.8")

    """

    BASE_URL = "/api/config"

    def get_config(
        self, element: str | None = None, detailed: bool = True
    ) -> dict[str, Any]:
        """Get Pi-hole configuration.

        Retrieves the complete configuration or a specific subset of your Pi-hole instance.

        Args:
            element: Optional configuration element path (e.g., 'dns', 'dns/upstreams', 'dhcp').
                    If None, returns the complete configuration.
            detailed: Return detailed information about the configuration (defaults to True).

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

        Examples::

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

        """
        # Build the endpoint URL
        endpoint = self.BASE_URL if element is None else f"{self.BASE_URL}/{element}"

        # Only pass detailed parameter if it's not the default (True) and we have an element
        params = (
            {"detailed": detailed}
            if element is not None and detailed is False
            else None
        )

        if params is not None:
            response = make_pihole_request(
                self._client,
                "GET",
                endpoint,
                params=params,
            )
        else:
            response = make_pihole_request(
                self._client,
                "GET",
                endpoint,
            )

        result: dict[str, Any] = response.json()
        config_data: dict[str, Any] = result["config"]
        return config_data

    def update_config(
        self,
        config: dict[str, Any],
        restart: bool = True,
    ) -> dict[str, Any]:
        """Update Pi-hole configuration.

        This API hook allows to modify the config of your Pi-hole. This endpoint supports
        changing multiple properties at once when you specify several in the payload.

        Args:
            config: Configuration dictionary with the settings to update.
                   Should follow the structure: {"dns": {...}, "dhcp": {...}, etc.}
            restart: Whether to restart FTL after the change (defaults to True).
                    Set to False if you want to avoid a restart when making multiple
                    independent changes. You will need to restart FTL manually later.

        Returns:
            Dictionary containing the updated Pi-hole configuration.

        Raises:
            PiHoleConnectionError: Connection failed.
            PiHoleAuthenticationError: Authentication failed.
            PiHoleServerError: Server error.
            PiHoleAPIError: Other API errors.

        Examples::

            # Update DNS settings
            new_config = {
                "dns": {
                    "upstreams": ["1.1.1.1", "1.0.0.1"],
                    "queryLogging": True,
                    "dnssec": True
                }
            }
            updated_config = config.update_config(new_config)

            # Update DHCP settings
            dhcp_config = {
                "dhcp": {
                    "active": True,
                    "start": "192.168.1.100",
                    "end": "192.168.1.200",
                    "router": "192.168.1.1",
                    "netmask": "255.255.255.0",
                    "leaseTime": "24h"
                }
            }
            updated_config = config.update_config(dhcp_config)

            # Update multiple sections at once
            multi_config = {
                "dns": {
                    "upstreams": ["8.8.8.8", "8.8.4.4"],
                    "port": 53
                },
                "webserver": {
                    "port": "80o,443os"
                }
            }
            updated_config = config.update_config(multi_config)

            # Update without restarting FTL (for batch operations)
            config.update_config({"dns": {"upstreams": ["1.1.1.1"]}}, restart=False)
            config.update_config({"dns": {"port": 5353}}, restart=False)
            # Restart FTL manually later or with the final update
            config.update_config({"dns": {"queryLogging": False}}, restart=True)

        """
        params = {"restart": restart}
        payload = {"config": config}

        response = make_pihole_request(
            self._client,
            "PATCH",
            self.BASE_URL,
            params=params,
            json=payload,
        )

        result: dict[str, Any] = response.json()
        config_data: dict[str, Any] = result["config"]
        return config_data

    def add_config_item(
        self,
        element: str,
        value: str,
        restart: bool = True,
    ) -> bool:
        """Add an item to a configuration array.

        Adds a single value to a configuration array element (e.g., adding an upstream
        DNS server to the upstreams list).

        Args:
            element: Configuration element path (e.g., 'dns/upstreams', 'webserver/headers').
            value: Value to add to the configuration array.
            restart: Whether to restart FTL after the change (defaults to True).

        Returns:
            True if the item was successfully added.

        Raises:
            PiHoleConnectionError: Connection failed.
            PiHoleAuthenticationError: Authentication failed.
            PiHoleServerError: Server error.
            PiHoleAPIError: Other API errors.

        Examples::

            # Add upstream DNS server
            success = config.add_config_item("dns/upstreams", "1.1.1.1")
            print(f"Added upstream: {success}")

            # Add custom DNS host entry
            success = config.add_config_item("dns/hosts", "192.168.1.10 myserver.local")

            # Add web server header
            success = config.add_config_item(
                "webserver/headers",
                "X-Custom-Header: MyValue"
            )

            # Add DHCP static host entry
            success = config.add_config_item(
                "dhcp/hosts",
                "12:34:56:78:9A:BC,192.168.1.50,laptop"
            )

            # Add without restarting FTL
            success = config.add_config_item("dns/upstreams", "8.8.8.8", restart=False)

        """
        # URL encode the element and value for safe transmission
        encoded_element = quote(element, safe="")
        encoded_value = quote(value, safe="")

        endpoint = f"{self.BASE_URL}/{encoded_element}/{encoded_value}"
        params = {"restart": restart}

        response = make_pihole_request(
            self._client,
            "PUT",
            endpoint,
            params=params,
        )

        # Pi-hole returns 201 Created on successful addition
        return response.status_code == 201

    def remove_config_item(
        self,
        element: str,
        value: str,
        restart: bool = True,
    ) -> bool:
        """Remove an item from a configuration array.

        Removes a single value from a configuration array element (e.g., removing an
        upstream DNS server from the upstreams list).

        Args:
            element: Configuration element path (e.g., 'dns/upstreams', 'webserver/headers').
            value: Value to remove from the configuration array.
            restart: Whether to restart FTL after the change (defaults to True).

        Returns:
            True if the item was successfully removed.

        Raises:
            PiHoleConnectionError: Connection failed.
            PiHoleAuthenticationError: Authentication failed.
            PiHoleServerError: Server error.
            PiHoleAPIError: Other API errors.

        Examples::

            # Remove upstream DNS server
            success = config.remove_config_item("dns/upstreams", "8.8.8.8")
            print(f"Removed upstream: {success}")

            # Remove custom DNS host entry
            success = config.remove_config_item("dns/hosts", "192.168.1.10 myserver.local")

            # Remove web server header
            success = config.remove_config_item(
                "webserver/headers",
                "X-Custom-Header: MyValue"
            )

            # Remove DHCP static host entry
            success = config.remove_config_item(
                "dhcp/hosts",
                "12:34:56:78:9A:BC,192.168.1.50,laptop"
            )

            # Remove without restarting FTL
            success = config.remove_config_item("dns/upstreams", "1.1.1.1", restart=False)

        """
        # URL encode the element and value for safe transmission
        encoded_element = quote(element, safe="")
        encoded_value = quote(value, safe="")

        endpoint = f"{self.BASE_URL}/{encoded_element}/{encoded_value}"
        params = {"restart": restart}

        response = make_pihole_request(
            self._client,
            "DELETE",
            endpoint,
            params=params,
        )

        # Pi-hole returns 204 No Content on success
        return response.status_code == 204
