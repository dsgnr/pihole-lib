"""Pi-hole Config API client."""

from typing import Any
from urllib.parse import quote

from pihole_lib.base import BasePiHoleAPIClient
from pihole_lib.utils import make_pihole_request


class PiHoleConfig(BasePiHoleAPIClient):
    """Pi-hole Config API client.

    Handles configuration endpoints for Pi-hole settings.

    Examples::

        from pihole_lib import PiHoleClient

        with PiHoleClient("http://192.168.1.100", password="secret") as client:
            # Get current configuration
            config = client.config.get_config()
            print(f"DNS upstreams: {config['dns']['upstreams']}")

            # Update configuration
            client.config.update_config({"dns": {"upstreams": ["1.1.1.1"]}})

            # Add/remove config items
            client.config.add_config_item("dns/upstreams", "8.8.8.8")
            client.config.remove_config_item("dns/upstreams", "8.8.8.8")

    """

    BASE_URL = "/api/config"

    def get_config(
        self, element: str | None = None, detailed: bool = True
    ) -> dict[str, Any]:
        """Get Pi-hole configuration.

        Args:
            element: Optional configuration element path (e.g., 'dns', 'dhcp').
                    If None, returns the complete configuration.
            detailed: Return detailed information (defaults to True).

        Returns:
            Dictionary containing the Pi-hole configuration.
        """
        endpoint = f"{self.BASE_URL}/{element}" if element else self.BASE_URL

        # Only pass params if we have an element and detailed is False
        if element and not detailed:
            response = make_pihole_request(
                self._client,
                "GET",
                endpoint,
                params={"detailed": detailed},
            )
        else:
            response = make_pihole_request(
                self._client,
                "GET",
                endpoint,
            )
        result: dict[str, Any] = response.json()
        return dict(result["config"])

    def update_config(
        self,
        config: dict[str, Any],
        restart: bool = True,
    ) -> dict[str, Any]:
        """Update Pi-hole configuration.

        Args:
            config: Configuration dictionary with settings to update.
            restart: Whether to restart FTL after the change (defaults to True).

        Returns:
            Dictionary containing the updated configuration.
        """
        response = make_pihole_request(
            self._client,
            "PATCH",
            self.BASE_URL,
            params={"restart": restart},
            json={"config": config},
        )
        result: dict[str, Any] = response.json()
        return dict(result["config"])

    def add_config_item(
        self,
        element: str,
        value: str,
        restart: bool = True,
    ) -> bool:
        """Add an item to a configuration array.

        Args:
            element: Configuration element path (e.g., 'dns/upstreams').
            value: Value to add to the configuration array.
            restart: Whether to restart FTL after the change (defaults to True).

        Returns:
            True if the item was successfully added.
        """
        encoded_element = quote(element, safe="")
        encoded_value = quote(value, safe="")
        endpoint = f"{self.BASE_URL}/{encoded_element}/{encoded_value}"

        response = make_pihole_request(
            self._client,
            "PUT",
            endpoint,
            params={"restart": restart},
        )
        return bool(response.status_code == 201)

    def remove_config_item(
        self,
        element: str,
        value: str,
        restart: bool = True,
    ) -> bool:
        """Remove an item from a configuration array.

        Args:
            element: Configuration element path (e.g., 'dns/upstreams').
            value: Value to remove from the configuration array.
            restart: Whether to restart FTL after the change (defaults to True).

        Returns:
            True if the item was successfully removed.
        """
        encoded_element = quote(element, safe="")
        encoded_value = quote(value, safe="")
        endpoint = f"{self.BASE_URL}/{encoded_element}/{encoded_value}"

        response = make_pihole_request(
            self._client,
            "DELETE",
            endpoint,
            params={"restart": restart},
        )
        return bool(response.status_code == 204)
