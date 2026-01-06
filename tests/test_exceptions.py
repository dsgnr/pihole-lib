"""Tests for Pi-hole API exceptions."""

import pytest

from pihole_lib.exceptions import (
    PiHoleAPIError,
    PiHoleAuthenticationError,
    PiHoleConnectionError,
    PiHoleServerError,
)


class TestPiHoleAPIError:
    """Test the base API error class."""

    def test_basic_error(self):
        """Basic error should work with just a message."""
        error = PiHoleAPIError("Something went wrong")

        assert str(error) == "Something went wrong"
        assert error.message == "Something went wrong"
        assert error.status_code is None

    def test_error_with_status_code(self):
        """Error should store status code when provided."""
        error = PiHoleAPIError("Bad request", status_code=400)

        assert str(error) == "Bad request"
        assert error.message == "Bad request"
        assert error.status_code == 400

    def test_error_inheritance(self):
        """API error should be a proper exception."""
        error = PiHoleAPIError("Test error")

        assert isinstance(error, Exception)
        assert isinstance(error, PiHoleAPIError)

    def test_error_can_be_raised(self):
        """Error should be raisable and catchable."""
        with pytest.raises(PiHoleAPIError) as exc_info:
            raise PiHoleAPIError("Test error", status_code=500)

        assert exc_info.value.message == "Test error"
        assert exc_info.value.status_code == 500


class TestPiHoleConnectionError:
    """Test connection error class."""

    def test_connection_error_inheritance(self):
        """Connection error should inherit from API error."""
        error = PiHoleConnectionError("Connection failed")

        assert isinstance(error, PiHoleAPIError)
        assert isinstance(error, PiHoleConnectionError)
        assert str(error) == "Connection failed"

    def test_connection_error_with_status_code(self):
        """Connection error should support status codes."""
        error = PiHoleConnectionError("Timeout", status_code=408)

        assert error.message == "Timeout"
        assert error.status_code == 408

    def test_can_catch_as_base_exception(self):
        """Connection error should be catchable as base API error."""
        with pytest.raises(PiHoleAPIError):
            raise PiHoleConnectionError("Network error")


class TestPiHoleAuthenticationError:
    """Test authentication error class."""

    def test_auth_error_inheritance(self):
        """Auth error should inherit from API error."""
        error = PiHoleAuthenticationError("Login failed")

        assert isinstance(error, PiHoleAPIError)
        assert isinstance(error, PiHoleAuthenticationError)
        assert str(error) == "Login failed"

    def test_auth_error_with_status_code(self):
        """Auth error should support status codes."""
        error = PiHoleAuthenticationError("Unauthorized", status_code=401)

        assert error.message == "Unauthorized"
        assert error.status_code == 401

    def test_can_catch_as_base_exception(self):
        """Auth error should be catchable as base API error."""
        with pytest.raises(PiHoleAPIError):
            raise PiHoleAuthenticationError("Bad password")


class TestPiHoleServerError:
    """Test server error class."""

    def test_server_error_inheritance(self):
        """Server error should inherit from API error."""
        error = PiHoleServerError("Internal server error")

        assert isinstance(error, PiHoleAPIError)
        assert isinstance(error, PiHoleServerError)
        assert str(error) == "Internal server error"

    def test_server_error_with_status_code(self):
        """Server error should support status codes."""
        error = PiHoleServerError("Service unavailable", status_code=503)

        assert error.message == "Service unavailable"
        assert error.status_code == 503

    def test_can_catch_as_base_exception(self):
        """Server error should be catchable as base API error."""
        with pytest.raises(PiHoleAPIError):
            raise PiHoleServerError("Database error")


class TestExceptionHierarchy:
    """Test the exception hierarchy works correctly."""

    def test_catch_all_api_errors(self):
        """Should be able to catch all Pi-hole errors with base class."""
        errors_to_test = [
            PiHoleAPIError("Generic error"),
            PiHoleConnectionError("Connection error"),
            PiHoleAuthenticationError("Auth error"),
            PiHoleServerError("Server error"),
        ]

        for error in errors_to_test:
            with pytest.raises(PiHoleAPIError):
                raise error

    def test_specific_error_catching(self):
        """Should be able to catch specific error types."""
        # Test catching specific connection errors
        with pytest.raises(PiHoleConnectionError):
            raise PiHoleConnectionError("Network down")

        # Test catching specific auth errors
        with pytest.raises(PiHoleAuthenticationError):
            raise PiHoleAuthenticationError("Wrong password")

        # Test catching specific server errors
        with pytest.raises(PiHoleServerError):
            raise PiHoleServerError("Database crashed")

    def test_error_type_checking(self):
        """Should be able to check error types properly."""
        conn_error = PiHoleConnectionError("Connection failed")
        auth_error = PiHoleAuthenticationError("Login failed")
        server_error = PiHoleServerError("Server crashed")

        # All should be API errors
        assert isinstance(conn_error, PiHoleAPIError)
        assert isinstance(auth_error, PiHoleAPIError)
        assert isinstance(server_error, PiHoleAPIError)

        # But should be distinguishable
        assert isinstance(conn_error, PiHoleConnectionError)
        assert not isinstance(conn_error, PiHoleAuthenticationError)
        assert not isinstance(conn_error, PiHoleServerError)

        assert isinstance(auth_error, PiHoleAuthenticationError)
        assert not isinstance(auth_error, PiHoleConnectionError)
        assert not isinstance(auth_error, PiHoleServerError)

        assert isinstance(server_error, PiHoleServerError)
        assert not isinstance(server_error, PiHoleConnectionError)
        assert not isinstance(server_error, PiHoleAuthenticationError)
