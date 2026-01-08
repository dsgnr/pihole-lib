"""Pi-hole Groups management."""

from urllib.parse import quote

from .base import BasePiHoleAPIClient
from .models import (
    Group,
    GroupRequest,
    GroupsResponse,
)
from .utils import check_api_errors, make_pihole_request


class PiHoleGroups(BasePiHoleAPIClient):
    """Pi-hole Groups management client.

    This class provides methods to interact with Pi-hole's groups functionality,
    including creating, reading, updating, and deleting groups.

    Uses a PiHoleClient instance for making authenticated requests.

    Examples::

        from pihole_lib import PiHoleClient, PiHoleGroups

        with PiHoleClient("http://192.168.1.100", password="secret") as client:
            groups = PiHoleGroups(client)

            # Get all groups
            all_groups = groups.get_groups()
            for group in all_groups.groups:
                print(f"Group: {group.name} (ID: {group.id})")

            # Create a new group
            new_group = groups.create_group(
                name="test_group",
                comment="Test group for development",
                enabled=True
            )
            print(f"Created group: {new_group.groups[0].name}")

            # Update a group
            updated_group = groups.update_group(
                name="test_group",
                new_name="updated_group",
                comment="Updated comment",
                enabled=False
            )

            # Delete a group
            success = groups.delete_group("updated_group")
            print(f"Group deleted: {success}")

    """

    BASE_URL = "/api/groups"

    def get_groups(self, name: str | None = None) -> GroupsResponse:
        """Get groups from Pi-hole.

        Args:
            name: Optional group name to filter by. If provided, only the
                 specified group will be returned.

        Returns:
            GroupsResponse: Response containing groups and metadata.

        Raises:
            PiHoleConnectionError: If connection to Pi-hole fails.
            PiHoleAuthenticationError: If authentication fails.
            PiHoleAPIError: If the API request fails.

        Examples::

            # Get all groups
            all_groups = groups.get_groups()
            print(f"Found {len(all_groups.groups)} groups")

            # Get specific group
            specific_group = groups.get_groups(name="test_group")
            if specific_group.groups:
                group = specific_group.groups[0]
                print(f"Group: {group.name}, Enabled: {group.enabled}")

        """
        endpoint = self.BASE_URL
        if name:
            encoded_name = quote(name, safe="")
            endpoint = f"{self.BASE_URL}/{encoded_name}"

        response = make_pihole_request(
            self._client,
            "GET",
            endpoint,
        )
        return GroupsResponse.model_validate(response.json())

    def create_group(
        self,
        name: str,
        comment: str | None = None,
        enabled: bool = True,
    ) -> list[Group]:
        """Create a new group.

        Args:
            name: Group name.
            comment: Optional user-provided comment for the group.
            enabled: Whether the group should be enabled. Defaults to True.

        Returns:
            List of Group objects returned by the API.

        Raises:
            PiHoleConnectionError: If connection to Pi-hole fails.
            PiHoleAuthenticationError: If authentication fails.
            PiHoleServerError: If Pi-hole reports an error (e.g., group already exists).
            PiHoleAPIError: If the API request fails.

        Examples::

            # Create a simple group
            groups_list = groups.create_group("new_group")
            print(f"Created group: {groups_list[0].name}")

            # Create a group with comment
            groups_list = groups.create_group(
                name="family_devices",
                comment="Devices used by family members",
                enabled=True
            )

        """
        group_request = GroupRequest(
            name=name,
            comment=comment,
            enabled=enabled,
        )

        response = make_pihole_request(
            self._client,
            "POST",
            self.BASE_URL,
            json=group_request.model_dump(exclude_none=True),
        )

        response_data = response.json()

        # Check for Pi-hole errors in the response
        check_api_errors(response_data, name, "create group")

        # Optimize model creation
        groups_data = response_data["groups"]
        return [Group.model_validate(group_data) for group_data in groups_data]

    def update_group(
        self,
        name: str,
        new_name: str | None = None,
        comment: str | None = None,
        enabled: bool = True,
    ) -> GroupsResponse:
        """Update an existing group.

        Args:
            name: Current name of the group to update.
            new_name: New name for the group. If None, keeps current name.
            comment: New comment for the group.
            enabled: Whether the group should be enabled.

        Returns:
            GroupsResponse: Response containing the updated group and metadata.

        Raises:
            PiHoleConnectionError: If connection to Pi-hole fails.
            PiHoleAuthenticationError: If authentication fails.
            PiHoleAPIError: If the API request fails (e.g., group not found).

        Examples::

            # Update group name
            result = groups.update_group("old_name", new_name="new_name")

            # Update group comment and status
            result = groups.update_group(
                name="test_group",
                comment="Updated comment",
                enabled=False
            )

        """
        encoded_name = quote(name, safe="")

        group_request = GroupRequest(
            name=new_name or name,
            comment=comment,
            enabled=enabled,
        )

        response = make_pihole_request(
            self._client,
            "PUT",
            f"{self.BASE_URL}/{encoded_name}",
            json=group_request.model_dump(exclude_none=True),
        )
        return GroupsResponse.model_validate(response.json())

    def delete_group(self, name: str) -> bool:
        """Delete a group.

        Args:
            name: Name of the group to delete.

        Returns:
            True if the group was deleted successfully.

        Raises:
            PiHoleConnectionError: If connection to Pi-hole fails.
            PiHoleAuthenticationError: If authentication fails.
            PiHoleAPIError: If the API request fails (e.g., group not found).

        Examples::

            # Delete a group
            success = groups.delete_group("test_group")
            if success:
                print("Group deleted successfully")

        """
        encoded_name = quote(name, safe="")

        response = make_pihole_request(
            self._client,
            "DELETE",
            f"{self.BASE_URL}/{encoded_name}",
        )
        # DELETE returns 204 No Content on success
        return response.status_code == 204
