"""Integration tests for PiHoleDHCP."""

from pihole_lib import PiHoleDHCP
from pihole_lib.models.dhcp import DHCPLeasesInfo
from tests.conftest import integration


@integration
class TestPiHoleDHCPIntegration:
    """Integration test cases for PiHoleDHCP class."""

    def test_get_leases_integration(self, pihole_client):
        """Test DHCP leases retrieval against real Pi-hole instance."""
        dhcp = PiHoleDHCP(pihole_client)
        result = dhcp.get_leases()

        assert isinstance(result, DHCPLeasesInfo)
        assert isinstance(result.leases, list)

        # Validate lease structure if any exist
        for lease in result.leases:
            assert isinstance(lease.expires, int)
            assert isinstance(lease.name, str)
            assert isinstance(lease.hwaddr, str)
            assert isinstance(lease.ip, str)
            assert isinstance(lease.clientid, str)

    def test_delete_lease_integration(self, pihole_client):
        """Test DHCP lease deletion against real Pi-hole instance."""
        dhcp = PiHoleDHCP(pihole_client)

        # Try to delete a non-existent lease (should handle gracefully)
        try:
            result = dhcp.delete_lease("192.168.1.999")
            assert isinstance(result, bool)
        except Exception as e:
            from pihole_lib.exceptions import PiHoleAPIError

            assert isinstance(e, PiHoleAPIError)

    def test_constants_usage(self, pihole_client):
        """Test that the class uses the correct API endpoint constants."""
        dhcp = PiHoleDHCP(pihole_client)
        assert dhcp.BASE_URL == "/api/dhcp"
