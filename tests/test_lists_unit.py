"""Unit tests for PiHoleLists."""

from unittest.mock import patch

import pytest

from pihole_lib import PiHoleLists
from pihole_lib.exceptions import PiHoleConnectionError, PiHoleServerError
from pihole_lib.models.lists import BatchDeleteItem, ListType
from tests.conftest import SAMPLE_LIST_DATA, make_client, make_mock_response


@pytest.fixture
def lists_client(mock_client):
    """Create a PiHoleLists instance for testing."""
    return PiHoleLists(mock_client)


class TestPiHoleListsInit:
    """Test lists client initialization."""

    def test_init_with_client(self):
        """Lists client should initialize with a PiHoleClient."""
        client = make_client()
        lists_client = PiHoleLists(client)
        assert lists_client._client is client


class TestPiHoleListsGetLists:
    """Test lists retrieval functionality."""

    @patch("pihole_lib.lists.make_pihole_request")
    def test_get_lists_success(self, mock_request, lists_client, mock_client):
        """Should successfully get all lists."""
        mock_request.return_value = make_mock_response(
            json_data={
                "lists": [SAMPLE_LIST_DATA],
                "took": 0.123,
            }
        )

        result = lists_client.get_lists()

        mock_request.assert_called_once_with(
            mock_client, "GET", lists_client.BASE_URL, params=None
        )
        assert len(result) == 1
        assert result[0].address == "https://example.com/blocklist.txt"
        assert result[0].type == ListType.BLOCK

    @pytest.mark.parametrize(
        "list_type,expected_params",
        [
            (ListType.ALLOW, {"type": "allow"}),
            (ListType.BLOCK, {"type": "block"}),
        ],
    )
    @patch("pihole_lib.lists.make_pihole_request")
    def test_get_lists_with_type_filter(
        self, mock_request, lists_client, mock_client, list_type, expected_params
    ):
        """Should handle type filters correctly."""
        mock_request.return_value = make_mock_response(
            json_data={"lists": [], "took": 0.045}
        )

        lists_client.get_lists(list_type=list_type)

        mock_request.assert_called_with(
            mock_client, "GET", lists_client.BASE_URL, params=expected_params
        )

    @patch("pihole_lib.lists.make_pihole_request")
    def test_get_lists_with_name_filter(self, mock_request, lists_client, mock_client):
        """Should handle name filter correctly."""
        mock_request.return_value = make_mock_response(
            json_data={"lists": [], "took": 0.045}
        )

        lists_client.get_lists(list_name="my_list")

        mock_request.assert_called_with(
            mock_client, "GET", "/api/lists/my_list", params=None
        )


class TestPiHoleListsAddList:
    """Test list addition functionality."""

    @patch("pihole_lib.lists.make_pihole_request")
    def test_add_list_success(self, mock_request, lists_client, mock_client):
        """Should successfully add a new list."""
        mock_request.return_value = make_mock_response(
            json_data={
                "lists": [SAMPLE_LIST_DATA],
                "processed": {
                    "errors": [],
                    "success": [{"item": "https://example.com/blocklist.txt"}],
                },
                "took": 0.234,
            }
        )

        result = lists_client.add_list(
            address="https://example.com/blocklist.txt",
            list_type=ListType.BLOCK,
            comment="Test blocklist",
        )

        mock_request.assert_called_once_with(
            mock_client,
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
        assert len(result) == 1
        assert result[0].type == ListType.BLOCK

    @patch("pihole_lib.lists.make_pihole_request")
    def test_add_list_with_error(self, mock_request, lists_client):
        """Should raise PiHoleServerError when Pi-hole reports an error."""
        mock_request.return_value = make_mock_response(
            json_data={
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
        )

        with pytest.raises(PiHoleServerError) as exc_info:
            lists_client.add_list("duplicate.com", ListType.BLOCK)

        assert "UNIQUE constraint failed" in str(exc_info.value)

    @patch("pihole_lib.lists.make_pihole_request")
    def test_add_list_defaults(self, mock_request, lists_client, mock_client):
        """Should use correct defaults for optional parameters."""
        mock_request.return_value = make_mock_response(
            json_data={"lists": [], "took": 0.089}
        )

        lists_client.add_list("test.com", ListType.BLOCK)

        mock_request.assert_called_once_with(
            mock_client,
            "POST",
            lists_client.BASE_URL,
            params={"type": "block"},
            json={"address": "test.com", "groups": [0], "enabled": True},
        )


class TestPiHoleListsDeleteList:
    """Test list deletion functionality."""

    @pytest.mark.parametrize(
        "list_type,expected_params",
        [
            (ListType.BLOCK, {"type": "block"}),
            (ListType.ALLOW, {"type": "allow"}),
        ],
    )
    @patch("pihole_lib.lists.make_pihole_request")
    def test_delete_list_success(
        self, mock_request, lists_client, mock_client, list_type, expected_params
    ):
        """Should successfully delete a list."""
        mock_request.return_value = make_mock_response(status_code=204)

        result = lists_client.delete_list(address="example.com", list_type=list_type)

        mock_request.assert_called_once_with(
            mock_client, "DELETE", "/api/lists/example.com", params=expected_params
        )
        assert result is True

    @pytest.mark.parametrize(
        "exception_class,message",
        [
            (PiHoleConnectionError, "Connection failed"),
            (PiHoleServerError, "Server error"),
        ],
    )
    @patch("pihole_lib.lists.make_pihole_request")
    def test_delete_list_errors(
        self, mock_request, lists_client, exception_class, message
    ):
        """Should propagate errors from make_pihole_request."""
        mock_request.side_effect = exception_class(message)

        with pytest.raises(exception_class, match=message):
            lists_client.delete_list(address="test.com", list_type=ListType.BLOCK)


class TestPiHoleListsUpdateList:
    """Test list update functionality."""

    @patch("pihole_lib.lists.make_pihole_request")
    def test_update_list_success(self, mock_request, lists_client, mock_client):
        """Should successfully update a list."""
        mock_request.return_value = make_mock_response(
            json_data={
                "lists": [
                    {
                        **SAMPLE_LIST_DATA,
                        "address": "updated.example.com",
                        "type": "allow",
                        "comment": "Updated comment",
                        "enabled": False,
                        "groups": [0, 1],
                    }
                ],
                "processed": {
                    "success": [{"item": "updated.example.com"}],
                    "errors": [],
                },
                "took": 0.003,
            }
        )

        result = lists_client.update_list(
            address="updated.example.com",
            list_type=ListType.ALLOW,
            comment="Updated comment",
            groups=[0, 1],
            enabled=False,
        )

        assert hasattr(result, "lists")
        assert result.lists[0].comment == "Updated comment"
        assert result.lists[0].enabled is False


class TestPiHoleListsBatchDelete:
    """Test batch list deletion functionality."""

    @pytest.mark.parametrize(
        "status_code,expected_result",
        [
            (204, True),
            (400, False),
        ],
    )
    @patch("pihole_lib.lists.make_pihole_request")
    def test_batch_delete_lists(
        self, mock_request, lists_client, status_code, expected_result
    ):
        """Should handle batch delete responses correctly."""
        mock_request.return_value = make_mock_response(status_code=status_code)

        items = [
            BatchDeleteItem(item="example1.com", type=ListType.ALLOW),
            BatchDeleteItem(item="example2.com", type=ListType.BLOCK),
        ]

        result = lists_client.batch_delete_lists(items)
        assert result is expected_result


class TestPiHoleListsSearchDomains:
    """Test domain search functionality."""

    @patch("pihole_lib.lists.make_pihole_request")
    def test_search_domains_success(self, mock_request, lists_client):
        """Should successfully search for domains."""
        mock_request.return_value = make_mock_response(
            json_data={
                "search": {
                    "domains": [],
                    "gravity": [{**SAMPLE_LIST_DATA, "address": "pgl.example.com"}],
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
        )

        result = lists_client.search_domains("example.com")

        assert hasattr(result, "search")
        assert result.search.results.total == 1
        assert result.search.parameters.domain == "example.com"

    @pytest.mark.parametrize(
        "partial,max_results,debug",
        [
            (True, 10, True),
            (False, 50, False),
        ],
    )
    @patch("pihole_lib.lists.make_pihole_request")
    def test_search_domains_with_options(
        self, mock_request, lists_client, partial, max_results, debug
    ):
        """Should search with custom options."""
        mock_request.return_value = make_mock_response(
            json_data={
                "search": {
                    "domains": [],
                    "gravity": [],
                    "results": {
                        "domains": {"exact": 0, "regex": 0},
                        "gravity": {"allow": 0, "block": 0},
                        "total": 0,
                    },
                    "parameters": {
                        "N": max_results,
                        "partial": partial,
                        "domain": "example",
                        "debug": debug,
                    },
                },
                "took": 0.0005,
            }
        )

        result = lists_client.search_domains(
            domain="example", partial=partial, max_results=max_results, debug=debug
        )

        assert result.search.parameters.partial is partial
        assert result.search.parameters.N == max_results
        assert result.search.parameters.debug is debug
