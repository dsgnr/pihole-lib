"""Pi-hole Groups management."""

from urllib.parse import quote

from pihole_lib.base import BasePiHoleAPIClient
from pihole_lib.models.groups import Group, GroupRequest, GroupsResponse
from pihole_lib.utils import check_api_errors, make_pihole_request


class PiHoleGroups(BasePiHoleAPIClient):
    """Pi-hole Groups management client.

    Provides methods to create, read, update, and delete groups.

    Examples::

        from pihole_lib import PiHoleClient

        with PiHoleClient("http://192.168.1.100", password="secret") as client:
            # Get all groups
            all_groups = client.groups.get_groups()
            for group in all_groups:
                print(f"Group: {group.name}")

            # Create a new group
            client.groups.create_group(name="family_devices", comment="Family")

            # Delete a group
            client.groups.delete_group("family_devices")

    """

    BASE_URL = "/api/groups"

    def get_groups(self, name: str | None = None) -> list[Group]:
        """Get groups from Pi-hole.

        Args:
            name: Optional group name to filter by.

        Returns:
            List of Group objects.
        """
        endpoint = self.BASE_URL
        if name:
            encoded_name = quote(name, safe="")
            endpoint = f"{self.BASE_URL}/{encoded_name}"

        response = make_pihole_request(self._client, "GET", endpoint)
        return GroupsResponse.model_validate(response.json()).groups

    def create_group(
        self,
        name: str,
        comment: str | None = None,
        enabled: bool = True,
    ) -> list[Group]:
        """Create a new group.

        Args:
            name: Group name.
            comment: Optional comment for the group.
            enabled: Whether the group should be enabled. Defaults to True.

        Returns:
            List of Group objects returned by the API.
        """
        request_data = GroupRequest(name=name, comment=comment, enabled=enabled)
        response = make_pihole_request(
            self._client,
            "POST",
            self.BASE_URL,
            json=request_data.model_dump(exclude_none=True),
        )
        response_data = response.json()
        check_api_errors(response_data, name, "create group")
        return [Group.model_validate(g) for g in response_data["groups"]]

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
            GroupsResponse containing the updated group.
        """
        encoded_name = quote(name, safe="")
        request_data = GroupRequest(
            name=new_name or name,
            comment=comment,
            enabled=enabled,
        )
        response = make_pihole_request(
            self._client,
            "PUT",
            f"{self.BASE_URL}/{encoded_name}",
            json=request_data.model_dump(exclude_none=True),
        )
        return GroupsResponse.model_validate(response.json())

    def delete_group(self, name: str) -> bool:
        """Delete a group.

        Args:
            name: Name of the group to delete.

        Returns:
            True if the group was deleted successfully.
        """
        encoded_name = quote(name, safe="")
        response = make_pihole_request(
            self._client,
            "DELETE",
            f"{self.BASE_URL}/{encoded_name}",
        )
        return bool(response.status_code == 204)
