"""Integration tests for PiHoleInfo against real Pi-hole."""

import pytest

from pihole_lib import PiHoleClient, PiHoleInfo
from pihole_lib.exceptions import PiHoleConnectionError
from pihole_lib.models import LoginInfo

from .constants import (
    CONNECTION_FAILED_MESSAGE,
    PIHOLE_BASE_URL,
    PIHOLE_TEST_PASSWORD,
    TEST_INVALID_HOST_URL,
)


class TestPiHoleInfoLoginInfo:
    """Test login info functionality against real Pi-hole."""

    def test_get_login_info_success(self, pihole_container):
        """Should successfully retrieve login info from Pi-hole."""
        client = PiHoleClient(
            base_url=PIHOLE_BASE_URL, password=PIHOLE_TEST_PASSWORD, verify_ssl=False
        )
        info_client = PiHoleInfo(client)

        login_info = info_client.get_login_info()

        assert isinstance(login_info, LoginInfo)
        assert isinstance(login_info.https_port, int)
        assert login_info.https_port >= 0  # Should be 0 or positive
        assert isinstance(login_info.dns, bool)
        assert isinstance(login_info.took, (int, float))
        assert login_info.took >= 0  # Processing time should be non-negative

        client.close()

    def test_get_login_info_connection_error(self):
        """Network errors should raise connection error."""
        client = PiHoleClient(
            base_url=TEST_INVALID_HOST_URL,
            password=PIHOLE_TEST_PASSWORD,
            timeout=1,  # Short timeout
        )
        info_client = PiHoleInfo(client)

        with pytest.raises(PiHoleConnectionError, match=CONNECTION_FAILED_MESSAGE):
            info_client.get_login_info()

        client.close()

    def test_get_login_info_multiple_calls(self, pihole_container):
        """Multiple calls should work consistently."""
        client = PiHoleClient(
            base_url=PIHOLE_BASE_URL, password=PIHOLE_TEST_PASSWORD, verify_ssl=False
        )
        info_client = PiHoleInfo(client)

        # Make multiple calls
        info1 = info_client.get_login_info()
        info2 = info_client.get_login_info()

        # Should get consistent results
        assert info1.https_port == info2.https_port
        assert info1.dns == info2.dns
        # Processing times may differ slightly
        assert isinstance(info1.took, (int, float))
        assert isinstance(info2.took, (int, float))

        client.close()

    def test_get_login_info_session_reuse(self, pihole_container):
        """Should reuse client session across multiple calls."""
        client = PiHoleClient(
            base_url=PIHOLE_BASE_URL, password=PIHOLE_TEST_PASSWORD, verify_ssl=False
        )
        info_client = PiHoleInfo(client)

        # First call creates session in client
        info1 = info_client.get_login_info()
        first_session = client._session

        # Second call should reuse client session
        info2 = info_client.get_login_info()
        second_session = client._session

        assert first_session is second_session
        assert isinstance(info1, LoginInfo)
        assert isinstance(info2, LoginInfo)

        client.close()

    def test_get_login_info_with_client_context_manager(self, pihole_container):
        """Should work when client is used as context manager."""
        with PiHoleClient(
            base_url=PIHOLE_BASE_URL, password=PIHOLE_TEST_PASSWORD, verify_ssl=False
        ) as client:
            info_client = PiHoleInfo(client)
            login_info = info_client.get_login_info()

            assert isinstance(login_info, LoginInfo)
            assert client.is_authenticated()  # Client context manager authenticates


class TestPiHoleInfoWorkflows:
    """Test complete info client workflows with real Pi-hole."""

    def test_full_workflow_success(self, pihole_container):
        """Test complete workflow from init to cleanup."""
        # Test the full workflow
        with PiHoleClient(
            base_url=PIHOLE_BASE_URL, password=PIHOLE_TEST_PASSWORD, verify_ssl=False
        ) as client:
            info_client = PiHoleInfo(client)
            login_info = info_client.get_login_info()
            assert isinstance(login_info, LoginInfo)

        # Client should be cleaned up after its context manager

    def test_manual_session_management(self, pihole_container):
        """Test manual session management without context manager."""
        client = PiHoleClient(
            base_url=PIHOLE_BASE_URL, password=PIHOLE_TEST_PASSWORD, verify_ssl=False
        )
        info_client = PiHoleInfo(client)

        # Initially no session
        assert client._session is None

        # Get login info (creates session in client)
        login_info = info_client.get_login_info()
        assert isinstance(login_info, LoginInfo)
        assert client._session is not None

        # Manually clean up client
        client.close()
        assert client._session is None

    def test_multiple_info_clients_same_client(self, pihole_container):
        """Test that multiple info clients can share the same client."""
        client = PiHoleClient(
            base_url=PIHOLE_BASE_URL, password=PIHOLE_TEST_PASSWORD, verify_ssl=False
        )
        info_client1 = PiHoleInfo(client)
        info_client2 = PiHoleInfo(client)

        # Both should use the same client
        assert info_client1._client is client
        assert info_client2._client is client

        # Both should work and share the same session
        info1 = info_client1.get_login_info()
        info2 = info_client2.get_login_info()

        # Should get the same data
        assert info1.https_port == info2.https_port
        assert info1.dns == info2.dns

        # Should share the same session
        assert info_client1._client._session is info_client2._client._session

        client.close()
