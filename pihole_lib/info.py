"""Pi-hole Info API client."""

from pihole_lib.base import BasePiHoleAPIClient
from pihole_lib.models.ftl import DatabaseInfo, FTLInfo
from pihole_lib.models.host import HostInfo
from pihole_lib.models.messages import MessagesCountInfo, MessagesInfo
from pihole_lib.models.session import ClientInfo, LoginInfo
from pihole_lib.models.system import SystemInfo
from pihole_lib.models.version import VersionInfo
from pihole_lib.utils import make_pihole_request


class PiHoleInfo(BasePiHoleAPIClient):
    """Pi-hole Info API client.

    Handles information endpoints for system status and diagnostics.

    Examples::

        from pihole_lib import PiHoleClient

        with PiHoleClient("http://192.168.1.100", password="secret") as client:
            # Get login info
            login_info = client.info.get_login_info()
            print(f"DNS running: {login_info.dns}")

            # Get system info
            system_info = client.info.get_system_info()
            print(f"Uptime: {system_info.system.uptime}s")

            # Get version info
            version = client.info.get_version_info()
            print(f"Pi-hole: {version.version.core.local.version}")

    """

    BASE_URL = "/api/info"

    def get_login_info(self) -> LoginInfo:
        """Get login page related information.

        Returns:
            LoginInfo with HTTPS port and DNS status.
        """
        response = make_pihole_request(
            self._client,
            "GET",
            f"{self.BASE_URL}/login",
        )
        return LoginInfo.model_validate(response.json())

    def get_client_info(self) -> ClientInfo:
        """Get client request information.

        Returns:
            ClientInfo with remote address, HTTP version, method, and headers.
        """
        response = make_pihole_request(
            self._client,
            "GET",
            f"{self.BASE_URL}/client",
        )
        return ClientInfo.model_validate(response.json())

    def get_database_info(self) -> DatabaseInfo:
        """Get database information.

        Returns:
            DatabaseInfo with file size, permissions, query counts, etc.
        """
        response = make_pihole_request(
            self._client,
            "GET",
            f"{self.BASE_URL}/database",
        )
        return DatabaseInfo.model_validate(response.json())

    def get_ftl_info(self) -> FTLInfo:
        """Get FTL runtime information.

        Returns:
            FTLInfo with database stats, process info, and resource usage.
        """
        response = make_pihole_request(
            self._client,
            "GET",
            f"{self.BASE_URL}/ftl",
        )
        return FTLInfo.model_validate(response.json())

    def get_host_info(self) -> HostInfo:
        """Get host system information.

        Returns:
            HostInfo with uname details, hardware model, and DMI data.
        """
        response = make_pihole_request(
            self._client,
            "GET",
            f"{self.BASE_URL}/host",
        )
        return HostInfo.model_validate(response.json())

    def get_version_info(self) -> VersionInfo:
        """Get Pi-hole version information.

        Returns:
            VersionInfo for all Pi-hole components.
        """
        response = make_pihole_request(
            self._client,
            "GET",
            f"{self.BASE_URL}/version",
        )
        return VersionInfo.model_validate(response.json())

    def get_system_info(self) -> SystemInfo:
        """Get system resource information.

        Returns:
            SystemInfo with uptime, memory, CPU, and FTL resource usage.
        """
        response = make_pihole_request(
            self._client,
            "GET",
            f"{self.BASE_URL}/system",
        )
        return SystemInfo.model_validate(response.json())

    def get_messages(self) -> MessagesInfo:
        """Get system messages.

        Returns:
            MessagesInfo with diagnosis messages.
        """
        response = make_pihole_request(
            self._client,
            "GET",
            f"{self.BASE_URL}/messages",
        )
        return MessagesInfo.model_validate(response.json())

    def get_messages_count(self) -> MessagesCountInfo:
        """Get system messages count.

        Returns:
            MessagesCountInfo with message count.
        """
        response = make_pihole_request(
            self._client,
            "GET",
            f"{self.BASE_URL}/messages/count",
        )
        return MessagesCountInfo.model_validate(response.json())
