"""Unit tests for PiHoleClients (no network calls)."""

from unittest.mock import Mock, patch

import pytest

from pihole_lib import PiHoleClient, PiHoleClients
from pihole_lib.exceptions import PiHoleServerError
from pihole_lib.models import ClientBatchDeleteItem

from .constants import (
    TEST_LOCALHOST_URL,
    TEST_SECRET_PASSWORD,
)


class TestPiHoleClientsInit:
    """Test clients client initialization."""

    def test_init_with_client(self):
        """Clients client should initialize with a PiHoleClient."""
        client = PiHoleClient(TEST_LOCALHOST_URL, password=TEST_SECRET_PASSWORD)
        clients_client = PiHoleClients(client)

        assert clients_client._client is client


class TestPiHoleClientsGetClients:
    """Test clients retrieval functionality (no network calls)."""

    @patch("pihole_lib.clients.make_pihole_request")
    def test_get_clients_success(self, mock_request):
        """Should successfully get all clients."""
        client = PiHoleClient(TEST_LOCALHOST_URL, password=TEST_SECRET_PASSWORD)
        clients_client = PiHoleClients(client)

        mock_response = Mock()
        mock_response.json.return_value = {
            "clients": [
                {
                    "client": "192.168.1.100",
                    "name": "laptop",
                    "comment": "Test client",
                    "groups": [0],
                    "id": 1,
                    "date_added": 1640995200,
                    "date_modified": 1640995200,
                }
            ],
            "took": 0.001,
        }
        mock_request.return_value = mock_response

        result = clients_client.get_clients()

        assert len(result) == 1
        assert result[0].client == "192.168.1.100"
        assert result[0].name == "laptop"
        assert result[0].comment == "Test client"
        assert result[0].groups == [0]
        assert result[0].id == 1

        mock_request.assert_called_once_with(client, "GET", "/api/clients")

    @patch("pihole_lib.clients.make_pihole_request")
    def test_get_clients_with_specific_client(self, mock_request):
        """Should successfully get a specific client."""
        client = PiHoleClient(TEST_LOCALHOST_URL, password=TEST_SECRET_PASSWORD)
        clients_client = PiHoleClients(client)

        mock_response = Mock()
        mock_response.json.return_value = {
            "clients": [
                {
                    "client": "192.168.1.100",
                    "name": "laptop",
                    "comment": "Test client",
                    "groups": [0],
                    "id": 1,
                    "date_added": 1640995200,
                    "date_modified": 1640995200,
                }
            ],
            "took": 0.001,
        }
        mock_request.return_value = mock_response

        result = clients_client.get_clients(client="192.168.1.100")

        assert len(result) == 1
        assert result[0].client == "192.168.1.100"

        mock_request.assert_called_once_with(
            client, "GET", "/api/clients/192.168.1.100"
        )

    @patch("pihole_lib.clients.make_pihole_request")
    def test_get_clients_with_mac_address(self, mock_request):
        """Should successfully get a client by MAC address with URL encoding."""
        client = PiHoleClient(TEST_LOCALHOST_URL, password=TEST_SECRET_PASSWORD)
        clients_client = PiHoleClients(client)

        mock_response = Mock()
        mock_response.json.return_value = {
            "clients": [
                {
                    "client": "12:34:56:78:9A:BC",
                    "name": "",
                    "comment": "MAC client",
                    "groups": [0],
                    "id": 2,
                    "date_added": 1640995200,
                    "date_modified": 1640995200,
                }
            ],
            "took": 0.001,
        }
        mock_request.return_value = mock_response

        result = clients_client.get_clients(client="12:34:56:78:9A:BC")

        assert len(result) == 1
        assert result[0].client == "12:34:56:78:9A:BC"

        # MAC address should be URL encoded
        mock_request.assert_called_once_with(
            client, "GET", "/api/clients/12%3A34%3A56%3A78%3A9A%3ABC"
        )

    @patch("pihole_lib.clients.make_pihole_request")
    def test_get_clients_empty_response(self, mock_request):
        """Should handle empty clients response."""
        client = PiHoleClient(TEST_LOCALHOST_URL, password=TEST_SECRET_PASSWORD)
        clients_client = PiHoleClients(client)

        mock_response = Mock()
        mock_response.json.return_value = {
            "clients": [],
            "took": 0.001,
        }
        mock_request.return_value = mock_response

        result = clients_client.get_clients()

        assert len(result) == 0
        mock_request.assert_called_once_with(client, "GET", "/api/clients")


class TestPiHoleClientsAddClient:
    """Test client addition functionality (no network calls)."""

    @patch("pihole_lib.clients.check_api_errors")
    @patch("pihole_lib.clients.make_pihole_request")
    def test_add_client_success(self, mock_request, mock_check_errors):
        """Should successfully add a new client."""
        client = PiHoleClient(TEST_LOCALHOST_URL, password=TEST_SECRET_PASSWORD)
        clients_client = PiHoleClients(client)

        mock_response = Mock()
        mock_response.json.return_value = {
            "clients": [
                {
                    "client": "192.168.1.100",
                    "name": "",
                    "comment": "Test client",
                    "groups": [0],
                    "id": 1,
                    "date_added": 1640995200,
                    "date_modified": 1640995200,
                }
            ],
            "processed": {"errors": [], "success": [{"item": "192.168.1.100"}]},
            "took": 0.001,
        }
        mock_request.return_value = mock_response

        result = clients_client.add_client(
            client="192.168.1.100", comment="Test client", groups=[0]
        )

        assert len(result) == 1
        assert result[0].client == "192.168.1.100"
        assert result[0].comment == "Test client"

        mock_request.assert_called_once_with(
            client,
            "POST",
            "/api/clients",
            json={"client": "192.168.1.100", "comment": "Test client", "groups": [0]},
        )
        mock_check_errors.assert_called_once()

    @patch("pihole_lib.clients.check_api_errors")
    @patch("pihole_lib.clients.make_pihole_request")
    def test_add_client_with_defaults(self, mock_request, mock_check_errors):
        """Should add client with default groups when not specified."""
        client = PiHoleClient(TEST_LOCALHOST_URL, password=TEST_SECRET_PASSWORD)
        clients_client = PiHoleClients(client)

        mock_response = Mock()
        mock_response.json.return_value = {
            "clients": [
                {
                    "client": "192.168.1.100",
                    "name": "",
                    "comment": None,
                    "groups": [0],
                    "id": 1,
                    "date_added": 1640995200,
                    "date_modified": 1640995200,
                }
            ],
            "processed": {"errors": [], "success": [{"item": "192.168.1.100"}]},
            "took": 0.001,
        }
        mock_request.return_value = mock_response

        result = clients_client.add_client(client="192.168.1.100")

        assert len(result) == 1
        assert result[0].groups == [0]  # Default group

        mock_request.assert_called_once_with(
            client,
            "POST",
            "/api/clients",
            json={"client": "192.168.1.100", "groups": [0]},
        )

    @patch("pihole_lib.clients.check_api_errors")
    @patch("pihole_lib.clients.make_pihole_request")
    def test_add_client_mac_address(self, mock_request, mock_check_errors):
        """Should successfully add a client by MAC address."""
        client = PiHoleClient(TEST_LOCALHOST_URL, password=TEST_SECRET_PASSWORD)
        clients_client = PiHoleClients(client)

        mock_response = Mock()
        mock_response.json.return_value = {
            "clients": [
                {
                    "client": "12:34:56:78:9A:BC",
                    "name": "",
                    "comment": "MAC client",
                    "groups": [0],
                    "id": 2,
                    "date_added": 1640995200,
                    "date_modified": 1640995200,
                }
            ],
            "processed": {"errors": [], "success": [{"item": "12:34:56:78:9A:BC"}]},
            "took": 0.001,
        }
        mock_request.return_value = mock_response

        result = clients_client.add_client(
            client="12:34:56:78:9A:BC", comment="MAC client"
        )

        assert len(result) == 1
        assert result[0].client == "12:34:56:78:9A:BC"

    @patch("pihole_lib.clients.check_api_errors")
    @patch("pihole_lib.clients.make_pihole_request")
    def test_add_client_hostname(self, mock_request, mock_check_errors):
        """Should successfully add a client by hostname."""
        client = PiHoleClient(TEST_LOCALHOST_URL, password=TEST_SECRET_PASSWORD)
        clients_client = PiHoleClients(client)

        mock_response = Mock()
        mock_response.json.return_value = {
            "clients": [
                {
                    "client": "laptop.local",
                    "name": "",
                    "comment": "Hostname client",
                    "groups": [0],
                    "id": 3,
                    "date_added": 1640995200,
                    "date_modified": 1640995200,
                }
            ],
            "processed": {"errors": [], "success": [{"item": "laptop.local"}]},
            "took": 0.001,
        }
        mock_request.return_value = mock_response

        result = clients_client.add_client(
            client="laptop.local", comment="Hostname client"
        )

        assert len(result) == 1
        assert result[0].client == "laptop.local"

    @patch("pihole_lib.clients.check_api_errors")
    @patch("pihole_lib.clients.make_pihole_request")
    def test_add_client_api_error(self, mock_request, mock_check_errors):
        """Should handle API errors when adding client."""
        client = PiHoleClient(TEST_LOCALHOST_URL, password=TEST_SECRET_PASSWORD)
        clients_client = PiHoleClients(client)

        mock_response = Mock()
        mock_response.json.return_value = {
            "clients": [],
            "processed": {
                "errors": [{"item": "192.168.1.100", "error": "Client already exists"}],
                "success": [],
            },
            "took": 0.001,
        }
        mock_request.return_value = mock_response
        mock_check_errors.side_effect = PiHoleServerError("Client already exists")

        with pytest.raises(PiHoleServerError, match="Client already exists"):
            clients_client.add_client(client="192.168.1.100")


class TestPiHoleClientsUpdateClient:
    """Test client update functionality (no network calls)."""

    @patch("pihole_lib.clients.check_api_errors")
    @patch("pihole_lib.clients.make_pihole_request")
    def test_update_client_success(self, mock_request, mock_check_errors):
        """Should successfully update a client."""
        client = PiHoleClient(TEST_LOCALHOST_URL, password=TEST_SECRET_PASSWORD)
        clients_client = PiHoleClients(client)

        mock_response = Mock()
        mock_response.json.return_value = {
            "clients": [
                {
                    "client": "192.168.1.100",
                    "name": "laptop",
                    "comment": "Updated comment",
                    "groups": [0, 1],
                    "id": 1,
                    "date_added": 1640995200,
                    "date_modified": 1640995300,
                }
            ],
            "processed": {"errors": [], "success": [{"item": "192.168.1.100"}]},
            "took": 0.001,
        }
        mock_request.return_value = mock_response

        result = clients_client.update_client(
            client="192.168.1.100", comment="Updated comment", groups=[0, 1]
        )

        assert len(result.clients) == 1
        assert result.clients[0].comment == "Updated comment"
        assert result.clients[0].groups == [0, 1]
        assert result.processed is not None
        assert len(result.processed.success) == 1

        mock_request.assert_called_once_with(
            client,
            "PUT",
            "/api/clients/192.168.1.100",
            json={"comment": "Updated comment", "groups": [0, 1]},
        )

    @patch("pihole_lib.clients.check_api_errors")
    @patch("pihole_lib.clients.make_pihole_request")
    def test_update_client_with_defaults(self, mock_request, mock_check_errors):
        """Should update client with default groups when not specified."""
        client = PiHoleClient(TEST_LOCALHOST_URL, password=TEST_SECRET_PASSWORD)
        clients_client = PiHoleClients(client)

        mock_response = Mock()
        mock_response.json.return_value = {
            "clients": [
                {
                    "client": "192.168.1.100",
                    "name": "laptop",
                    "comment": "Updated comment",
                    "groups": [0],
                    "id": 1,
                    "date_added": 1640995200,
                    "date_modified": 1640995300,
                }
            ],
            "processed": {"errors": [], "success": [{"item": "192.168.1.100"}]},
            "took": 0.001,
        }
        mock_request.return_value = mock_response

        clients_client.update_client(client="192.168.1.100", comment="Updated comment")

        mock_request.assert_called_once_with(
            client,
            "PUT",
            "/api/clients/192.168.1.100",
            json={"comment": "Updated comment", "groups": [0]},
        )

    @patch("pihole_lib.clients.check_api_errors")
    @patch("pihole_lib.clients.make_pihole_request")
    def test_update_client_mac_address_encoding(self, mock_request, mock_check_errors):
        """Should properly URL encode MAC address in update request."""
        client = PiHoleClient(TEST_LOCALHOST_URL, password=TEST_SECRET_PASSWORD)
        clients_client = PiHoleClients(client)

        mock_response = Mock()
        mock_response.json.return_value = {
            "clients": [
                {
                    "client": "12:34:56:78:9A:BC",
                    "name": "",
                    "comment": "Updated MAC client",
                    "groups": [0],
                    "id": 2,
                    "date_added": 1640995200,
                    "date_modified": 1640995300,
                }
            ],
            "processed": {"errors": [], "success": [{"item": "12:34:56:78:9A:BC"}]},
            "took": 0.001,
        }
        mock_request.return_value = mock_response

        clients_client.update_client(
            client="12:34:56:78:9A:BC", comment="Updated MAC client"
        )

        # MAC address should be URL encoded in the endpoint
        mock_request.assert_called_once_with(
            client,
            "PUT",
            "/api/clients/12%3A34%3A56%3A78%3A9A%3ABC",
            json={"comment": "Updated MAC client", "groups": [0]},
        )


class TestPiHoleClientsDeleteClient:
    """Test client deletion functionality (no network calls)."""

    @patch("pihole_lib.clients.make_pihole_request")
    def test_delete_client_success(self, mock_request):
        """Should successfully delete a client."""
        client = PiHoleClient(TEST_LOCALHOST_URL, password=TEST_SECRET_PASSWORD)
        clients_client = PiHoleClients(client)

        mock_response = Mock()
        mock_response.status_code = 204
        mock_request.return_value = mock_response

        result = clients_client.delete_client("192.168.1.100")

        assert result is True
        mock_request.assert_called_once_with(
            client, "DELETE", "/api/clients/192.168.1.100"
        )

    @patch("pihole_lib.clients.make_pihole_request")
    def test_delete_client_mac_address_encoding(self, mock_request):
        """Should properly URL encode MAC address in delete request."""
        client = PiHoleClient(TEST_LOCALHOST_URL, password=TEST_SECRET_PASSWORD)
        clients_client = PiHoleClients(client)

        mock_response = Mock()
        mock_response.status_code = 204
        mock_request.return_value = mock_response

        result = clients_client.delete_client("12:34:56:78:9A:BC")

        assert result is True
        # MAC address should be URL encoded
        mock_request.assert_called_once_with(
            client, "DELETE", "/api/clients/12%3A34%3A56%3A78%3A9A%3ABC"
        )

    @patch("pihole_lib.clients.make_pihole_request")
    def test_delete_client_not_found(self, mock_request):
        """Should handle client not found (non-204 response)."""
        client = PiHoleClient(TEST_LOCALHOST_URL, password=TEST_SECRET_PASSWORD)
        clients_client = PiHoleClients(client)

        mock_response = Mock()
        mock_response.status_code = 404
        mock_request.return_value = mock_response

        result = clients_client.delete_client("192.168.1.100")

        assert result is False


class TestPiHoleClientsBatchDelete:
    """Test batch client deletion functionality (no network calls)."""

    @patch("pihole_lib.clients.make_pihole_request")
    def test_batch_delete_clients_success(self, mock_request):
        """Should successfully batch delete clients."""
        client = PiHoleClient(TEST_LOCALHOST_URL, password=TEST_SECRET_PASSWORD)
        clients_client = PiHoleClients(client)

        mock_response = Mock()
        mock_response.status_code = 204
        mock_request.return_value = mock_response

        items = [
            ClientBatchDeleteItem(item="192.168.1.100"),
            ClientBatchDeleteItem(item="12:34:56:78:9A:BC"),
        ]

        result = clients_client.batch_delete_clients(items)

        assert result is True
        mock_request.assert_called_once_with(
            client,
            "POST",
            "/api/clients:batchDelete",
            json=[
                {"item": "192.168.1.100"},
                {"item": "12:34:56:78:9A:BC"},
            ],
        )

    @patch("pihole_lib.clients.make_pihole_request")
    def test_batch_delete_clients_failure(self, mock_request):
        """Should handle batch delete failure."""
        client = PiHoleClient(TEST_LOCALHOST_URL, password=TEST_SECRET_PASSWORD)
        clients_client = PiHoleClients(client)

        mock_response = Mock()
        mock_response.status_code = 400
        mock_request.return_value = mock_response

        items = [
            ClientBatchDeleteItem(item="192.168.1.100"),
        ]

        result = clients_client.batch_delete_clients(items)

        assert result is False


class TestPiHoleClientsGetSuggestions:
    """Test client suggestions functionality (no network calls)."""

    @patch("pihole_lib.clients.make_pihole_request")
    def test_get_client_suggestions_success(self, mock_request):
        """Should successfully get client suggestions."""
        client = PiHoleClient(TEST_LOCALHOST_URL, password=TEST_SECRET_PASSWORD)
        clients_client = PiHoleClients(client)

        mock_response = Mock()
        mock_response.json.return_value = {
            "clients": [
                {
                    "client": "192.168.1.200",
                    "name": "unknown-device",
                    "comment": None,
                    "groups": [0],
                    "id": 10,
                    "date_added": 1640995200,
                    "date_modified": 1640995200,
                }
            ],
            "took": 0.001,
        }
        mock_request.return_value = mock_response

        result = clients_client.get_client_suggestions()

        assert len(result) == 1
        assert result[0].client == "192.168.1.200"
        assert result[0].name == "unknown-device"

        mock_request.assert_called_once_with(client, "GET", "/api/clients/_suggestions")

    @patch("pihole_lib.clients.make_pihole_request")
    def test_get_client_suggestions_empty(self, mock_request):
        """Should handle empty suggestions response."""
        client = PiHoleClient(TEST_LOCALHOST_URL, password=TEST_SECRET_PASSWORD)
        clients_client = PiHoleClients(client)

        mock_response = Mock()
        mock_response.json.return_value = {
            "clients": [],
            "took": 0.001,
        }
        mock_request.return_value = mock_response

        result = clients_client.get_client_suggestions()

        assert len(result) == 0
        mock_request.assert_called_once_with(client, "GET", "/api/clients/_suggestions")
