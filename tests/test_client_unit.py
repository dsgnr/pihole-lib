"""Unit tests for PiHoleClient (no network calls)."""

import requests

from pihole_lib import PiHoleClient

from .constants import (
    TEST_LOCALHOST_URL,
    TEST_SECRET_PASSWORD,
    TEST_SESSION_ID,
)


class TestPiHoleClientInit:
    """Test client initialization."""

    def test_init_with_defaults(self):
        """Client should initialize with sensible defaults."""
        client = PiHoleClient(TEST_LOCALHOST_URL, password=TEST_SECRET_PASSWORD)

        assert client.base_url == TEST_LOCALHOST_URL
        assert client._password == TEST_SECRET_PASSWORD
        assert client.timeout == 30
        assert client.verify_ssl is True
        assert client._session_id is None
        assert client._session is None

    def test_init_with_custom_values(self):
        """Client should accept custom timeout and SSL settings."""
        client = PiHoleClient(
            TEST_LOCALHOST_URL, password="my-password", timeout=60, verify_ssl=False
        )

        assert client.base_url == TEST_LOCALHOST_URL
        assert client._password == "my-password"
        assert client.timeout == 60
        assert client.verify_ssl is False

    def test_init_requires_password(self):
        """Client should work with any password string."""
        # Empty password should work (will fail at auth time)
        client = PiHoleClient(TEST_LOCALHOST_URL, password="")
        assert client._password == ""

        # Long password should work
        long_password = "a" * 1000
        client = PiHoleClient(TEST_LOCALHOST_URL, password=long_password)
        assert client._password == long_password


class TestPiHoleClientSessionManagement:
    """Test session creation and management (no network calls)."""

    def test_ensure_session_creates_session(self):
        """_ensure_session should create a requests session."""
        client = PiHoleClient(TEST_LOCALHOST_URL, password=TEST_SECRET_PASSWORD)
        assert client._session is None

        client._ensure_session()

        assert client._session is not None
        assert isinstance(client._session, requests.Session)
        assert client._session.verify is True

    def test_ensure_session_respects_ssl_setting(self):
        """_ensure_session should set SSL verification based on init."""
        client = PiHoleClient(
            TEST_LOCALHOST_URL, password=TEST_SECRET_PASSWORD, verify_ssl=False
        )
        client._ensure_session()

        assert client._session.verify is False

    def test_ensure_session_idempotent(self):
        """_ensure_session should not create multiple sessions."""
        client = PiHoleClient(TEST_LOCALHOST_URL, password=TEST_SECRET_PASSWORD)
        client._ensure_session()
        first_session = client._session

        client._ensure_session()

        assert client._session is first_session

    def test_close_without_session(self):
        """close() should work even if no session exists."""
        client = PiHoleClient(TEST_LOCALHOST_URL, password=TEST_SECRET_PASSWORD)
        # Should not raise an exception
        client.close()


class TestPiHoleClientStatusMethods:
    """Test status checking methods."""

    def test_is_authenticated_false_when_no_session(self):
        """is_authenticated should return False when no session ID."""
        client = PiHoleClient(TEST_LOCALHOST_URL, password=TEST_SECRET_PASSWORD)
        assert client.is_authenticated() is False

    def test_is_authenticated_true_when_session_exists(self):
        """is_authenticated should return True when session ID exists."""
        client = PiHoleClient(TEST_LOCALHOST_URL, password=TEST_SECRET_PASSWORD)
        client._session_id = TEST_SESSION_ID
        assert client.is_authenticated() is True

    def test_get_session_id_none_when_no_session(self):
        """get_session_id should return None when no session."""
        client = PiHoleClient(TEST_LOCALHOST_URL, password=TEST_SECRET_PASSWORD)
        assert client.get_session_id() is None

    def test_get_session_id_returns_session_when_exists(self):
        """get_session_id should return session ID when it exists."""
        client = PiHoleClient(TEST_LOCALHOST_URL, password=TEST_SECRET_PASSWORD)
        client._session_id = TEST_SESSION_ID
        assert client.get_session_id() == TEST_SESSION_ID
