"""Unit tests for PiHolePADD class."""

from unittest.mock import Mock, patch

import pytest

from pihole_lib import PiHoleClient, PiHolePADD
from pihole_lib.exceptions import PiHoleAPIError
from pihole_lib.models import PADDInfo


class TestPiHolePADD:
    """Test cases for PiHolePADD class."""

    @pytest.fixture
    def mock_client(self):
        """Create a mock PiHoleClient for testing."""
        client = Mock(spec=PiHoleClient)
        client.base_url = "http://localhost"
        client._session = Mock()
        return client

    @pytest.fixture
    def padd_client(self, mock_client):
        """Create a PiHolePADD instance for testing."""
        return PiHolePADD(mock_client)

    @patch("pihole_lib.padd.make_pihole_request")
    def test_get_dashboard_data_success(self, mock_request, padd_client, mock_client):
        """Test successful dashboard data retrieval."""
        # Mock response data (simplified version of actual response)
        mock_response = {
            "active_clients": 5,
            "gravity_size": 79811,
            "top_domain": "example.com",
            "top_blocked": "ads.example.com",
            "top_client": "192.168.1.100",
            "recent_blocked": "tracker.example.com",
            "blocking": "enabled",
            "queries": {"total": 1000, "blocked": 150, "percent_blocked": 15.0},
            "cache": {"size": 10000, "inserted": 500, "evicted": 50},
            "system": {
                "uptime": 86400,
                "memory": {
                    "ram": {
                        "total": 8025428,
                        "free": 7000000,
                        "used": 1025428,
                        "available": 7500000,
                        "%used": 12.8,
                    },
                    "swap": {
                        "total": 1048572,
                        "free": 1048572,
                        "used": 0,
                        "%used": 0.0,
                    },
                },
                "procs": 280,
                "cpu": {
                    "nprocs": 4,
                    "%cpu": 5.2,
                    "load": {"raw": [0.5, 0.3, 0.1], "percent": [12.5, 7.5, 2.5]},
                },
                "ftl": {"%mem": 0.5, "%cpu": 1.2},
            },
            "node_name": "pihole",
            "host_model": "Raspberry Pi 4",
            "iface": {
                "v4": {
                    "addr": "192.168.1.10",
                    "rx_bytes": {"value": 1.5, "unit": "M"},
                    "tx_bytes": {"value": 500.0, "unit": "K"},
                    "num_addrs": 1,
                    "name": "eth0",
                    "gw_addr": "192.168.1.1",
                },
                "v6": {"addr": None, "num_addrs": 0, "name": "eth0", "gw_addr": None},
            },
            "version": {
                "core": {
                    "local": {"version": "v6.3", "branch": "master", "hash": "abc123"},
                    "remote": {"version": "v6.3", "hash": "abc123"},
                },
                "web": {
                    "local": {"version": "v6.4", "branch": "master", "hash": "def456"},
                    "remote": {"version": "v6.4", "hash": "def456"},
                },
                "ftl": {
                    "local": {
                        "version": "v6.4.1",
                        "branch": "master",
                        "hash": "ghi789",
                        "date": "2025-01-01 12:00:00 +0000",
                    },
                    "remote": {"version": "v6.4.1", "hash": "ghi789"},
                },
                "docker": {"local": "2025.01.1", "remote": "2025.01.1"},
            },
            "config": {
                "dhcp_active": True,
                "dhcp_start": "192.168.1.100",
                "dhcp_end": "192.168.1.200",
                "dhcp_ipv6": False,
                "dns_domain": "lan",
                "dns_port": 53,
                "dns_num_upstreams": 2,
                "dns_dnssec": True,
                "dns_revServer_active": False,
                "privacy_level": 0,
            },
            "%mem": 0.8,
            "%cpu": 2.1,
            "pid": 1234,
            "sensors": {"cpu_temp": 45.5, "hot_limit": 60, "unit": "C"},
            "took": 0.001,
        }
        mock_request.return_value.json.return_value = mock_response

        # Call method
        result = padd_client.get_dashboard_data()

        # Verify request was made correctly
        mock_request.assert_called_once_with(
            mock_client,
            "GET",
            padd_client.BASE_URL,
        )

        # Verify result
        assert isinstance(result, PADDInfo)
        assert result.active_clients == 5
        assert result.gravity_size == 79811
        assert result.top_domain == "example.com"
        assert result.blocking == "enabled"

        # Check nested structures
        assert result.queries.total == 1000
        assert result.queries.blocked == 150
        assert result.queries.percent_blocked == 15.0

        assert result.system.uptime == 86400
        assert result.system.memory.ram.total == 8025428
        assert result.system.cpu.nprocs == 4

        assert result.iface.v4.addr == "192.168.1.10"
        assert result.iface.v4.gw_addr == "192.168.1.1"

        assert result.version.core.local.version == "v6.3"
        assert result.config.dhcp_active is True
        assert result.sensors.cpu_temp == 45.5

    @patch("pihole_lib.padd.make_pihole_request")
    def test_get_dashboard_data_with_nulls(self, mock_request, padd_client):
        """Test dashboard data retrieval with null values."""
        # Mock response with null values
        mock_response = {
            "active_clients": 0,
            "gravity_size": 0,
            "top_domain": None,
            "top_blocked": None,
            "top_client": None,
            "recent_blocked": None,
            "blocking": "disabled",
            "queries": {"total": 0, "blocked": 0, "percent_blocked": 0.0},
            "cache": {"size": 10000, "inserted": 0, "evicted": 0},
            "system": {
                "uptime": 100,
                "memory": {
                    "ram": {
                        "total": 1000000,
                        "free": 900000,
                        "used": 100000,
                        "available": 950000,
                        "%used": 10.0,
                    },
                    "swap": {"total": 0, "free": 0, "used": 0, "%used": 0.0},
                },
                "procs": 50,
                "cpu": {
                    "nprocs": 1,
                    "%cpu": 1.0,
                    "load": {"raw": [0.1], "percent": [10.0]},
                },
                "ftl": {"%mem": 0.1, "%cpu": 0.5},
            },
            "node_name": "test",
            "host_model": None,
            "iface": {
                "v4": {
                    "addr": "127.0.0.1",
                    "rx_bytes": {"value": 0.0, "unit": ""},
                    "tx_bytes": {"value": 0.0, "unit": ""},
                    "num_addrs": 1,
                    "name": "lo",
                    "gw_addr": None,
                },
                "v6": {"addr": None, "num_addrs": 0, "name": "lo", "gw_addr": None},
            },
            "version": {
                "core": {
                    "local": {"version": "v6.0", "branch": None, "hash": "000"},
                    "remote": {"version": "v6.0", "hash": "000"},
                },
                "web": {
                    "local": {"version": "v6.0", "branch": None, "hash": "000"},
                    "remote": {"version": "v6.0", "hash": "000"},
                },
                "ftl": {
                    "local": {
                        "version": "v6.0",
                        "branch": None,
                        "hash": "000",
                        "date": None,
                    },
                    "remote": {"version": "v6.0", "hash": "000"},
                },
                "docker": {"local": "2025.01.1", "remote": "2025.01.1"},
            },
            "config": {
                "dhcp_active": False,
                "dhcp_start": "",
                "dhcp_end": "",
                "dhcp_ipv6": False,
                "dns_domain": "local",
                "dns_port": 53,
                "dns_num_upstreams": 1,
                "dns_dnssec": False,
                "dns_revServer_active": False,
                "privacy_level": 0,
            },
            "%mem": 0.1,
            "%cpu": 0.5,
            "pid": 100,
            "sensors": {"cpu_temp": None, "hot_limit": 60, "unit": "C"},
            "took": 0.001,
        }
        mock_request.return_value.json.return_value = mock_response

        # Call method
        result = padd_client.get_dashboard_data()

        # Verify result handles null values correctly
        assert isinstance(result, PADDInfo)
        assert result.top_domain is None
        assert result.top_blocked is None
        assert result.host_model is None
        assert result.sensors.cpu_temp is None

    @patch("pihole_lib.padd.make_pihole_request")
    def test_get_dashboard_data_api_error(self, mock_request, padd_client):
        """Test dashboard data retrieval with API error."""
        # Mock API error
        mock_request.side_effect = PiHoleAPIError("API request failed")

        # Call method and expect exception
        with pytest.raises(PiHoleAPIError, match="API request failed"):
            padd_client.get_dashboard_data()

    def test_inheritance(self, padd_client):
        """Test that PiHolePADD inherits from BasePiHoleAPIClient."""
        from pihole_lib.base import BasePiHoleAPIClient

        assert isinstance(padd_client, BasePiHoleAPIClient)
