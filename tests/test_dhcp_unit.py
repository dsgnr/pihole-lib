"""Unit tests for PiHoleDHCP."""

from unittest.mock import patch

import pytest

from pihole_lib import PiHoleDHCP
from pihole_lib.exceptions import PiHoleAPIError
from pihole_lib.models.dhcp import DHCPLease, DHCPLeasesInfo
from tests.conftest import SAMPLE_DHCP_LEASE_DATA, make_mock_response


@pytest.fixture
def dhcp_client(mock_client):
    """Create a PiHoleDHCP instance for testing."""
    return PiHoleDHCP(mock_client)


class TestPiHoleDHCP:
    """Test cases for PiHoleDHCP class."""

    @patch("pihole_lib.dhcp.make_pihole_request")
    def test_get_leases_success(self, mock_request, dhcp_client, mock_client):
        """Test successful DHCP leases retrieval."""
        mock_request.return_value = make_mock_response(
            json_data={
                "leases": [
                    SAMPLE_DHCP_LEASE_DATA,
                    {
                        **SAMPLE_DHCP_LEASE_DATA,
                        "expires": 0,
                        "name": "phone",
                        "ip": "192.168.1.101",
                    },
                ],
                "took": 0.001,
            }
        )

        result = dhcp_client.get_leases()

        mock_request.assert_called_once_with(
            mock_client, "GET", f"{dhcp_client.BASE_URL}/leases"
        )
        assert isinstance(result, DHCPLeasesInfo)
        assert len(result.leases) == 2
        assert isinstance(result.leases[0], DHCPLease)
        assert result.leases[0].name == "laptop"
        assert result.leases[1].expires == 0  # Infinite lease

    @patch("pihole_lib.dhcp.make_pihole_request")
    def test_get_leases_empty(self, mock_request, dhcp_client):
        """Test DHCP leases retrieval with no active leases."""
        mock_request.return_value = make_mock_response(
            json_data={"leases": [], "took": 0.0001}
        )

        result = dhcp_client.get_leases()

        assert isinstance(result, DHCPLeasesInfo)
        assert len(result.leases) == 0

    @patch("pihole_lib.dhcp.make_pihole_request")
    def test_get_leases_api_error(self, mock_request, dhcp_client):
        """Test DHCP leases retrieval with API error."""
        mock_request.side_effect = PiHoleAPIError("API request failed")

        with pytest.raises(PiHoleAPIError, match="API request failed"):
            dhcp_client.get_leases()

    @pytest.mark.parametrize(
        "status_code,expected_result",
        [
            (204, True),
            (400, False),
        ],
    )
    @patch("pihole_lib.dhcp.make_pihole_request")
    def test_delete_lease(
        self, mock_request, dhcp_client, mock_client, status_code, expected_result
    ):
        """Test DHCP lease deletion with various responses."""
        mock_request.return_value = make_mock_response(status_code=status_code)

        result = dhcp_client.delete_lease("192.168.1.100")

        mock_request.assert_called_once_with(
            mock_client, "DELETE", f"{dhcp_client.BASE_URL}/leases/192.168.1.100"
        )
        assert result is expected_result

    @patch("pihole_lib.dhcp.make_pihole_request")
    def test_delete_lease_api_error(self, mock_request, dhcp_client):
        """Test DHCP lease deletion with API error."""
        mock_request.side_effect = PiHoleAPIError("Invalid IP address")

        with pytest.raises(PiHoleAPIError, match="Invalid IP address"):
            dhcp_client.delete_lease("invalid-ip")

    def test_inheritance(self, dhcp_client):
        """Test that PiHoleDHCP inherits from BasePiHoleAPIClient."""
        from pihole_lib.base import BasePiHoleAPIClient

        assert isinstance(dhcp_client, BasePiHoleAPIClient)
