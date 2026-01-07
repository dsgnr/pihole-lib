"""Pi-hole Info API client."""

from typing import TYPE_CHECKING

from .base import BasePiHoleAPIClient
from .constants import API_INFO_CLIENT, API_INFO_DATABASE, API_INFO_FTL, API_INFO_LOGIN
from .models import ClientInfo, DatabaseInfo, FTLInfo, LoginInfo
from .utils import make_pihole_request

if TYPE_CHECKING:
    pass


class PiHoleInfo(BasePiHoleAPIClient):
    """Pi-hole Info API client.

    Handles information endpoints that don't require authentication.
    Uses a PiHoleClient instance for making requests.

    Examples:
        ```python
        from pihole_lib import PiHoleClient, PiHoleInfo

        # Create client and info instance
        client = PiHoleClient("http://192.168.1.100", password="secret")
        info = PiHoleInfo(client)
        login_info = info.get_login_info()
        client.close()

        # Or within client context
        with PiHoleClient("http://192.168.1.100", password="secret") as client:
            info = PiHoleInfo(client)
            login_info = info.get_login_info()
        ```
    """

    def get_login_info(self) -> LoginInfo:
        """Get login page related information.

        This API hook returns information used on the login page to possibly
        display messages/warnings.

        Returns:
            LoginInfo: Login page information including HTTPS port, DNS status,
                      and request processing time.

        Raises:
            PiHoleConnectionError: Connection failed.
            PiHoleServerError: Server error.
            PiHoleAPIError: Other API errors.
        """
        response = make_pihole_request(
            self._client,
            "GET",
            API_INFO_LOGIN,
        )

        data = response.json()
        return LoginInfo(**data)

    def get_client_info(self) -> ClientInfo:
        """Get client request information.

        This API hook returns information about the current HTTP request,
        including client IP, HTTP version, method, and headers.

        Returns:
            ClientInfo: Client request information including remote address,
                       HTTP version, method, and headers.

        Raises:
            PiHoleConnectionError: Connection failed.
            PiHoleAuthenticationError: Authentication failed.
            PiHoleServerError: Server error.
            PiHoleAPIError: Other API errors.

        Examples:
            ```python
            with PiHoleClient("http://192.168.1.100", password="secret") as client:
                info = PiHoleInfo(client)
                client_info = info.get_client_info()
                print(f"Client IP: {client_info.remote_addr}")
                print(f"HTTP Version: {client_info.http_version}")
                print(f"Method: {client_info.method}")
                for header in client_info.headers:
                    print(f"Header: {header.name} = {header.value}")
            ```
        """
        response = make_pihole_request(
            self._client,
            "GET",
            API_INFO_CLIENT,
        )

        data = response.json()
        return ClientInfo(**data)

    def get_database_info(self) -> DatabaseInfo:
        """Get database information.

        This API hook returns a collection of various long-term database properties infos.

        Returns:
            DatabaseInfo: Database information including file size, permissions,
                         ownership, query counts, and SQLite version.

        Raises:
            PiHoleConnectionError: Connection failed.
            PiHoleAuthenticationError: Authentication failed.
            PiHoleServerError: Server error.
            PiHoleAPIError: Other API errors.

        Examples:
            ```python
            with PiHoleClient("http://192.168.1.100", password="secret") as client:
                info = PiHoleInfo(client)
                db_info = info.get_database_info()
                print(f"Database size: {db_info.size} bytes")
                print(f"SQLite version: {db_info.sqlite_version}")
                print(f"Queries in memory: {db_info.queries}")
                print(f"Queries on disk: {db_info.queries_disk}")
                print(f"File owner: {db_info.owner.user.name}")
            ```
        """
        response = make_pihole_request(
            self._client,
            "GET",
            API_INFO_DATABASE,
        )

        data = response.json()
        return DatabaseInfo(**data)

    def get_ftl_info(self) -> FTLInfo:
        """Get FTL information.

        This API hook returns runtime information about the FTL process, including
        database statistics, process details, resource usage, and dnsmasq statistics.

        Returns:
            FTLInfo: FTL information including database stats, process info,
                    resource usage, and dnsmasq statistics.

        Raises:
            PiHoleConnectionError: Connection failed.
            PiHoleAuthenticationError: Authentication failed.
            PiHoleServerError: Server error.
            PiHoleAPIError: Other API errors.

        Examples:
            ```python
            with PiHoleClient("http://192.168.1.100", password="secret") as client:
                info = PiHoleInfo(client)
                ftl_info = info.get_ftl_info()
                print(f"Process ID: {ftl_info.ftl.pid}")
                print(f"Uptime: {ftl_info.ftl.uptime} seconds")
                print(f"Memory usage: {ftl_info.ftl.mem_percent}%")
                print(f"CPU usage: {ftl_info.ftl.cpu_percent}%")
                print(f"Gravity domains: {ftl_info.ftl.database.gravity}")
                print(f"Total clients: {ftl_info.ftl.clients.total}")
                print(f"Active clients: {ftl_info.ftl.clients.active}")
            ```
        """
        response = make_pihole_request(
            self._client,
            "GET",
            API_INFO_FTL,
        )

        data = response.json()
        return FTLInfo(**data)
