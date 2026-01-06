"""Unit tests for PiHoleLists (no network calls)."""

from unittest.mock import Mock, patch

from pihole_lib import PiHoleClient, PiHoleLists
from pihole_lib.models import ListsResponse, ListType, PiHoleList

from .constants import (
    TEST_LOCALHOST_URL,
    TEST_REQUEST_TIME,
    TEST_SECRET_PASSWORD,
)


class TestPiHoleListsInit:
    """Test lists client initialization."""

    def test_init_with_client(self):
        """Lists client should initialize with a PiHoleClient."""
        client = PiHoleClient(TEST_LOCALHOST_URL, password=TEST_SECRET_PASSWORD)
        lists_client = PiHoleLists(client)

        assert lists_client._client is client

    def test_init_stores_client_reference(self):
        """Lists client should store reference to the provided client."""
        client = PiHoleClient(TEST_LOCALHOST_URL, password=TEST_SECRET_PASSWORD)
        lists_client = PiHoleLists(client)

        # Should be able to access client properties through the stored reference
        assert lists_client._client.base_url == TEST_LOCALHOST_URL
        assert lists_client._client._password == TEST_SECRET_PASSWORD


class TestPiHoleListsGetLists:
    """Test lists retrieval functionality (no network calls)."""

    def test_get_lists_uses_client_session(self):
        """get_lists should use the client through make_pihole_request."""
        client = PiHoleClient(TEST_LOCALHOST_URL, password=TEST_SECRET_PASSWORD)
        lists_client = PiHoleLists(client)

        assert client._session is None

        # Mock the make_pihole_request to avoid network calls
        with patch("pihole_lib.lists.make_pihole_request") as mock_request:
            mock_response = Mock()
            mock_response.json.return_value = {
                "lists": [],
                "took": TEST_REQUEST_TIME,
            }
            mock_request.return_value = mock_response

            lists_client.get_lists()

        # Verify make_pihole_request was called with the client
        mock_request.assert_called_once_with(
            client,
            "GET",
            "/api/lists",
            params=None,
        )

    @patch("pihole_lib.lists.make_pihole_request")
    def test_get_lists_all_success(self, mock_request):
        """Should successfully get all lists."""
        client = PiHoleClient(TEST_LOCALHOST_URL, password=TEST_SECRET_PASSWORD)
        lists_client = PiHoleLists(client)

        # Mock successful response with sample list data
        mock_response = Mock()
        mock_response.json.return_value = {
            "lists": [
                {
                    "address": "https://example.com/blocklist.txt",
                    "type": "block",
                    "comment": "Test blocklist",
                    "groups": [0],
                    "enabled": True,
                    "id": 1,
                    "date_added": 1640995200,
                    "date_modified": 1640995200,
                    "date_updated": 1640995200,
                    "number": 1000,
                    "invalid_domains": 5,
                    "abp_entries": 0,
                    "status": 1,
                }
            ],
            "took": TEST_REQUEST_TIME,
        }
        mock_request.return_value = mock_response

        result = lists_client.get_lists()

        assert isinstance(result, ListsResponse)
        assert len(result.lists) == 1
        assert result.took == TEST_REQUEST_TIME

        list_item = result.lists[0]
        assert isinstance(list_item, PiHoleList)
        assert list_item.address == "https://example.com/blocklist.txt"
        assert list_item.type == ListType.BLOCK
        assert list_item.comment == "Test blocklist"
        assert list_item.enabled is True
        assert list_item.id == 1

        mock_request.assert_called_once_with(
            client,
            "GET",
            "/api/lists",
            params=None,
        )

    @patch("pihole_lib.lists.make_pihole_request")
    def test_get_lists_with_type_filter(self, mock_request):
        """Should filter lists by type."""
        client = PiHoleClient(TEST_LOCALHOST_URL, password=TEST_SECRET_PASSWORD)
        lists_client = PiHoleLists(client)

        mock_response = Mock()
        mock_response.json.return_value = {
            "lists": [],
            "took": TEST_REQUEST_TIME,
        }
        mock_request.return_value = mock_response

        result = lists_client.get_lists(list_type=ListType.ALLOW)

        assert isinstance(result, ListsResponse)
        mock_request.assert_called_once_with(
            client,
            "GET",
            "/api/lists",
            params={"type": "allow"},
        )

    @patch("pihole_lib.lists.make_pihole_request")
    def test_get_lists_with_name_filter(self, mock_request):
        """Should filter lists by name."""
        client = PiHoleClient(TEST_LOCALHOST_URL, password=TEST_SECRET_PASSWORD)
        lists_client = PiHoleLists(client)

        mock_response = Mock()
        mock_response.json.return_value = {
            "lists": [],
            "took": TEST_REQUEST_TIME,
        }
        mock_request.return_value = mock_response

        result = lists_client.get_lists(list_name="my_list")

        assert isinstance(result, ListsResponse)
        mock_request.assert_called_once_with(
            client,
            "GET",
            "/api/lists/my_list",
            params=None,
        )

    @patch("pihole_lib.lists.make_pihole_request")
    def test_get_lists_with_both_filters(self, mock_request):
        """Should handle both name and type filters."""
        client = PiHoleClient(TEST_LOCALHOST_URL, password=TEST_SECRET_PASSWORD)
        lists_client = PiHoleLists(client)

        mock_response = Mock()
        mock_response.json.return_value = {
            "lists": [],
            "took": TEST_REQUEST_TIME,
        }
        mock_request.return_value = mock_response

        result = lists_client.get_lists(list_name="my_list", list_type=ListType.BLOCK)

        assert isinstance(result, ListsResponse)
        mock_request.assert_called_once_with(
            client,
            "GET",
            "/api/lists/my_list",
            params={"type": "block"},
        )

    def test_get_lists_uses_client_properties(self):
        """get_lists should use client's base_url and timeout."""
        client = PiHoleClient(
            TEST_LOCALHOST_URL,
            password=TEST_SECRET_PASSWORD,
            timeout=60,
            verify_ssl=False,
        )
        lists_client = PiHoleLists(client)

        # Verify lists client uses client properties
        assert lists_client._client.base_url == TEST_LOCALHOST_URL
        assert lists_client._client.timeout == 60
        assert lists_client._client.verify_ssl is False
