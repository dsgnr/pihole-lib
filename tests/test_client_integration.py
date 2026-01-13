"""Integration tests for PiHoleClient."""

import pytest

from pihole_lib import PiHoleClient
from pihole_lib.exceptions import (
    PiHoleAuthenticationError,
    PiHoleConnectionError,
)
from tests.conftest import integration
from tests.constants import (
    CONNECTION_FAILED_MESSAGE,
    PIHOLE_BASE_URL,
    PIHOLE_TEST_PASSWORD,
    TEST_EXCEPTION_MESSAGE,
    TEST_INVALID_HOST_URL,
    TEST_INVALID_SESSION_ID,
    TEST_WRONG_PASSWORD,
)


@integration
class TestPiHoleClientAuthentication:
    """Test authentication against real Pi-hole."""

    def test_authenticate_success(self, pihole_container):
        """Successful authentication should set session ID."""
        client = PiHoleClient(
            base_url=PIHOLE_BASE_URL,
            password=PIHOLE_TEST_PASSWORD,
            verify_ssl=False,
        )

        client._ensure_session()
        client._authenticate()

        assert client._session_id is not None
        assert len(client._session_id) > 0

        client.close()

    def test_authenticate_invalid_password(self, pihole_container):
        """Invalid password should raise authentication error."""
        client = PiHoleClient(
            base_url=PIHOLE_BASE_URL,
            password=TEST_WRONG_PASSWORD,
            verify_ssl=False,
        )

        client._ensure_session()

        with pytest.raises(PiHoleAuthenticationError):
            client._authenticate()

        client.close()

    def test_authenticate_empty_password(self, pihole_container):
        """Empty password should raise authentication error."""
        client = PiHoleClient(
            base_url=PIHOLE_BASE_URL,
            password="",
            verify_ssl=False,
        )

        client._ensure_session()

        with pytest.raises(PiHoleAuthenticationError):
            client._authenticate()

        client.close()

    def test_authenticate_connection_error(self):
        """Network errors should raise connection error."""
        client = PiHoleClient(
            base_url=TEST_INVALID_HOST_URL,
            password=TEST_WRONG_PASSWORD,
            timeout=1,  # Short timeout
        )

        client._ensure_session()

        with pytest.raises(PiHoleConnectionError, match=CONNECTION_FAILED_MESSAGE):
            client._authenticate()

        client.close()


@integration
class TestPiHoleClientContextManager:
    """Test context manager functionality with real Pi-hole."""

    def test_context_manager_enter_and_exit(self, pihole_container):
        """Context manager should authenticate and clean up properly."""
        client = PiHoleClient(
            base_url=PIHOLE_BASE_URL,
            password=PIHOLE_TEST_PASSWORD,
            verify_ssl=False,
        )

        # Test context manager
        with client as authenticated_client:
            assert authenticated_client is client
            assert client.is_authenticated()
            assert client.get_session_id() is not None

        # Should be cleaned up after context
        assert not client.is_authenticated()
        assert client.get_session_id() is None

    def test_context_manager_exit_with_exception(self, pihole_container):
        """Context manager should clean up even when there's an exception."""
        client = PiHoleClient(
            base_url=PIHOLE_BASE_URL,
            password=PIHOLE_TEST_PASSWORD,
            verify_ssl=False,
        )

        try:
            with client:
                assert client.is_authenticated()
                # Raise an exception to test cleanup
                raise ValueError(TEST_EXCEPTION_MESSAGE)
        except ValueError:
            pass  # Expected

        # Should still be cleaned up
        assert not client.is_authenticated()
        assert client.get_session_id() is None


@integration
class TestPiHoleClientSessionCleanup:
    """Test session cleanup with real Pi-hole."""

    def test_close_with_session_and_session_id(self, pihole_container):
        """close() should delete session and close HTTP session."""
        client = PiHoleClient(
            base_url=PIHOLE_BASE_URL,
            password=PIHOLE_TEST_PASSWORD,
            verify_ssl=False,
        )

        client._ensure_session()
        client._authenticate()

        # Verify we have a session
        assert client.is_authenticated()
        session_id = client.get_session_id()
        assert session_id is not None

        client.close()

        # Should clear internal state
        assert client._session is None
        assert client._session_id is None
        assert not client.is_authenticated()

    def test_close_handles_delete_failure_gracefully(self, pihole_container):
        """close() should handle logout failures gracefully."""
        client = PiHoleClient(
            base_url=PIHOLE_BASE_URL,
            password=PIHOLE_TEST_PASSWORD,
            verify_ssl=False,
        )

        client._ensure_session()
        client._authenticate()

        # Manually corrupt the session ID to simulate failure
        client._session_id = TEST_INVALID_SESSION_ID

        # Should not raise an exception
        client.close()

        # Should still clean up internal state
        assert client._session is None
        assert client._session_id is None


@integration
class TestPiHoleClientWorkflows:
    """Test complete client workflows with real Pi-hole."""

    def test_full_workflow_success(self, pihole_container):
        """Test complete workflow from init to cleanup."""
        # Test the full workflow
        with PiHoleClient(
            base_url=PIHOLE_BASE_URL,
            password=PIHOLE_TEST_PASSWORD,
            verify_ssl=False,
        ) as client:
            assert client.is_authenticated()
            session_id = client.get_session_id()
            assert session_id is not None
            assert len(session_id) > 0

        # Should be cleaned up after context manager
        assert not client.is_authenticated()
        assert client.get_session_id() is None

    def test_manual_session_management(self, pihole_container):
        """Test manual session management without context manager."""
        client = PiHoleClient(
            base_url=PIHOLE_BASE_URL,
            password=PIHOLE_TEST_PASSWORD,
            verify_ssl=False,
        )

        # Initially not authenticated
        assert not client.is_authenticated()

        # Manually set up and authenticate
        client._ensure_session()
        client._authenticate()

        assert client.is_authenticated()
        session_id = client.get_session_id()
        assert session_id is not None

        # Manually clean up
        client.close()

        assert not client.is_authenticated()
        assert client.get_session_id() is None

    def test_multiple_clients_get_different_sessions(self, pihole_container):
        """Test that different clients get different session IDs."""
        client1 = PiHoleClient(
            base_url=PIHOLE_BASE_URL,
            password=PIHOLE_TEST_PASSWORD,
            verify_ssl=False,
        )
        client2 = PiHoleClient(
            base_url=PIHOLE_BASE_URL,
            password=PIHOLE_TEST_PASSWORD,
            verify_ssl=False,
        )

        with client1, client2:
            session_id_1 = client1.get_session_id()
            session_id_2 = client2.get_session_id()

            # Different clients should have different sessions
            assert session_id_1 != session_id_2
            assert session_id_1 is not None
            assert session_id_2 is not None

    def test_session_reuse_within_client(self, pihole_container):
        """Test that session ID remains consistent within client lifecycle."""
        client = PiHoleClient(
            base_url=PIHOLE_BASE_URL,
            password=PIHOLE_TEST_PASSWORD,
            verify_ssl=False,
        )

        with client:
            session_id_1 = client.get_session_id()
            session_id_2 = client.get_session_id()

            # Session should remain the same
            assert session_id_1 == session_id_2
            assert session_id_1 is not None
