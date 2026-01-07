"""Integration tests for PiHoleInfo against real Pi-hole."""

import pytest

from pihole_lib import PiHoleClient, PiHoleInfo
from pihole_lib.exceptions import PiHoleConnectionError
from pihole_lib.models import ClientInfo, LoginInfo

from .constants import (
    CONNECTION_FAILED_MESSAGE,
    PIHOLE_BASE_URL,
    PIHOLE_TEST_PASSWORD,
    TEST_INVALID_HOST_URL,
)


class TestPiHoleInfoLoginInfo:
    """Test login info functionality against real Pi-hole."""

    def test_get_login_info_success(self, pihole_container):
        """Should successfully retrieve login info from Pi-hole."""
        client = PiHoleClient(
            base_url=PIHOLE_BASE_URL, password=PIHOLE_TEST_PASSWORD, verify_ssl=False
        )
        info_client = PiHoleInfo(client)

        login_info = info_client.get_login_info()

        assert isinstance(login_info, LoginInfo)
        assert isinstance(login_info.https_port, int)
        assert login_info.https_port >= 0  # Should be 0 or positive
        assert isinstance(login_info.dns, bool)

        client.close()

    def test_get_login_info_connection_error(self):
        """Network errors should raise connection error."""
        client = PiHoleClient(
            base_url=TEST_INVALID_HOST_URL,
            password=PIHOLE_TEST_PASSWORD,
            timeout=1,  # Short timeout
        )
        info_client = PiHoleInfo(client)

        with pytest.raises(PiHoleConnectionError, match=CONNECTION_FAILED_MESSAGE):
            info_client.get_login_info()

        client.close()

    def test_get_login_info_session_management(self, pihole_container):
        """Test that client session is properly managed."""
        client = PiHoleClient(
            base_url=PIHOLE_BASE_URL, password=PIHOLE_TEST_PASSWORD, verify_ssl=False
        )
        info_client = PiHoleInfo(client)

        # Call should work and create session in client
        info = info_client.get_login_info()
        assert info.https_port >= 0  # Should be valid port number
        assert isinstance(info.dns, bool)
        assert isinstance(info, LoginInfo)

        # Session should be created
        assert client._session is not None

        client.close()

    def test_get_login_info_with_client_context_manager(self, pihole_container):
        """Should work when client is used as context manager."""
        with PiHoleClient(
            base_url=PIHOLE_BASE_URL, password=PIHOLE_TEST_PASSWORD, verify_ssl=False
        ) as client:
            info_client = PiHoleInfo(client)
            login_info = info_client.get_login_info()

            assert isinstance(login_info, LoginInfo)
            assert client.is_authenticated()  # Client context manager authenticates


class TestPiHoleInfoWorkflows:
    """Test complete info client workflows with real Pi-hole."""

    def test_full_workflow_success(self, pihole_container):
        """Test complete workflow from init to cleanup."""
        # Test the full workflow
        with PiHoleClient(
            base_url=PIHOLE_BASE_URL, password=PIHOLE_TEST_PASSWORD, verify_ssl=False
        ) as client:
            info_client = PiHoleInfo(client)
            login_info = info_client.get_login_info()
            assert isinstance(login_info, LoginInfo)

        # Client should be cleaned up after its context manager

    def test_manual_session_management(self, pihole_container):
        """Test manual session management without context manager."""
        client = PiHoleClient(
            base_url=PIHOLE_BASE_URL, password=PIHOLE_TEST_PASSWORD, verify_ssl=False
        )
        info_client = PiHoleInfo(client)

        # Initially no session
        assert client._session is None

        # Get login info (creates session in client)
        login_info = info_client.get_login_info()
        assert isinstance(login_info, LoginInfo)
        assert client._session is not None

        # Manually clean up client
        client.close()
        assert client._session is None

    def test_multiple_info_clients_same_client(self, pihole_container):
        """Test that multiple info clients can share the same client."""
        client = PiHoleClient(
            base_url=PIHOLE_BASE_URL, password=PIHOLE_TEST_PASSWORD, verify_ssl=False
        )
        info_client1 = PiHoleInfo(client)
        info_client2 = PiHoleInfo(client)

        # Both should use the same client
        assert info_client1._client is client
        assert info_client2._client is client

        # Both should work and share the same session
        info1 = info_client1.get_login_info()
        info2 = info_client2.get_login_info()

        # Should get the same data
        assert info1.https_port == info2.https_port
        assert info1.dns == info2.dns

        # Should share the same session
        assert info_client1._client._session is info_client2._client._session

        client.close()


class TestPiHoleInfoClientInfo:
    """Test client info functionality against real Pi-hole."""

    def test_get_client_info_success(self, pihole_container):
        """Should successfully retrieve client info from Pi-hole."""
        with PiHoleClient(
            base_url=PIHOLE_BASE_URL, password=PIHOLE_TEST_PASSWORD, verify_ssl=False
        ) as client:
            info_client = PiHoleInfo(client)

            client_info = info_client.get_client_info()

            assert isinstance(client_info, ClientInfo)
            assert isinstance(client_info.remote_addr, str)
            assert len(client_info.remote_addr) > 0
            assert isinstance(client_info.http_version, str)
            assert client_info.http_version in ["1.0", "1.1", "2.0"]
            assert isinstance(client_info.method, str)
            assert client_info.method == "GET"
            assert isinstance(client_info.headers, list)
            assert len(client_info.headers) > 0

            # Check that headers have the expected structure
            for header in client_info.headers:
                assert hasattr(header, "name")
                assert hasattr(header, "value")
                assert isinstance(header.name, str)
                assert isinstance(header.value, str)

    def test_get_client_info_connection_error(self):
        """Network errors should raise connection error."""
        client = PiHoleClient(
            base_url=TEST_INVALID_HOST_URL,
            password=PIHOLE_TEST_PASSWORD,
            timeout=1,  # Short timeout
        )
        info_client = PiHoleInfo(client)

        with pytest.raises(PiHoleConnectionError, match=CONNECTION_FAILED_MESSAGE):
            info_client.get_client_info()

        client.close()

    def test_get_client_info_headers_content(self, pihole_container):
        """Should return expected headers in client info."""
        with PiHoleClient(
            base_url=PIHOLE_BASE_URL, password=PIHOLE_TEST_PASSWORD, verify_ssl=False
        ) as client:
            info_client = PiHoleInfo(client)

            client_info = info_client.get_client_info()

            # Should have common HTTP headers
            header_names = [header.name for header in client_info.headers]
            assert "Host" in header_names
            assert "User-Agent" in header_names

            # Find the Host header and verify it
            host_header = next(h for h in client_info.headers if h.name == "Host")
            assert "localhost:8080" in host_header.value


class TestPiHoleInfoDatabaseInfo:
    """Test database info functionality against real Pi-hole."""

    def test_get_database_info_success(self, pihole_container):
        """Should successfully retrieve database info from Pi-hole."""
        with PiHoleClient(
            base_url=PIHOLE_BASE_URL, password=PIHOLE_TEST_PASSWORD, verify_ssl=False
        ) as client:
            info_client = PiHoleInfo(client)

            db_info = info_client.get_database_info()

            # Verify basic structure
            assert hasattr(db_info, "size")
            assert hasattr(db_info, "type")
            assert hasattr(db_info, "mode")
            assert hasattr(db_info, "owner")
            assert hasattr(db_info, "queries")
            assert hasattr(db_info, "sqlite_version")

            # Verify data types and reasonable values
            assert isinstance(db_info.size, int)
            assert db_info.size > 0  # Database should have some size
            assert isinstance(db_info.type, str)
            assert "file" in db_info.type.lower()  # Should be some kind of file
            assert isinstance(db_info.mode, str)
            assert len(db_info.mode) > 0  # Should have permissions
            assert isinstance(db_info.queries, int)
            assert db_info.queries >= 0  # Queries count should be non-negative
            assert isinstance(db_info.sqlite_version, str)
            assert len(db_info.sqlite_version) > 0  # Should have version string

            # Verify owner structure
            assert hasattr(db_info.owner, "user")
            assert hasattr(db_info.owner, "group")
            assert hasattr(db_info.owner.user, "uid")
            assert hasattr(db_info.owner.user, "name")
            assert hasattr(db_info.owner.group, "gid")
            assert hasattr(db_info.owner.group, "name")

            # Verify owner data types
            assert isinstance(db_info.owner.user.uid, int)
            assert isinstance(db_info.owner.user.name, str)
            assert isinstance(db_info.owner.group.gid, int)
            assert isinstance(db_info.owner.group.name, str)

    def test_get_database_info_connection_error(self):
        """Network errors should raise connection error."""
        client = PiHoleClient(
            base_url=TEST_INVALID_HOST_URL,
            password=PIHOLE_TEST_PASSWORD,
            timeout=1,  # Short timeout
        )
        info_client = PiHoleInfo(client)

        with pytest.raises(PiHoleConnectionError, match=CONNECTION_FAILED_MESSAGE):
            info_client.get_database_info()

        client.close()

    def test_get_database_info_timestamps(self, pihole_container):
        """Should return valid timestamps in database info."""
        with PiHoleClient(
            base_url=PIHOLE_BASE_URL, password=PIHOLE_TEST_PASSWORD, verify_ssl=False
        ) as client:
            info_client = PiHoleInfo(client)

            db_info = info_client.get_database_info()

            # Verify timestamp fields exist and are reasonable
            assert hasattr(db_info, "atime")
            assert hasattr(db_info, "mtime")
            assert hasattr(db_info, "ctime")
            assert hasattr(db_info, "earliest_timestamp")
            assert hasattr(db_info, "earliest_timestamp_disk")

            # Timestamps should be integers (Unix timestamps)
            assert isinstance(db_info.atime, int)
            assert isinstance(db_info.mtime, int)
            assert isinstance(db_info.ctime, int)
            assert isinstance(db_info.earliest_timestamp, int)
            assert isinstance(db_info.earliest_timestamp_disk, int)

            # Timestamps should be reasonable (after year 2000, before year 2100)
            min_timestamp = 946684800  # 2000-01-01
            max_timestamp = 4102444800  # 2100-01-01

            assert min_timestamp <= db_info.atime <= max_timestamp
            assert min_timestamp <= db_info.mtime <= max_timestamp
            assert min_timestamp <= db_info.ctime <= max_timestamp

            # Query timestamps can be 0 if no queries exist
            assert db_info.earliest_timestamp >= 0
            assert db_info.earliest_timestamp_disk >= 0


class TestPiHoleInfoFTLInfo:
    """Test FTL info functionality against real Pi-hole."""

    def test_get_ftl_info_success(self, pihole_container):
        """Should successfully retrieve FTL info from Pi-hole."""
        with PiHoleClient(
            base_url=PIHOLE_BASE_URL, password=PIHOLE_TEST_PASSWORD, verify_ssl=False
        ) as client:
            info_client = PiHoleInfo(client)

            ftl_info = info_client.get_ftl_info()

            # Verify basic structure and types
            assert hasattr(ftl_info, "ftl")

            # Verify data types
            assert isinstance(ftl_info.ftl.pid, int)
            assert isinstance(ftl_info.ftl.uptime, float)
            assert isinstance(ftl_info.ftl.mem_percent, float)
            assert isinstance(ftl_info.ftl.cpu_percent, float)
            assert isinstance(ftl_info.ftl.allow_destructive, bool)

            # Verify reasonable values
            assert ftl_info.ftl.pid > 0  # Process ID should be positive
            assert ftl_info.ftl.uptime >= 0  # Uptime should be non-negative
            assert ftl_info.ftl.mem_percent >= 0  # Memory usage should be non-negative
            assert ftl_info.ftl.cpu_percent >= 0  # CPU usage should be non-negative

            # Verify FTL structure
            assert hasattr(ftl_info.ftl, "database")
            assert hasattr(ftl_info.ftl, "privacy_level")
            assert hasattr(ftl_info.ftl, "query_frequency")
            assert hasattr(ftl_info.ftl, "clients")

            # Verify database structure
            assert hasattr(ftl_info.ftl.database, "gravity")
            assert hasattr(ftl_info.ftl.database, "groups")
            assert hasattr(ftl_info.ftl.database, "lists")
            assert hasattr(ftl_info.ftl.database, "clients")

            # Verify clients structure
            assert hasattr(ftl_info.ftl.clients, "total")
            assert hasattr(ftl_info.ftl.clients, "active")

            # Verify dnsmasq structure
            assert hasattr(ftl_info.ftl.dnsmasq, "dns_queries_forwarded")
            assert hasattr(ftl_info.ftl.dnsmasq, "tcp_connections")

    def test_get_ftl_info_connection_error(self):
        """Network errors should raise connection error."""
        client = PiHoleClient(
            base_url=TEST_INVALID_HOST_URL,
            password=PIHOLE_TEST_PASSWORD,
            timeout=1,  # Short timeout
        )
        info_client = PiHoleInfo(client)

        with pytest.raises(PiHoleConnectionError, match=CONNECTION_FAILED_MESSAGE):
            info_client.get_ftl_info()

        client.close()

    def test_get_ftl_info_database_stats(self, pihole_container):
        """Should return valid database statistics."""
        with PiHoleClient(
            base_url=PIHOLE_BASE_URL, password=PIHOLE_TEST_PASSWORD, verify_ssl=False
        ) as client:
            info_client = PiHoleInfo(client)

            ftl_info = info_client.get_ftl_info()

            # Database stats should be non-negative integers
            assert isinstance(ftl_info.ftl.database.gravity, int)
            assert isinstance(ftl_info.ftl.database.groups, int)
            assert isinstance(ftl_info.ftl.database.lists, int)
            assert isinstance(ftl_info.ftl.database.clients, int)

            assert ftl_info.ftl.database.gravity >= 0
            assert ftl_info.ftl.database.groups >= 0
            assert ftl_info.ftl.database.lists >= 0
            assert ftl_info.ftl.database.clients >= 0

            # Privacy level should be valid (0-4)
            assert 0 <= ftl_info.ftl.privacy_level <= 4

            # Query frequency should be non-negative
            assert ftl_info.ftl.query_frequency >= 0

    def test_get_ftl_info_process_details(self, pihole_container):
        """Should return valid process details."""
        with PiHoleClient(
            base_url=PIHOLE_BASE_URL, password=PIHOLE_TEST_PASSWORD, verify_ssl=False
        ) as client:
            info_client = PiHoleInfo(client)

            ftl_info = info_client.get_ftl_info()

            # Process ID should be reasonable (1-65535 typically)
            assert 1 <= ftl_info.ftl.pid <= 65535

            # Uptime should be reasonable (less than a year in seconds)
            assert 0 <= ftl_info.ftl.uptime <= 31536000  # 1 year in seconds

            # Resource usage should be reasonable percentages
            assert 0 <= ftl_info.ftl.mem_percent <= 100
            assert 0 <= ftl_info.ftl.cpu_percent <= 100

            # Allow destructive should be a boolean
            assert isinstance(ftl_info.ftl.allow_destructive, bool)

    def test_get_ftl_info_client_stats(self, pihole_container):
        """Should return valid client statistics."""
        with PiHoleClient(
            base_url=PIHOLE_BASE_URL, password=PIHOLE_TEST_PASSWORD, verify_ssl=False
        ) as client:
            info_client = PiHoleInfo(client)

            ftl_info = info_client.get_ftl_info()

            # Client stats should be non-negative
            assert ftl_info.ftl.clients.total >= 0
            assert ftl_info.ftl.clients.active >= 0

            # Active clients should not exceed total clients
            assert ftl_info.ftl.clients.active <= ftl_info.ftl.clients.total


class TestPiHoleInfoHostInfo:
    """Test host info functionality against real Pi-hole."""

    def test_get_host_info_success(self, pihole_container):
        """Should successfully retrieve host info from Pi-hole."""
        with PiHoleClient(
            base_url=PIHOLE_BASE_URL, password=PIHOLE_TEST_PASSWORD, verify_ssl=False
        ) as client:
            info_client = PiHoleInfo(client)

            host_info = info_client.get_host_info()

            # Verify basic structure
            assert hasattr(host_info, "host")
            assert hasattr(host_info.host, "uname")
            assert hasattr(host_info.host, "model")
            assert hasattr(host_info.host, "dmi")

            # Verify uname structure and types
            assert hasattr(host_info.host.uname, "domainname")
            assert hasattr(host_info.host.uname, "machine")
            assert hasattr(host_info.host.uname, "nodename")
            assert hasattr(host_info.host.uname, "release")
            assert hasattr(host_info.host.uname, "sysname")
            assert hasattr(host_info.host.uname, "version")

            assert isinstance(host_info.host.uname.domainname, str)
            assert isinstance(host_info.host.uname.machine, str)
            assert isinstance(host_info.host.uname.nodename, str)
            assert isinstance(host_info.host.uname.release, str)
            assert isinstance(host_info.host.uname.sysname, str)
            assert isinstance(host_info.host.uname.version, str)

            # Verify reasonable values
            assert len(host_info.host.uname.machine) > 0  # Should have architecture
            assert len(host_info.host.uname.nodename) > 0  # Should have hostname
            assert len(host_info.host.uname.release) > 0  # Should have kernel release
            assert host_info.host.uname.sysname == "Linux"  # Pi-hole runs on Linux
            assert len(host_info.host.uname.version) > 0  # Should have kernel version

            # Verify DMI structure
            assert hasattr(host_info.host.dmi, "bios")
            assert hasattr(host_info.host.dmi, "board")
            assert hasattr(host_info.host.dmi, "product")
            assert hasattr(host_info.host.dmi, "sys")

            # Model can be None (especially in containers)
            assert host_info.host.model is None or isinstance(host_info.host.model, str)

    def test_get_host_info_connection_error(self):
        """Network errors should raise connection error."""
        client = PiHoleClient(
            base_url=TEST_INVALID_HOST_URL,
            password=PIHOLE_TEST_PASSWORD,
            timeout=1,  # Short timeout
        )
        info_client = PiHoleInfo(client)

        with pytest.raises(PiHoleConnectionError, match=CONNECTION_FAILED_MESSAGE):
            info_client.get_host_info()

        client.close()

    def test_get_host_info_container_environment(self, pihole_container):
        """Should handle container environment specifics."""
        with PiHoleClient(
            base_url=PIHOLE_BASE_URL, password=PIHOLE_TEST_PASSWORD, verify_ssl=False
        ) as client:
            info_client = PiHoleInfo(client)

            host_info = info_client.get_host_info()

            # Container-specific checks
            # Hostname is typically a container ID (hex string)
            assert len(host_info.host.uname.nodename) > 0

            # Architecture should be valid
            assert host_info.host.uname.machine in [
                "x86_64",
                "aarch64",
                "armv7l",
                "i386",
            ]

            # Kernel release should contain version info
            assert "." in host_info.host.uname.release  # Should have version numbers

            # Model is typically None in containers
            assert host_info.host.model is None

            # DMI info is typically None in containers
            assert host_info.host.dmi.bios.vendor is None
            assert host_info.host.dmi.sys.vendor is None

    def test_get_host_info_system_details(self, pihole_container):
        """Should return valid system details."""
        with PiHoleClient(
            base_url=PIHOLE_BASE_URL, password=PIHOLE_TEST_PASSWORD, verify_ssl=False
        ) as client:
            info_client = PiHoleInfo(client)

            host_info = info_client.get_host_info()

            # System name should be Linux
            assert host_info.host.uname.sysname == "Linux"

            # Domain name is often "(none)" in containers
            assert isinstance(host_info.host.uname.domainname, str)

            # Version should contain build information
            assert "#" in host_info.host.uname.version  # Kernel build info
            assert "SMP" in host_info.host.uname.version  # Symmetric multiprocessing

            # Release should be a valid kernel version
            version_parts = host_info.host.uname.release.split(".")
            assert len(version_parts) >= 2  # At least major.minor
