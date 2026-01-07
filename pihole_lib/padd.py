"""Pi-hole PADD (Pi-hole API Dashboard Data) management."""

from pihole_lib.base import BasePiHoleAPIClient
from pihole_lib.constants import API_PADD
from pihole_lib.models import PADDInfo
from pihole_lib.utils import make_pihole_request


class PiHolePADD(BasePiHoleAPIClient):
    """Pi-hole PADD (Pi-hole API Dashboard Data) client.

    This class provides methods to retrieve comprehensive dashboard data
    from Pi-hole, including statistics, system information, network details,
    and configuration summaries.

    Uses a PiHoleClient instance for making authenticated requests.

    Examples:
        ```python
        from pihole_lib import PiHoleClient, PiHolePADD

        with PiHoleClient("http://192.168.1.100", password="secret") as client:
            padd = PiHolePADD(client)

            # Get comprehensive dashboard data
            dashboard = padd.get_dashboard_data()
            print(f"Active clients: {dashboard.active_clients}")
            print(f"Gravity size: {dashboard.gravity_size}")
            print(f"Blocking status: {dashboard.blocking}")
            print(f"Total queries: {dashboard.queries.total}")
            print(f"Blocked queries: {dashboard.queries.blocked}")
        ```
    """

    def get_dashboard_data(self) -> PADDInfo:
        """Get comprehensive Pi-hole dashboard data.

        This endpoint provides summarized data for the Pi-hole dashboard,
        including query statistics, system information, network details,
        version information, and configuration summaries.

        Returns:
            PADDInfo: Comprehensive dashboard data including statistics,
                     system info, network details, and configuration.

        Raises:
            PiHoleConnectionError: If connection to Pi-hole fails.
            PiHoleAuthenticationError: If authentication fails.
            PiHoleAPIError: If the API request fails.

        Examples:
            ```python
            # Get dashboard data
            data = padd.get_dashboard_data()

            # Access query statistics
            print(f"Total queries: {data.queries.total}")
            print(f"Blocked: {data.queries.blocked} ({data.queries.percent_blocked}%)")

            # Access system information
            print(f"System uptime: {data.system.uptime} seconds")
            print(f"Memory usage: {data.system.memory.ram.percent_used}%")
            print(f"CPU usage: {data.system.cpu.percent_cpu}%")

            # Access network information
            print(f"IPv4 address: {data.iface.v4.addr}")
            print(f"Gateway: {data.iface.v4.gw_addr}")

            # Access version information
            print(f"Pi-hole core: {data.version.core.local.version}")
            print(f"FTL version: {data.version.ftl.local.version}")

            # Access configuration
            print(f"DHCP active: {data.config.dhcp_active}")
            print(f"DNS port: {data.config.dns_port}")
            ```
        """
        response_data = make_pihole_request(
            self._client,
            "GET",
            API_PADD,
        )
        return PADDInfo(**response_data.json())
