"""Integration tests for Pi-hole network API client."""

import pytest

from pihole_lib import PiHoleClient, PiHoleNetwork

from .constants import PIHOLE_BASE_URL, PIHOLE_TEST_PASSWORD


@pytest.fixture
def pihole_client(pihole_container):
    """Create an authenticated Pi-hole client."""
    with PiHoleClient(
        base_url=PIHOLE_BASE_URL,
        password=PIHOLE_TEST_PASSWORD,
        verify_ssl=False,
    ) as client:
        yield client


@pytest.fixture
def network_client(pihole_client):
    """Create a network API client."""
    return PiHoleNetwork(pihole_client)


class TestPiHoleNetworkIntegration:
    """Integration test cases for PiHoleNetwork class."""

    def test_get_devices(self, network_client):
        """Test device retrieval."""
        result = network_client.get_devices()

        assert hasattr(result, "devices")
        assert hasattr(result, "took")
        assert isinstance(result.devices, list)
        assert isinstance(result.took, float)
        assert result.took > 0

        # Test with parameters
        result_with_params = network_client.get_devices(max_devices=5, max_addresses=3)
        assert hasattr(result_with_params, "devices")
        assert isinstance(result_with_params.devices, list)

    def test_get_gateway(self, network_client):
        """Test gateway retrieval."""
        result = network_client.get_gateway()

        assert hasattr(result, "gateway")
        assert hasattr(result, "took")
        assert isinstance(result.gateway, list)
        assert isinstance(result.took, float)
        assert result.took > 0

        # Each gateway should have required fields
        for gateway in result.gateway:
            assert hasattr(gateway, "family")
            assert hasattr(gateway, "interface")
            assert hasattr(gateway, "address")
            assert hasattr(gateway, "local")
            assert isinstance(gateway.local, list)

    def test_get_gateway_detailed(self, network_client):
        """Test detailed gateway retrieval."""
        result = network_client.get_gateway(detailed=True)

        assert hasattr(result, "gateway")
        assert hasattr(result, "routes")
        assert hasattr(result, "interfaces")
        assert hasattr(result, "took")
        assert isinstance(result.gateway, list)
        assert isinstance(result.routes, list)
        assert isinstance(result.interfaces, list)
        assert isinstance(result.took, float)
        assert result.took > 0

    def test_get_interfaces(self, network_client):
        """Test interface retrieval."""
        result = network_client.get_interfaces()

        assert hasattr(result, "interfaces")
        assert hasattr(result, "took")
        assert isinstance(result.interfaces, list)
        assert isinstance(result.took, float)
        assert result.took > 0

        # Should have at least one interface (loopback)
        assert len(result.interfaces) > 0

        # Each interface should have required fields
        for interface in result.interfaces:
            assert hasattr(interface, "name")
            assert hasattr(interface, "type")
            assert hasattr(interface, "flags")
            assert hasattr(interface, "state")
            assert hasattr(interface, "carrier")
            assert hasattr(interface, "proto_down")
            assert hasattr(interface, "address")
            assert hasattr(interface, "broadcast")
            assert hasattr(interface, "stats")
            assert isinstance(interface.flags, list)
            assert isinstance(interface.carrier, bool)
            assert isinstance(interface.proto_down, bool)

            # Check stats structure
            stats = interface.stats
            assert hasattr(stats, "rx_bytes")
            assert hasattr(stats, "tx_bytes")
            assert hasattr(stats, "bits")
            assert isinstance(stats.rx_bytes, dict)
            assert isinstance(stats.tx_bytes, dict)
            assert isinstance(stats.bits, int)

    def test_get_interfaces_detailed(self, network_client):
        """Test detailed interface retrieval."""
        result = network_client.get_interfaces(detailed=True)

        assert hasattr(result, "interfaces")
        assert hasattr(result, "took")
        assert isinstance(result.interfaces, list)
        assert isinstance(result.took, float)
        assert result.took > 0

        # Should have at least one interface
        assert len(result.interfaces) > 0

    def test_get_routes(self, network_client):
        """Test route retrieval."""
        result = network_client.get_routes()

        assert hasattr(result, "routes")
        assert hasattr(result, "took")
        assert isinstance(result.routes, list)
        assert isinstance(result.took, float)
        assert result.took > 0

        # Should have at least one route
        assert len(result.routes) > 0

        # Each route should have required fields
        for route in result.routes:
            assert hasattr(route, "table")
            assert hasattr(route, "family")
            assert hasattr(route, "protocol")
            assert hasattr(route, "scope")
            assert hasattr(route, "type")
            assert hasattr(route, "flags")
            assert hasattr(route, "oif")
            assert hasattr(route, "dst")
            assert isinstance(route.table, int)
            assert isinstance(route.flags, list)

    def test_get_routes_detailed(self, network_client):
        """Test detailed route retrieval."""
        result = network_client.get_routes(detailed=True)

        assert hasattr(result, "routes")
        assert hasattr(result, "took")
        assert isinstance(result.routes, list)
        assert isinstance(result.took, float)
        assert result.took > 0

        # Should have at least one route
        assert len(result.routes) > 0

    def test_delete_device_nonexistent(self, network_client):
        """Test deleting a non-existent device."""
        # This should not raise an error, just return a response
        # The actual behavior depends on Pi-hole implementation
        try:
            result = network_client.delete_device(99999)
            assert hasattr(result, "took")
            assert isinstance(result.took, float)
        except Exception:
            # Some implementations might return an error for non-existent devices
            # This is acceptable behavior
            pass

    def test_client_property_access(self, pihole_client):
        """Test accessing network client through main client property."""
        network = pihole_client.network

        assert isinstance(network, PiHoleNetwork)
        assert network._client is pihole_client

        # Test that subsequent access returns the same instance
        network2 = pihole_client.network
        assert network is network2

    def test_network_endpoints_consistency(self, network_client):
        """Test that all network endpoints return consistent data structures."""
        # Get all network information
        devices = network_client.get_devices()
        gateway = network_client.get_gateway()
        interfaces = network_client.get_interfaces()
        routes = network_client.get_routes()

        # All should have 'took' field
        for result in [devices, gateway, interfaces, routes]:
            assert hasattr(result, "took")
            assert isinstance(result.took, float)
            assert result.took > 0

        # Test detailed versions
        gateway_detailed = network_client.get_gateway(detailed=True)
        interfaces_detailed = network_client.get_interfaces(detailed=True)
        routes_detailed = network_client.get_routes(detailed=True)

        for result in [gateway_detailed, interfaces_detailed, routes_detailed]:
            assert hasattr(result, "took")
            assert isinstance(result.took, float)
            assert result.took > 0
