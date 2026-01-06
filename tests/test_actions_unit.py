"""Unit tests for PiHoleActions class."""

from unittest.mock import Mock, patch

import pytest

from pihole_lib import PiHoleActions, PiHoleClient
from pihole_lib.exceptions import (
    PiHoleAPIError,
    PiHoleAuthenticationError,
    PiHoleConnectionError,
    PiHoleServerError,
)

from .constants import PIHOLE_BASE_URL


@pytest.fixture
def mock_client():
    """Create a mock PiHoleClient for testing."""
    client = Mock(spec=PiHoleClient)
    client.base_url = PIHOLE_BASE_URL
    client.timeout = 30
    client.verify_ssl = True
    client._session_id = "test-session-id"
    return client


@pytest.fixture
def actions_client(mock_client):
    """Create a PiHoleActions instance with mock client."""
    return PiHoleActions(mock_client)


class TestPiHoleActionsInit:
    """Test PiHoleActions initialization."""

    def test_init_with_client(self, mock_client):
        """Test initialization with a client."""
        actions = PiHoleActions(mock_client)
        assert actions._client is mock_client


class TestUpdateGravity:
    """Test update_gravity method."""

    @patch("pihole_lib.actions.make_pihole_request")
    def test_update_gravity_basic(self, mock_request, actions_client):
        """Test basic gravity update without color."""
        # Mock response with streaming content
        mock_response = Mock()
        mock_response.iter_lines.return_value = [
            "  [✓] DNS resolution is available",
            "",  # Empty line should be skipped
            "  [i] Neutrino emissions detected...",
            "  [✓] Done.",
        ]
        mock_request.return_value = mock_response

        # Call the method and collect results
        lines = list(actions_client.update_gravity())

        # Verify the request was made correctly
        mock_request.assert_called_once_with(
            actions_client._client,
            "POST",
            "/api/action/gravity",
            params=None,
            stream=True,
        )

        # Verify the output (empty lines should be filtered out)
        expected_lines = [
            "  [✓] DNS resolution is available",
            "  [i] Neutrino emissions detected...",
            "  [✓] Done.",
        ]
        assert lines == expected_lines

    @patch("pihole_lib.actions.make_pihole_request")
    def test_update_gravity_with_color(self, mock_request, actions_client):
        """Test gravity update with color parameter."""
        # Mock response with streaming content
        mock_response = Mock()
        mock_response.iter_lines.return_value = [
            "  [✓] DNS resolution is available",
            "  [i] Neutrino emissions detected...",
        ]
        mock_request.return_value = mock_response

        # Call the method with color=True
        lines = list(actions_client.update_gravity(color=True))

        # Verify the request was made with color parameter
        mock_request.assert_called_once_with(
            actions_client._client,
            "POST",
            "/api/action/gravity",
            params={"color": "true"},
            stream=True,
        )

        # Verify the output
        expected_lines = [
            "  [✓] DNS resolution is available",
            "  [i] Neutrino emissions detected...",
        ]
        assert lines == expected_lines

    @patch("pihole_lib.actions.make_pihole_request")
    def test_update_gravity_with_color_false(self, mock_request, actions_client):
        """Test gravity update with color=False (should not include color param)."""
        # Mock response
        mock_response = Mock()
        mock_response.iter_lines.return_value = ["  [✓] Done."]
        mock_request.return_value = mock_response

        # Call the method with color=False
        list(actions_client.update_gravity(color=False))

        # Verify the request was made without color parameter
        mock_request.assert_called_once_with(
            actions_client._client,
            "POST",
            "/api/action/gravity",
            params=None,
            stream=True,
        )

    @patch("pihole_lib.actions.make_pihole_request")
    def test_update_gravity_empty_response(self, mock_request, actions_client):
        """Test gravity update with empty response."""
        # Mock response with no content
        mock_response = Mock()
        mock_response.iter_lines.return_value = []
        mock_request.return_value = mock_response

        # Call the method
        lines = list(actions_client.update_gravity())

        # Verify empty result
        assert lines == []

    @patch("pihole_lib.actions.make_pihole_request")
    def test_update_gravity_only_empty_lines(self, mock_request, actions_client):
        """Test gravity update with only empty lines."""
        # Mock response with only empty lines
        mock_response = Mock()
        mock_response.iter_lines.return_value = ["", "", ""]
        mock_request.return_value = mock_response

        # Call the method
        lines = list(actions_client.update_gravity())

        # Verify empty result (empty lines should be filtered out)
        assert lines == []

    @patch("pihole_lib.actions.make_pihole_request")
    def test_update_gravity_connection_error(self, mock_request, actions_client):
        """Test gravity update with connection error."""
        mock_request.side_effect = PiHoleConnectionError("Connection failed")

        with pytest.raises(PiHoleConnectionError, match="Connection failed"):
            list(actions_client.update_gravity())

    @patch("pihole_lib.actions.make_pihole_request")
    def test_update_gravity_authentication_error(self, mock_request, actions_client):
        """Test gravity update with authentication error."""
        mock_request.side_effect = PiHoleAuthenticationError("Invalid credentials")

        with pytest.raises(PiHoleAuthenticationError, match="Invalid credentials"):
            list(actions_client.update_gravity())

    @patch("pihole_lib.actions.make_pihole_request")
    def test_update_gravity_server_error(self, mock_request, actions_client):
        """Test gravity update with server error."""
        mock_request.side_effect = PiHoleServerError("Server error: 500")

        with pytest.raises(PiHoleServerError, match="Server error: 500"):
            list(actions_client.update_gravity())

    @patch("pihole_lib.actions.make_pihole_request")
    def test_update_gravity_api_error(self, mock_request, actions_client):
        """Test gravity update with API error."""
        mock_request.side_effect = PiHoleAPIError("Bad request")

        with pytest.raises(PiHoleAPIError, match="Bad request"):
            list(actions_client.update_gravity())

    @patch("pihole_lib.actions.make_pihole_request")
    def test_update_gravity_mixed_content(self, mock_request, actions_client):
        """Test gravity update with mixed content (empty and non-empty lines)."""
        # Mock response with mixed content
        mock_response = Mock()
        mock_response.iter_lines.return_value = [
            "  [✓] Starting...",
            "",
            "  [i] Processing...",
            "",
            "",
            "  [✓] Done.",
            "",
        ]
        mock_request.return_value = mock_response

        # Call the method
        lines = list(actions_client.update_gravity())

        # Verify only non-empty lines are returned
        expected_lines = [
            "  [✓] Starting...",
            "  [i] Processing...",
            "  [✓] Done.",
        ]
        assert lines == expected_lines
