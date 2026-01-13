"""Pi-hole network API client."""

from pihole_lib.base import BasePiHoleAPIClient
from pihole_lib.models.network import (
    NetworkDeviceDeleteResponse,
    NetworkDevicesResponse,
    NetworkGatewayDetailedResponse,
    NetworkGatewayResponse,
    NetworkInterfacesResponse,
    NetworkRoutesResponse,
)
from pihole_lib.utils import make_pihole_request


class PiHoleNetwork(BasePiHoleAPIClient):
    """Pi-hole network API client.

    Provides methods to gather network information as seen by Pi-hole.

    Examples::

        from pihole_lib import PiHoleClient

        with PiHoleClient("http://192.168.1.100", password="secret") as client:
            # Get network devices
            devices = client.network.get_devices()
            for device in devices.devices:
                print(f"{device.name}: {device.hwaddr}")

            # Get gateway info
            gateway = client.network.get_gateway()

            # Get interfaces
            interfaces = client.network.get_interfaces()

    """

    BASE_URL = "/api/network"

    def get_devices(
        self,
        max_devices: int | None = None,
        max_addresses: int | None = None,
    ) -> NetworkDevicesResponse:
        """Get info about devices in your local network.

        Args:
            max_devices: Maximum number of devices to show (optional).
            max_addresses: Maximum addresses per device (optional).

        Returns:
            NetworkDevicesResponse containing device information.
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
            params=params or None,
        )
        return NetworkDevicesResponse.model_validate(response.json())

    def get_gateway(
        self, detailed: bool = False
    ) -> NetworkGatewayResponse | NetworkGatewayDetailedResponse:
        """Get info about the gateway.

        Args:
            detailed: If True, include detailed interface and route info.

        Returns:
            NetworkGatewayResponse or NetworkGatewayDetailedResponse.
        """
        response = make_pihole_request(
            self._client,
            "GET",
            f"{self.BASE_URL}/gateway",
            params={"detailed": detailed},
        )
        if detailed:
            return NetworkGatewayDetailedResponse.model_validate(response.json())
        return NetworkGatewayResponse.model_validate(response.json())

    def get_interfaces(self, detailed: bool = False) -> NetworkInterfacesResponse:
        """Get info about network interfaces.

        Args:
            detailed: If True, include more detailed information.

        Returns:
            NetworkInterfacesResponse containing interface information.
        """
        response = make_pihole_request(
            self._client,
            "GET",
            f"{self.BASE_URL}/interfaces",
            params={"detailed": detailed},
        )
        return NetworkInterfacesResponse.model_validate(response.json())

    def get_routes(self, detailed: bool = False) -> NetworkRoutesResponse:
        """Get info about network routes.

        Args:
            detailed: If True, include more detailed information.

        Returns:
            NetworkRoutesResponse containing route information.
        """
        response = make_pihole_request(
            self._client,
            "GET",
            f"{self.BASE_URL}/routes",
            params={"detailed": detailed},
        )
        return NetworkRoutesResponse.model_validate(response.json())

    def delete_device(self, device_id: int) -> NetworkDeviceDeleteResponse:
        """Delete a device from the network table.

        Args:
            device_id: Device ID to delete.

        Returns:
            NetworkDeviceDeleteResponse containing operation result.
        """
        response = make_pihole_request(
            self._client,
            "DELETE",
            f"{self.BASE_URL}/devices/{device_id}",
        )
        return NetworkDeviceDeleteResponse.model_validate(response.json())
