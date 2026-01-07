"""Pi-hole DHCP management."""

from pihole_lib.base import BasePiHoleAPIClient
from pihole_lib.models import DHCPLeasesInfo
from pihole_lib.utils import make_pihole_request


class PiHoleDHCP(BasePiHoleAPIClient):
    """Pi-hole DHCP management client.

    This class provides methods to interact with Pi-hole's DHCP functionality,
    including retrieving currently active DHCP leases.

    Uses a PiHoleClient instance for making authenticated requests.

    Examples:
        ```python
        from pihole_lib import PiHoleClient, PiHoleDHCP

        with PiHoleClient("http://192.168.1.100", password="secret") as client:
            dhcp = PiHoleDHCP(client)

            # Get currently active DHCP leases
            leases = dhcp.get_leases()
            print(f"Found {len(leases.leases)} active DHCP leases")

            for lease in leases.leases:
                print(f"{lease.name} ({lease.ip}) - {lease.hwaddr}")
        ```
    """

    BASE_URL = "/api/dhcp"

    def get_leases(self) -> DHCPLeasesInfo:
        """Get currently active DHCP leases.

        Returns:
            DHCPLeasesInfo: Information about currently active DHCP leases.

        Raises:
            PiHoleConnectionError: If connection to Pi-hole fails.
            PiHoleAuthenticationError: If authentication fails.
            PiHoleAPIError: If the API request fails.

        Examples:
            ```python
            # Get active DHCP leases
            leases = dhcp.get_leases()
            print(f"Found {len(leases.leases)} active leases")

            # Display lease information
            for lease in leases.leases:
                print(f"Device: {lease.name}")
                print(f"IP: {lease.ip}")
                print(f"MAC: {lease.hwaddr}")
                print(f"Client ID: {lease.clientid}")
            ```
        """
        response_data = make_pihole_request(
            self._client,
            "GET",
            f"{self.BASE_URL}/leases",
        )
        return DHCPLeasesInfo.model_validate(response_data.json())

    def delete_lease(self, ip: str) -> bool:
        """Delete a currently active DHCP lease.

        Managing DHCP leases is only possible when the DHCP server is enabled.
        This endpoint removes a currently active DHCP lease by IP address.

        Args:
            ip: IP address of the lease to delete (e.g., "192.168.1.100").

        Returns:
            True if the lease was successfully deleted.

        Raises:
            PiHoleConnectionError: If connection to Pi-hole fails.
            PiHoleAuthenticationError: If authentication fails.
            PiHoleAPIError: If the API request fails (e.g., invalid IP, lease not found).

        Examples:
            ```python
            # Delete a specific DHCP lease
            success = dhcp.delete_lease("192.168.1.100")
            if success:
                print("DHCP lease deleted successfully")

            # Get leases and delete the first one
            leases = dhcp.get_leases()
            if leases.leases:
                first_lease_ip = leases.leases[0].ip
                success = dhcp.delete_lease(first_lease_ip)
                print(f"Deleted lease for {first_lease_ip}: {success}")
            ```
        """
        response = make_pihole_request(
            self._client,
            "DELETE",
            f"{self.BASE_URL}/leases/{ip}",
        )
        # DELETE returns 204 No Content on success
        return response.status_code == 204
