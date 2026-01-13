"""Unit tests for PiHoleClient."""

import requests

from pihole_lib import PiHoleClient
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
