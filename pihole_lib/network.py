"""Pi-hole network API client."""

from typing import TYPE_CHECKING

from .base import BasePiHoleAPIClient
from .models import (
    NetworkDeviceDeleteResponse,
    NetworkDevicesResponse,
    NetworkGatewayDetailedResponse,
    NetworkGatewayResponse,
    NetworkInterfacesResponse,
    NetworkRoutesResponse,
)
from .utils import make_pihole_request

if TYPE_CHECKING:
    pass


class PiHoleNetwork(BasePiHoleAPIClient):
    """Pi-hole network API client.

    Provides methods to gather advanced information about your network
    as seen by your Pi-hole.
    """

    BASE_URL = "/api/network"

    def get_devices(
        self,
        max_devices: int | None = None,
        max_addresses: int | None = None,
    ) -> NetworkDevicesResponse:
        """Get info about the devices in your local network as seen by your Pi-hole.

        By default, the number of shown devices is limited to 10. Devices are ordered
        by when your Pi-hole has received the last query from this device (most recent first).

        Args:
            max_devices: Maximum number of devices to show (optional).
            max_addresses: Maximum number of addresses to show per device (optional).

        Returns:
            NetworkDevicesResponse containing device information.

        Raises:
            PiHoleAPIError: API request failed.
            PiHoleAuthenticationError: Authentication failed.
            PiHoleConnectionError: Connection failed.
            PiHoleServerError: Server error.
        """
        params = {}
        if max_devices is not None:
            params["max_devices"] = max_devices
        if max_addresses is not None:
            params["max_addresses"] = max_addresses

        response = make_pihole_request(
            self._client,
            "GET",
            f"{self.BASE_URL}/devices",
            params=params,
        )
        return NetworkDevicesResponse.model_validate(response.json())

    def get_gateway(
        self, detailed: bool = False
    ) -> NetworkGatewayResponse | NetworkGatewayDetailedResponse:
        """Get info about the gateway of your Pi-hole.

        Args:
            detailed: If True, include detailed information about individual
                     interfaces and routes. Note that available information
                     is dependent on the interface type and state.

        Returns:
            NetworkGatewayResponse or NetworkGatewayDetailedResponse containing gateway information.

        Raises:
            PiHoleAPIError: API request failed.
            PiHoleAuthenticationError: Authentication failed.
            PiHoleConnectionError: Connection failed.
            PiHoleServerError: Server error.
        """
        params = {"detailed": detailed}
        response = make_pihole_request(
            self._client,
            "GET",
            f"{self.BASE_URL}/gateway",
            params=params,
        )

        if detailed:
            return NetworkGatewayDetailedResponse.model_validate(response.json())
        return NetworkGatewayResponse.model_validate(response.json())

    def get_interfaces(self, detailed: bool = False) -> NetworkInterfacesResponse:
        """Get info about the interfaces of your Pi-hole.

        Note that not all described fields are applicable to any routing type.
        Users must not rely on the presence of any field without checking the
        route type first.

        Args:
            detailed: If True, include more detailed information about individual
                     interfaces where available information is dependent on the
                     interface type and state.

        Returns:
            NetworkInterfacesResponse containing interface information.

        Raises:
            PiHoleAPIError: API request failed.
            PiHoleAuthenticationError: Authentication failed.
            PiHoleConnectionError: Connection failed.
            PiHoleServerError: Server error.
        """
        params = {"detailed": detailed}
        response = make_pihole_request(
            self._client,
            "GET",
            f"{self.BASE_URL}/interfaces",
            params=params,
        )
        return NetworkInterfacesResponse.model_validate(response.json())

    def get_routes(self, detailed: bool = False) -> NetworkRoutesResponse:
        """Get info about the routes of your Pi-hole.

        Note that not all described fields are applicable to any routing type.
        Users must not rely on the presence of any field without checking the
        route type first.

        Args:
            detailed: If True, include more detailed information about individual
                     routes where available information is dependent on the route
                     type and state.

        Returns:
            NetworkRoutesResponse containing route information.

        Raises:
            PiHoleAPIError: API request failed.
            PiHoleAuthenticationError: Authentication failed.
            PiHoleConnectionError: Connection failed.
            PiHoleServerError: Server error.
        """
        params = {"detailed": detailed}
        response = make_pihole_request(
            self._client,
            "GET",
            f"{self.BASE_URL}/routes",
            params=params,
        )
        return NetworkRoutesResponse.model_validate(response.json())

    def delete_device(self, device_id: int) -> NetworkDeviceDeleteResponse:
        """Delete a device from the network table.

        This will also remove all associated IP addresses and hostnames.

        Args:
            device_id: Device ID to delete.

        Returns:
            NetworkDeviceDeleteResponse containing operation result.

        Raises:
            PiHoleAPIError: API request failed.
            PiHoleAuthenticationError: Authentication failed.
            PiHoleConnectionError: Connection failed.
            PiHoleServerError: Server error.
        """
        response = make_pihole_request(
            self._client,
            "DELETE",
            f"{self.BASE_URL}/devices/{device_id}",
        )
        return NetworkDeviceDeleteResponse.model_validate(response.json())
