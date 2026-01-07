"""Integration tests for PiHoleDHCP class."""

import pytest

from pihole_lib import PiHoleClient, PiHoleDHCP
from pihole_lib.models import DHCPLeasesInfo
from tests.constants import PIHOLE_BASE_URL, PIHOLE_TEST_PASSWORD


class TestPiHoleDHCPIntegration:
    """Integration test cases for PiHoleDHCP class."""

    @pytest.fixture
    def dhcp_client(self):
        """Create a PiHoleDHCP instance for integration testing."""
        client = PiHoleClient(
            PIHOLE_BASE_URL, password=PIHOLE_TEST_PASSWORD, verify_ssl=False
        )
        client.__enter__()  # Authenticate
        dhcp = PiHoleDHCP(client)
        yield dhcp
        client.__exit__(None, None, None)  # Clean up

    def test_get_leases_integration(self, dhcp_client):
        """Test DHCP leases retrieval against real Pi-hole instance."""
        # Get DHCP leases
        result = dhcp_client.get_leases()

        # Verify result structure
        assert isinstance(result, DHCPLeasesInfo)
        assert hasattr(result, "leases")
        assert isinstance(result.leases, list)

        # In test environment, there may be no active DHCP leases
        # but the structure should still be valid
        for lease in result.leases:
            assert hasattr(lease, "expires")
            assert hasattr(lease, "name")
            assert hasattr(lease, "hwaddr")
            assert hasattr(lease, "ip")
            assert hasattr(lease, "clientid")

            # Validate data types
            assert isinstance(lease.expires, int)
            assert isinstance(lease.name, str)
            assert isinstance(lease.hwaddr, str)
            assert isinstance(lease.ip, str)
            assert isinstance(lease.clientid, str)

    def test_delete_lease_integration(self, dhcp_client):
        """Test DHCP lease deletion against real Pi-hole instance."""
        # Try to delete a non-existent lease (should handle gracefully)
        # In a real environment, this would return False or raise an appropriate exception
        try:
            result = dhcp_client.delete_lease("192.168.1.999")
            # If it returns False, that's expected for non-existent lease
            assert isinstance(result, bool)
        except Exception as e:
            # If it raises an exception, it should be a PiHoleAPIError
            from pihole_lib.exceptions import PiHoleAPIError

            assert isinstance(e, PiHoleAPIError)
