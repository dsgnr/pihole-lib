"""Pi-hole DHCP management."""

from pihole_lib.base import BasePiHoleAPIClient
from pihole_lib.constants import API_DHCP_LEASES
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
            API_DHCP_LEASES,
        )
        return DHCPLeasesInfo(**response_data.json())
