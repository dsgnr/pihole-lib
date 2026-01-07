"""Integration tests for PiHoleClients against real Pi-hole."""

import pytest

from pihole_lib import PiHoleClient, PiHoleClients
from pihole_lib.exceptions import PiHoleServerError
from pihole_lib.models import ClientBatchDeleteItem

from .constants import (
    PIHOLE_BASE_URL,
    PIHOLE_TEST_PASSWORD,
)


class TestPiHoleClientsIntegration:
    """Test client management against real Pi-hole."""

    def test_get_clients_empty(self):
        """Should get empty clients list initially."""
        with PiHoleClient(PIHOLE_BASE_URL, password=PIHOLE_TEST_PASSWORD) as client:
            clients = PiHoleClients(client)

            result = clients.get_clients()

            # Should return a list (may be empty initially)
            assert isinstance(result, list)

    def test_client_lifecycle(self):
        """Test complete client lifecycle: add, get, update, delete."""
        with PiHoleClient(PIHOLE_BASE_URL, password=PIHOLE_TEST_PASSWORD) as client:
            clients = PiHoleClients(client)

            # Clean up any existing test clients first
            try:
                clients.delete_client("192.168.1.100")
            except Exception:
                pass  # Ignore if client doesn't exist

            # 1. Add a new client
            added_clients = clients.add_client(
                client="192.168.1.100", comment="Integration test client", groups=[0]
            )

            assert len(added_clients) == 1
            added_client = added_clients[0]
            assert added_client.client == "192.168.1.100"
            assert added_client.comment == "Integration test client"
            assert added_client.groups == [0]
            assert added_client.id > 0
            assert added_client.date_added > 0
            assert added_client.date_modified > 0

            # 2. Get all clients (should include our new client)
            all_clients = clients.get_clients()
            assert len(all_clients) >= 1

            # Find our client in the list
            our_client = None
            for c in all_clients:
                if c.client == "192.168.1.100":
                    our_client = c
                    break

            assert our_client is not None
            assert our_client.comment == "Integration test client"

            # 3. Get specific client
            specific_clients = clients.get_clients(client="192.168.1.100")
            assert len(specific_clients) == 1
            assert specific_clients[0].client == "192.168.1.100"
            assert specific_clients[0].comment == "Integration test client"

            # 4. Update the client
            update_response = clients.update_client(
                client="192.168.1.100",
                comment="Updated integration test client",
                groups=[0],
            )

            assert len(update_response.clients) == 1
            updated_client = update_response.clients[0]
            assert updated_client.comment == "Updated integration test client"
            # Date modified should be greater than or equal to the original
            assert updated_client.date_modified >= added_client.date_modified

            # Verify processing results
            assert update_response.processed is not None
            assert len(update_response.processed.success) == 1
            assert len(update_response.processed.errors) == 0
            assert update_response.processed.success[0].item == "192.168.1.100"

            # 5. Delete the client
            delete_success = clients.delete_client("192.168.1.100")
            assert delete_success is True

            # 6. Verify client is deleted
            final_clients = clients.get_clients()
            for c in final_clients:
                assert c.client != "192.168.1.100"

    def test_add_client_mac_address(self):
        """Test adding client by MAC address."""
        with PiHoleClient(PIHOLE_BASE_URL, password=PIHOLE_TEST_PASSWORD) as client:
            clients = PiHoleClients(client)

            # Clean up any existing test client first
            try:
                clients.delete_client("12:34:56:78:9A:BC")
            except Exception:
                pass

            # Add client by MAC address
            added_clients = clients.add_client(
                client="12:34:56:78:9A:BC", comment="MAC address client", groups=[0]
            )

            assert len(added_clients) == 1
            added_client = added_clients[0]
            assert added_client.client == "12:34:56:78:9A:BC"
            assert added_client.comment == "MAC address client"

            # Get specific client by MAC address
            specific_clients = clients.get_clients(client="12:34:56:78:9A:BC")
            assert len(specific_clients) == 1
            assert specific_clients[0].client == "12:34:56:78:9A:BC"

            # Clean up
            delete_success = clients.delete_client("12:34:56:78:9A:BC")
            assert delete_success is True

    def test_add_client_hostname(self):
        """Test adding client by hostname."""
        with PiHoleClient(PIHOLE_BASE_URL, password=PIHOLE_TEST_PASSWORD) as client:
            clients = PiHoleClients(client)

            # Clean up any existing test client first
            try:
                clients.delete_client("test-hostname.local")
            except Exception:
                pass

            # Add client by hostname
            added_clients = clients.add_client(
                client="test-hostname.local", comment="Hostname client", groups=[0]
            )

            assert len(added_clients) == 1
            added_client = added_clients[0]
            assert added_client.client == "test-hostname.local"
            assert added_client.comment == "Hostname client"

            # Clean up
            delete_success = clients.delete_client("test-hostname.local")
            assert delete_success is True

    def test_add_duplicate_client(self):
        """Test adding duplicate client should fail."""
        with PiHoleClient(PIHOLE_BASE_URL, password=PIHOLE_TEST_PASSWORD) as client:
            clients = PiHoleClients(client)

            # Clean up any existing test client first
            try:
                clients.delete_client("192.168.1.101")
            except Exception:
                pass

            # Add client first time
            clients.add_client(
                client="192.168.1.101", comment="First client", groups=[0]
            )

            # Try to add same client again - should fail
            with pytest.raises(PiHoleServerError):
                clients.add_client(
                    client="192.168.1.101", comment="Duplicate client", groups=[0]
                )

            # Clean up
            clients.delete_client("192.168.1.101")

    def test_batch_delete_clients(self):
        """Test batch deletion of multiple clients."""
        with PiHoleClient(PIHOLE_BASE_URL, password=PIHOLE_TEST_PASSWORD) as client:
            clients = PiHoleClients(client)

            # Clean up any existing test clients first
            test_clients = ["192.168.1.102", "192.168.1.103", "12:34:56:78:9A:BD"]
            for test_client in test_clients:
                try:
                    clients.delete_client(test_client)
                except Exception:
                    pass

            # Add multiple clients
            clients.add_client(
                client="192.168.1.102", comment="Batch test client 1", groups=[0]
            )
            clients.add_client(
                client="192.168.1.103", comment="Batch test client 2", groups=[0]
            )
            clients.add_client(
                client="12:34:56:78:9A:BD", comment="Batch test MAC client", groups=[0]
            )

            # Verify clients were added
            all_clients = clients.get_clients()
            added_client_ids = set()
            for c in all_clients:
                if c.client in test_clients:
                    added_client_ids.add(c.client)
            assert len(added_client_ids) == 3

            # Batch delete
            items_to_delete = [
                ClientBatchDeleteItem(item="192.168.1.102"),
                ClientBatchDeleteItem(item="192.168.1.103"),
                ClientBatchDeleteItem(item="12:34:56:78:9A:BD"),
            ]

            batch_success = clients.batch_delete_clients(items_to_delete)
            assert batch_success is True

            # Verify clients were deleted
            final_clients = clients.get_clients()
            for c in final_clients:
                assert c.client not in test_clients

    def test_get_client_suggestions(self):
        """Test getting client suggestions."""
        with PiHoleClient(PIHOLE_BASE_URL, password=PIHOLE_TEST_PASSWORD) as client:
            clients = PiHoleClients(client)

            # Get client suggestions
            suggestions = clients.get_client_suggestions()

            # Should return a list (may be empty in test environment)
            assert isinstance(suggestions, list)

            # If there are suggestions, verify structure
            for suggestion in suggestions:
                assert hasattr(suggestion, "client")
                assert hasattr(suggestion, "name")
                assert hasattr(suggestion, "comment")
                assert hasattr(suggestion, "groups")
                assert hasattr(suggestion, "id")
                assert hasattr(suggestion, "date_added")
                assert hasattr(suggestion, "date_modified")

    def test_update_nonexistent_client(self):
        """Test updating a client that doesn't exist."""
        with PiHoleClient(PIHOLE_BASE_URL, password=PIHOLE_TEST_PASSWORD) as client:
            clients = PiHoleClients(client)

            # Try to update a client that doesn't exist
            # Pi-hole may or may not raise an error for this, so we just check it doesn't crash
            try:
                response = clients.update_client(
                    client="192.168.1.999", comment="Nonexistent client", groups=[0]
                )
                # If it succeeds, check the response structure
                assert hasattr(response, "clients")
                assert hasattr(response, "processed")
            except PiHoleServerError:
                # This is also acceptable behavior
                pass

    def test_delete_nonexistent_client(self):
        """Test deleting a client that doesn't exist."""
        with PiHoleClient(PIHOLE_BASE_URL, password=PIHOLE_TEST_PASSWORD) as client:
            clients = PiHoleClients(client)

            # Try to delete a client that doesn't exist
            # Pi-hole may return True even for non-existent clients
            result = clients.delete_client("192.168.1.999")
            # Just check that it returns a boolean
            assert isinstance(result, bool)

    def test_client_with_property_access(self):
        """Test client management using property access on PiHoleClient."""
        with PiHoleClient(PIHOLE_BASE_URL, password=PIHOLE_TEST_PASSWORD) as client:
            # Clean up any existing test client first
            try:
                client.clients.delete_client("192.168.1.104")
            except Exception:
                pass

            # Add client using property access
            added_clients = client.clients.add_client(
                client="192.168.1.104", comment="Property access test", groups=[0]
            )

            assert len(added_clients) == 1
            assert added_clients[0].client == "192.168.1.104"

            # Get clients using property access
            all_clients = client.clients.get_clients()
            assert isinstance(all_clients, list)

            # Find our client
            our_client = None
            for c in all_clients:
                if c.client == "192.168.1.104":
                    our_client = c
                    break

            assert our_client is not None
            assert our_client.comment == "Property access test"

            # Update using property access
            update_response = client.clients.update_client(
                client="192.168.1.104",
                comment="Updated via property access",
                groups=[0],
            )

            assert len(update_response.clients) == 1
            assert update_response.clients[0].comment == "Updated via property access"

            # Delete using property access
            delete_success = client.clients.delete_client("192.168.1.104")
            assert delete_success is True
