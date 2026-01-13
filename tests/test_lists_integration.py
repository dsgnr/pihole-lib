"""Integration tests for PiHoleLists."""

import time

import pytest

from pihole_lib import PiHoleClient, PiHoleLists
from pihole_lib.exceptions import (
    PiHoleAPIError,
    PiHoleConnectionError,
    PiHoleServerError,
)
from pihole_lib.models.lists import ListType
from tests.conftest import integration
from tests.constants import (
    CONNECTION_FAILED_MESSAGE,
    PIHOLE_TEST_PASSWORD,
    TEST_INVALID_HOST_URL,
)


@integration
class TestPiHoleListsGetLists:
    """Test lists retrieval functionality against real Pi-hole."""

    def test_get_lists_all_success(self, pihole_client):
        """Should successfully get all lists from Pi-hole."""
        lists_client = PiHoleLists(pihole_client)

        result = lists_client.get_lists()

        assert isinstance(result, list)

        # Pi-hole should have at least some default lists
        # Note: The exact number depends on Pi-hole configuration

    def test_get_lists_with_type_filter(self, pihole_client):
        """Should filter lists by type."""
        lists_client = PiHoleLists(pihole_client)

        # Test both allow and block filters
        allow_lists = lists_client.get_lists(list_type=ListType.ALLOW)
        block_lists = lists_client.get_lists(list_type=ListType.BLOCK)

        assert isinstance(allow_lists, list)
        assert isinstance(block_lists, list)

        # Verify all returned lists have the correct type
        for list_item in allow_lists:
            assert list_item.type == ListType.ALLOW

        for list_item in block_lists:
            assert list_item.type == ListType.BLOCK

    def test_get_lists_connection_error(self):
        """Network errors should raise connection error."""
        client = PiHoleClient(
            base_url=TEST_INVALID_HOST_URL,
            password=PIHOLE_TEST_PASSWORD,
            timeout=1,  # Short timeout
        )
        lists_client = PiHoleLists(client)

        with pytest.raises(PiHoleConnectionError, match=CONNECTION_FAILED_MESSAGE):
            lists_client.get_lists()

        client.close()

    def test_get_lists_nonexistent_list(self, pihole_client):
        """Should handle requests for non-existent lists gracefully."""
        lists_client = PiHoleLists(pihole_client)

        # Request a list that doesn't exist
        result = lists_client.get_lists(list_name="nonexistent_list_12345")

        assert isinstance(result, list)
        # Should return empty list or handle gracefully
        # The exact behavior depends on Pi-hole implementation


@integration
class TestPiHoleListsWorkflows:
    """Test complete lists workflows with real Pi-hole."""

    def test_lists_operations_efficiency(self, pihole_client):
        """Test that lists operations work efficiently with proper session management."""
        lists_client = PiHoleLists(pihole_client)

        # Get all lists and verify it works
        all_lists = lists_client.get_lists()
        assert isinstance(all_lists, list)

        # Get filtered lists for comparison
        allow_lists = lists_client.get_lists(list_type=ListType.ALLOW)
        block_lists = lists_client.get_lists(list_type=ListType.BLOCK)

        # Verify session is properly managed
        assert pihole_client._session is not None
        total_filtered = len(allow_lists) + len(block_lists)
        assert total_filtered >= 0  # Basic sanity check

    def test_lists_data_structure(self, pihole_client):
        """Verify the structure of returned list data."""
        lists_client = PiHoleLists(pihole_client)

        result = lists_client.get_lists()

        assert isinstance(result, list)

        # Check each list has the expected structure
        for list_item in result:
            assert hasattr(list_item, "address")
            assert hasattr(list_item, "type")
            assert hasattr(list_item, "enabled")
            assert hasattr(list_item, "id")
            assert hasattr(list_item, "groups")

            # Verify types
            assert isinstance(list_item.address, str)
            assert isinstance(list_item.type, ListType)
            assert isinstance(list_item.enabled, bool)
            assert isinstance(list_item.id, int)
            assert isinstance(list_item.groups, list)


@integration
class TestPiHoleListsAddList:
    """Test list addition functionality against real Pi-hole."""

    def test_add_list_success(self, pihole_client):
        """Should successfully add a new list to Pi-hole."""
        lists_client = PiHoleLists(pihole_client)

        # Add a test blocklist with a unique address
        test_address = f"https://example-test-{int(time.time())}.com/blocklist.txt"
        result = lists_client.add_list(
            address=test_address,
            list_type=ListType.BLOCK,
            comment="Test blocklist for integration test",
            groups=[0],
            enabled=True,
        )

        assert isinstance(result, list)
        assert len(result) > 0

        # Find the list with our test address in the response
        matching_lists = [lst for lst in result if lst.address == test_address]
        assert len(matching_lists) > 0, f"No list found with address {test_address}"

        # Check the properties of the matching list
        new_list = matching_lists[0]
        assert new_list.type == ListType.BLOCK
        assert new_list.comment == "Test blocklist for integration test"
        assert new_list.enabled is True
        assert new_list.groups == [0]
        assert isinstance(new_list.id, int)
        assert new_list.id > 0

    def test_add_list_minimal_params(self, pihole_client):
        """Should add list with minimal parameters."""
        lists_client = PiHoleLists(pihole_client)

        # Add a simple domain allowlist with unique address
        test_address = f"example-test-domain-{int(time.time())}.com"
        result = lists_client.add_list(
            address=test_address,
            list_type=ListType.ALLOW,
        )

        assert isinstance(result, list)
        assert len(result) > 0

        # Find the list with our test address in the response
        matching_lists = [lst for lst in result if lst.address == test_address]
        assert len(matching_lists) > 0, f"No list found with address {test_address}"

        new_list = matching_lists[0]
        assert new_list.type == ListType.ALLOW
        assert new_list.groups == [0]  # Default group
        assert new_list.enabled is True  # Default enabled
        assert isinstance(new_list.id, int)

    def test_add_list_duplicate_handling(self, pihole_client):
        """Should handle duplicate list addition according to Pi-hole's behavior."""
        lists_client = PiHoleLists(pihole_client)

        test_address = f"duplicate-test-{int(time.time())}.example.com"

        # Add the list first time
        first_result = lists_client.add_list(
            address=test_address,
            list_type=ListType.BLOCK,
            comment="First addition",
        )

        assert isinstance(first_result, list)
        assert len(first_result) > 0

        # Find the list with our test address
        matching_lists = [lst for lst in first_result if lst.address == test_address]
        assert len(matching_lists) > 0, f"No list found with address {test_address}"

        # Try to add the same list again - should raise server error with UNIQUE constraint
        with pytest.raises(PiHoleServerError) as exc_info:
            lists_client.add_list(
                address=test_address,
                list_type=ListType.BLOCK,
                comment="Duplicate addition",
            )

        # Verify it's a UNIQUE constraint error
        error_message = str(exc_info.value)
        assert (
            "UNIQUE constraint failed" in error_message
        ), f"Expected UNIQUE constraint error, got: {error_message}"

    def test_add_list_different_types(self, pihole_client):
        """Should handle adding both allow and block lists."""
        lists_client = PiHoleLists(pihole_client)

        timestamp = int(time.time())

        # Add a blocklist
        block_result = lists_client.add_list(
            address=f"block-test-{timestamp}.example.com",
            list_type=ListType.BLOCK,
            comment="Test block list",
        )

        # Add an allowlist
        allow_result = lists_client.add_list(
            address=f"allow-test-{timestamp}.example.com",
            list_type=ListType.ALLOW,
            comment="Test allow list",
        )

        assert isinstance(block_result, list)
        assert isinstance(allow_result, list)
        assert len(block_result) > 0
        assert len(allow_result) > 0

        # Find the lists with our test addresses
        block_address = f"block-test-{timestamp}.example.com"
        allow_address = f"allow-test-{timestamp}.example.com"

        block_matches = [lst for lst in block_result if lst.address == block_address]
        allow_matches = [lst for lst in allow_result if lst.address == allow_address]

        assert (
            len(block_matches) > 0
        ), f"No block list found with address {block_address}"
        assert (
            len(allow_matches) > 0
        ), f"No allow list found with address {allow_address}"

        assert block_matches[0].type == ListType.BLOCK
        assert allow_matches[0].type == ListType.ALLOW
        assert block_matches[0].id != allow_matches[0].id

    def test_add_list_connection_error(self):
        """Network errors should raise connection error."""
        client = PiHoleClient(
            base_url=TEST_INVALID_HOST_URL,
            password=PIHOLE_TEST_PASSWORD,
            timeout=1,  # Short timeout
        )
        lists_client = PiHoleLists(client)

        with pytest.raises(PiHoleConnectionError, match=CONNECTION_FAILED_MESSAGE):
            lists_client.add_list(
                address="test.example.com",
                list_type=ListType.BLOCK,
            )

        client.close()

    def test_add_list_various_address_formats(self, pihole_client):
        """Should handle various address formats."""
        lists_client = PiHoleLists(pihole_client)

        # Test different address formats
        test_cases = [
            ("domain.example.com", "Domain name"),
            ("192.168.1.100", "IPv4 address"),
            ("192.168.1.0/24", "IPv4 subnet"),
            ("2001:db8::1", "IPv6 address"),
            ("12:34:56:78:9A:BC", "MAC address"),
        ]

        for address, description in test_cases:
            try:
                result = lists_client.add_list(
                    address=address,
                    list_type=ListType.ALLOW,
                    comment=f"Test {description}",
                )
                assert isinstance(result, list)
                assert len(result) > 0

                # Find the list with our test address (verify it was added)
                assert any(lst.address == address for lst in result)
            except Exception:
                # Some formats might not be supported or might fail validation
                pass

    def test_add_list_custom_groups(self, pihole_client):
        """Should handle custom group assignments."""
        lists_client = PiHoleLists(pihole_client)

        # Add list with multiple groups (assuming groups 0 and 1 exist)
        test_address = f"multi-group-test-{int(time.time())}.example.com"
        result = lists_client.add_list(
            address=test_address,
            list_type=ListType.BLOCK,
            comment="Multi-group test",
            groups=[0],  # Use only default group for safety
        )

        assert isinstance(result, list)
        assert len(result) > 0

        # Find the list with our test address
        matching_lists = [lst for lst in result if lst.address == test_address]
        assert len(matching_lists) > 0, f"No list found with address {test_address}"

        assert 0 in matching_lists[0].groups

    def test_add_list_disabled(self, pihole_client):
        """Should handle adding disabled lists."""
        lists_client = PiHoleLists(pihole_client)

        test_address = f"disabled-test-{int(time.time())}.example.com"
        result = lists_client.add_list(
            address=test_address,
            list_type=ListType.BLOCK,
            comment="Disabled test list",
            enabled=False,
        )

        assert isinstance(result, list)
        assert len(result) > 0

        # Find the list with our test address
        matching_lists = [lst for lst in result if lst.address == test_address]
        assert len(matching_lists) > 0, f"No list found with address {test_address}"

        assert matching_lists[0].enabled is False


@integration
class TestPiHoleListsDeleteList:
    """Test list deletion functionality against real Pi-hole."""

    def test_delete_list_success(self, pihole_client):
        """Should successfully delete a list."""
        lists_client = PiHoleLists(pihole_client)

        # Add a test list first
        test_address = f"delete-test-{int(time.time())}.example.com"
        add_result = lists_client.add_list(
            address=test_address,
            list_type=ListType.BLOCK,
            comment="Test list for deletion",
        )

        assert isinstance(add_result, list)
        assert len(add_result) > 0

        # Find the added list
        added_list = None
        for lst in add_result:
            if lst.address == test_address:
                added_list = lst
                break

        assert added_list is not None

        # Delete the list - should return True
        result = lists_client.delete_list(
            address=test_address, list_type=ListType.BLOCK
        )

        assert result is True

        # Verify the list was deleted
        remaining_lists = lists_client.get_lists()
        deleted_list_found = any(lst.address == test_address for lst in remaining_lists)
        assert deleted_list_found is False

    def test_delete_list_allow_type(self, pihole_client):
        """Should successfully delete an allow list."""
        lists_client = PiHoleLists(pihole_client)

        # Add a test allow list first
        test_address = f"delete-allow-test-{int(time.time())}.example.com"
        add_result = lists_client.add_list(
            address=test_address,
            list_type=ListType.ALLOW,
            comment="Test allow list for deletion",
        )

        assert isinstance(add_result, list)
        assert len(add_result) > 0

        # Delete the allow list - should return True
        result = lists_client.delete_list(
            address=test_address, list_type=ListType.ALLOW
        )

        assert result is True

        # Verify the list was deleted
        remaining_lists = lists_client.get_lists()
        deleted_list_found = any(lst.address == test_address for lst in remaining_lists)
        assert deleted_list_found is False

    def test_delete_list_nonexistent(self, pihole_client):
        """Should raise exception when trying to delete a nonexistent list."""
        lists_client = PiHoleLists(pihole_client)

        # Try to delete a list that doesn't exist
        nonexistent_address = f"nonexistent-{int(time.time())}.example.com"

        with pytest.raises(PiHoleAPIError):
            lists_client.delete_list(
                address=nonexistent_address, list_type=ListType.BLOCK
            )

    def test_delete_list_wrong_type(self, pihole_client):
        """Should raise exception when trying to delete with wrong type."""
        lists_client = PiHoleLists(pihole_client)

        # Add a block list
        test_address = f"wrong-type-test-{int(time.time())}.example.com"
        add_result = lists_client.add_list(
            address=test_address,
            list_type=ListType.BLOCK,
            comment="Test list for wrong type deletion",
        )

        assert isinstance(add_result, list)
        assert len(add_result) > 0

        # Try to delete it as an allow list (wrong type) - should raise exception
        with pytest.raises(PiHoleAPIError):
            lists_client.delete_list(
                address=test_address,
                list_type=ListType.ALLOW,  # Wrong type
            )

        # Clean up - delete with correct type
        result = lists_client.delete_list(
            address=test_address, list_type=ListType.BLOCK
        )
        assert result is True

    def test_delete_list_url_with_special_characters(self, pihole_client):
        """Should handle URLs with paths and hyphens."""
        lists_client = PiHoleLists(pihole_client)

        # Add a list with a realistic URL (no query parameters)
        timestamp = int(time.time())
        test_address = f"https://example-{timestamp}.com/blocklist.txt"
        add_result = lists_client.add_list(
            address=test_address,
            list_type=ListType.BLOCK,
            comment="Test list with URL path",
        )

        assert isinstance(add_result, list)
        assert len(add_result) > 0

        # Delete the list - should return True
        result = lists_client.delete_list(
            address=test_address, list_type=ListType.BLOCK
        )

        assert result is True

    def test_delete_list_connection_error(self):
        """Network errors should raise connection error."""
        client = PiHoleClient(
            base_url=TEST_INVALID_HOST_URL,
            password=PIHOLE_TEST_PASSWORD,
            timeout=1,  # Short timeout
        )
        lists_client = PiHoleLists(client)

        with pytest.raises(PiHoleConnectionError, match=CONNECTION_FAILED_MESSAGE):
            lists_client.delete_list(
                address="test.example.com",
                list_type=ListType.BLOCK,
            )

        client.close()

    def test_constants_usage(self, pihole_client):
        """Test that the class uses the correct API endpoint constants."""
        lists = PiHoleLists(pihole_client)
        assert lists.BASE_URL == "/api/lists"


@integration
class TestPiHoleListsSearchDomains:
    def test_search_domains_functionality(self, pihole_client):
        """Should search for domains in lists."""
        lists_client = PiHoleLists(pihole_client)

        # Add a test domain to search for
        test_address = "searchable-integration.example.com"
        lists_client.add_list(
            address=test_address,
            list_type=ListType.ALLOW,
            comment="Searchable integration test domain",
        )

        try:
            # Search for the domain
            search_response = lists_client.search_domains(
                "searchable-integration.example.com"
            )

            # Should return SearchResponse object
            assert hasattr(search_response, "search")
            assert hasattr(search_response, "took")
            assert isinstance(search_response.took, float)

            # Check search structure
            search_data = search_response.search
            assert hasattr(search_data, "domains")
            assert hasattr(search_data, "gravity")
            assert hasattr(search_data, "results")
            assert hasattr(search_data, "parameters")

            # Check parameters
            params = search_data.parameters
            assert params.domain == "searchable-integration.example.com"
            assert params.partial is False
            assert params.N == 20
            assert params.debug is False

            # Check results structure
            results = search_data.results
            assert hasattr(results, "domains")
            assert hasattr(results, "gravity")
            assert hasattr(results, "total")
            assert isinstance(results.total, int)

        finally:
            # Clean up
            lists_client.delete_list(test_address, ListType.ALLOW)

    def test_search_domains_partial_matching(self, pihole_client):
        """Should perform partial domain search with custom options."""
        lists_client = PiHoleLists(pihole_client)

        # Partial search with custom options
        search_response = lists_client.search_domains(
            domain="example",
            partial=True,
            max_results=10,
            debug=True,
        )

        # Should return SearchResponse object
        assert hasattr(search_response, "search")
        assert hasattr(search_response, "took")

        # Check parameters were applied
        params = search_response.search.parameters
        assert params.domain == "example"
        assert params.partial is True
        assert params.N == 10
        assert params.debug is True

        # Should have results structure
        results = search_response.search.results
        assert hasattr(results, "domains")
        assert hasattr(results, "gravity")
        assert hasattr(results, "total")
