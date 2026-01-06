"""Unit tests for PiHoleLists (no network calls)."""

from unittest.mock import Mock, patch

import pytest

from pihole_lib import PiHoleClient, PiHoleLists
from pihole_lib.exceptions import PiHoleServerError
from pihole_lib.models import ListType

from .constants import (
    TEST_LOCALHOST_URL,
    TEST_SECRET_PASSWORD,
)


class TestPiHoleListsInit:
    """Test lists client initialization."""

    def test_init_with_client(self):
        """Lists client should initialize with a PiHoleClient."""
        client = PiHoleClient(TEST_LOCALHOST_URL, password=TEST_SECRET_PASSWORD)
        lists_client = PiHoleLists(client)

        assert lists_client._client is client


class TestPiHoleListsGetLists:
    """Test lists retrieval functionality (no network calls)."""

    @patch("pihole_lib.lists.make_pihole_request")
    def test_get_lists_success(self, mock_request):
        """Should successfully get all lists."""
        client = PiHoleClient(TEST_LOCALHOST_URL, password=TEST_SECRET_PASSWORD)
        lists_client = PiHoleLists(client)

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
        }
        mock_request.return_value = mock_response

        result = lists_client.get_lists()

        assert isinstance(result, list)
        assert len(result) == 1
        assert result[0].address == "https://example.com/blocklist.txt"
        assert result[0].type == ListType.BLOCK

        mock_request.assert_called_once_with(
            client,
            "GET",
            "/api/lists",
            params=None,
        )

    @patch("pihole_lib.lists.make_pihole_request")
    def test_get_lists_with_filters(self, mock_request):
        """Should handle name and type filters."""
        client = PiHoleClient(TEST_LOCALHOST_URL, password=TEST_SECRET_PASSWORD)
        lists_client = PiHoleLists(client)

        mock_response = Mock()
        mock_response.json.return_value = {"lists": []}
        mock_request.return_value = mock_response

        # Test with type filter
        lists_client.get_lists(list_type=ListType.ALLOW)
        mock_request.assert_called_with(
            client,
            "GET",
            "/api/lists",
            params={"type": "allow"},
        )

        # Test with name filter
        lists_client.get_lists(list_name="my_list")
        mock_request.assert_called_with(
            client,
            "GET",
            "/api/lists/my_list",
            params=None,
        )


class TestPiHoleListsAddList:
    """Test list addition functionality (no network calls)."""

    @patch("pihole_lib.lists.make_pihole_request")
    def test_add_list_success(self, mock_request):
        """Should successfully add a new list."""
        client = PiHoleClient(TEST_LOCALHOST_URL, password=TEST_SECRET_PASSWORD)
        lists_client = PiHoleLists(client)

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
                    "number": 0,
                    "invalid_domains": 0,
                    "abp_entries": 0,
                    "status": 1,
                }
            ],
            "processed": {
                "errors": [],
                "success": [{"item": "https://example.com/blocklist.txt"}],
            },
        }
        mock_request.return_value = mock_response

        result = lists_client.add_list(
            address="https://example.com/blocklist.txt",
            list_type=ListType.BLOCK,
            comment="Test blocklist",
        )

        assert isinstance(result, list)
        assert len(result) == 1
        assert result[0].address == "https://example.com/blocklist.txt"
        assert result[0].type == ListType.BLOCK

        mock_request.assert_called_once_with(
            client,
            "POST",
            "/api/lists",
            params={"type": "block"},
            json={
                "address": "https://example.com/blocklist.txt",
                "comment": "Test blocklist",
                "groups": [0],
                "enabled": True,
            },
        )

    @patch("pihole_lib.lists.make_pihole_request")
    def test_add_list_with_error(self, mock_request):
        """Should raise PiHoleServerError when Pi-hole reports an error."""
        client = PiHoleClient(TEST_LOCALHOST_URL, password=TEST_SECRET_PASSWORD)
        lists_client = PiHoleLists(client)

        mock_response = Mock()
        mock_response.json.return_value = {
            "lists": [],
            "processed": {
                "errors": [
                    {
                        "item": "duplicate.com",
                        "error": "UNIQUE constraint failed: adlist.address, adlist.type",
                    }
                ],
                "success": [],
            },
        }
        mock_request.return_value = mock_response

        with pytest.raises(PiHoleServerError) as exc_info:
            lists_client.add_list("duplicate.com", ListType.BLOCK)

        assert "UNIQUE constraint failed" in str(exc_info.value)
        assert "duplicate.com" in str(exc_info.value)

    @patch("pihole_lib.lists.make_pihole_request")
    def test_add_list_no_processed_field(self, mock_request):
        """Should work when response has no processed field."""
        client = PiHoleClient(TEST_LOCALHOST_URL, password=TEST_SECRET_PASSWORD)
        lists_client = PiHoleLists(client)

        mock_response = Mock()
        mock_response.json.return_value = {
            "lists": [
                {
                    "address": "simple.com",
                    "type": "allow",
                    "comment": None,
                    "groups": [0],
                    "enabled": True,
                    "id": 1,
                    "date_added": 1640995200,
                    "date_modified": 1640995200,
                    "date_updated": 1640995200,
                    "number": 0,
                    "invalid_domains": 0,
                    "abp_entries": 0,
                    "status": 1,
                }
            ]
            # No processed field
        }
        mock_request.return_value = mock_response

        result = lists_client.add_list("simple.com", ListType.ALLOW)

        assert isinstance(result, list)
        assert len(result) == 1
        assert result[0].address == "simple.com"

    @patch("pihole_lib.lists.make_pihole_request")
    def test_add_list_defaults(self, mock_request):
        """Should use correct defaults for optional parameters."""
        client = PiHoleClient(TEST_LOCALHOST_URL, password=TEST_SECRET_PASSWORD)
        lists_client = PiHoleLists(client)

        mock_response = Mock()
        mock_response.json.return_value = {"lists": []}
        mock_request.return_value = mock_response

        lists_client.add_list("test.com", ListType.BLOCK)

        # Verify defaults were used
        mock_request.assert_called_once_with(
            client,
            "POST",
            "/api/lists",
            params={"type": "block"},
            json={
                "address": "test.com",
                "groups": [0],  # Default group
                "enabled": True,  # Default enabled
            },
        )
