"""Tests for utility functions."""

from unittest.mock import Mock

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
            (404, PiHoleAPIError, "endpoint not found"),
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

    def test_endpoint_name_in_error(self):
        """Should include endpoint name in error messages."""
        response = Mock()
        response.status_code = 404

        with pytest.raises(PiHoleAPIError, match="test endpoint not found"):
            handle_pihole_response(response, endpoint_name="test")

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
        session = Mock()
        response = Mock()
        response.status_code = 200
        session.request.return_value = response

        result = make_pihole_request(session, "GET", "http://test.com")

        assert result is response
        session.request.assert_called_once_with("GET", "http://test.com")

    def test_connection_error(self):
        """Should raise PiHoleConnectionError for connection issues."""
        session = Mock()
        session.request.side_effect = requests.ConnectionError("Connection failed")

        with pytest.raises(PiHoleConnectionError, match="Connection failed"):
            make_pihole_request(session, "GET", "http://test.com")

    def test_passes_kwargs(self):
        """Should pass additional kwargs to the request method."""
        session = Mock()
        response = Mock()
        response.status_code = 200
        session.request.return_value = response

        make_pihole_request(
            session, "POST", "http://test.com", json={"test": "data"}, timeout=30
        )

        session.request.assert_called_once_with(
            "POST", "http://test.com", json={"test": "data"}, timeout=30
        )
