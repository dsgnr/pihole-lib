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
            "took": 0.123,
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
            lists_client.BASE_URL,
            params=None,
        )

    @patch("pihole_lib.lists.make_pihole_request")
    def test_get_lists_with_filters(self, mock_request):
        """Should handle name and type filters."""
        client = PiHoleClient(TEST_LOCALHOST_URL, password=TEST_SECRET_PASSWORD)
        lists_client = PiHoleLists(client)

        mock_response = Mock()
        mock_response.json.return_value = {"lists": [], "took": 0.045}
        mock_request.return_value = mock_response

        # Test with type filter
        result = lists_client.get_lists(list_type=ListType.ALLOW)
        assert isinstance(result, list)
        assert len(result) == 0
        mock_request.assert_called_with(
            client,
            "GET",
            lists_client.BASE_URL,
            params={"type": "allow"},
        )

        # Test with name filter
        result = lists_client.get_lists(list_name="my_list")
        assert isinstance(result, list)
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
            "took": 0.234,
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
            lists_client.BASE_URL,
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
            ],
            "took": 0.156,
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
        mock_response.json.return_value = {"lists": [], "took": 0.089}
        mock_request.return_value = mock_response

        result = lists_client.add_list("test.com", ListType.BLOCK)

        assert isinstance(result, list)
        assert len(result) == 0

        # Verify defaults were used
        mock_request.assert_called_once_with(
            client,
            "POST",
            lists_client.BASE_URL,
            params={"type": "block"},
            json={
                "address": "test.com",
                "groups": [0],  # Default group
                "enabled": True,  # Default enabled
            },
        )


class TestPiHoleListsDeleteList:
    """Test list deletion functionality (no network calls)."""

    @patch("pihole_lib.lists.make_pihole_request")
    def test_delete_list_success(self, mock_request):
        """Should successfully delete a list."""
        client = PiHoleClient(TEST_LOCALHOST_URL, password=TEST_SECRET_PASSWORD)
        lists_client = PiHoleLists(client)

        mock_response = Mock()
        mock_response.status_code = 204  # No Content
        mock_request.return_value = mock_response

        result = lists_client.delete_list(
            address="https://example.com/blocklist.txt", list_type=ListType.BLOCK
        )

        assert result is True

        mock_request.assert_called_once_with(
            client,
            "DELETE",
            "/api/lists/https://example.com/blocklist.txt",
            params={"type": "block"},
        )

    @patch("pihole_lib.lists.make_pihole_request")
    def test_delete_list_allow_type(self, mock_request):
        """Should handle allow list deletion."""
        client = PiHoleClient(TEST_LOCALHOST_URL, password=TEST_SECRET_PASSWORD)
        lists_client = PiHoleLists(client)

        mock_response = Mock()
        mock_response.status_code = 204
        mock_request.return_value = mock_response

        result = lists_client.delete_list(
            address="example.com", list_type=ListType.ALLOW
        )

        assert result is True

        mock_request.assert_called_once_with(
            client,
            "DELETE",
            "/api/lists/example.com",
            params={"type": "allow"},
        )

    @patch("pihole_lib.lists.make_pihole_request")
    def test_delete_list_connection_error(self, mock_request):
        """Should propagate connection errors from make_pihole_request."""
        from pihole_lib.exceptions import PiHoleConnectionError

        client = PiHoleClient(TEST_LOCALHOST_URL, password=TEST_SECRET_PASSWORD)
        lists_client = PiHoleLists(client)

        mock_request.side_effect = PiHoleConnectionError("Connection failed")

        with pytest.raises(PiHoleConnectionError, match="Connection failed"):
            lists_client.delete_list(address="test.com", list_type=ListType.BLOCK)

    @patch("pihole_lib.lists.make_pihole_request")
    def test_delete_list_server_error(self, mock_request):
        """Should propagate server errors from make_pihole_request."""
        from pihole_lib.exceptions import PiHoleServerError

        client = PiHoleClient(TEST_LOCALHOST_URL, password=TEST_SECRET_PASSWORD)
        lists_client = PiHoleLists(client)

        mock_request.side_effect = PiHoleServerError("Server error")

        with pytest.raises(PiHoleServerError, match="Server error"):
            lists_client.delete_list(address="error.com", list_type=ListType.BLOCK)

    @patch("pihole_lib.lists.make_pihole_request")
    def test_delete_list_url_with_path(self, mock_request):
        """Should handle URLs with paths."""
        client = PiHoleClient(TEST_LOCALHOST_URL, password=TEST_SECRET_PASSWORD)
        lists_client = PiHoleLists(client)

        mock_response = Mock()
        mock_response.status_code = 204
        mock_request.return_value = mock_response

        # Test with URL containing path
        url_with_path = "https://example.com/blocklist.txt"

        result = lists_client.delete_list(
            address=url_with_path, list_type=ListType.BLOCK
        )

        assert result is True

        mock_request.assert_called_once_with(
            client,
            "DELETE",
            f"/api/lists/{url_with_path}",
            params={"type": "block"},
        )


class TestPiHoleListsUpdateList:
    """Test list update functionality (no network calls)."""

    @patch("pihole_lib.lists.make_pihole_request")
    def test_update_list_success(self, mock_request):
        """Should successfully update a list."""
        client = PiHoleClient(TEST_LOCALHOST_URL, password=TEST_SECRET_PASSWORD)
        lists_client = PiHoleLists(client)

        mock_response = Mock()
        mock_response.json.return_value = {
            "lists": [
                {
                    "address": "updated.example.com",
                    "type": "allow",
                    "comment": "Updated comment",
                    "groups": [0, 1],
                    "enabled": False,
                    "id": 3,
                    "date_added": 1767805943,
                    "date_modified": 1767805950,
                    "date_updated": 0,
                    "number": 0,
                    "invalid_domains": 0,
                    "abp_entries": 0,
                    "status": 0,
                }
            ],
            "processed": {
                "success": [{"item": "updated.example.com"}],
                "errors": [],
            },
            "took": 0.003,
        }
        mock_request.return_value = mock_response

        result = lists_client.update_list(
            address="updated.example.com",
            list_type=ListType.ALLOW,
            comment="Updated comment",
            groups=[0, 1],
            enabled=False,
        )

        # Should return ListsResponse object
        assert hasattr(result, "lists")
        assert hasattr(result, "processed")
        assert hasattr(result, "took")
        assert len(result.lists) == 1
        assert result.lists[0].address == "updated.example.com"
        assert result.lists[0].comment == "Updated comment"
        assert result.lists[0].enabled is False
        assert result.lists[0].groups == [0, 1]

    @patch("pihole_lib.lists.make_pihole_request")
    def test_update_list_authentication_error(self, mock_request):
        """Should raise PiHoleAuthenticationError on auth failure."""
        from pihole_lib.exceptions import PiHoleAuthenticationError

        client = PiHoleClient(TEST_LOCALHOST_URL, password=TEST_SECRET_PASSWORD)
        lists_client = PiHoleLists(client)

        mock_request.side_effect = PiHoleAuthenticationError("Authentication failed")

        with pytest.raises(PiHoleAuthenticationError):
            lists_client.update_list(
                address="test.com",
                list_type=ListType.ALLOW,
                comment="test",
            )


class TestPiHoleListsBatchDelete:
    """Test batch list deletion functionality (no network calls)."""

    @patch("pihole_lib.lists.make_pihole_request")
    def test_batch_delete_lists_success(self, mock_request):
        """Should successfully batch delete lists."""
        from pihole_lib.models import BatchDeleteItem

        client = PiHoleClient(TEST_LOCALHOST_URL, password=TEST_SECRET_PASSWORD)
        lists_client = PiHoleLists(client)

        # Mock successful response (204 No Content)
        mock_response = Mock()
        mock_response.status_code = 204
        mock_request.return_value = mock_response

        items_to_delete = [
            BatchDeleteItem(item="example1.com", type=ListType.ALLOW),
            BatchDeleteItem(item="example2.com", type=ListType.BLOCK),
        ]

        result = lists_client.batch_delete_lists(items_to_delete)

        assert result is True

    @patch("pihole_lib.lists.make_pihole_request")
    def test_batch_delete_lists_connection_error(self, mock_request):
        """Should raise PiHoleConnectionError on connection failure."""
        from pihole_lib.exceptions import PiHoleConnectionError

        client = PiHoleClient(TEST_LOCALHOST_URL, password=TEST_SECRET_PASSWORD)
        lists_client = PiHoleLists(client)

        mock_request.side_effect = PiHoleConnectionError("Connection failed")

        with pytest.raises(PiHoleConnectionError):
            lists_client.batch_delete_lists([])

    @patch("pihole_lib.lists.make_pihole_request")
    def test_batch_delete_lists_api_error(self, mock_request):
        """Should raise PiHoleAPIError on other API errors."""
        from pihole_lib.exceptions import PiHoleAPIError
        from pihole_lib.models import BatchDeleteItem

        client = PiHoleClient(TEST_LOCALHOST_URL, password=TEST_SECRET_PASSWORD)
        lists_client = PiHoleLists(client)

        mock_request.side_effect = PiHoleAPIError("API error")

        with pytest.raises(PiHoleAPIError):
            lists_client.batch_delete_lists(
                [BatchDeleteItem(item="test.com", type=ListType.ALLOW)]
            )


class TestPiHoleListsSearchDomains:
    """Test domain search functionality (no network calls)."""

    @patch("pihole_lib.lists.make_pihole_request")
    def test_search_domains_success(self, mock_request):
        """Should successfully search for domains."""
        client = PiHoleClient(TEST_LOCALHOST_URL, password=TEST_SECRET_PASSWORD)
        lists_client = PiHoleLists(client)

        mock_response = Mock()
        mock_response.json.return_value = {
            "search": {
                "domains": [],
                "gravity": [
                    {
                        "address": "pgl.example.com",
                        "type": "block",
                        "comment": "Found in gravity",
                        "groups": [0],
                        "enabled": True,
                        "id": 1,
                        "date_added": 1767805907,
                        "date_modified": 1767805907,
                        "date_updated": 1767805908,
                        "number": 79811,
                        "invalid_domains": 1,
                        "abp_entries": 0,
                        "status": 0,
                    }
                ],
                "results": {
                    "domains": {"exact": 0, "regex": 0},
                    "gravity": {"allow": 0, "block": 1},
                    "total": 1,
                },
                "parameters": {
                    "N": 20,
                    "partial": False,
                    "domain": "example.com",
                    "debug": False,
                },
            },
            "took": 0.0004,
        }
        mock_request.return_value = mock_response

        result = lists_client.search_domains("example.com")

        # Should return SearchResponse object
        assert hasattr(result, "search")
        assert hasattr(result, "took")
        assert result.took == 0.0004

        # Check search data structure
        search_data = result.search
        assert hasattr(search_data, "domains")
        assert hasattr(search_data, "gravity")
        assert hasattr(search_data, "results")
        assert hasattr(search_data, "parameters")

        # Check results
        assert len(search_data.domains) == 0
        assert len(search_data.gravity) == 1
        assert search_data.gravity[0].address == "pgl.example.com"
        assert search_data.results.total == 1
        assert search_data.results.gravity.block == 1

        # Check parameters
        params = search_data.parameters
        assert params.domain == "example.com"
        assert params.partial is False
        assert params.N == 20
        assert params.debug is False

    @patch("pihole_lib.lists.make_pihole_request")
    def test_search_domains_with_options(self, mock_request):
        """Should search with custom options."""
        client = PiHoleClient(TEST_LOCALHOST_URL, password=TEST_SECRET_PASSWORD)
        lists_client = PiHoleLists(client)

        mock_response = Mock()
        mock_response.json.return_value = {
            "search": {
                "domains": [],
                "gravity": [],
                "results": {
                    "domains": {"exact": 0, "regex": 0},
                    "gravity": {"allow": 0, "block": 0},
                    "total": 0,
                },
                "parameters": {
                    "N": 50,
                    "partial": True,
                    "domain": "example",
                    "debug": True,
                },
            },
            "took": 0.0005,
        }
        mock_request.return_value = mock_response

        result = lists_client.search_domains(
            domain="example",
            partial=True,
            max_results=50,
            debug=True,
        )

        # Check parameters were applied
        params = result.search.parameters
        assert params.domain == "example"
        assert params.partial is True
        assert params.N == 50
        assert params.debug is True

    @patch("pihole_lib.lists.make_pihole_request")
    def test_search_domains_server_error(self, mock_request):
        """Should raise PiHoleServerError on server error."""
        client = PiHoleClient(TEST_LOCALHOST_URL, password=TEST_SECRET_PASSWORD)
        lists_client = PiHoleLists(client)

        mock_request.side_effect = PiHoleServerError("Server error")

        with pytest.raises(PiHoleServerError):
            lists_client.search_domains("test.com")
