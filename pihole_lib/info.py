"""Pi-hole Info API client."""

from typing import TYPE_CHECKING

from .base import BasePiHoleAPIClient
from .constants import (
    API_INFO_CLIENT,
    API_INFO_DATABASE,
    API_INFO_FTL,
    API_INFO_HOST,
    API_INFO_LOGIN,
    API_INFO_MESSAGES,
    API_INFO_MESSAGES_COUNT,
    API_INFO_SYSTEM,
    API_INFO_VERSION,
)
from .models import (
    ClientInfo,
    DatabaseInfo,
    FTLInfo,
    HostInfo,
    LoginInfo,
    MessagesCountInfo,
    MessagesInfo,
    SystemInfo,
    VersionInfo,
)
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

    def get_host_info(self) -> HostInfo:
        """Get host system information.

        This API hook returns a collection of host infos.

        Returns:
            HostInfo: Host system information including uname details, hardware model,
                     and DMI/SMBIOS data.

        Raises:
            PiHoleConnectionError: Connection failed.
            PiHoleAuthenticationError: Authentication failed.
            PiHoleServerError: Server error.
            PiHoleAPIError: Other API errors.

        Examples:
            ```python
            with PiHoleClient("http://192.168.1.100", password="secret") as client:
                info = PiHoleInfo(client)
                host_info = info.get_host_info()
                print(f"Hostname: {host_info.host.uname.nodename}")
                print(f"OS: {host_info.host.uname.sysname} {host_info.host.uname.release}")
                print(f"Architecture: {host_info.host.uname.machine}")
                print(f"Hardware model: {host_info.host.model}")
                if host_info.host.dmi.sys.vendor:
                    print(f"System vendor: {host_info.host.dmi.sys.vendor}")
            ```
        """
        response = make_pihole_request(
            self._client,
            "GET",
            API_INFO_HOST,
        )

        data = response.json()
        return HostInfo(**data)

    def get_version_info(self) -> VersionInfo:
        """Get Pi-hole version information.

        Request versions of the individual Pi-hole components.

        Returns:
            VersionInfo: Version information for all Pi-hole components including
                        local and remote versions, git hashes, and build dates.

        Raises:
            PiHoleConnectionError: Connection failed.
            PiHoleAuthenticationError: Authentication failed.
            PiHoleServerError: Server error.
            PiHoleAPIError: Other API errors.

        Examples:
            ```python
            with PiHoleClient("http://192.168.1.100", password="secret") as client:
                info = PiHoleInfo(client)
                version_info = info.get_version_info()
                print(f"Pi-hole Core: {version_info.version.core.local.version}")
                print(f"Web Interface: {version_info.version.web.local.version}")
                print(f"FTL: {version_info.version.ftl.local.version}")
                print(f"Docker: {version_info.version.docker.local}")

                # Check if updates are available
                if version_info.version.core.local.version != version_info.version.core.remote.version:
                    print("Core update available!")
            ```
        """
        response = make_pihole_request(
            self._client,
            "GET",
            API_INFO_VERSION,
        )

        data = response.json()
        return VersionInfo(**data)

    def get_system_info(self) -> SystemInfo:
        """Get system resource information.

        This API hook returns comprehensive system resource information including
        memory usage, CPU statistics, process count, and FTL resource usage.

        Returns:
            SystemInfo: System resource information including uptime, memory usage,
                       CPU statistics, process count, and FTL resource usage.

        Raises:
            PiHoleConnectionError: Connection failed.
            PiHoleAuthenticationError: Authentication failed.
            PiHoleServerError: Server error.
            PiHoleAPIError: Other API errors.

        Examples:
            ```python
            with PiHoleClient("http://192.168.1.100", password="secret") as client:
                info = PiHoleInfo(client)
                system_info = info.get_system_info()
                print(f"Uptime: {system_info.system.uptime} seconds")
                print(f"RAM Usage: {system_info.system.memory.ram.percent_used:.1f}%")
                print(f"CPU Cores: {system_info.system.cpu.nprocs}")
                print(f"CPU Usage: {system_info.system.cpu.percent_cpu:.1f}%")
                print(f"Processes: {system_info.system.procs}")
                print(f"FTL Memory: {system_info.system.ftl.percent_mem:.2f}%")
                print(f"Load Average: {system_info.system.cpu.load.raw}")
            ```
        """
        response = make_pihole_request(
            self._client,
            "GET",
            API_INFO_SYSTEM,
        )

        data = response.json()
        return SystemInfo(**data)

    def get_messages(self) -> MessagesInfo:
        """Get system messages.

        Request Pi-hole diagnosis messages.

        Returns:
            MessagesInfo: System messages including message ID, timestamp, type,
                         plain text content, and HTML-formatted content.

        Raises:
            PiHoleConnectionError: Connection failed.
            PiHoleAuthenticationError: Authentication failed.
            PiHoleServerError: Server error.
            PiHoleAPIError: Other API errors.

        Examples:
            ```python
            with PiHoleClient("http://192.168.1.100", password="secret") as client:
                info = PiHoleInfo(client)
                messages_info = info.get_messages()
                print(f"Total messages: {len(messages_info.messages)}")

                for message in messages_info.messages:
                    print(f"[{message.type.upper()}] {message.plain}")
                    print(f"  ID: {message.id}")
                    print(f"  Time: {message.timestamp}")
                    print(f"  HTML: {message.html}")
            ```
        """
        response = make_pihole_request(
            self._client,
            "GET",
            API_INFO_MESSAGES,
        )

        data = response.json()
        return MessagesInfo(**data)

    def get_messages_count(self) -> MessagesCountInfo:
        """Get system messages count.

        Request number of Pi-hole diagnosis messages.

        Returns:
            MessagesCountInfo: Count of system messages.

        Raises:
            PiHoleConnectionError: Connection failed.
            PiHoleAuthenticationError: Authentication failed.
            PiHoleServerError: Server error.
            PiHoleAPIError: Other API errors.

        Examples:
            ```python
            with PiHoleClient("http://192.168.1.100", password="secret") as client:
                info = PiHoleInfo(client)
                messages_count = info.get_messages_count()
                print(f"Total messages: {messages_count.count}")

                # More efficient than getting all messages if you only need the count
                if messages_count.count > 0:
                    print("There are messages to review")
                else:
                    print("No messages")
            ```
        """
        response = make_pihole_request(
            self._client,
            "GET",
            API_INFO_MESSAGES_COUNT,
        )

        data = response.json()
        return MessagesCountInfo(**data)
