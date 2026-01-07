"""Unit tests for Pi-hole network API client."""

from unittest.mock import Mock, patch

import pytest

from pihole_lib import PiHoleClient, PiHoleNetwork
from pihole_lib.exceptions import PiHoleAPIError, PiHoleAuthenticationError

from .constants import PIHOLE_BASE_URL, TEST_SESSION_ID


@pytest.fixture
def mock_client():
    """Create a mock Pi-hole client."""
    client = PiHoleClient(PIHOLE_BASE_URL, "password")
    client._session_id = TEST_SESSION_ID
    return client


@pytest.fixture
def network_client(mock_client):
    """Create a network API client."""
    return PiHoleNetwork(mock_client)


class TestPiHoleNetwork:
    """Test cases for PiHoleNetwork class."""

    def test_init(self, mock_client):
        """Test network client initialization."""
        network = PiHoleNetwork(mock_client)
        assert network._client is mock_client

    def test_get_devices_success(self, network_client):
        """Test successful device retrieval."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "devices": [
                {
                    "id": 1,
                    "hwaddr": "aa:bb:cc:dd:ee:ff",
                    "interface": "eth0",
                    "name": "Test Device",
                    "first_seen": 1640995200,
                    "last_query": 1640995300,
                    "num_queries": 100,
                    "addresses": [
                        {
                            "ip": "192.168.1.100",
                            "hostname": "test-device.local",
                            "last_query": 1640995300,
                        }
                    ],
                }
            ],
            "took": 0.001,
        }

        with patch(
            "pihole_lib.network.make_pihole_request", return_value=mock_response
        ):
            result = network_client.get_devices()

        assert len(result.devices) == 1
        device = result.devices[0]
        assert device.id == 1
        assert device.hwaddr == "aa:bb:cc:dd:ee:ff"
        assert device.interface == "eth0"
        assert device.name == "Test Device"
        assert device.first_seen == 1640995200
        assert device.last_query == 1640995300
        assert device.num_queries == 100
        assert len(device.addresses) == 1
        assert device.addresses[0].ip == "192.168.1.100"
        assert device.addresses[0].hostname == "test-device.local"
        assert device.addresses[0].last_query == 1640995300
        assert result.took == 0.001

    def test_get_devices_with_params(self, network_client):
        """Test device retrieval with parameters."""
        mock_response = Mock()
        mock_response.json.return_value = {"devices": [], "took": 0.001}

        with patch(
            "pihole_lib.network.make_pihole_request", return_value=mock_response
        ) as mock_request:
            network_client.get_devices(max_devices=5, max_addresses=3)

            # Check that the request was made with correct parameters
            mock_request.assert_called_once_with(
                network_client._client,
                "GET",
                "/api/network/devices",
                params={"max_devices": 5, "max_addresses": 3},
            )

    def test_get_devices_empty(self, network_client):
        """Test device retrieval with empty response."""
        mock_response = Mock()
        mock_response.json.return_value = {"devices": [], "took": 0.001}

        with patch(
            "pihole_lib.network.make_pihole_request", return_value=mock_response
        ):
            result = network_client.get_devices()

        assert len(result.devices) == 0
        assert result.took == 0.001

    def test_get_gateway_success(self, network_client):
        """Test successful gateway retrieval."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "gateway": [
                {
                    "family": "inet",
                    "interface": "eth0",
                    "address": "192.168.1.1",
                    "local": ["192.168.1.100"],
                }
            ],
            "took": 0.001,
        }

        with patch(
            "pihole_lib.network.make_pihole_request", return_value=mock_response
        ):
            result = network_client.get_gateway()

        assert len(result.gateway) == 1
        gateway = result.gateway[0]
        assert gateway.family == "inet"
        assert gateway.interface == "eth0"
        assert gateway.address == "192.168.1.1"
        assert gateway.local == ["192.168.1.100"]
        assert result.took == 0.001

    def test_get_gateway_detailed(self, network_client):
        """Test detailed gateway retrieval."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "gateway": [
                {
                    "family": "inet",
                    "interface": "eth0",
                    "address": "192.168.1.1",
                    "local": ["192.168.1.100"],
                }
            ],
            "routes": [
                {
                    "table": 254,
                    "family": "inet",
                    "protocol": "boot",
                    "scope": "universe",
                    "type": "unicast",
                    "flags": [],
                    "gateway": "192.168.1.1",
                    "oif": "eth0",
                    "dst": "default",
                }
            ],
            "interfaces": [
                {
                    "name": "eth0",
                    "speed": 1000,
                    "type": "ether",
                    "flags": ["up", "broadcast", "running", "multicast"],
                    "state": "up",
                    "carrier": True,
                    "proto_down": False,
                    "address": "aa:bb:cc:dd:ee:ff",
                    "broadcast": "ff:ff:ff:ff:ff:ff",
                    "stats": {
                        "rx_bytes": {"value": 1000, "unit": "K"},
                        "tx_bytes": {"value": 500, "unit": "K"},
                        "bits": 64,
                    },
                }
            ],
            "took": 0.001,
        }

        with patch(
            "pihole_lib.network.make_pihole_request", return_value=mock_response
        ) as mock_request:
            result = network_client.get_gateway(detailed=True)

            # Check that the request was made with detailed parameter
            mock_request.assert_called_once_with(
                network_client._client,
                "GET",
                "/api/network/gateway",
                params={"detailed": True},
            )

        assert len(result.gateway) == 1
        assert len(result.routes) == 1
        assert len(result.interfaces) == 1
        assert result.took == 0.001

    def test_get_interfaces_success(self, network_client):
        """Test successful interface retrieval."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "interfaces": [
                {
                    "name": "eth0",
                    "speed": 1000,
                    "type": "ether",
                    "flags": ["up", "broadcast", "running", "multicast"],
                    "state": "up",
                    "carrier": True,
                    "proto_down": False,
                    "address": "aa:bb:cc:dd:ee:ff",
                    "broadcast": "ff:ff:ff:ff:ff:ff",
                    "stats": {
                        "rx_bytes": {"value": 1000, "unit": "K"},
                        "tx_bytes": {"value": 500, "unit": "K"},
                        "bits": 64,
                    },
                    "addresses": [
                        {
                            "family": "inet",
                            "scope": "universe",
                            "flags": ["permanent"],
                            "prefixlen": 24,
                            "address": "192.168.1.100",
                            "address_type": "private",
                            "local": "192.168.1.100",
                            "local_type": "private",
                            "broadcast": "192.168.1.255",
                            "broadcast_type": "private",
                            "label": "eth0",
                            "prefered": 4294967295,
                            "valid": 4294967295,
                            "cstamp": 1640995200.0,
                            "tstamp": 1640995200.0,
                        }
                    ],
                }
            ],
            "took": 0.001,
        }

        with patch(
            "pihole_lib.network.make_pihole_request", return_value=mock_response
        ):
            result = network_client.get_interfaces()

        assert len(result.interfaces) == 1
        interface = result.interfaces[0]
        assert interface.name == "eth0"
        assert interface.speed == 1000
        assert interface.type == "ether"
        assert interface.flags == ["up", "broadcast", "running", "multicast"]
        assert interface.state == "up"
        assert interface.carrier is True
        assert interface.proto_down is False
        assert interface.address == "aa:bb:cc:dd:ee:ff"
        assert interface.broadcast == "ff:ff:ff:ff:ff:ff"
        assert interface.stats.rx_bytes == {"value": 1000, "unit": "K"}
        assert interface.stats.tx_bytes == {"value": 500, "unit": "K"}
        assert interface.stats.bits == 64
        assert len(interface.addresses) == 1
        assert interface.addresses[0].family == "inet"
        assert interface.addresses[0].address == "192.168.1.100"
        assert result.took == 0.001

    def test_get_interfaces_detailed(self, network_client):
        """Test detailed interface retrieval."""
        mock_response = Mock()
        mock_response.json.return_value = {"interfaces": [], "took": 0.001}

        with patch(
            "pihole_lib.network.make_pihole_request", return_value=mock_response
        ) as mock_request:
            network_client.get_interfaces(detailed=True)

            # Check that the request was made with detailed parameter
            mock_request.assert_called_once_with(
                network_client._client,
                "GET",
                "/api/network/interfaces",
                params={"detailed": True},
            )

    def test_get_routes_success(self, network_client):
        """Test successful route retrieval."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "routes": [
                {
                    "table": 254,
                    "family": "inet",
                    "protocol": "boot",
                    "scope": "universe",
                    "type": "unicast",
                    "flags": [],
                    "gateway": "192.168.1.1",
                    "oif": "eth0",
                    "dst": "default",
                }
            ],
            "took": 0.001,
        }

        with patch(
            "pihole_lib.network.make_pihole_request", return_value=mock_response
        ):
            result = network_client.get_routes()

        assert len(result.routes) == 1
        route = result.routes[0]
        assert route.table == 254
        assert route.family == "inet"
        assert route.protocol == "boot"
        assert route.scope == "universe"
        assert route.type == "unicast"
        assert route.flags == []
        assert route.gateway == "192.168.1.1"
        assert route.oif == "eth0"
        assert route.dst == "default"
        assert result.took == 0.001

    def test_get_routes_detailed(self, network_client):
        """Test detailed route retrieval."""
        mock_response = Mock()
        mock_response.json.return_value = {"routes": [], "took": 0.001}

        with patch(
            "pihole_lib.network.make_pihole_request", return_value=mock_response
        ) as mock_request:
            network_client.get_routes(detailed=True)

            # Check that the request was made with detailed parameter
            mock_request.assert_called_once_with(
                network_client._client,
                "GET",
                "/api/network/routes",
                params={"detailed": True},
            )

    def test_delete_device_success(self, network_client):
        """Test successful device deletion."""
        mock_response = Mock()
        mock_response.json.return_value = {"took": 0.001}

        with patch(
            "pihole_lib.network.make_pihole_request", return_value=mock_response
        ) as mock_request:
            result = network_client.delete_device(123)

            mock_request.assert_called_once_with(
                network_client._client,
                "DELETE",
                "/api/network/devices/123",
            )

        assert result.took == 0.001

    def test_get_devices_api_error(self, network_client):
        """Test API error handling."""
        with patch(
            "pihole_lib.network.make_pihole_request",
            side_effect=PiHoleAPIError("API Error"),
        ):
            with pytest.raises(PiHoleAPIError):
                network_client.get_devices()

    def test_get_devices_auth_error(self, network_client):
        """Test authentication error handling."""
        with patch(
            "pihole_lib.network.make_pihole_request",
            side_effect=PiHoleAuthenticationError("Auth Error"),
        ):
            with pytest.raises(PiHoleAuthenticationError):
                network_client.get_devices()

    def test_delete_device_not_found(self, network_client):
        """Test device deletion when device not found."""
        with patch(
            "pihole_lib.network.make_pihole_request",
            side_effect=PiHoleAPIError("Not Found"),
        ):
            with pytest.raises(PiHoleAPIError):
                network_client.delete_device(999)
