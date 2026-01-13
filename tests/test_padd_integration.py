"""Integration tests for PiHolePADD."""

from pihole_lib import PiHolePADD
from pihole_lib.models.padd import PADDInfo
from tests.conftest import integration


@integration
class TestPiHolePADDIntegration:
    """Integration test cases for PiHolePADD class."""

    def test_get_dashboard_data_integration(self, pihole_client):
        padd = PiHolePADD(pihole_client)

        result = padd.get_dashboard_data()

        # Verify the result is a valid PADDInfo instance
        assert isinstance(result, PADDInfo)
        # Verify key fields are present
        assert hasattr(result, "active_clients")
        assert hasattr(result, "blocking")
        assert hasattr(result, "queries")
        assert hasattr(result, "system")

    def test_constants_usage(self, pihole_client):
        """Test that the class uses the correct API endpoint constants."""
        padd = PiHolePADD(pihole_client)
        assert padd.BASE_URL == "/api/padd"
