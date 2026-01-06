"""Tests for utility functions."""

from unittest.mock import Mock, patch

import pytest
import requests

from pihole_lib.exceptions import (
    PiHoleAPIError,
    PiHoleAuthenticationError,
    PiHoleConnectionError,
    PiHoleServerError,
)
from pihole_lib.utils import handle_pihole_response, make_pihole_request


class TestHandlePiHoleResponse:
    """Test the handle_pihole_response utility function."""

    def test_success_response(self):
        """Should not raise exception for 200 status code."""
        response = Mock()
        response.status_code = 200

        # Should not raise any exception
        handle_pihole_response(response)

    def test_authentication_errors(self):
        """Should raise authentication errors for 401/403."""
        response_401 = Mock()
        response_401.status_code = 401

        response_403 = Mock()
        response_403.status_code = 403

        # Should always treat as auth errors since we use PiHoleClient
        with pytest.raises(PiHoleAuthenticationError, match="Invalid credentials"):
            handle_pihole_response(response_401)

        with pytest.raises(PiHoleAuthenticationError, match="Access denied"):
            handle_pihole_response(response_403)

    def test_client_errors(self):
        """Should raise appropriate errors for 4xx status codes."""
        test_cases = [
            (400, PiHoleAPIError, "Bad request"),
            (404, PiHoleAPIError, "Endpoint not found"),
            (429, PiHoleAPIError, "Too many requests"),
        ]

        for status_code, expected_exception, expected_message in test_cases:
            response = Mock()
            response.status_code = status_code

            with pytest.raises(expected_exception, match=expected_message):
                handle_pihole_response(response)

    def test_server_errors(self):
        """Should raise server error for 5xx status codes."""
        response = Mock()
        response.status_code = 500

        with pytest.raises(PiHoleServerError, match="Server error: 500"):
            handle_pihole_response(response)

    def test_no_endpoint_name_in_error(self):
        """Should handle errors without endpoint names."""
        response = Mock()
        response.status_code = 404

        with pytest.raises(PiHoleAPIError, match="Endpoint not found"):
            handle_pihole_response(response)

    def test_other_http_errors(self):
        """Should handle other HTTP errors gracefully."""
        response = Mock()
        response.status_code = 418  # I'm a teapot
        response.raise_for_status.side_effect = requests.HTTPError("418 I'm a teapot")

        with pytest.raises(PiHoleAPIError, match="HTTP error"):
            handle_pihole_response(response)


class TestMakePiHoleRequest:
    """Test the make_pihole_request utility function."""

    def test_successful_request(self):
        """Should return response for successful requests."""
        client = Mock()
        client.base_url = "http://test.com"
        client.timeout = 30
        client._session = Mock()
        client._ensure_session = Mock()

        response = Mock()
        response.status_code = 200
        client._session.request.return_value = response

        result = make_pihole_request(client, "GET", "/api/test")

        assert result is response
        client._ensure_session.assert_called_once()
        client._session.request.assert_called_once_with(
            "GET",
            "http://test.com/api/test",
            json=None,
            files=None,
            params=None,
            timeout=30,
        )

    def test_connection_error(self):
        """Should raise PiHoleConnectionError for connection issues."""
        client = Mock()
        client.base_url = "http://test.com"
        client.timeout = 30
        client._session = Mock()
        client._ensure_session = Mock()
        client._session.request.side_effect = requests.ConnectionError(
            "Connection failed"
        )

        with pytest.raises(PiHoleConnectionError, match="Connection failed"):
            make_pihole_request(client, "GET", "/api/test")

    def test_passes_data_and_files(self):
        """Should pass files to the request method."""
        client = Mock()
        client.base_url = "http://test.com"
        client.timeout = 30
        client._session = Mock()
        client._ensure_session = Mock()

        response = Mock()
        response.status_code = 200
        client._session.request.return_value = response

        test_files = {"file": ("test.txt", b"content", "text/plain")}

        make_pihole_request(client, "POST", "/api/test", files=test_files)

        client._session.request.assert_called_once_with(
            "POST",
            "http://test.com/api/test",
            json=None,
            files=test_files,
            params=None,
            timeout=30,
        )

    def test_passes_json_data(self):
        """Should pass JSON data to the request method."""
        client = Mock()
        client.base_url = "http://test.com"
        client.timeout = 30
        client._session = Mock()
        client._ensure_session = Mock()

        response = Mock()
        response.status_code = 200
        client._session.request.return_value = response

        test_json = {"password": "secret"}

        make_pihole_request(client, "POST", "/api/auth", json=test_json)

        client._session.request.assert_called_once_with(
            "POST",
            "http://test.com/api/auth",
            json=test_json,
            files=None,
            params=None,
            timeout=30,
        )

    def test_generates_endpoint_name_from_path(self):
        """Should handle responses without endpoint names."""
        client = Mock()
        client.base_url = "http://test.com"
        client.timeout = 30
        client._session = Mock()
        client._ensure_session = Mock()

        # Mock handle_pihole_response to capture that no endpoint_name is passed
        with patch("pihole_lib.utils.handle_pihole_response") as mock_handle:
            response = Mock()
            response.status_code = 200
            client._session.request.return_value = response

            make_pihole_request(client, "GET", "/api/info/login")

            # Verify handle_pihole_response was called without endpoint name
            mock_handle.assert_called_once_with(response)

    def test_uses_client_timeout_by_default(self):
        """Should use client timeout when not specified."""
        client = Mock()
        client.base_url = "http://test.com"
        client.timeout = 45
        client._session = Mock()
        client._ensure_session = Mock()

        response = Mock()
        response.status_code = 200
        client._session.request.return_value = response

        make_pihole_request(client, "GET", "/api/test")

        client._session.request.assert_called_once_with(
            "GET",
            "http://test.com/api/test",
            json=None,
            files=None,
            params=None,
            timeout=45,
        )
