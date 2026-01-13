"""Pi-hole DHCP management."""

from pihole_lib.base import BasePiHoleAPIClient
from pihole_lib.models.dhcp import DHCPLeasesInfo
from pihole_lib.utils import make_pihole_request


class PiHoleDHCP(BasePiHoleAPIClient):
    """Pi-hole DHCP management client.

    Provides methods to interact with Pi-hole's DHCP functionality.

    Examples::

        from pihole_lib import PiHoleClient

        with PiHoleClient("http://192.168.1.100", password="secret") as client:
            # Get active DHCP leases
            leases = client.dhcp.get_leases()
            for lease in leases.leases:
                print(f"{lease.name} ({lease.ip}) - {lease.hwaddr}")

            # Delete a lease
            client.dhcp.delete_lease("192.168.1.100")

    """

    BASE_URL = "/api/dhcp"

    def get_leases(self) -> DHCPLeasesInfo:
        """Get currently active DHCP leases.

        Returns:
            DHCPLeasesInfo containing active lease information.
        """
        response = make_pihole_request(
            self._client,
            "GET",
            f"{self.BASE_URL}/leases",
        )
        return DHCPLeasesInfo.model_validate(response.json())

    def delete_lease(self, ip: str) -> bool:
        """Delete a currently active DHCP lease.

        Args:
            ip: IP address of the lease to delete.

        Returns:
            True if the lease was successfully deleted.
        """
        response = make_pihole_request(
            self._client,
            "DELETE",
            f"{self.BASE_URL}/leases/{ip}",
        )
        return bool(response.status_code == 204)
