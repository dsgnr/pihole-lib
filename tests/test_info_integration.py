"""Integration tests for PiHoleInfo."""

import pytest

from pihole_lib import PiHoleClient, PiHoleInfo
from pihole_lib.exceptions import PiHoleConnectionError
from pihole_lib.models.session import ClientInfo, LoginInfo
from tests.conftest import integration
from tests.constants import (
    CONNECTION_FAILED_MESSAGE,
    PIHOLE_BASE_URL,
    PIHOLE_TEST_PASSWORD,
    TEST_INVALID_HOST_URL,
)


@integration
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


@integration
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


@integration
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


@integration
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


@integration
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


@integration
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


@integration
class TestPiHoleInfoVersionInfo:
    """Test version info functionality against real Pi-hole."""

    def test_get_version_info_success(self, pihole_container):
        """Should successfully retrieve version info from Pi-hole."""
        with PiHoleClient(
            base_url=PIHOLE_BASE_URL, password=PIHOLE_TEST_PASSWORD, verify_ssl=False
        ) as client:
            info_client = PiHoleInfo(client)

            version_info = info_client.get_version_info()

            # Verify basic structure
            assert hasattr(version_info, "version")
            assert hasattr(version_info.version, "core")
            assert hasattr(version_info.version, "web")
            assert hasattr(version_info.version, "ftl")
            assert hasattr(version_info.version, "docker")

            # Verify core version structure
            assert hasattr(version_info.version.core, "local")
            assert hasattr(version_info.version.core, "remote")
            assert hasattr(version_info.version.core.local, "version")
            assert hasattr(version_info.version.core.local, "branch")
            assert hasattr(version_info.version.core.local, "hash")
            assert hasattr(version_info.version.core.remote, "version")
            assert hasattr(version_info.version.core.remote, "hash")

            # Verify web version structure
            assert hasattr(version_info.version.web.local, "version")
            assert hasattr(version_info.version.web.local, "branch")
            assert hasattr(version_info.version.web.local, "hash")

            # Verify FTL version structure
            assert hasattr(version_info.version.ftl.local, "version")
            assert hasattr(version_info.version.ftl.local, "branch")
            assert hasattr(version_info.version.ftl.local, "hash")
            assert hasattr(version_info.version.ftl.local, "date")

            # Verify Docker version structure
            assert hasattr(version_info.version.docker, "local")
            assert hasattr(version_info.version.docker, "remote")

            # Verify data types
            assert isinstance(version_info.version.core.local.version, str)
            assert isinstance(version_info.version.core.local.hash, str)
            assert isinstance(version_info.version.docker.local, str)

    def test_get_version_info_connection_error(self):
        """Network errors should raise connection error."""
        client = PiHoleClient(
            base_url=TEST_INVALID_HOST_URL,
            password=PIHOLE_TEST_PASSWORD,
            timeout=1,  # Short timeout
        )
        info_client = PiHoleInfo(client)

        with pytest.raises(PiHoleConnectionError, match=CONNECTION_FAILED_MESSAGE):
            info_client.get_version_info()

        client.close()

    def test_get_version_info_version_format(self, pihole_container):
        """Should return properly formatted version information."""
        with PiHoleClient(
            base_url=PIHOLE_BASE_URL, password=PIHOLE_TEST_PASSWORD, verify_ssl=False
        ) as client:
            info_client = PiHoleInfo(client)

            version_info = info_client.get_version_info()

            # Versions should follow semantic versioning pattern
            assert version_info.version.core.local.version.startswith("v")
            assert version_info.version.web.local.version.startswith("v")
            assert version_info.version.ftl.local.version.startswith("v")

            # Hashes should be git commit hashes (typically 7+ characters)
            assert len(version_info.version.core.local.hash) >= 7
            assert len(version_info.version.web.local.hash) >= 7
            assert len(version_info.version.ftl.local.hash) >= 7

            # Branch should be a valid git branch name
            assert len(version_info.version.core.local.branch) > 0
            assert " " not in version_info.version.core.local.branch

            # FTL should have a build date
            assert version_info.version.ftl.local.date is not None
            assert len(version_info.version.ftl.local.date) > 0

    def test_get_version_info_docker_versions(self, pihole_container):
        """Should return valid Docker version information."""
        with PiHoleClient(
            base_url=PIHOLE_BASE_URL, password=PIHOLE_TEST_PASSWORD, verify_ssl=False
        ) as client:
            info_client = PiHoleInfo(client)

            version_info = info_client.get_version_info()

            # Docker versions should be strings
            assert isinstance(version_info.version.docker.local, str)
            assert isinstance(version_info.version.docker.remote, str)

            # Docker versions should not be empty
            assert len(version_info.version.docker.local) > 0
            assert len(version_info.version.docker.remote) > 0

            # Docker versions typically follow YYYY.MM.N format or "dev"
            local_docker = version_info.version.docker.local
            assert local_docker == "dev" or "." in local_docker

    def test_get_version_info_consistency(self, pihole_container):
        """Should return consistent version information."""
        with PiHoleClient(
            base_url=PIHOLE_BASE_URL, password=PIHOLE_TEST_PASSWORD, verify_ssl=False
        ) as client:
            info_client = PiHoleInfo(client)

            version_info = info_client.get_version_info()

            # Local versions should always be available
            assert version_info.version.core.local.version is not None
            assert version_info.version.web.local.version is not None
            assert version_info.version.ftl.local.version is not None

            # Remote versions might be None if Pi-hole can't access remote repositories
            # This is common in containerized environments without internet access
            # But if they exist, they should be valid strings
            if version_info.version.core.remote.version is not None:
                assert isinstance(version_info.version.core.remote.version, str)
            if version_info.version.web.remote.version is not None:
                assert isinstance(version_info.version.web.remote.version, str)
            if version_info.version.ftl.remote.version is not None:
                assert isinstance(version_info.version.ftl.remote.version, str)

            # Hashes should be consistent format
            for component in [
                version_info.version.core,
                version_info.version.web,
                version_info.version.ftl,
            ]:
                assert len(component.local.hash) >= 7
                # Local hashes should be alphanumeric
                assert component.local.hash.isalnum()

                # Remote hashes might be None, but if they exist, should be valid
                if component.remote.hash is not None:
                    assert len(component.remote.hash) >= 7
                    assert component.remote.hash.isalnum()


@integration
class TestPiHoleInfoSystemInfo:
    """Test system info functionality against real Pi-hole."""

    def test_get_system_info_success(self, pihole_container):
        """Should successfully retrieve system info from Pi-hole."""
        with PiHoleClient(
            base_url=PIHOLE_BASE_URL, password=PIHOLE_TEST_PASSWORD, verify_ssl=False
        ) as client:
            info_client = PiHoleInfo(client)

            system_info = info_client.get_system_info()

            # Verify basic structure
            assert hasattr(system_info, "system")
            assert hasattr(system_info.system, "uptime")
            assert hasattr(system_info.system, "memory")
            assert hasattr(system_info.system, "procs")
            assert hasattr(system_info.system, "cpu")
            assert hasattr(system_info.system, "ftl")

            # Verify memory structure
            assert hasattr(system_info.system.memory, "ram")
            assert hasattr(system_info.system.memory, "swap")
            assert hasattr(system_info.system.memory.ram, "total")
            assert hasattr(system_info.system.memory.ram, "free")
            assert hasattr(system_info.system.memory.ram, "used")
            assert hasattr(system_info.system.memory.ram, "available")
            assert hasattr(system_info.system.memory.ram, "percent_used")

            # Verify CPU structure
            assert hasattr(system_info.system.cpu, "nprocs")
            assert hasattr(system_info.system.cpu, "percent_cpu")
            assert hasattr(system_info.system.cpu, "load")
            assert hasattr(system_info.system.cpu.load, "raw")
            assert hasattr(system_info.system.cpu.load, "percent")

            # Verify FTL structure
            assert hasattr(system_info.system.ftl, "percent_mem")
            assert hasattr(system_info.system.ftl, "percent_cpu")

            # Verify data types
            assert isinstance(system_info.system.uptime, int)
            assert isinstance(system_info.system.procs, int)
            assert isinstance(system_info.system.memory.ram.total, int)
            assert isinstance(system_info.system.memory.ram.percent_used, float)
            assert isinstance(system_info.system.cpu.nprocs, int)
            assert isinstance(system_info.system.cpu.load.raw, list)

    def test_get_system_info_connection_error(self):
        """Network errors should raise connection error."""
        client = PiHoleClient(
            base_url=TEST_INVALID_HOST_URL,
            password=PIHOLE_TEST_PASSWORD,
            timeout=1,  # Short timeout
        )
        info_client = PiHoleInfo(client)

        with pytest.raises(PiHoleConnectionError, match=CONNECTION_FAILED_MESSAGE):
            info_client.get_system_info()

        client.close()

    def test_get_system_info_reasonable_values(self, pihole_container):
        """Should return reasonable system values."""
        with PiHoleClient(
            base_url=PIHOLE_BASE_URL, password=PIHOLE_TEST_PASSWORD, verify_ssl=False
        ) as client:
            info_client = PiHoleInfo(client)

            system_info = info_client.get_system_info()

            # Uptime should be positive
            assert system_info.system.uptime > 0

            # Process count should be reasonable
            assert 10 <= system_info.system.procs <= 10000

            # Memory values should be reasonable
            assert system_info.system.memory.ram.total > 0
            assert system_info.system.memory.ram.free >= 0
            assert system_info.system.memory.ram.used >= 0
            assert system_info.system.memory.ram.available >= 0
            assert 0 <= system_info.system.memory.ram.percent_used <= 100

            # Swap values should be non-negative
            assert system_info.system.memory.swap.total >= 0
            assert system_info.system.memory.swap.free >= 0
            assert system_info.system.memory.swap.used >= 0
            assert 0 <= system_info.system.memory.swap.percent_used <= 100

            # CPU values should be reasonable
            assert system_info.system.cpu.nprocs > 0
            assert system_info.system.cpu.percent_cpu >= 0
            assert len(system_info.system.cpu.load.raw) == 3
            assert len(system_info.system.cpu.load.percent) == 3

            # FTL resource usage should be reasonable
            assert system_info.system.ftl.percent_mem >= 0
            assert system_info.system.ftl.percent_cpu >= 0

    def test_get_system_info_memory_consistency(self, pihole_container):
        """Should return consistent memory information."""
        with PiHoleClient(
            base_url=PIHOLE_BASE_URL, password=PIHOLE_TEST_PASSWORD, verify_ssl=False
        ) as client:
            info_client = PiHoleInfo(client)

            system_info = info_client.get_system_info()

            ram = system_info.system.memory.ram
            swap = system_info.system.memory.swap

            # RAM consistency checks
            assert ram.used + ram.free <= ram.total + 1000  # Allow small discrepancy
            assert ram.available <= ram.total
            assert ram.used >= 0

            # Swap consistency checks
            if swap.total > 0:
                assert (
                    swap.used + swap.free <= swap.total + 100
                )  # Allow small discrepancy
                assert swap.used >= 0
                assert swap.free >= 0

    def test_get_system_info_load_averages(self, pihole_container):
        """Should return valid load average information."""
        with PiHoleClient(
            base_url=PIHOLE_BASE_URL, password=PIHOLE_TEST_PASSWORD, verify_ssl=False
        ) as client:
            info_client = PiHoleInfo(client)

            system_info = info_client.get_system_info()

            load = system_info.system.cpu.load

            # Load averages should be non-negative
            for raw_load in load.raw:
                assert raw_load >= 0

            for percent_load in load.percent:
                assert percent_load >= 0

            # Raw and percent should be related (percent = raw * 100 / nprocs)
            nprocs = system_info.system.cpu.nprocs
            for i in range(3):
                expected_percent = (load.raw[i] * 100) / nprocs
                # Allow some floating point tolerance
                assert abs(load.percent[i] - expected_percent) < 0.1


@integration
class TestPiHoleInfoMessagesInfo:
    """Test messages info functionality against real Pi-hole."""

    def test_get_messages_success(self, pihole_container):
        """Should successfully retrieve messages from Pi-hole."""
        with PiHoleClient(
            base_url=PIHOLE_BASE_URL, password=PIHOLE_TEST_PASSWORD, verify_ssl=False
        ) as client:
            info_client = PiHoleInfo(client)

            messages_info = info_client.get_messages()

            # Verify basic structure
            assert hasattr(messages_info, "messages")
            assert isinstance(messages_info.messages, list)

            # Messages can be empty in a fresh Pi-hole installation
            # If there are messages, verify their structure
            for message in messages_info.messages:
                assert hasattr(message, "id")
                assert hasattr(message, "timestamp")
                assert hasattr(message, "type")
                assert hasattr(message, "plain")
                assert hasattr(message, "html")

                # Verify data types
                assert isinstance(message.id, int)
                assert isinstance(message.timestamp, int)
                assert isinstance(message.type, str)
                assert isinstance(message.plain, str)
                assert isinstance(message.html, str)

                # Verify reasonable values
                assert message.id > 0
                assert message.timestamp > 0
                assert len(message.type) > 0
                assert len(message.plain) > 0
                assert len(message.html) > 0

    def test_get_messages_connection_error(self):
        """Network errors should raise connection error."""
        client = PiHoleClient(
            base_url=TEST_INVALID_HOST_URL,
            password=PIHOLE_TEST_PASSWORD,
            timeout=1,  # Short timeout
        )
        info_client = PiHoleInfo(client)

        with pytest.raises(PiHoleConnectionError, match=CONNECTION_FAILED_MESSAGE):
            info_client.get_messages()

        client.close()

    def test_get_messages_empty_list(self, pihole_container):
        """Should handle empty messages list gracefully."""
        with PiHoleClient(
            base_url=PIHOLE_BASE_URL, password=PIHOLE_TEST_PASSWORD, verify_ssl=False
        ) as client:
            info_client = PiHoleInfo(client)

            messages_info = info_client.get_messages()

            # Fresh Pi-hole installations typically have no messages
            assert isinstance(messages_info.messages, list)
            # Length can be 0 or more, both are valid

    def test_get_messages_message_types(self, pihole_container):
        """Should return valid message types if messages exist."""
        with PiHoleClient(
            base_url=PIHOLE_BASE_URL, password=PIHOLE_TEST_PASSWORD, verify_ssl=False
        ) as client:
            info_client = PiHoleInfo(client)

            messages_info = info_client.get_messages()

            for message in messages_info.messages:
                # Message type should be a non-empty string
                assert isinstance(message.type, str)
                assert len(message.type) > 0
                # For now, just verify it's a reasonable string (could be any type Pi-hole uses)
                assert message.type.replace("_", "").replace("-", "").isalnum()

    def test_get_messages_content_consistency(self, pihole_container):
        """Should return consistent plain and HTML content."""
        with PiHoleClient(
            base_url=PIHOLE_BASE_URL, password=PIHOLE_TEST_PASSWORD, verify_ssl=False
        ) as client:
            info_client = PiHoleInfo(client)

            messages_info = info_client.get_messages()

            # If messages exist, verify content consistency
            for message in messages_info.messages:
                # Plain text should not contain HTML tags
                assert "<" not in message.plain or ">" not in message.plain

                # HTML content should contain the plain text content (approximately)
                # Remove HTML tags for basic comparison
                import re

                html_text = re.sub(r"<[^>]+>", "", message.html)
                # Basic check that core content is similar
                assert len(html_text.strip()) > 0


@integration
class TestPiHoleInfoMessagesCountInfo:
    """Test messages count info functionality against real Pi-hole."""

    def test_get_messages_count_success(self, pihole_container):
        """Should successfully retrieve messages count from Pi-hole."""
        with PiHoleClient(
            base_url=PIHOLE_BASE_URL, password=PIHOLE_TEST_PASSWORD, verify_ssl=False
        ) as client:
            info_client = PiHoleInfo(client)

            messages_count = info_client.get_messages_count()

            # Verify basic structure
            assert hasattr(messages_count, "count")
            assert isinstance(messages_count.count, int)
            assert messages_count.count >= 0  # Count should be non-negative

    def test_get_messages_count_connection_error(self):
        """Network errors should raise connection error."""
        client = PiHoleClient(
            base_url=TEST_INVALID_HOST_URL,
            password=PIHOLE_TEST_PASSWORD,
            timeout=1,  # Short timeout
        )
        info_client = PiHoleInfo(client)

        with pytest.raises(PiHoleConnectionError, match=CONNECTION_FAILED_MESSAGE):
            info_client.get_messages_count()

        client.close()

    def test_get_messages_count_consistency(self, pihole_container):
        """Should return consistent count with get_messages."""
        with PiHoleClient(
            base_url=PIHOLE_BASE_URL, password=PIHOLE_TEST_PASSWORD, verify_ssl=False
        ) as client:
            info_client = PiHoleInfo(client)

            # Get count and messages
            messages_count = info_client.get_messages_count()
            messages_info = info_client.get_messages()

            # Count should match the length of messages array
            assert messages_count.count == len(messages_info.messages)

    def test_constants_usage(self, pihole_container):
        """Test that the class uses the correct API endpoint constants."""
        with PiHoleClient(
            base_url=PIHOLE_BASE_URL, password=PIHOLE_TEST_PASSWORD, verify_ssl=False
        ) as client:
            info = PiHoleInfo(client)
            assert info.BASE_URL == "/api/info"
