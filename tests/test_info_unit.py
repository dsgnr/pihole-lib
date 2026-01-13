"""Unit tests for PiHoleInfo."""

from unittest.mock import patch

import pytest

from pihole_lib import PiHoleInfo
from tests.conftest import make_client, make_mock_response

# Sample response data for tests
SAMPLE_CLIENT_INFO = {
    "remote_addr": "192.168.1.100",
    "http_version": "1.1",
    "method": "GET",
    "headers": [
        {"name": "Host", "value": "localhost:8080"},
        {"name": "User-Agent", "value": "python-requests/2.32.5"},
    ],
    "took": 0.001,
}

SAMPLE_DATABASE_INFO = {
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

SAMPLE_FTL_INFO = {
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
        "%mem": 0.109,
        "%cpu": 0.06,
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

SAMPLE_HOST_INFO = {
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
            "board": {"name": "0K240Y", "vendor": "Dell Inc.", "version": "A01"},
            "product": {"name": "OptiPlex 7090", "family": "OptiPlex", "version": ""},
            "sys": {"vendor": "Dell Inc."},
        },
    },
    "took": 0.001,
}

SAMPLE_VERSION_INFO = {
    "version": {
        "core": {
            "local": {"version": "v6.3", "branch": "master", "hash": "5a23c9c3"},
            "remote": {"version": "v6.3", "hash": "5a23c9c3"},
        },
        "web": {
            "local": {"version": "v6.4", "branch": "master", "hash": "cd0c392d"},
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

SAMPLE_SYSTEM_INFO = {
    "system": {
        "uptime": 86400,
        "memory": {
            "ram": {
                "total": 8000000000,
                "free": 4000000000,
                "used": 4000000000,
                "available": 5000000000,
                "%used": 50.0,
            },
            "swap": {"total": 2000000000, "free": 2000000000, "used": 0, "%used": 0.0},
        },
        "procs": 150,
        "cpu": {
            "nprocs": 4,
            "%cpu": 15.0,
            "load": {"raw": [0.5, 0.4, 0.3], "percent": [12.5, 10.0, 7.5]},
        },
        "ftl": {"%mem": 0.109, "%cpu": 0.06},
    },
    "took": 0.001,
}


@pytest.fixture
def info_client(mock_client):
    """Create a PiHoleInfo instance for testing."""
    return PiHoleInfo(mock_client)


class TestPiHoleInfoInit:
    """Test info client initialization."""

    def test_init_with_client(self):
        """Info client should initialize with a PiHoleClient."""
        client = make_client()
        info_client = PiHoleInfo(client)
        assert info_client._client is client

    def test_get_login_info_creates_session(self):
        """get_login_info should create client session."""
        client = make_client()
        info_client = PiHoleInfo(client)
        assert client._session is None

        try:
            info_client.get_login_info()
        except Exception:
            pass  # Expected to fail without network

        assert client._session is not None


class TestPiHoleInfoEndpoints:
    """Test all info endpoint methods."""

    @pytest.mark.parametrize(
        "method,endpoint,response_data,result_attr",
        [
            ("get_client_info", "/client", SAMPLE_CLIENT_INFO, "remote_addr"),
            ("get_database_info", "/database", SAMPLE_DATABASE_INFO, "size"),
            ("get_ftl_info", "/ftl", SAMPLE_FTL_INFO, "ftl"),
            ("get_host_info", "/host", SAMPLE_HOST_INFO, "host"),
            ("get_version_info", "/version", SAMPLE_VERSION_INFO, "version"),
            ("get_system_info", "/system", SAMPLE_SYSTEM_INFO, "system"),
        ],
    )
    @patch("pihole_lib.info.make_pihole_request")
    def test_info_endpoints(
        self,
        mock_request,
        info_client,
        mock_client,
        method,
        endpoint,
        response_data,
        result_attr,
    ):
        """Test all info endpoint methods return correct data."""
        mock_request.return_value = make_mock_response(json_data=response_data)

        result = getattr(info_client, method)()

        mock_request.assert_called_once_with(
            mock_client, "GET", f"{info_client.BASE_URL}{endpoint}"
        )
        assert hasattr(result, result_attr)


class TestPiHoleInfoClientInfo:
    """Test client info specific functionality."""

    @patch("pihole_lib.info.make_pihole_request")
    def test_get_client_info_headers(self, mock_request, info_client):
        """Should parse headers correctly."""
        mock_request.return_value = make_mock_response(json_data=SAMPLE_CLIENT_INFO)

        result = info_client.get_client_info()

        assert len(result.headers) == 2
        assert result.headers[0].name == "Host"
        assert result.headers[0].value == "localhost:8080"

    @patch("pihole_lib.info.make_pihole_request")
    def test_get_client_info_empty_headers(self, mock_request, info_client):
        """Should handle empty headers list."""
        mock_request.return_value = make_mock_response(
            json_data={**SAMPLE_CLIENT_INFO, "headers": []}
        )

        result = info_client.get_client_info()
        assert len(result.headers) == 0


class TestPiHoleInfoDatabaseInfo:
    """Test database info specific functionality."""

    @patch("pihole_lib.info.make_pihole_request")
    def test_get_database_info_owner(self, mock_request, info_client):
        """Should parse owner information correctly."""
        mock_request.return_value = make_mock_response(json_data=SAMPLE_DATABASE_INFO)

        result = info_client.get_database_info()

        assert result.owner.user.uid == 1000
        assert result.owner.user.name == "pihole"
        assert result.owner.group.gid == 1000
        assert result.owner.group.name == "pihole"


class TestPiHoleInfoFTLInfo:
    """Test FTL info specific functionality."""

    @patch("pihole_lib.info.make_pihole_request")
    def test_get_ftl_info_structure(self, mock_request, info_client):
        """Should parse FTL info structure correctly."""
        mock_request.return_value = make_mock_response(json_data=SAMPLE_FTL_INFO)

        result = info_client.get_ftl_info()

        assert result.ftl.pid == 191
        assert result.ftl.uptime == 12470.752492
        assert result.ftl.database.gravity == 79811
        assert result.ftl.clients.total == 0


class TestPiHoleInfoHostInfo:
    """Test host info specific functionality."""

    @patch("pihole_lib.info.make_pihole_request")
    def test_get_host_info_uname(self, mock_request, info_client):
        """Should parse uname information correctly."""
        mock_request.return_value = make_mock_response(json_data=SAMPLE_HOST_INFO)

        result = info_client.get_host_info()

        assert result.host.uname.sysname == "Linux"
        assert result.host.uname.machine == "x86_64"
        assert result.host.model == "Dell OptiPlex 7090"

    @patch("pihole_lib.info.make_pihole_request")
    def test_get_host_info_null_values(self, mock_request, info_client):
        """Should handle null values in host info."""
        null_host_info = {
            "host": {
                "uname": SAMPLE_HOST_INFO["host"]["uname"],
                "model": None,
                "dmi": {
                    "bios": {"vendor": None},
                    "board": {"name": None, "vendor": None, "version": None},
                    "product": {"name": None, "family": None, "version": None},
                    "sys": {"vendor": None},
                },
            },
            "took": 0.001,
        }
        mock_request.return_value = make_mock_response(json_data=null_host_info)

        result = info_client.get_host_info()

        assert result.host.model is None
        assert result.host.dmi.bios.vendor is None


class TestPiHoleInfoVersionInfo:
    """Test version info specific functionality."""

    @patch("pihole_lib.info.make_pihole_request")
    def test_get_version_info_components(self, mock_request, info_client):
        """Should parse all version components correctly."""
        mock_request.return_value = make_mock_response(json_data=SAMPLE_VERSION_INFO)

        result = info_client.get_version_info()

        assert result.version.core.local.version == "v6.3"
        assert result.version.web.local.version == "v6.4"
        assert result.version.ftl.local.version == "v6.4.1"
        assert result.version.docker.local == "2025.11.1"


class TestPiHoleInfoSystemInfo:
    """Test system info specific functionality."""

    @patch("pihole_lib.info.make_pihole_request")
    def test_get_system_info_structure(self, mock_request, info_client):
        """Should parse system info structure correctly."""
        mock_request.return_value = make_mock_response(json_data=SAMPLE_SYSTEM_INFO)

        result = info_client.get_system_info()

        assert result.system.uptime == 86400
        assert result.system.procs == 150
        assert result.system.cpu.nprocs == 4


class TestPiHoleInfoClientProperties:
    """Test that info client uses client properties correctly."""

    def test_uses_client_properties(self):
        """Info client should use client's base_url and timeout."""
        client = make_client(timeout=60, verify_ssl=False)
        info_client = PiHoleInfo(client)

        assert info_client._client.timeout == 60
        assert info_client._client.verify_ssl is False
