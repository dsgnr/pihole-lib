"""Unit tests for PiHoleGroups."""

from unittest.mock import patch

import pytest

from pihole_lib.exceptions import PiHoleServerError
from pihole_lib.groups import PiHoleGroups
from pihole_lib.models.groups import Group, GroupsResponse
from tests.conftest import SAMPLE_GROUP_DATA, make_mock_response


@pytest.fixture
def groups_client(mock_client):
    """Create a PiHoleGroups instance with mock client."""
    return PiHoleGroups(mock_client)


class TestPiHoleGroups:
    """Test cases for PiHoleGroups class."""

    @patch("pihole_lib.groups.make_pihole_request")
    def test_get_groups_all(self, mock_request, groups_client):
        """Test getting all groups."""
        mock_request.return_value = make_mock_response(
            json_data={
                "groups": [
                    SAMPLE_GROUP_DATA,
                    {**SAMPLE_GROUP_DATA, "name": "test_group", "id": 1},
                ],
                "took": 0.003,
                "processed": None,
            }
        )

        result = groups_client.get_groups()

        mock_request.assert_called_once_with(
            groups_client._client, "GET", groups_client.BASE_URL
        )
        assert isinstance(result, list)
        assert len(result) == 2
        assert result[0].name == "Default"

    @patch("pihole_lib.groups.make_pihole_request")
    def test_get_groups_specific(self, mock_request, groups_client):
        """Test getting a specific group."""
        mock_request.return_value = make_mock_response(
            json_data={
                "groups": [{**SAMPLE_GROUP_DATA, "name": "test_group"}],
                "took": 0.002,
                "processed": None,
            }
        )

        result = groups_client.get_groups(name="test_group")

        mock_request.assert_called_once_with(
            groups_client._client, "GET", f"{groups_client.BASE_URL}/test_group"
        )
        assert len(result) == 1
        assert result[0].name == "test_group"

    @patch("pihole_lib.groups.make_pihole_request")
    def test_create_group(self, mock_request, groups_client):
        """Test creating a group."""
        mock_request.return_value = make_mock_response(
            json_data={
                "groups": [
                    {
                        **SAMPLE_GROUP_DATA,
                        "name": "new_group",
                        "comment": "New test group",
                        "id": 2,
                    }
                ],
                "processed": {"success": [{"item": "new_group"}], "errors": []},
                "took": 0.005,
            }
        )

        result = groups_client.create_group(
            name="new_group", comment="New test group", enabled=True
        )

        mock_request.assert_called_once_with(
            groups_client._client,
            "POST",
            groups_client.BASE_URL,
            json={"name": "new_group", "comment": "New test group", "enabled": True},
        )
        assert isinstance(result, list)
        assert len(result) == 1
        assert isinstance(result[0], Group)
        assert result[0].name == "new_group"

    @patch("pihole_lib.groups.make_pihole_request")
    def test_update_group(self, mock_request, groups_client):
        """Test updating a group."""
        mock_request.return_value = make_mock_response(
            json_data={
                "groups": [
                    {
                        **SAMPLE_GROUP_DATA,
                        "name": "updated_group",
                        "comment": "Updated comment",
                        "enabled": False,
                    }
                ],
                "processed": {"success": [{"item": "updated_group"}], "errors": []},
                "took": 0.004,
            }
        )

        result = groups_client.update_group(
            name="old_group",
            new_name="updated_group",
            comment="Updated comment",
            enabled=False,
        )

        mock_request.assert_called_once_with(
            groups_client._client,
            "PUT",
            f"{groups_client.BASE_URL}/old_group",
            json={
                "name": "updated_group",
                "comment": "Updated comment",
                "enabled": False,
            },
        )
        assert isinstance(result, GroupsResponse)
        assert result.groups[0].name == "updated_group"
        assert result.groups[0].enabled is False

    @pytest.mark.parametrize(
        "status_code,expected_result",
        [
            (204, True),
            (404, False),
        ],
    )
    @patch("pihole_lib.groups.make_pihole_request")
    def test_delete_group(
        self, mock_request, groups_client, status_code, expected_result
    ):
        """Test deleting a group."""
        mock_request.return_value = make_mock_response(status_code=status_code)

        result = groups_client.delete_group("test_group")

        mock_request.assert_called_once_with(
            groups_client._client, "DELETE", f"{groups_client.BASE_URL}/test_group"
        )
        assert result is expected_result

    @patch("pihole_lib.groups.make_pihole_request")
    def test_create_group_api_error(self, mock_request, groups_client):
        """Test creating a group with API error."""
        mock_request.return_value = make_mock_response(
            json_data={
                "groups": [],
                "processed": {
                    "success": [],
                    "errors": [
                        {
                            "item": "existing_group",
                            "error": "UNIQUE constraint failed: group.name",
                        }
                    ],
                },
                "took": 0.001,
            }
        )

        with pytest.raises(
            PiHoleServerError,
            match="Failed to create group 'existing_group': UNIQUE constraint failed",
        ):
            groups_client.create_group("existing_group")

    def test_inheritance(self, groups_client):
        """Test that PiHoleGroups inherits from BasePiHoleAPIClient."""
        from pihole_lib.base import BasePiHoleAPIClient

        assert isinstance(groups_client, BasePiHoleAPIClient)

    def test_constants_usage(self, groups_client):
        """Test that the class uses the correct API endpoint constants."""
        assert groups_client.BASE_URL == "/api/groups"
