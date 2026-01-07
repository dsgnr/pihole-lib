"""Unit tests for PiHoleDHCP class."""

from unittest.mock import Mock, patch

import pytest

from pihole_lib import PiHoleClient, PiHoleDHCP
from pihole_lib.constants import API_DHCP_LEASES
from pihole_lib.exceptions import PiHoleAPIError
from pihole_lib.models import DHCPLease, DHCPLeasesInfo


class TestPiHoleDHCP:
    """Test cases for PiHoleDHCP class."""

    @pytest.fixture
    def mock_client(self):
        """Create a mock PiHoleClient for testing."""
        client = Mock(spec=PiHoleClient)
        client.base_url = "http://localhost"
        client._session = Mock()
        return client

    @pytest.fixture
    def dhcp_client(self, mock_client):
        """Create a PiHoleDHCP instance for testing."""
        return PiHoleDHCP(mock_client)

    @patch("pihole_lib.dhcp.make_pihole_request")
    def test_get_leases_success(self, mock_request, dhcp_client, mock_client):
        """Test successful DHCP leases retrieval."""
        # Mock response data
        mock_response = {
            "leases": [
                {
                    "expires": 1640995200,
                    "name": "laptop",
                    "hwaddr": "aa:bb:cc:dd:ee:ff",
                    "ip": "192.168.1.100",
                    "clientid": "01:aa:bb:cc:dd:ee:ff",
                },
                {
                    "expires": 0,
                    "name": "phone",
                    "hwaddr": "11:22:33:44:55:66",
                    "ip": "192.168.1.101",
                    "clientid": "01:11:22:33:44:55:66",
                },
            ],
            "took": 0.001,
        }
        mock_request.return_value.json.return_value = mock_response

        # Call method
        result = dhcp_client.get_leases()

        # Verify request was made correctly
        mock_request.assert_called_once_with(
            mock_client,
            "GET",
            "/api/dhcp/leases",
        )

        # Verify result
        assert isinstance(result, DHCPLeasesInfo)
        assert len(result.leases) == 2

        # Check first lease
        lease1 = result.leases[0]
        assert isinstance(lease1, DHCPLease)
        assert lease1.expires == 1640995200
        assert lease1.name == "laptop"
        assert lease1.hwaddr == "aa:bb:cc:dd:ee:ff"
        assert lease1.ip == "192.168.1.100"
        assert lease1.clientid == "01:aa:bb:cc:dd:ee:ff"

        # Check second lease (infinite lease)
        lease2 = result.leases[1]
        assert isinstance(lease2, DHCPLease)
        assert lease2.expires == 0  # Infinite lease
        assert lease2.name == "phone"
        assert lease2.hwaddr == "11:22:33:44:55:66"
        assert lease2.ip == "192.168.1.101"
        assert lease2.clientid == "01:11:22:33:44:55:66"

    @patch("pihole_lib.dhcp.make_pihole_request")
    def test_get_leases_empty(self, mock_request, dhcp_client):
        """Test DHCP leases retrieval with no active leases."""
        # Mock empty response
        mock_response = {"leases": [], "took": 0.0001}
        mock_request.return_value.json.return_value = mock_response

        # Call method
        result = dhcp_client.get_leases()

        # Verify result
        assert isinstance(result, DHCPLeasesInfo)
        assert len(result.leases) == 0

    @patch("pihole_lib.dhcp.make_pihole_request")
    def test_get_leases_api_error(self, mock_request, dhcp_client):
        """Test DHCP leases retrieval with API error."""
        # Mock API error
        mock_request.side_effect = PiHoleAPIError("API request failed")

        # Call method and expect exception
        with pytest.raises(PiHoleAPIError, match="API request failed"):
            dhcp_client.get_leases()

    def test_inheritance(self, dhcp_client):
        """Test that PiHoleDHCP inherits from BasePiHoleAPIClient."""
        from pihole_lib.base import BasePiHoleAPIClient

        assert isinstance(dhcp_client, BasePiHoleAPIClient)

    def test_constants_usage(self, dhcp_client):
        """Test that the class uses the correct API endpoint constant."""
        assert API_DHCP_LEASES == "/api/dhcp/leases"

    @patch("pihole_lib.dhcp.make_pihole_request")
    def test_delete_lease_success(self, mock_request, dhcp_client, mock_client):
        """Test successful DHCP lease deletion."""
        # Mock successful response (204 No Content)
        mock_response = Mock()
        mock_response.status_code = 204
        mock_request.return_value = mock_response

        # Call method
        result = dhcp_client.delete_lease("192.168.1.100")

        # Verify request was made correctly
        mock_request.assert_called_once_with(
            mock_client,
            "DELETE",
            "/api/dhcp/leases/192.168.1.100",
        )

        # Verify result
        assert result is True

    @patch("pihole_lib.dhcp.make_pihole_request")
    def test_delete_lease_not_found(self, mock_request, dhcp_client):
        """Test DHCP lease deletion when lease not found."""
        # Mock 400 response for invalid/not found lease
        mock_response = Mock()
        mock_response.status_code = 400
        mock_request.return_value = mock_response

        # Call method
        result = dhcp_client.delete_lease("192.168.1.999")

        # Verify result
        assert result is False

    @patch("pihole_lib.dhcp.make_pihole_request")
    def test_delete_lease_api_error(self, mock_request, dhcp_client):
        """Test DHCP lease deletion with API error."""
        # Mock API error
        mock_request.side_effect = PiHoleAPIError("Invalid IP address")

        # Call method and expect exception
        with pytest.raises(PiHoleAPIError, match="Invalid IP address"):
            dhcp_client.delete_lease("invalid-ip")
