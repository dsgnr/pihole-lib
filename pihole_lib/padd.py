"""Pi-hole PADD (Pi-hole API Dashboard Data) management."""

from pihole_lib.base import BasePiHoleAPIClient
from pihole_lib.models.padd import PADDInfo
from pihole_lib.utils import make_pihole_request


class PiHolePADD(BasePiHoleAPIClient):
    """Pi-hole PADD (Pi-hole API Dashboard Data) client.

    Provides comprehensive dashboard data including statistics,
    system information, network details, and configuration summaries.

    Examples::

        from pihole_lib import PiHoleClient

        with PiHoleClient("http://192.168.1.100", password="secret") as client:
            dashboard = client.padd.get_dashboard_data()
            print(f"Active clients: {dashboard.active_clients}")
            print(f"Total queries: {dashboard.queries.total}")
            print(f"Blocked: {dashboard.queries.blocked}")

    """

    BASE_URL = "/api/padd"

    def get_dashboard_data(self) -> PADDInfo:
        """Get comprehensive Pi-hole dashboard data.

        Returns:
            PADDInfo with statistics, system info, network details, and config.
        """
        response = make_pihole_request(
            self._client,
            "GET",
            self.BASE_URL,
        )
        return PADDInfo.model_validate(response.json())
