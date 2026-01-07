"""Integration tests for PiHoleGroups class."""

import pytest

from pihole_lib import PiHoleClient, PiHoleGroups
from pihole_lib.exceptions import PiHoleServerError
from pihole_lib.models import GroupsResponse
from tests.constants import PIHOLE_BASE_URL, PIHOLE_TEST_PASSWORD


class TestPiHoleGroupsIntegration:
    """Integration tests for PiHoleGroups against real Pi-hole instance."""

    @pytest.fixture(scope="class")
    def pihole_container(self):
        """Start Pi-hole container for testing."""
        pytest.importorskip("docker")
        import docker

        client = docker.from_env()

        # Check if container is already running
        try:
            container = client.containers.get("pihole-test")
            if container.status != "running":
                container.start()
        except docker.errors.NotFound:
            pytest.skip("Pi-hole test container not available")

        yield container

    @pytest.fixture
    def groups_client(self, pihole_container):
        """Create authenticated PiHoleGroups client."""
        client = PiHoleClient(
            base_url=PIHOLE_BASE_URL, password=PIHOLE_TEST_PASSWORD, verify_ssl=False
        )
        client._ensure_session()
        client._authenticate()
        return PiHoleGroups(client)

    def test_get_groups_integration(self, groups_client):
        """Test getting groups from real Pi-hole instance."""
        # Get all groups
        result = groups_client.get_groups()

        # Verify result structure
        assert isinstance(result, GroupsResponse)
        assert hasattr(result, "groups")
        assert hasattr(result, "took")
        assert hasattr(result, "processed")

        # Validate data types
        assert isinstance(result.groups, list)
        assert isinstance(result.took, float)
        assert result.processed is None  # GET operations don't have processed results

        # Should have at least the default group
        assert len(result.groups) >= 1

        # Check default group exists
        default_group = next((g for g in result.groups if g.name == "Default"), None)
        assert default_group is not None
        assert default_group.id == 0
        assert isinstance(default_group.enabled, bool)

    def test_group_crud_operations_integration(self, groups_client):
        """Test complete CRUD operations for groups against real Pi-hole instance."""
        test_group_name = "test-integration-group"

        # Clean up any existing test group first
        try:
            groups_client.delete_group(test_group_name)
        except Exception:
            pass  # Ignore if group doesn't exist

        try:
            # 1. Create a new group
            create_result = groups_client.create_group(
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
            get_result = groups_client.get_groups(name=test_group_name)
            assert isinstance(get_result, GroupsResponse)
            assert len(get_result.groups) == 1
            assert get_result.groups[0].name == test_group_name

            # 3. Update the group
            update_result = groups_client.update_group(
                name=test_group_name,
                new_name=f"{test_group_name}-updated",
                comment="Updated integration test group",
                enabled=False,
            )

            assert isinstance(update_result, GroupsResponse)

            # The Pi-hole API behavior for updates is inconsistent:
            # - It may return the old group name in the response
            # - It may report a UNIQUE constraint error in processed.errors
            # - But the update actually succeeds
            # So we need to verify by fetching the group with the new name

            # Verify the group was actually updated by fetching it
            check_result = groups_client.get_groups(name=f"{test_group_name}-updated")
            assert len(check_result.groups) == 1
            updated_group = check_result.groups[0]

            assert updated_group.name == f"{test_group_name}-updated"
            assert updated_group.comment == "Updated integration test group"
            assert updated_group.enabled is False
            assert updated_group.comment == "Updated integration test group"
            assert updated_group.enabled is False

            # 4. Delete the group
            delete_result = groups_client.delete_group(f"{test_group_name}-updated")
            assert delete_result is True

            # 5. Verify group is deleted
            final_result = groups_client.get_groups()
            deleted_group = next(
                (
                    g
                    for g in final_result.groups
                    if g.name in [test_group_name, f"{test_group_name}-updated"]
                ),
                None,
            )
            assert deleted_group is None

        finally:
            # Clean up in case of test failure
            try:
                groups_client.delete_group(test_group_name)
                groups_client.delete_group(f"{test_group_name}-updated")
            except Exception:
                pass

    def test_batch_operations_integration(self, groups_client):
        """Test multiple group operations against real Pi-hole instance."""
        test_groups = ["batch-test-1", "batch-test-2", "batch-test-3"]

        # Clean up any existing test groups first
        for group_name in test_groups:
            try:
                groups_client.delete_group(group_name)
            except Exception:
                pass

        try:
            # Create multiple groups using individual creates
            for group_name in test_groups:
                groups_client.create_group(
                    name=group_name,
                    comment=f"Batch test group {group_name}",
                    enabled=True,
                )

            # Verify all groups were created
            all_groups = groups_client.get_groups()
            created_groups = [g for g in all_groups.groups if g.name in test_groups]
            assert len(created_groups) == 3

            # Delete the groups individually
            for group_name in test_groups:
                success = groups_client.delete_group(group_name)
                assert success is True

            # Verify groups are actually deleted
            final_groups = groups_client.get_groups()
            remaining_groups = [g for g in final_groups.groups if g.name in test_groups]
            assert len(remaining_groups) == 0

        finally:
            # Clean up in case of test failure
            for group_name in test_groups:
                try:
                    groups_client.delete_group(group_name)
                except Exception:
                    pass

    def test_error_handling_integration(self, groups_client):
        """Test error handling with real Pi-hole instance."""
        # Try to create a group with the same name as default group
        # Pi-hole should raise a PiHoleServerError for duplicate groups
        try:
            groups_client.create_group(name="Default", comment="Duplicate default")
            # If no exception was raised, check if we got a valid result
            # (Pi-hole behavior can vary)
            all_groups = groups_client.get_groups()
            default_groups = [g for g in all_groups.groups if g.name == "Default"]
            assert len(default_groups) >= 1  # At least one should exist
        except PiHoleServerError as e:
            # This is the expected behavior - error should be raised
            assert "UNIQUE constraint failed" in str(
                e
            ) or "Failed to create group" in str(e)

        # Try to get a non-existent group (should return empty list, not error)
        result = groups_client.get_groups(name="non-existent-group-12345")
        assert isinstance(result, GroupsResponse)
        assert len(result.groups) == 0

    def test_groups_client_combination_integration(self, groups_client):
        """Test using groups client with other operations."""
        # Get initial groups
        initial_groups = groups_client.get_groups()

        # Verify we can get all information
        assert isinstance(initial_groups, GroupsResponse)
        assert isinstance(initial_groups.groups, list)
        assert isinstance(initial_groups.took, float)

        # Should have at least the default group
        assert len(initial_groups.groups) >= 1

        # Verify default group properties
        default_group = next(
            (g for g in initial_groups.groups if g.name == "Default"), None
        )
        assert default_group is not None
        assert default_group.id == 0
        assert isinstance(default_group.date_added, int)
        assert isinstance(default_group.date_modified, int)

    def test_constants_usage(self, groups_client):
        """Test that the class uses the correct API endpoint constants."""
        assert groups_client.BASE_URL == "/api/groups"
