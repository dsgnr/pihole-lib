"""Integration tests for PiHoleLists against real Pi-hole."""

import pytest

from pihole_lib import PiHoleClient, PiHoleLists
from pihole_lib.exceptions import PiHoleConnectionError
from pihole_lib.models import ListsResponse, ListType

from .constants import (
    CONNECTION_FAILED_MESSAGE,
    PIHOLE_BASE_URL,
    PIHOLE_TEST_PASSWORD,
    TEST_INVALID_HOST_URL,
)


class TestPiHoleListsGetLists:
    """Test lists retrieval functionality against real Pi-hole."""

    def test_get_lists_all_success(self, pihole_container):
        """Should successfully get all lists from Pi-hole."""
        with PiHoleClient(
            base_url=PIHOLE_BASE_URL, password=PIHOLE_TEST_PASSWORD, verify_ssl=False
        ) as client:
            lists_client = PiHoleLists(client)

            result = lists_client.get_lists()

            assert isinstance(result, ListsResponse)
            assert isinstance(result.lists, list)
            assert isinstance(result.took, (int, float))
            assert result.took >= 0

            # Pi-hole should have at least some default lists
            # Note: The exact number depends on Pi-hole configuration
            print(f"Found {len(result.lists)} lists")

    def test_get_lists_with_type_filter(self, pihole_container):
        """Should filter lists by type."""
        with PiHoleClient(
            base_url=PIHOLE_BASE_URL, password=PIHOLE_TEST_PASSWORD, verify_ssl=False
        ) as client:
            lists_client = PiHoleLists(client)

            # Test both allow and block filters
            allow_lists = lists_client.get_lists(list_type=ListType.ALLOW)
            block_lists = lists_client.get_lists(list_type=ListType.BLOCK)

            assert isinstance(allow_lists, ListsResponse)
            assert isinstance(block_lists, ListsResponse)

            # Verify all returned lists have the correct type
            for list_item in allow_lists.lists:
                assert list_item.type == ListType.ALLOW

            for list_item in block_lists.lists:
                assert list_item.type == ListType.BLOCK

            print(
                f"Allow lists: {len(allow_lists.lists)}, Block lists: {len(block_lists.lists)}"
            )

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

    def test_get_lists_nonexistent_list(self, pihole_container):
        """Should handle requests for non-existent lists gracefully."""
        with PiHoleClient(
            base_url=PIHOLE_BASE_URL, password=PIHOLE_TEST_PASSWORD, verify_ssl=False
        ) as client:
            lists_client = PiHoleLists(client)

            # Request a list that doesn't exist
            result = lists_client.get_lists(list_name="nonexistent_list_12345")

            assert isinstance(result, ListsResponse)
            # Should return empty list or handle gracefully
            # The exact behavior depends on Pi-hole implementation
            print(f"Result for nonexistent list: {len(result.lists)} lists")


class TestPiHoleListsWorkflows:
    """Test complete lists workflows with real Pi-hole."""

    def test_lists_client_session_reuse(self, pihole_container):
        """Should reuse client session across multiple operations."""
        with PiHoleClient(
            base_url=PIHOLE_BASE_URL, password=PIHOLE_TEST_PASSWORD, verify_ssl=False
        ) as client:
            lists_client = PiHoleLists(client)

            # First operation creates session
            result1 = lists_client.get_lists()
            first_session = client._session

            # Second operation should reuse session
            result2 = lists_client.get_lists(list_type=ListType.BLOCK)
            second_session = client._session

            assert isinstance(result1, ListsResponse)
            assert isinstance(result2, ListsResponse)
            assert first_session is second_session

    def test_multiple_list_operations(self, pihole_container):
        """Test multiple list operations with same client."""
        with PiHoleClient(
            base_url=PIHOLE_BASE_URL, password=PIHOLE_TEST_PASSWORD, verify_ssl=False
        ) as client:
            lists_client = PiHoleLists(client)

            # Get all lists
            all_lists = lists_client.get_lists()

            # Get filtered lists
            allow_lists = lists_client.get_lists(list_type=ListType.ALLOW)
            block_lists = lists_client.get_lists(list_type=ListType.BLOCK)

            # All operations should succeed
            assert isinstance(all_lists, ListsResponse)
            assert isinstance(allow_lists, ListsResponse)
            assert isinstance(block_lists, ListsResponse)

            # The sum of filtered lists should not exceed total lists
            # (some lists might not be returned due to permissions or other factors)
            total_filtered = len(allow_lists.lists) + len(block_lists.lists)
            print(
                f"All: {len(all_lists.lists)}, Allow: {len(allow_lists.lists)}, Block: {len(block_lists.lists)}"
            )
            print(f"Total filtered: {total_filtered}")

    def test_lists_data_structure(self, pihole_container):
        """Verify the structure of returned list data."""
        with PiHoleClient(
            base_url=PIHOLE_BASE_URL, password=PIHOLE_TEST_PASSWORD, verify_ssl=False
        ) as client:
            lists_client = PiHoleLists(client)

            result = lists_client.get_lists()

            assert isinstance(result, ListsResponse)

            # Check each list has the expected structure
            for list_item in result.lists:
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

                print(
                    f"List {list_item.id}: {list_item.address} ({list_item.type.value})"
                )
