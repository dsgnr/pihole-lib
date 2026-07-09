"""Integration tests for PiHoleGroups."""

from pihole_lib import PiHoleGroups
from pihole_lib.exceptions import PiHoleAPIError
from pihole_lib.models.groups import GroupsResponse
from tests.conftest import integration


@integration
class TestPiHoleGroupsIntegration:
    """Integration tests for PiHoleGroups against real Pi-hole instance."""

    def test_get_groups_integration(self, pihole_client):
        """Test getting groups from real Pi-hole instance."""
        groups = PiHoleGroups(pihole_client)

        # Get all groups
        result = groups.get_groups()

        # Verify result structure
        assert isinstance(result, list)

        # Should have at least the default group
        assert len(result) >= 1

        # Check default group exists
        default_group = next((g for g in result if g.name == "Default"), None)
        assert default_group is not None
        assert default_group.id == 0
        assert isinstance(default_group.enabled, bool)

    def test_group_crud_operations_integration(self, pihole_client):
        """Test complete CRUD operations for groups against real Pi-hole instance."""
        groups = PiHoleGroups(pihole_client)
        test_group_name = "test-integration-group"

        # Clean up any existing test group first
        try:
            groups.delete_group(test_group_name)
        except Exception:
            pass  # Ignore if group doesn't exist

        try:
            # 1. Create a new group
            create_result = groups.create_group(
                name=test_group_name,
                comment="Integration test group",
                enabled=True,
            )

            assert isinstance(create_result, list)
            assert len(create_result) >= 1

            # Find our created group
            created_group = next(
                (g for g in create_result if g.name == test_group_name), None
            )
            assert created_group is not None
            assert created_group.name == test_group_name
            assert created_group.comment == "Integration test group"
            assert created_group.enabled is True
            assert isinstance(created_group.id, int)

            # 2. Read the group back
            get_result = groups.get_groups(name=test_group_name)
            assert isinstance(get_result, list)
            assert len(get_result) == 1
            assert get_result[0].name == test_group_name

            # 3. Update the group
            update_result = groups.update_group(
                name=test_group_name,
                new_name=f"{test_group_name}-updated",
                comment="Updated integration test group",
                enabled=False,
            )

            assert isinstance(update_result, GroupsResponse)

            # Verify the group was actually updated by fetching it
            check_result = groups.get_groups(name=f"{test_group_name}-updated")
            assert len(check_result) == 1
            updated_group = check_result[0]

            assert updated_group.name == f"{test_group_name}-updated"
            assert updated_group.comment == "Updated integration test group"
            assert updated_group.enabled is False

            # 4. Delete the group
            delete_result = groups.delete_group(f"{test_group_name}-updated")
            assert delete_result is True

            # 5. Verify group is deleted
            final_result = groups.get_groups()
            deleted_group = next(
                (
                    g
                    for g in final_result
                    if g.name in [test_group_name, f"{test_group_name}-updated"]
                ),
                None,
            )
            assert deleted_group is None

        finally:
            # Clean up in case of test failure
            try:
                groups.delete_group(test_group_name)
                groups.delete_group(f"{test_group_name}-updated")
            except Exception:
                pass

    def test_batch_operations_integration(self, pihole_client):
        """Test multiple group operations against real Pi-hole instance."""
        groups = PiHoleGroups(pihole_client)
        test_groups = ["batch-test-1", "batch-test-2", "batch-test-3"]

        # Clean up any existing test groups first
        for group_name in test_groups:
            try:
                groups.delete_group(group_name)
            except Exception:
                pass

        try:
            # Create multiple groups using individual creates
            for group_name in test_groups:
                groups.create_group(
                    name=group_name,
                    comment=f"Batch test group {group_name}",
                    enabled=True,
                )

            # Verify all groups were created
            all_groups = groups.get_groups()
            created_groups = [g for g in all_groups if g.name in test_groups]
            assert len(created_groups) == 3

            # Delete the groups individually
            for group_name in test_groups:
                success = groups.delete_group(group_name)
                assert success is True

            # Verify groups are actually deleted
            final_groups = groups.get_groups()
            remaining_groups = [g for g in final_groups if g.name in test_groups]
            assert len(remaining_groups) == 0

        finally:
            # Clean up in case of test failure
            for group_name in test_groups:
                try:
                    groups.delete_group(group_name)
                except Exception:
                    pass

    def test_error_handling_integration(self, pihole_client):
        """Test error handling with real Pi-hole instance."""
        groups = PiHoleGroups(pihole_client)

        # Try to create a group with the same name as default group.
        # Pi-hole surfaces the UNIQUE constraint violation as HTTP 400
        # ("Could not add to gravity database"), which the library maps
        # to PiHoleAPIError.
        try:
            groups.create_group(name="Default", comment="Duplicate default")
            # If no exception was raised, check if we got a valid result
            # (Pi-hole behavior can vary)
            all_groups = groups.get_groups()
            default_groups = [g for g in all_groups if g.name == "Default"]
            assert len(default_groups) >= 1  # At least one should exist
        except PiHoleAPIError as e:
            # Expected behavior: the API rejects the duplicate.
            message = str(e)
            assert (
                "UNIQUE constraint failed" in message
                or "Failed to create group" in message
                or "Could not add to gravity database" in message
            )

        # Try to get a non-existent group (should return empty list, not error)
        result = groups.get_groups(name="non-existent-group-12345")
        assert isinstance(result, list)
        assert len(result) == 0

    def test_groups_client_combination_integration(self, pihole_client):
        """Test using groups client with other operations."""
        groups = PiHoleGroups(pihole_client)

        # Get initial groups
        initial_groups = groups.get_groups()

        # Verify we can get all information
        assert isinstance(initial_groups, list)

        # Should have at least the default group
        assert len(initial_groups) >= 1

        # Verify default group properties
        default_group = next((g for g in initial_groups if g.name == "Default"), None)
        assert default_group is not None
        assert default_group.id == 0
        assert isinstance(default_group.date_added, int)
        assert isinstance(default_group.date_modified, int)

    def test_constants_usage(self, pihole_client):
        """Test that the class uses the correct API endpoint constants."""
        groups = PiHoleGroups(pihole_client)
        assert groups.BASE_URL == "/api/groups"
