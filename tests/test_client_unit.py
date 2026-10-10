"""Unit tests for PiHoleClient."""

from unittest.mock import Mock, patch

import pytest
import requests

from pihole_lib import PiHoleClient
from pihole_lib.exceptions import PiHoleAPIError
from tests.constants import TEST_LOCALHOST_URL, TEST_SECRET_PASSWORD, TEST_SESSION_ID


class TestPiHoleClientInit:
    """Test PiHoleClient initialization."""

    def test_defaults(self):
        """Test default initialization values."""
        client = PiHoleClient(TEST_LOCALHOST_URL, password=TEST_SECRET_PASSWORD)

        assert client.base_url == TEST_LOCALHOST_URL
        assert client._password == TEST_SECRET_PASSWORD
        assert client.timeout == 30
        assert client.verify_ssl is True
        assert client._session is None
        assert client._session_id is None

    def test_custom_values(self):
        """Test initialization with custom values."""
        client = PiHoleClient(
            TEST_LOCALHOST_URL,
            password="custom-password",
            timeout=60,
            verify_ssl=False,
        )

        assert client.timeout == 60
        assert client.verify_ssl is False
        assert client._password == "custom-password"

    def test_password_edge_cases(self):
        """Test password handling edge cases."""
        assert PiHoleClient(TEST_LOCALHOST_URL, password="")._password == ""

        long_password = "x" * 1000
        assert (
            PiHoleClient(TEST_LOCALHOST_URL, password=long_password)._password
            == long_password
        )


class TestPiHoleClientSession:
    """Test session management."""

    def test_ensure_session_creates_session(self):
        """Test that _ensure_session creates a requests session."""
        client = PiHoleClient(TEST_LOCALHOST_URL, password=TEST_SECRET_PASSWORD)

        client._ensure_session()

        assert isinstance(client._session, requests.Session)
        assert client._session.verify is True

    def test_ensure_session_respects_ssl_setting(self):
        """Test that session respects verify_ssl setting."""
        client = PiHoleClient(
            TEST_LOCALHOST_URL,
            password=TEST_SECRET_PASSWORD,
            verify_ssl=False,
        )

        client._ensure_session()

        assert client._session.verify is False

    def test_ensure_session_is_idempotent(self):
        """Test that _ensure_session doesn't recreate existing session."""
        client = PiHoleClient(TEST_LOCALHOST_URL, password=TEST_SECRET_PASSWORD)

        client._ensure_session()
        first_session = client._session

        client._ensure_session()

        assert client._session is first_session

    def test_close_without_session(self):
        """Test that close() works without an active session."""
        client = PiHoleClient(TEST_LOCALHOST_URL, password=TEST_SECRET_PASSWORD)
        client.close()  # Should not raise


class TestPiHoleClientAuthState:
    """Test authentication state management."""

    def test_is_authenticated_false_without_session_id(self):
        """Test is_authenticated returns False without session ID."""
        client = PiHoleClient(TEST_LOCALHOST_URL, password=TEST_SECRET_PASSWORD)
        assert client.is_authenticated() is False

    def test_is_authenticated_true_with_session_id(self):
        """Test is_authenticated returns True with session ID."""
        client = PiHoleClient(TEST_LOCALHOST_URL, password=TEST_SECRET_PASSWORD)
        client._session_id = TEST_SESSION_ID
        assert client.is_authenticated() is True

    def test_get_session_id_none_when_missing(self):
        """Test get_session_id returns None when not set."""
        client = PiHoleClient(TEST_LOCALHOST_URL, password=TEST_SECRET_PASSWORD)
        assert client.get_session_id() is None

    def test_get_session_id_returns_value(self):
        """Test get_session_id returns the session ID when set."""
        client = PiHoleClient(TEST_LOCALHOST_URL, password=TEST_SECRET_PASSWORD)
        client._session_id = TEST_SESSION_ID
        assert client.get_session_id() == TEST_SESSION_ID


class TestPiHoleClientPostAuth:
    """Test login retry behaviour."""

    @staticmethod
    def _client() -> PiHoleClient:
        return PiHoleClient(TEST_LOCALHOST_URL, password=TEST_SECRET_PASSWORD)

    @patch("pihole_lib.client.time.sleep")
    @patch("pihole_lib.client.make_pihole_request")
    def test_retries_after_rate_limit(self, mock_request, mock_sleep):
        """A 429 from /api/auth is retried after a delay."""
        success = Mock()
        mock_request.side_effect = [
            PiHoleAPIError("Too many requests", status_code=429),
            success,
        ]

        assert self._client()._post_auth() is success
        assert mock_request.call_count == 2
        mock_sleep.assert_called_once()

    @patch("pihole_lib.client.time.sleep")
    @patch("pihole_lib.client.make_pihole_request")
    def test_rate_limit_raised_after_retries_exhausted(self, mock_request, mock_sleep):
        """The last 429 is raised once every attempt has been used."""
        client = self._client()
        mock_request.side_effect = PiHoleAPIError("Too many", status_code=429)

        with pytest.raises(PiHoleAPIError) as exc_info:
            client._post_auth()

        assert exc_info.value.status_code == 429
        assert mock_request.call_count == client._AUTH_CONNECT_RETRIES

    @patch("pihole_lib.client.time.sleep")
    @patch("pihole_lib.client.make_pihole_request")
    def test_other_api_errors_not_retried(self, mock_request, mock_sleep):
        """Errors other than 429 are raised immediately."""
        mock_request.side_effect = PiHoleAPIError("Bad request", status_code=400)

        with pytest.raises(PiHoleAPIError):
            self._client()._post_auth()

        assert mock_request.call_count == 1
        mock_sleep.assert_not_called()


class TestPiHoleClientAuthenticate:
    """Test the public authenticate method."""

    @patch("pihole_lib.client.make_pihole_request")
    def test_authenticate_stores_session_id(self, mock_request):
        """authenticate() is public and stores the returned session ID."""
        mock_request.return_value = Mock(
            json=lambda: {"session": {"valid": True, "sid": TEST_SESSION_ID}}
        )
        client = PiHoleClient(TEST_LOCALHOST_URL, password=TEST_SECRET_PASSWORD)

        client.authenticate()

        assert client.get_session_id() == TEST_SESSION_ID
