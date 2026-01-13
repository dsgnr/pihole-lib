"""Unit tests for PiHoleClients."""

from unittest.mock import patch

import pytest

from pihole_lib import PiHoleClients
from pihole_lib.exceptions import PiHoleServerError
from pihole_lib.models.client_mgmt import ClientBatchDeleteItem
from tests.conftest import SAMPLE_CLIENT_DATA, make_client, make_mock_response


@pytest.fixture
def clients_client(mock_client):
    """Create a PiHoleClients instance for testing."""
    return PiHoleClients(mock_client)


class TestPiHoleClientsInit:
    """Test clients client initialization."""

    def test_init_with_client(self):
        """Clients client should initialize with a PiHoleClient."""
        client = make_client()
        clients_client = PiHoleClients(client)
        assert clients_client._client is client


class TestPiHoleClientsGetClients:
    """Test clients retrieval functionality."""

    @patch("pihole_lib.clients.make_pihole_request")
    def test_get_clients_success(self, mock_request, clients_client, mock_client):
        """Should successfully get all clients."""
        mock_request.return_value = make_mock_response(
            json_data={
                "clients": [SAMPLE_CLIENT_DATA],
                "took": 0.001,
            }
        )

        result = clients_client.get_clients()

        mock_request.assert_called_once_with(mock_client, "GET", "/api/clients")
        assert len(result) == 1
        assert result[0].client == "192.168.1.100"

    @pytest.mark.parametrize(
        "client_id,expected_endpoint",
        [
            ("192.168.1.100", "/api/clients/192.168.1.100"),
            ("12:34:56:78:9A:BC", "/api/clients/12%3A34%3A56%3A78%3A9A%3ABC"),
        ],
    )
    @patch("pihole_lib.clients.make_pihole_request")
    def test_get_clients_specific(
        self, mock_request, clients_client, mock_client, client_id, expected_endpoint
    ):
        """Should get specific client with proper URL encoding."""
        mock_request.return_value = make_mock_response(
            json_data={
                "clients": [{**SAMPLE_CLIENT_DATA, "client": client_id}],
                "took": 0.001,
            }
        )

        result = clients_client.get_clients(client=client_id)

        mock_request.assert_called_once_with(mock_client, "GET", expected_endpoint)
        assert len(result) == 1

    @patch("pihole_lib.clients.make_pihole_request")
    def test_get_clients_empty(self, mock_request, clients_client):
        """Should handle empty clients response."""
        mock_request.return_value = make_mock_response(
            json_data={"clients": [], "took": 0.001}
        )

        result = clients_client.get_clients()
        assert len(result) == 0


class TestPiHoleClientsAddClient:
    """Test client addition functionality."""

    @patch("pihole_lib.clients.check_api_errors")
    @patch("pihole_lib.clients.make_pihole_request")
    def test_add_client_success(
        self, mock_request, mock_check_errors, clients_client, mock_client
    ):
        """Should successfully add a new client."""
        mock_request.return_value = make_mock_response(
            json_data={
                "clients": [SAMPLE_CLIENT_DATA],
                "processed": {"errors": [], "success": [{"item": "192.168.1.100"}]},
                "took": 0.001,
            }
        )

        result = clients_client.add_client(
            client="192.168.1.100", comment="Test client", groups=[0]
        )

        mock_request.assert_called_once_with(
            mock_client,
            "POST",
            "/api/clients",
            json={"client": "192.168.1.100", "comment": "Test client", "groups": [0]},
        )
        assert len(result) == 1

    @patch("pihole_lib.clients.check_api_errors")
    @patch("pihole_lib.clients.make_pihole_request")
    def test_add_client_with_defaults(
        self, mock_request, mock_check_errors, clients_client, mock_client
    ):
        """Should add client with default groups when not specified."""
        mock_request.return_value = make_mock_response(
            json_data={
                "clients": [{**SAMPLE_CLIENT_DATA, "comment": None}],
                "processed": {"errors": [], "success": [{"item": "192.168.1.100"}]},
                "took": 0.001,
            }
        )

        clients_client.add_client(client="192.168.1.100")

        mock_request.assert_called_once_with(
            mock_client,
            "POST",
            "/api/clients",
            json={"client": "192.168.1.100", "groups": [0]},
        )

    @patch("pihole_lib.clients.check_api_errors")
    @patch("pihole_lib.clients.make_pihole_request")
    def test_add_client_api_error(
        self, mock_request, mock_check_errors, clients_client
    ):
        """Should handle API errors when adding client."""
        mock_request.return_value = make_mock_response(
            json_data={
                "clients": [],
                "processed": {
                    "errors": [
                        {"item": "192.168.1.100", "error": "Client already exists"}
                    ],
                    "success": [],
                },
                "took": 0.001,
            }
        )
        mock_check_errors.side_effect = PiHoleServerError("Client already exists")

        with pytest.raises(PiHoleServerError, match="Client already exists"):
            clients_client.add_client(client="192.168.1.100")


class TestPiHoleClientsUpdateClient:
    """Test client update functionality."""

    @patch("pihole_lib.clients.check_api_errors")
    @patch("pihole_lib.clients.make_pihole_request")
    def test_update_client_success(
        self, mock_request, mock_check_errors, clients_client, mock_client
    ):
        """Should successfully update a client."""
        mock_request.return_value = make_mock_response(
            json_data={
                "clients": [
                    {
                        **SAMPLE_CLIENT_DATA,
                        "comment": "Updated comment",
                        "groups": [0, 1],
                    }
                ],
                "processed": {"errors": [], "success": [{"item": "192.168.1.100"}]},
                "took": 0.001,
            }
        )

        result = clients_client.update_client(
            client="192.168.1.100", comment="Updated comment", groups=[0, 1]
        )

        mock_request.assert_called_once_with(
            mock_client,
            "PUT",
            "/api/clients/192.168.1.100",
            json={"comment": "Updated comment", "groups": [0, 1]},
        )
        assert result.clients[0].comment == "Updated comment"

    @patch("pihole_lib.clients.check_api_errors")
    @patch("pihole_lib.clients.make_pihole_request")
    def test_update_client_mac_address_encoding(
        self, mock_request, mock_check_errors, clients_client, mock_client
    ):
        """Should properly URL encode MAC address in update request."""
        mock_request.return_value = make_mock_response(
            json_data={
                "clients": [{**SAMPLE_CLIENT_DATA, "client": "12:34:56:78:9A:BC"}],
                "processed": {"errors": [], "success": [{"item": "12:34:56:78:9A:BC"}]},
                "took": 0.001,
            }
        )

        clients_client.update_client(client="12:34:56:78:9A:BC", comment="Updated")

        mock_request.assert_called_once_with(
            mock_client,
            "PUT",
            "/api/clients/12%3A34%3A56%3A78%3A9A%3ABC",
            json={"comment": "Updated", "groups": [0]},
        )


class TestPiHoleClientsDeleteClient:
    """Test client deletion functionality."""

    @pytest.mark.parametrize(
        "status_code,expected_result",
        [
            (204, True),
            (404, False),
        ],
    )
    @patch("pihole_lib.clients.make_pihole_request")
    def test_delete_client(
        self, mock_request, clients_client, mock_client, status_code, expected_result
    ):
        """Should handle delete responses correctly."""
        mock_request.return_value = make_mock_response(status_code=status_code)

        result = clients_client.delete_client("192.168.1.100")

        mock_request.assert_called_once_with(
            mock_client, "DELETE", "/api/clients/192.168.1.100"
        )
        assert result is expected_result

    @patch("pihole_lib.clients.make_pihole_request")
    def test_delete_client_mac_address_encoding(
        self, mock_request, clients_client, mock_client
    ):
        """Should properly URL encode MAC address in delete request."""
        mock_request.return_value = make_mock_response(status_code=204)

        clients_client.delete_client("12:34:56:78:9A:BC")

        mock_request.assert_called_once_with(
            mock_client, "DELETE", "/api/clients/12%3A34%3A56%3A78%3A9A%3ABC"
        )


class TestPiHoleClientsBatchDelete:
    """Test batch client deletion functionality."""

    @pytest.mark.parametrize(
        "status_code,expected_result",
        [
            (204, True),
            (400, False),
        ],
    )
    @patch("pihole_lib.clients.make_pihole_request")
    def test_batch_delete_clients(
        self, mock_request, clients_client, mock_client, status_code, expected_result
    ):
        """Should handle batch delete responses correctly."""
        mock_request.return_value = make_mock_response(status_code=status_code)

        items = [
            ClientBatchDeleteItem(item="192.168.1.100"),
            ClientBatchDeleteItem(item="12:34:56:78:9A:BC"),
        ]

        result = clients_client.batch_delete_clients(items)

        mock_request.assert_called_once_with(
            mock_client,
            "POST",
            "/api/clients:batchDelete",
            json=[{"item": "192.168.1.100"}, {"item": "12:34:56:78:9A:BC"}],
        )
        assert result is expected_result


class TestPiHoleClientsGetSuggestions:
    """Test client suggestions functionality."""

    @patch("pihole_lib.clients.make_pihole_request")
    def test_get_client_suggestions(self, mock_request, clients_client, mock_client):
        """Should successfully get client suggestions."""
        mock_request.return_value = make_mock_response(
            json_data={
                "clients": [{**SAMPLE_CLIENT_DATA, "name": "unknown-device"}],
                "took": 0.001,
            }
        )

        result = clients_client.get_client_suggestions()

        mock_request.assert_called_once_with(
            mock_client, "GET", "/api/clients/_suggestions"
        )
        assert len(result) == 1
        assert result[0].name == "unknown-device"
