"""Unit tests for PiHoleGroups class."""

from unittest.mock import Mock, patch

import pytest

from pihole_lib.exceptions import PiHoleServerError
from pihole_lib.groups import PiHoleGroups
from pihole_lib.models import (
    Group,
    GroupsResponse,
)


class TestPiHoleGroups:
    """Test cases for PiHoleGroups class."""

    @pytest.fixture
    def mock_client(self):
        """Create a mock PiHoleClient."""
        return Mock()

    @pytest.fixture
    def groups_client(self, mock_client):
        """Create a PiHoleGroups instance with mock client."""
        return PiHoleGroups(mock_client)

    @patch("pihole_lib.groups.make_pihole_request")
    def test_get_groups_all(self, mock_request, groups_client):
        """Test getting all groups."""
        # Mock response
        mock_response = Mock()
        mock_response.json.return_value = {
            "groups": [
                {
                    "name": "Default",
                    "comment": "The default group",
                    "enabled": True,
                    "id": 0,
                    "date_added": 1594670974,
                    "date_modified": 1611157897,
                },
                {
                    "name": "test_group",
                    "comment": "Test group",
                    "enabled": True,
                    "id": 1,
                    "date_added": 1611239095,
                    "date_modified": 1611239099,
                },
            ],
            "took": 0.003,
            "processed": None,
        }
        mock_request.return_value = mock_response

        # Call method
        result = groups_client.get_groups()

        # Verify API call
        mock_request.assert_called_once_with(
            groups_client._client,
            "GET",
            groups_client.BASE_URL,
        )

        # Verify result
        assert isinstance(result, GroupsResponse)
        assert len(result.groups) == 2
        assert result.groups[0].name == "Default"
        assert result.groups[0].enabled is True
        assert result.groups[1].name == "test_group"
        assert result.took == 0.003

    @patch("pihole_lib.groups.make_pihole_request")
    def test_get_groups_specific(self, mock_request, groups_client):
        """Test getting a specific group."""
        # Mock response
        mock_response = Mock()
        mock_response.json.return_value = {
            "groups": [
                {
                    "name": "test_group",
                    "comment": "Test group",
                    "enabled": True,
                    "id": 1,
                    "date_added": 1611239095,
                    "date_modified": 1611239099,
                }
            ],
            "took": 0.002,
            "processed": None,
        }
        mock_request.return_value = mock_response

        # Call method
        result = groups_client.get_groups(name="test_group")

        # Verify API call
        mock_request.assert_called_once_with(
            groups_client._client,
            "GET",
            f"{groups_client.BASE_URL}/test_group",
        )

        # Verify result
        assert isinstance(result, GroupsResponse)
        assert len(result.groups) == 1
        assert result.groups[0].name == "test_group"

    @patch("pihole_lib.groups.make_pihole_request")
    def test_create_group(self, mock_request, groups_client):
        """Test creating a group."""
        # Mock response
        mock_response = Mock()
        mock_response.json.return_value = {
            "groups": [
                {
                    "name": "new_group",
                    "comment": "New test group",
                    "enabled": True,
                    "id": 2,
                    "date_added": 1611239200,
                    "date_modified": 1611239200,
                }
            ],
            "processed": {
                "success": [{"item": "new_group"}],
                "errors": [],
            },
            "took": 0.005,
        }
        mock_request.return_value = mock_response

        # Call method
        result = groups_client.create_group(
            name="new_group",
            comment="New test group",
            enabled=True,
        )

        # Verify API call
        mock_request.assert_called_once_with(
            groups_client._client,
            "POST",
            groups_client.BASE_URL,
            json={
                "name": "new_group",
                "comment": "New test group",
                "enabled": True,
            },
        )

        # Verify result
        assert isinstance(result, list)
        assert len(result) == 1
        assert isinstance(result[0], Group)
        assert result[0].name == "new_group"
        assert result[0].comment == "New test group"

    @patch("pihole_lib.groups.make_pihole_request")
    def test_update_group(self, mock_request, groups_client):
        """Test updating a group."""
        # Mock response
        mock_response = Mock()
        mock_response.json.return_value = {
            "groups": [
                {
                    "name": "updated_group",
                    "comment": "Updated comment",
                    "enabled": False,
                    "id": 1,
                    "date_added": 1611239095,
                    "date_modified": 1611239300,
                }
            ],
            "processed": {
                "success": [{"item": "updated_group"}],
                "errors": [],
            },
            "took": 0.004,
        }
        mock_request.return_value = mock_response

        # Call method
        result = groups_client.update_group(
            name="old_group",
            new_name="updated_group",
            comment="Updated comment",
            enabled=False,
        )

        # Verify API call
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

        # Verify result
        assert isinstance(result, GroupsResponse)
        assert result.groups[0].name == "updated_group"
        assert result.groups[0].comment == "Updated comment"
        assert result.groups[0].enabled is False

    @patch("pihole_lib.groups.make_pihole_request")
    def test_delete_group(self, mock_request, groups_client):
        """Test deleting a group."""
        # Mock response
        mock_response = Mock()
        mock_response.status_code = 204
        mock_request.return_value = mock_response

        # Call method
        result = groups_client.delete_group("test_group")

        # Verify API call
        mock_request.assert_called_once_with(
            groups_client._client,
            "DELETE",
            f"{groups_client.BASE_URL}/test_group",
        )

        # Verify result
        assert result is True

    @patch("pihole_lib.groups.make_pihole_request")
    def test_delete_group_not_found(self, mock_request, groups_client):
        """Test deleting a group that returns non-204 status."""
        # Mock response
        mock_response = Mock()
        mock_response.status_code = 404
        mock_request.return_value = mock_response

        # Call method
        result = groups_client.delete_group("nonexistent_group")

        # Verify result
        assert result is False

    @patch("pihole_lib.groups.make_pihole_request")
    def test_create_group_api_error(self, mock_request, groups_client):
        """Test creating a group with API error."""
        # Mock response with error
        mock_response = Mock()
        mock_response.json.return_value = {
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
        mock_request.return_value = mock_response

        # Call method and expect exception
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
