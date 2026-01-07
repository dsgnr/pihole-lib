"""Unit tests for PiHoleInfo (no network calls)."""

from unittest.mock import Mock, patch

from pihole_lib import PiHoleClient, PiHoleInfo

from .constants import (
    TEST_LOCALHOST_URL,
    TEST_SECRET_PASSWORD,
)


class TestPiHoleInfoInit:
    """Test info client initialization."""

    def test_init_with_client(self):
        """Info client should initialize with a PiHoleClient."""
        client = PiHoleClient(TEST_LOCALHOST_URL, password=TEST_SECRET_PASSWORD)
        info_client = PiHoleInfo(client)

        assert info_client._client is client

    def test_init_stores_client_reference(self):
        """Info client should store reference to the provided client."""
        client = PiHoleClient(TEST_LOCALHOST_URL, password=TEST_SECRET_PASSWORD)
        info_client = PiHoleInfo(client)

        # Should be able to access client properties through the stored reference
        assert info_client._client.base_url == TEST_LOCALHOST_URL
        assert info_client._client._password == TEST_SECRET_PASSWORD


class TestPiHoleInfoLoginInfo:
    """Test info client login info functionality (no network calls)."""

    def test_get_login_info_uses_client_session(self):
        """get_login_info should use the client's session."""
        client = PiHoleClient(TEST_LOCALHOST_URL, password=TEST_SECRET_PASSWORD)
        info_client = PiHoleInfo(client)

        assert client._session is None

        # This would fail in real usage due to no network, but we're testing
        # that it ensures the client has a session
        try:
            info_client.get_login_info()
        except Exception:
            # Expected to fail due to no network, but client session should be created
            pass

        assert client._session is not None


class TestPiHoleInfoClientInfo:
    """Test info client get_client_info functionality (no network calls)."""

    @patch("pihole_lib.info.make_pihole_request")
    def test_get_client_info_success(self, mock_request):
        """Should successfully get client info."""
        client = PiHoleClient(TEST_LOCALHOST_URL, password=TEST_SECRET_PASSWORD)
        info_client = PiHoleInfo(client)

        mock_response = Mock()
        mock_response.json.return_value = {
            "remote_addr": "192.168.1.100",
            "http_version": "1.1",
            "method": "GET",
            "headers": [
                {"name": "Host", "value": "localhost:8080"},
                {"name": "User-Agent", "value": "python-requests/2.32.5"},
            ],
            "took": 0.001,
        }
        mock_request.return_value = mock_response

        result = info_client.get_client_info()

        # Verify the request was made correctly
        mock_request.assert_called_once_with(
            client,
            "GET",
            f"{info_client.BASE_URL}/client",
        )

        # Verify the response structure
        assert result.remote_addr == "192.168.1.100"
        assert result.http_version == "1.1"
        assert result.method == "GET"
        assert len(result.headers) == 2
        assert result.headers[0].name == "Host"
        assert result.headers[0].value == "localhost:8080"
        assert result.headers[1].name == "User-Agent"
        assert result.headers[1].value == "python-requests/2.32.5"

    @patch("pihole_lib.info.make_pihole_request")
    def test_get_client_info_empty_headers(self, mock_request):
        """Should handle empty headers list."""
        client = PiHoleClient(TEST_LOCALHOST_URL, password=TEST_SECRET_PASSWORD)
        info_client = PiHoleInfo(client)

        mock_response = Mock()
        mock_response.json.return_value = {
            "remote_addr": "127.0.0.1",
            "http_version": "2.0",
            "method": "POST",
            "headers": [],
            "took": 0.001,
        }
        mock_request.return_value = mock_response

        result = info_client.get_client_info()

        assert result.remote_addr == "127.0.0.1"
        assert result.http_version == "2.0"
        assert result.method == "POST"
        assert len(result.headers) == 0


class TestPiHoleInfoDatabaseInfo:
    """Test info client get_database_info functionality (no network calls)."""

    @patch("pihole_lib.info.make_pihole_request")
    def test_get_database_info_success(self, mock_request):
        """Should successfully get database info."""
        client = PiHoleClient(TEST_LOCALHOST_URL, password=TEST_SECRET_PASSWORD)
        info_client = PiHoleInfo(client)

        mock_response = Mock()
        mock_response.json.return_value = {
            "size": 90112,
            "type": "Regular file",
            "mode": "rw-r-----",
            "atime": 1767779556,
            "mtime": 1767779556,
            "ctime": 1767779556,
            "owner": {
                "user": {"uid": 1000, "name": "pihole", "info": ""},
                "group": {"gid": 1000, "name": "pihole"},
            },
            "queries": 0,
            "earliest_timestamp": 0,
            "queries_disk": 0,
            "earliest_timestamp_disk": 0,
            "sqlite_version": "3.51.0",
            "took": 0.001,
        }
        mock_request.return_value = mock_response

        result = info_client.get_database_info()

        # Verify the request was made correctly
        mock_request.assert_called_once_with(
            client,
            "GET",
            f"{info_client.BASE_URL}/database",
        )

        # Verify the response structure
        assert result.size == 90112
        assert result.type == "Regular file"
        assert result.mode == "rw-r-----"
        assert result.atime == 1767779556
        assert result.mtime == 1767779556
        assert result.ctime == 1767779556
        assert result.owner.user.uid == 1000
        assert result.owner.user.name == "pihole"
        assert result.owner.user.info == ""
        assert result.owner.group.gid == 1000
        assert result.owner.group.name == "pihole"
        assert result.queries == 0
        assert result.earliest_timestamp == 0
        assert result.queries_disk == 0
        assert result.earliest_timestamp_disk == 0
        assert result.sqlite_version == "3.51.0"

    @patch("pihole_lib.info.make_pihole_request")
    def test_get_database_info_with_queries(self, mock_request):
        """Should handle database info with queries."""
        client = PiHoleClient(TEST_LOCALHOST_URL, password=TEST_SECRET_PASSWORD)
        info_client = PiHoleInfo(client)

        mock_response = Mock()
        mock_response.json.return_value = {
            "size": 1048576,
            "type": "Regular file",
            "mode": "rw-r--r--",
            "atime": 1767779556,
            "mtime": 1767779556,
            "ctime": 1767779556,
            "owner": {
                "user": {"uid": 999, "name": "ftl", "info": "FTL user"},
                "group": {"gid": 999, "name": "ftl"},
            },
            "queries": 1000,
            "earliest_timestamp": 1767700000,
            "queries_disk": 5000,
            "earliest_timestamp_disk": 1767600000,
            "sqlite_version": "3.45.0",
            "took": 0.002,
        }
        mock_request.return_value = mock_response

        result = info_client.get_database_info()

        assert result.size == 1048576
        assert result.queries == 1000
        assert result.earliest_timestamp == 1767700000
        assert result.queries_disk == 5000
        assert result.earliest_timestamp_disk == 1767600000
        assert result.owner.user.name == "ftl"
        assert result.owner.user.info == "FTL user"
        assert result.sqlite_version == "3.45.0"

    def test_get_login_info_uses_client_properties(self):
        """get_login_info should use client's base_url and timeout."""
        client = PiHoleClient(
            TEST_LOCALHOST_URL,
            password=TEST_SECRET_PASSWORD,
            timeout=60,
            verify_ssl=False,
        )
        info_client = PiHoleInfo(client)

        # Verify info client uses client properties
        assert info_client._client.base_url == TEST_LOCALHOST_URL
        assert info_client._client.timeout == 60
        assert info_client._client.verify_ssl is False


class TestPiHoleInfoFTLInfo:
    """Test info client get_ftl_info functionality (no network calls)."""

    @patch("pihole_lib.info.make_pihole_request")
    def test_get_ftl_info_success(self, mock_request):
        """Should successfully get FTL info."""
        client = PiHoleClient(TEST_LOCALHOST_URL, password=TEST_SECRET_PASSWORD)
        info_client = PiHoleInfo(client)

        mock_response = Mock()
        mock_response.json.return_value = {
            "ftl": {
                "database": {
                    "gravity": 79811,
                    "groups": 1,
                    "lists": 1,
                    "clients": 0,
                    "domains": {
                        "allowed": {"total": 0, "enabled": 0},
                        "denied": {"total": 0, "enabled": 0},
                    },
                    "regex": {
                        "allowed": {"total": 0, "enabled": 0},
                        "denied": {"total": 0, "enabled": 0},
                    },
                },
                "privacy_level": 0,
                "query_frequency": 0,
                "clients": {"total": 0, "active": 0},
                "pid": 191,
                "uptime": 12470.752492,
                "%mem": 0.10940226167440414,
                "%cpu": 0.0599999986588955,
                "allow_destructive": True,
                "dnsmasq": {
                    "dns_cache_inserted": 0,
                    "dns_cache_live_freed": 0,
                    "dns_queries_forwarded": 0,
                    "dns_auth_answered": 0,
                    "dns_local_answered": 0,
                    "dns_stale_answered": 0,
                    "dns_unanswered": 0,
                    "dnssec_max_crypto_use": 0,
                    "dnssec_max_sig_fail": 0,
                    "dnssec_max_work": 0,
                    "bootp": 0,
                    "pxe": 0,
                    "dhcp_ack": 0,
                    "dhcp_decline": 0,
                    "dhcp_discover": 0,
                    "dhcp_inform": 0,
                    "dhcp_nak": 0,
                    "dhcp_offer": 0,
                    "dhcp_release": 0,
                    "dhcp_request": 0,
                    "noanswer": 0,
                    "leases_allocated_4": 0,
                    "leases_pruned_4": 0,
                    "leases_allocated_6": 0,
                    "leases_pruned_6": 0,
                    "tcp_connections": 0,
                    "dhcp_leasequery": 0,
                    "dhcp_lease_unassigned": 0,
                    "dhcp_lease_actve": 0,
                    "dhcp_lease_unknown": 0,
                },
            },
            "took": 0.001,
        }
        mock_request.return_value = mock_response

        result = info_client.get_ftl_info()

        # Verify the request was made correctly
        mock_request.assert_called_once_with(
            client,
            "GET",
            f"{info_client.BASE_URL}/ftl",
        )

        # Verify the response structure
        assert result.ftl.pid == 191
        assert result.ftl.uptime == 12470.752492
        assert result.ftl.mem_percent == 0.10940226167440414
        assert result.ftl.cpu_percent == 0.0599999986588955
        assert result.ftl.allow_destructive is True
        assert result.ftl.database.gravity == 79811
        assert result.ftl.database.groups == 1
        assert result.ftl.database.lists == 1
        assert result.ftl.database.clients == 0
        assert result.ftl.privacy_level == 0
        assert result.ftl.query_frequency == 0
        assert result.ftl.clients.total == 0
        assert result.ftl.clients.active == 0
        assert result.ftl.dnsmasq.dns_cache_inserted == 0
        assert result.ftl.dnsmasq.tcp_connections == 0

    @patch("pihole_lib.info.make_pihole_request")
    def test_get_ftl_info_with_activity(self, mock_request):
        """Should handle FTL info with activity."""
        client = PiHoleClient(TEST_LOCALHOST_URL, password=TEST_SECRET_PASSWORD)
        info_client = PiHoleInfo(client)

        mock_response = Mock()
        mock_response.json.return_value = {
            "ftl": {
                "database": {
                    "gravity": 100000,
                    "groups": 5,
                    "lists": 10,
                    "clients": 25,
                    "domains": {
                        "allowed": {"total": 50, "enabled": 45},
                        "denied": {"total": 100, "enabled": 95},
                    },
                    "regex": {
                        "allowed": {"total": 5, "enabled": 5},
                        "denied": {"total": 10, "enabled": 8},
                    },
                },
                "privacy_level": 2,
                "query_frequency": 100,
                "clients": {"total": 25, "active": 15},
                "pid": 1234,
                "uptime": 86400.0,
                "%mem": 2.5,
                "%cpu": 1.2,
                "allow_destructive": False,
                "dnsmasq": {
                    "dns_cache_inserted": 1000,
                    "dns_cache_live_freed": 50,
                    "dns_queries_forwarded": 5000,
                    "dns_auth_answered": 100,
                    "dns_local_answered": 200,
                    "dns_stale_answered": 10,
                    "dns_unanswered": 5,
                    "dnssec_max_crypto_use": 0,
                    "dnssec_max_sig_fail": 0,
                    "dnssec_max_work": 0,
                    "bootp": 0,
                    "pxe": 0,
                    "dhcp_ack": 50,
                    "dhcp_decline": 0,
                    "dhcp_discover": 25,
                    "dhcp_inform": 5,
                    "dhcp_nak": 0,
                    "dhcp_offer": 25,
                    "dhcp_release": 10,
                    "dhcp_request": 30,
                    "noanswer": 2,
                    "leases_allocated_4": 20,
                    "leases_pruned_4": 5,
                    "leases_allocated_6": 0,
                    "leases_pruned_6": 0,
                    "tcp_connections": 10,
                    "dhcp_leasequery": 0,
                    "dhcp_lease_unassigned": 0,
                    "dhcp_lease_actve": 20,
                    "dhcp_lease_unknown": 0,
                },
            },
            "took": 0.002,
        }
        mock_request.return_value = mock_response

        result = info_client.get_ftl_info()

        assert result.ftl.pid == 1234
        assert result.ftl.uptime == 86400.0
        assert result.ftl.mem_percent == 2.5
        assert result.ftl.cpu_percent == 1.2
        assert result.ftl.allow_destructive is False
        assert result.ftl.database.gravity == 100000
        assert result.ftl.database.groups == 5
        assert result.ftl.clients.total == 25
        assert result.ftl.clients.active == 15
        assert result.ftl.dnsmasq.dns_queries_forwarded == 5000
        assert result.ftl.dnsmasq.dhcp_ack == 50

    @patch("pihole_lib.info.make_pihole_request")
    def test_get_ftl_info_minimal_response(self, mock_request):
        """Should handle minimal FTL info response."""
        client = PiHoleClient(TEST_LOCALHOST_URL, password=TEST_SECRET_PASSWORD)
        info_client = PiHoleInfo(client)

        mock_response = Mock()
        mock_response.json.return_value = {
            "ftl": {
                "database": {
                    "gravity": 0,
                    "groups": 1,
                    "lists": 0,
                    "clients": 0,
                    "domains": {
                        "allowed": {"total": 0, "enabled": 0},
                        "denied": {"total": 0, "enabled": 0},
                    },
                    "regex": {
                        "allowed": {"total": 0, "enabled": 0},
                        "denied": {"total": 0, "enabled": 0},
                    },
                },
                "privacy_level": 0,
                "query_frequency": 0,
                "clients": {"total": 0, "active": 0},
                "pid": 1,
                "uptime": 0.0,
                "%mem": 0.0,
                "%cpu": 0.0,
                "allow_destructive": True,
                "dnsmasq": {
                    "dns_cache_inserted": 0,
                    "dns_cache_live_freed": 0,
                    "dns_queries_forwarded": 0,
                    "dns_auth_answered": 0,
                    "dns_local_answered": 0,
                    "dns_stale_answered": 0,
                    "dns_unanswered": 0,
                    "dnssec_max_crypto_use": 0,
                    "dnssec_max_sig_fail": 0,
                    "dnssec_max_work": 0,
                    "bootp": 0,
                    "pxe": 0,
                    "dhcp_ack": 0,
                    "dhcp_decline": 0,
                    "dhcp_discover": 0,
                    "dhcp_inform": 0,
                    "dhcp_nak": 0,
                    "dhcp_offer": 0,
                    "dhcp_release": 0,
                    "dhcp_request": 0,
                    "noanswer": 0,
                    "leases_allocated_4": 0,
                    "leases_pruned_4": 0,
                    "leases_allocated_6": 0,
                    "leases_pruned_6": 0,
                    "tcp_connections": 0,
                    "dhcp_leasequery": 0,
                    "dhcp_lease_unassigned": 0,
                    "dhcp_lease_actve": 0,
                    "dhcp_lease_unknown": 0,
                },
            },
            "took": 0.001,
        }
        mock_request.return_value = mock_response

        result = info_client.get_ftl_info()

        assert result.ftl.pid == 1
        assert result.ftl.uptime == 0.0
        assert result.ftl.database.gravity == 0
        assert result.ftl.clients.total == 0


class TestPiHoleInfoHostInfo:
    """Test info client get_host_info functionality (no network calls)."""

    @patch("pihole_lib.info.make_pihole_request")
    def test_get_host_info_success(self, mock_request):
        """Should successfully get host info."""
        client = PiHoleClient(TEST_LOCALHOST_URL, password=TEST_SECRET_PASSWORD)
        info_client = PiHoleInfo(client)

        mock_response = Mock()
        mock_response.json.return_value = {
            "host": {
                "uname": {
                    "domainname": "(none)",
                    "machine": "x86_64",
                    "nodename": "pihole-server",
                    "release": "5.15.0-56-generic",
                    "sysname": "Linux",
                    "version": "#62-Ubuntu SMP Tue Nov 22 19:54:14 UTC 2022",
                },
                "model": "Dell OptiPlex 7090",
                "dmi": {
                    "bios": {"vendor": "Dell Inc."},
                    "board": {
                        "name": "0K240Y",
                        "vendor": "Dell Inc.",
                        "version": "A01",
                    },
                    "product": {
                        "name": "OptiPlex 7090",
                        "family": "OptiPlex",
                        "version": "",
                    },
                    "sys": {"vendor": "Dell Inc."},
                },
            },
            "took": 0.001,
        }
        mock_request.return_value = mock_response

        result = info_client.get_host_info()

        # Verify the request was made correctly
        mock_request.assert_called_once_with(
            client,
            "GET",
            f"{info_client.BASE_URL}/host",
        )

        # Verify the response structure
        assert result.host.uname.domainname == "(none)"
        assert result.host.uname.machine == "x86_64"
        assert result.host.uname.nodename == "pihole-server"
        assert result.host.uname.release == "5.15.0-56-generic"
        assert result.host.uname.sysname == "Linux"
        assert (
            result.host.uname.version == "#62-Ubuntu SMP Tue Nov 22 19:54:14 UTC 2022"
        )
        assert result.host.model == "Dell OptiPlex 7090"
        assert result.host.dmi.bios.vendor == "Dell Inc."
        assert result.host.dmi.board.name == "0K240Y"
        assert result.host.dmi.board.vendor == "Dell Inc."
        assert result.host.dmi.board.version == "A01"
        assert result.host.dmi.product.name == "OptiPlex 7090"
        assert result.host.dmi.product.family == "OptiPlex"
        assert result.host.dmi.product.version == ""
        assert result.host.dmi.sys.vendor == "Dell Inc."

    @patch("pihole_lib.info.make_pihole_request")
    def test_get_host_info_minimal_response(self, mock_request):
        """Should handle minimal host info response with null values."""
        client = PiHoleClient(TEST_LOCALHOST_URL, password=TEST_SECRET_PASSWORD)
        info_client = PiHoleInfo(client)

        mock_response = Mock()
        mock_response.json.return_value = {
            "host": {
                "uname": {
                    "domainname": "(none)",
                    "machine": "aarch64",
                    "nodename": "raspberrypi",
                    "release": "6.1.21-v8+",
                    "sysname": "Linux",
                    "version": "#1642 SMP PREEMPT Mon Apr  3 17:24:16 BST 2023",
                },
                "model": None,
                "dmi": {
                    "bios": {"vendor": None},
                    "board": {"name": None, "vendor": None, "version": None},
                    "product": {"name": None, "family": None, "version": None},
                    "sys": {"vendor": None},
                },
            },
            "took": 0.002,
        }
        mock_request.return_value = mock_response

        result = info_client.get_host_info()

        assert result.host.uname.machine == "aarch64"
        assert result.host.uname.nodename == "raspberrypi"
        assert result.host.uname.sysname == "Linux"
        assert result.host.model is None
        assert result.host.dmi.bios.vendor is None
        assert result.host.dmi.board.name is None
        assert result.host.dmi.product.name is None
        assert result.host.dmi.sys.vendor is None

    @patch("pihole_lib.info.make_pihole_request")
    def test_get_host_info_container_response(self, mock_request):
        """Should handle container host info response."""
        client = PiHoleClient(TEST_LOCALHOST_URL, password=TEST_SECRET_PASSWORD)
        info_client = PiHoleInfo(client)

        mock_response = Mock()
        mock_response.json.return_value = {
            "host": {
                "uname": {
                    "domainname": "(none)",
                    "machine": "aarch64",
                    "nodename": "716096fc064e",
                    "release": "6.10.14-linuxkit",
                    "sysname": "Linux",
                    "version": "#1 SMP Sat May 17 08:28:57 UTC 2025",
                },
                "model": None,
                "dmi": {
                    "bios": {"vendor": None},
                    "board": {"name": None, "vendor": None, "version": None},
                    "product": {"name": None, "family": None, "version": None},
                    "sys": {"vendor": None},
                },
            },
            "took": 0.0001,
        }
        mock_request.return_value = mock_response

        result = info_client.get_host_info()

        # Container-specific assertions
        assert (
            result.host.uname.nodename == "716096fc064e"
        )  # Container ID-like hostname
        assert "linuxkit" in result.host.uname.release  # Docker/container kernel
        assert result.host.model is None  # Containers don't have hardware models
        assert result.host.dmi.sys.vendor is None  # No DMI info in containers


class TestPiHoleInfoVersionInfo:
    """Test info client get_version_info functionality (no network calls)."""

    @patch("pihole_lib.info.make_pihole_request")
    def test_get_version_info_success(self, mock_request):
        """Should successfully get version info."""
        client = PiHoleClient(TEST_LOCALHOST_URL, password=TEST_SECRET_PASSWORD)
        info_client = PiHoleInfo(client)

        mock_response = Mock()
        mock_response.json.return_value = {
            "version": {
                "core": {
                    "local": {
                        "version": "v6.3",
                        "branch": "master",
                        "hash": "5a23c9c3",
                    },
                    "remote": {"version": "v6.3", "hash": "5a23c9c3"},
                },
                "web": {
                    "local": {
                        "version": "v6.4",
                        "branch": "master",
                        "hash": "cd0c392d",
                    },
                    "remote": {"version": "v6.4", "hash": "cd0c392d"},
                },
                "ftl": {
                    "local": {
                        "hash": "8d1add8d",
                        "branch": "master",
                        "version": "v6.4.1",
                        "date": "2025-11-27 18:02:19 +0000",
                    },
                    "remote": {"version": "v6.4.1", "hash": "8d1add8d"},
                },
                "docker": {"local": "2025.11.1", "remote": "2025.11.1"},
            },
            "took": 0.001,
        }
        mock_request.return_value = mock_response

        result = info_client.get_version_info()

        # Verify the request was made correctly
        mock_request.assert_called_once_with(
            client,
            "GET",
            f"{info_client.BASE_URL}/version",
        )

        # Verify the response structure
        assert result.version.core.local.version == "v6.3"
        assert result.version.core.local.branch == "master"
        assert result.version.core.local.hash == "5a23c9c3"
        assert result.version.core.remote.version == "v6.3"
        assert result.version.core.remote.hash == "5a23c9c3"

        assert result.version.web.local.version == "v6.4"
        assert result.version.web.local.branch == "master"
        assert result.version.web.local.hash == "cd0c392d"
        assert result.version.web.remote.version == "v6.4"
        assert result.version.web.remote.hash == "cd0c392d"

        assert result.version.ftl.local.version == "v6.4.1"
        assert result.version.ftl.local.branch == "master"
        assert result.version.ftl.local.hash == "8d1add8d"
        assert result.version.ftl.local.date == "2025-11-27 18:02:19 +0000"
        assert result.version.ftl.remote.version == "v6.4.1"
        assert result.version.ftl.remote.hash == "8d1add8d"

        assert result.version.docker.local == "2025.11.1"
        assert result.version.docker.remote == "2025.11.1"

    @patch("pihole_lib.info.make_pihole_request")
    def test_get_version_info_update_available(self, mock_request):
        """Should handle version info when updates are available."""
        client = PiHoleClient(TEST_LOCALHOST_URL, password=TEST_SECRET_PASSWORD)
        info_client = PiHoleInfo(client)

        mock_response = Mock()
        mock_response.json.return_value = {
            "version": {
                "core": {
                    "local": {"version": "v6.2", "branch": "master", "hash": "abc123"},
                    "remote": {"version": "v6.3", "hash": "def456"},
                },
                "web": {
                    "local": {"version": "v6.3", "branch": "master", "hash": "ghi789"},
                    "remote": {"version": "v6.4", "hash": "jkl012"},
                },
                "ftl": {
                    "local": {
                        "hash": "mno345",
                        "branch": "master",
                        "version": "v6.4.0",
                        "date": "2025-10-15 12:00:00 +0000",
                    },
                    "remote": {"version": "v6.4.1", "hash": "pqr678"},
                },
                "docker": {"local": "2025.10.1", "remote": "2025.11.1"},
            },
            "took": 0.002,
        }
        mock_request.return_value = mock_response

        result = info_client.get_version_info()

        # Verify updates are detected
        assert result.version.core.local.version != result.version.core.remote.version
        assert result.version.web.local.version != result.version.web.remote.version
        assert result.version.ftl.local.version != result.version.ftl.remote.version
        assert result.version.docker.local != result.version.docker.remote

        # Verify specific versions
        assert result.version.core.local.version == "v6.2"
        assert result.version.core.remote.version == "v6.3"
        assert result.version.ftl.local.version == "v6.4.0"
        assert result.version.ftl.remote.version == "v6.4.1"

    @patch("pihole_lib.info.make_pihole_request")
    def test_get_version_info_development_branch(self, mock_request):
        """Should handle version info from development branches."""
        client = PiHoleClient(TEST_LOCALHOST_URL, password=TEST_SECRET_PASSWORD)
        info_client = PiHoleInfo(client)

        mock_response = Mock()
        mock_response.json.return_value = {
            "version": {
                "core": {
                    "local": {
                        "version": "v6.4-dev",
                        "branch": "development",
                        "hash": "abc123",
                    },
                    "remote": {"version": "v6.3", "hash": "def456"},
                },
                "web": {
                    "local": {
                        "version": "v6.5-beta",
                        "branch": "beta",
                        "hash": "ghi789",
                    },
                    "remote": {"version": "v6.4", "hash": "jkl012"},
                },
                "ftl": {
                    "local": {
                        "hash": "mno345",
                        "branch": "development",
                        "version": "v6.5-dev",
                        "date": "2025-12-01 10:30:00 +0000",
                    },
                    "remote": {"version": "v6.4.1", "hash": "pqr678"},
                },
                "docker": {"local": "dev", "remote": "2025.11.1"},
            },
            "took": 0.001,
        }
        mock_request.return_value = mock_response

        result = info_client.get_version_info()

        # Verify development versions
        assert result.version.core.local.branch == "development"
        assert result.version.web.local.branch == "beta"
        assert result.version.ftl.local.branch == "development"
        assert "dev" in result.version.core.local.version
        assert "beta" in result.version.web.local.version
        assert "dev" in result.version.ftl.local.version
        assert result.version.docker.local == "dev"


class TestPiHoleInfoSystemInfo:
    """Test info client get_system_info functionality (no network calls)."""

    @patch("pihole_lib.info.make_pihole_request")
    def test_get_system_info_success(self, mock_request):
        """Should successfully get system info."""
        client = PiHoleClient(TEST_LOCALHOST_URL, password=TEST_SECRET_PASSWORD)
        info_client = PiHoleInfo(client)

        mock_response = Mock()
        mock_response.json.return_value = {
            "system": {
                "uptime": 4240,
                "memory": {
                    "ram": {
                        "total": 8025428,
                        "free": 7235000,
                        "used": 327224,
                        "available": 7540972,
                        "%used": 4.077340174256127,
                    },
                    "swap": {"total": 1048572, "free": 1048572, "used": 0, "%used": 0},
                },
                "procs": 283,
                "cpu": {
                    "nprocs": 10,
                    "%cpu": 183.17999267578125,
                    "load": {
                        "raw": [0.16015625, 0.26513671875, 0.265625],
                        "percent": [1.6015625, 2.6513671875, 2.65625],
                    },
                },
                "ftl": {"%mem": 0.10985083878040314, "%cpu": 0.2199999988079071},
            },
            "took": 0.001,
        }
        mock_request.return_value = mock_response

        result = info_client.get_system_info()

        # Verify the request was made correctly
        mock_request.assert_called_once_with(
            client,
            "GET",
            f"{info_client.BASE_URL}/system",
        )

        # Verify the response structure
        assert result.system.uptime == 4240
        assert result.system.procs == 283

        # Verify memory information
        assert result.system.memory.ram.total == 8025428
        assert result.system.memory.ram.free == 7235000
        assert result.system.memory.ram.used == 327224
        assert result.system.memory.ram.available == 7540972
        assert result.system.memory.ram.percent_used == 4.077340174256127

        assert result.system.memory.swap.total == 1048572
        assert result.system.memory.swap.free == 1048572
        assert result.system.memory.swap.used == 0
        assert result.system.memory.swap.percent_used == 0

        # Verify CPU information
        assert result.system.cpu.nprocs == 10
        assert result.system.cpu.percent_cpu == 183.17999267578125
        assert result.system.cpu.load.raw == [0.16015625, 0.26513671875, 0.265625]
        assert result.system.cpu.load.percent == [1.6015625, 2.6513671875, 2.65625]

        # Verify FTL information
        assert result.system.ftl.percent_mem == 0.10985083878040314
        assert result.system.ftl.percent_cpu == 0.2199999988079071

    @patch("pihole_lib.info.make_pihole_request")
    def test_get_system_info_high_usage(self, mock_request):
        """Should handle system info with high resource usage."""
        client = PiHoleClient(TEST_LOCALHOST_URL, password=TEST_SECRET_PASSWORD)
        info_client = PiHoleInfo(client)

        mock_response = Mock()
        mock_response.json.return_value = {
            "system": {
                "uptime": 86400,
                "memory": {
                    "ram": {
                        "total": 4194304,
                        "free": 419430,
                        "used": 3774874,
                        "available": 1048576,
                        "%used": 90.0,
                    },
                    "swap": {
                        "total": 2097152,
                        "free": 1048576,
                        "used": 1048576,
                        "%used": 50.0,
                    },
                },
                "procs": 500,
                "cpu": {
                    "nprocs": 4,
                    "%cpu": 400.0,
                    "load": {
                        "raw": [3.5, 2.8, 2.1],
                        "percent": [87.5, 70.0, 52.5],
                    },
                },
                "ftl": {"%mem": 5.5, "%cpu": 15.2},
            },
            "took": 0.002,
        }
        mock_request.return_value = mock_response

        result = info_client.get_system_info()

        # Verify high usage values
        assert result.system.uptime == 86400
        assert result.system.procs == 500
        assert result.system.memory.ram.percent_used == 90.0
        assert result.system.memory.swap.percent_used == 50.0
        assert result.system.cpu.nprocs == 4
        assert result.system.cpu.percent_cpu == 400.0
        assert result.system.cpu.load.raw == [3.5, 2.8, 2.1]
        assert result.system.ftl.percent_mem == 5.5
        assert result.system.ftl.percent_cpu == 15.2

    @patch("pihole_lib.info.make_pihole_request")
    def test_get_system_info_minimal_usage(self, mock_request):
        """Should handle system info with minimal resource usage."""
        client = PiHoleClient(TEST_LOCALHOST_URL, password=TEST_SECRET_PASSWORD)
        info_client = PiHoleInfo(client)

        mock_response = Mock()
        mock_response.json.return_value = {
            "system": {
                "uptime": 60,
                "memory": {
                    "ram": {
                        "total": 1048576,
                        "free": 1000000,
                        "used": 48576,
                        "available": 1000000,
                        "%used": 4.6,
                    },
                    "swap": {"total": 0, "free": 0, "used": 0, "%used": 0},
                },
                "procs": 50,
                "cpu": {
                    "nprocs": 1,
                    "%cpu": 5.0,
                    "load": {
                        "raw": [0.01, 0.02, 0.03],
                        "percent": [1.0, 2.0, 3.0],
                    },
                },
                "ftl": {"%mem": 0.1, "%cpu": 0.05},
            },
            "took": 0.0005,
        }
        mock_request.return_value = mock_response

        result = info_client.get_system_info()

        # Verify minimal usage values
        assert result.system.uptime == 60
        assert result.system.procs == 50
        assert result.system.memory.ram.percent_used == 4.6
        assert result.system.memory.swap.total == 0
        assert result.system.cpu.nprocs == 1
        assert result.system.cpu.percent_cpu == 5.0
        assert result.system.ftl.percent_mem == 0.1
        assert result.system.ftl.percent_cpu == 0.05


class TestPiHoleInfoMessagesInfo:
    """Test info client get_messages functionality (no network calls)."""

    @patch("pihole_lib.info.make_pihole_request")
    def test_get_messages_empty(self, mock_request):
        """Should successfully get empty messages list."""
        client = PiHoleClient(TEST_LOCALHOST_URL, password=TEST_SECRET_PASSWORD)
        info_client = PiHoleInfo(client)

        mock_response = Mock()
        mock_response.json.return_value = {
            "messages": [],
            "took": 0.001,
        }
        mock_request.return_value = mock_response

        result = info_client.get_messages()

        # Verify the request was made correctly
        mock_request.assert_called_once_with(
            client,
            "GET",
            f"{info_client.BASE_URL}/messages",
        )

        # Verify the response structure
        assert len(result.messages) == 0
        assert isinstance(result.messages, list)

    @patch("pihole_lib.info.make_pihole_request")
    def test_get_messages_with_content(self, mock_request):
        """Should successfully get messages with content."""
        client = PiHoleClient(TEST_LOCALHOST_URL, password=TEST_SECRET_PASSWORD)
        info_client = PiHoleInfo(client)

        mock_response = Mock()
        mock_response.json.return_value = {
            "messages": [
                {
                    "id": 1,
                    "timestamp": 1767779556,
                    "type": "info",
                    "plain": "Pi-hole started successfully",
                    "html": "<strong>Pi-hole</strong> started successfully",
                },
                {
                    "id": 2,
                    "timestamp": 1767779600,
                    "type": "warning",
                    "plain": "High memory usage detected",
                    "html": "<span class='warning'>High memory usage detected</span>",
                },
                {
                    "id": 3,
                    "timestamp": 1767779700,
                    "type": "error",
                    "plain": "Failed to update gravity database",
                    "html": "<span class='error'>Failed to update gravity database</span>",
                },
            ],
            "took": 0.002,
        }
        mock_request.return_value = mock_response

        result = info_client.get_messages()

        # Verify the response structure
        assert len(result.messages) == 3

        # Verify first message
        msg1 = result.messages[0]
        assert msg1.id == 1
        assert msg1.timestamp == 1767779556
        assert msg1.type == "info"
        assert msg1.plain == "Pi-hole started successfully"
        assert msg1.html == "<strong>Pi-hole</strong> started successfully"

        # Verify second message
        msg2 = result.messages[1]
        assert msg2.id == 2
        assert msg2.timestamp == 1767779600
        assert msg2.type == "warning"
        assert msg2.plain == "High memory usage detected"
        assert msg2.html == "<span class='warning'>High memory usage detected</span>"

        # Verify third message
        msg3 = result.messages[2]
        assert msg3.id == 3
        assert msg3.timestamp == 1767779700
        assert msg3.type == "error"
        assert msg3.plain == "Failed to update gravity database"
        assert (
            msg3.html == "<span class='error'>Failed to update gravity database</span>"
        )

    @patch("pihole_lib.info.make_pihole_request")
    def test_get_messages_single_message(self, mock_request):
        """Should handle single message response."""
        client = PiHoleClient(TEST_LOCALHOST_URL, password=TEST_SECRET_PASSWORD)
        info_client = PiHoleInfo(client)

        mock_response = Mock()
        mock_response.json.return_value = {
            "messages": [
                {
                    "id": 100,
                    "timestamp": 1767800000,
                    "type": "info",
                    "plain": "New Pi-hole version available: v6.5",
                    "html": "New <strong>Pi-hole</strong> version available: <em>v6.5</em>",
                }
            ],
            "took": 0.0005,
        }
        mock_request.return_value = mock_response

        result = info_client.get_messages()

        assert len(result.messages) == 1
        message = result.messages[0]
        assert message.id == 100
        assert message.type == "info"
        assert "v6.5" in message.plain
        assert "v6.5" in message.html
        assert "<strong>" in message.html
        assert "<em>" in message.html


class TestPiHoleInfoMessagesCountInfo:
    """Test info client get_messages_count functionality (no network calls)."""

    @patch("pihole_lib.info.make_pihole_request")
    def test_get_messages_count_zero(self, mock_request):
        """Should successfully get zero messages count."""
        client = PiHoleClient(TEST_LOCALHOST_URL, password=TEST_SECRET_PASSWORD)
        info_client = PiHoleInfo(client)

        mock_response = Mock()
        mock_response.json.return_value = {
            "count": 0,
            "took": 0.001,
        }
        mock_request.return_value = mock_response

        result = info_client.get_messages_count()

        # Verify the request was made correctly
        mock_request.assert_called_once_with(
            client,
            "GET",
            "/api/info/messages/count",
        )

        # Verify the response structure
        assert result.count == 0
        assert isinstance(result.count, int)

    @patch("pihole_lib.info.make_pihole_request")
    def test_get_messages_count_positive(self, mock_request):
        """Should successfully get positive messages count."""
        client = PiHoleClient(TEST_LOCALHOST_URL, password=TEST_SECRET_PASSWORD)
        info_client = PiHoleInfo(client)

        mock_response = Mock()
        mock_response.json.return_value = {
            "count": 5,
            "took": 0.002,
        }
        mock_request.return_value = mock_response

        result = info_client.get_messages_count()

        # Verify the response structure
        assert result.count == 5
        assert isinstance(result.count, int)

    @patch("pihole_lib.info.make_pihole_request")
    def test_get_messages_count_large_number(self, mock_request):
        """Should handle large message counts."""
        client = PiHoleClient(TEST_LOCALHOST_URL, password=TEST_SECRET_PASSWORD)
        info_client = PiHoleInfo(client)

        mock_response = Mock()
        mock_response.json.return_value = {
            "count": 1000,
            "took": 0.0005,
        }
        mock_request.return_value = mock_response

        result = info_client.get_messages_count()

        assert result.count == 1000
        assert isinstance(result.count, int)
