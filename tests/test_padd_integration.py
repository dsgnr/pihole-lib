"""Integration tests for PiHolePADD class."""

import pytest

from pihole_lib import PiHoleClient, PiHolePADD
from pihole_lib.models import PADDInfo
from tests.constants import PIHOLE_BASE_URL, PIHOLE_TEST_PASSWORD


class TestPiHolePADDIntegration:
    """Integration test cases for PiHolePADD class."""

    @pytest.fixture
    def padd_client(self):
        """Create a PiHolePADD instance for integration testing."""
        client = PiHoleClient(
            PIHOLE_BASE_URL, password=PIHOLE_TEST_PASSWORD, verify_ssl=False
        )
        client.__enter__()  # Authenticate
        padd = PiHolePADD(client)
        yield padd
        client.__exit__(None, None, None)  # Clean up

    def test_get_dashboard_data_integration(self, padd_client):
        """Test dashboard data retrieval against real Pi-hole instance."""
        # Get dashboard data
        result = padd_client.get_dashboard_data()

        # Verify result structure
        assert isinstance(result, PADDInfo)

        # Verify basic fields
        assert hasattr(result, "active_clients")
        assert hasattr(result, "gravity_size")
        assert hasattr(result, "blocking")
        assert hasattr(result, "queries")
        assert hasattr(result, "cache")
        assert hasattr(result, "system")
        assert hasattr(result, "node_name")
        assert hasattr(result, "iface")
        assert hasattr(result, "version")
        assert hasattr(result, "config")
        assert hasattr(result, "sensors")

        # Validate data types
        assert isinstance(result.active_clients, int)
        assert isinstance(result.gravity_size, int)
        assert isinstance(result.blocking, str)
        assert result.blocking in ["enabled", "disabled"]

        # Validate nested structures
        assert hasattr(result.queries, "total")
        assert hasattr(result.queries, "blocked")
        assert hasattr(result.queries, "percent_blocked")
        assert isinstance(result.queries.total, int)
        assert isinstance(result.queries.blocked, int)
        assert isinstance(result.queries.percent_blocked, float)

        assert hasattr(result.system, "uptime")
        assert hasattr(result.system, "memory")
        assert hasattr(result.system, "cpu")
        assert isinstance(result.system.uptime, int)

        assert hasattr(result.system.memory, "ram")
        assert hasattr(result.system.memory, "swap")
        assert isinstance(result.system.memory.ram.total, int)

        assert hasattr(result.iface, "v4")
        assert hasattr(result.iface, "v6")
        assert hasattr(result.iface.v4, "name")
        assert isinstance(result.iface.v4.name, str)

        assert hasattr(result.version, "core")
        assert hasattr(result.version, "web")
        assert hasattr(result.version, "ftl")
        assert hasattr(result.version, "docker")
        assert isinstance(result.version.core.local.version, str)

        assert hasattr(result.config, "dhcp_active")
        assert hasattr(result.config, "dns_port")
        assert isinstance(result.config.dhcp_active, bool)
        assert isinstance(result.config.dns_port, int)

        assert hasattr(result.sensors, "hot_limit")
        assert hasattr(result.sensors, "unit")
        assert isinstance(result.sensors.hot_limit, int)
        assert isinstance(result.sensors.unit, str)
