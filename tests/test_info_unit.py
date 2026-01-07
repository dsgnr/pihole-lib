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
            "/api/info/client",
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
            "/api/info/database",
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
            "/api/info/ftl",
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
