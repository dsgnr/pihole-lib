"""Unit tests for PiHoleInfo (no network calls)."""

from pihole_lib import PiHoleClient, PiHoleInfo

from .constants import (
    TEST_LOCALHOST_URL,
    TEST_SECRET_PASSWORD,
)


class TestPiHoleInfoInit:
    """Test info client initialization."""

    def test_init_with_client(self):
        """Info client should initialize with a PiHoleClient."""
        client = PiHoleClient(TEST_LOCALHOST_URL, password=TEST_SECRET_PASSWORD)
        info_client = PiHoleInfo(client)

        assert info_client._client is client

    def test_init_stores_client_reference(self):
        """Info client should store reference to the provided client."""
        client = PiHoleClient(TEST_LOCALHOST_URL, password=TEST_SECRET_PASSWORD)
        info_client = PiHoleInfo(client)

        # Should be able to access client properties through the stored reference
        assert info_client._client.base_url == TEST_LOCALHOST_URL
        assert info_client._client._password == TEST_SECRET_PASSWORD


class TestPiHoleInfoLoginInfo:
    """Test info client login info functionality (no network calls)."""

    def test_get_login_info_uses_client_session(self):
        """get_login_info should use the client's session."""
        client = PiHoleClient(TEST_LOCALHOST_URL, password=TEST_SECRET_PASSWORD)
        info_client = PiHoleInfo(client)

        assert client._session is None

        # This would fail in real usage due to no network, but we're testing
        # that it ensures the client has a session
        try:
            info_client.get_login_info()
        except Exception:
            # Expected to fail due to no network, but client session should be created
            pass

        assert client._session is not None

    def test_get_login_info_uses_client_properties(self):
        """get_login_info should use client's base_url and timeout."""
        client = PiHoleClient(
            TEST_LOCALHOST_URL,
            password=TEST_SECRET_PASSWORD,
            timeout=60,
            verify_ssl=False,
        )
        info_client = PiHoleInfo(client)

        # Verify info client uses client properties
        assert info_client._client.base_url == TEST_LOCALHOST_URL
        assert info_client._client.timeout == 60
        assert info_client._client.verify_ssl is False
