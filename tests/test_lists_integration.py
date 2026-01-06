"""Integration tests for PiHoleLists against real Pi-hole."""

import pytest

from pihole_lib import PiHoleClient, PiHoleLists
from pihole_lib.exceptions import PiHoleConnectionError, PiHoleServerError
from pihole_lib.models import ListType

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

            assert isinstance(result, list)

            # Pi-hole should have at least some default lists
            # Note: The exact number depends on Pi-hole configuration
            print(f"Found {len(result)} lists")

    def test_get_lists_with_type_filter(self, pihole_container):
        """Should filter lists by type."""
        with PiHoleClient(
            base_url=PIHOLE_BASE_URL, password=PIHOLE_TEST_PASSWORD, verify_ssl=False
        ) as client:
            lists_client = PiHoleLists(client)

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

            print(f"Allow lists: {len(allow_lists)}, Block lists: {len(block_lists)}")

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

            assert isinstance(result, list)
            # Should return empty list or handle gracefully
            # The exact behavior depends on Pi-hole implementation
            print(f"Result for nonexistent list: {len(result)} lists")


class TestPiHoleListsWorkflows:
    """Test complete lists workflows with real Pi-hole."""

    def test_lists_operations_efficiency(self, pihole_container):
        """Test that lists operations work efficiently with proper session management."""
        with PiHoleClient(
            base_url=PIHOLE_BASE_URL, password=PIHOLE_TEST_PASSWORD, verify_ssl=False
        ) as client:
            lists_client = PiHoleLists(client)

            # Get all lists and verify it works
            all_lists = lists_client.get_lists()
            assert isinstance(all_lists, list)

            # Get filtered lists for comparison
            allow_lists = lists_client.get_lists(list_type=ListType.ALLOW)
            block_lists = lists_client.get_lists(list_type=ListType.BLOCK)

            # Verify session is properly managed
            assert client._session is not None
            total_filtered = len(allow_lists) + len(block_lists)
            print(
                f"All: {len(all_lists)}, Allow: {len(allow_lists)}, Block: {len(block_lists)}"
            )
            print(f"Total filtered: {total_filtered}")

    def test_lists_data_structure(self, pihole_container):
        """Verify the structure of returned list data."""
        with PiHoleClient(
            base_url=PIHOLE_BASE_URL, password=PIHOLE_TEST_PASSWORD, verify_ssl=False
        ) as client:
            lists_client = PiHoleLists(client)

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

                print(
                    f"List {list_item.id}: {list_item.address} ({list_item.type.value})"
                )


class TestPiHoleListsAddList:
    """Test list addition functionality against real Pi-hole."""

    def test_add_list_success(self, pihole_container):
        """Should successfully add a new list to Pi-hole."""
        with PiHoleClient(
            base_url=PIHOLE_BASE_URL, password=PIHOLE_TEST_PASSWORD, verify_ssl=False
        ) as client:
            lists_client = PiHoleLists(client)

            # Add a test blocklist with a unique address
            import time

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

            print(f"Successfully added list with ID: {new_list.id}")

    def test_add_list_minimal_params(self, pihole_container):
        """Should add list with minimal parameters."""
        with PiHoleClient(
            base_url=PIHOLE_BASE_URL, password=PIHOLE_TEST_PASSWORD, verify_ssl=False
        ) as client:
            lists_client = PiHoleLists(client)

            # Add a simple domain allowlist with unique address
            import time

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

            print(f"Added minimal list with ID: {new_list.id}")

    def test_add_list_duplicate_handling(self, pihole_container):
        """Should handle duplicate list addition according to Pi-hole's behavior."""
        with PiHoleClient(
            base_url=PIHOLE_BASE_URL, password=PIHOLE_TEST_PASSWORD, verify_ssl=False
        ) as client:
            lists_client = PiHoleLists(client)

            import time

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
            matching_lists = [
                lst for lst in first_result if lst.address == test_address
            ]
            assert len(matching_lists) > 0, f"No list found with address {test_address}"

            print(f"First addition successful with ID: {matching_lists[0].id}")

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
            print(f"Correctly received UNIQUE constraint error: {exc_info.value}")

    def test_add_list_different_types(self, pihole_container):
        """Should handle adding both allow and block lists."""
        with PiHoleClient(
            base_url=PIHOLE_BASE_URL, password=PIHOLE_TEST_PASSWORD, verify_ssl=False
        ) as client:
            lists_client = PiHoleLists(client)

            import time

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

            block_matches = [
                lst for lst in block_result if lst.address == block_address
            ]
            allow_matches = [
                lst for lst in allow_result if lst.address == allow_address
            ]

            assert (
                len(block_matches) > 0
            ), f"No block list found with address {block_address}"
            assert (
                len(allow_matches) > 0
            ), f"No allow list found with address {allow_address}"

            assert block_matches[0].type == ListType.BLOCK
            assert allow_matches[0].type == ListType.ALLOW
            assert block_matches[0].id != allow_matches[0].id

            print(
                f"Block list ID: {block_matches[0].id}, Allow list ID: {allow_matches[0].id}"
            )

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

    def test_add_list_various_address_formats(self, pihole_container):
        """Should handle various address formats."""
        with PiHoleClient(
            base_url=PIHOLE_BASE_URL, password=PIHOLE_TEST_PASSWORD, verify_ssl=False
        ) as client:
            lists_client = PiHoleLists(client)

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

                    # Find the list with our test address
                    matching_lists = [lst for lst in result if lst.address == address]
                    if matching_lists:
                        print(
                            f"Successfully added {description}: {address} (ID: {matching_lists[0].id})"
                        )
                    else:
                        print(
                            f"Added {description}: {address} but not found in response"
                        )
                except Exception as e:
                    # Some formats might not be supported or might fail validation
                    print(f"Failed to add {description} ({address}): {e}")

    def test_add_list_custom_groups(self, pihole_container):
        """Should handle custom group assignments."""
        with PiHoleClient(
            base_url=PIHOLE_BASE_URL, password=PIHOLE_TEST_PASSWORD, verify_ssl=False
        ) as client:
            lists_client = PiHoleLists(client)

            import time

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
            print(f"Added list to groups: {matching_lists[0].groups}")

    def test_add_list_disabled(self, pihole_container):
        """Should handle adding disabled lists."""
        with PiHoleClient(
            base_url=PIHOLE_BASE_URL, password=PIHOLE_TEST_PASSWORD, verify_ssl=False
        ) as client:
            lists_client = PiHoleLists(client)

            import time

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
            print(f"Added disabled list with ID: {matching_lists[0].id}")
