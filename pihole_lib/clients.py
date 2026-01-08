"""Pi-hole Clients API client."""

from urllib.parse import quote

from .base import BasePiHoleAPIClient
from .models import (
    Client,
    ClientBatchDeleteItem,
    ClientRequest,
    ClientsResponse,
    ClientSuggestionsResponse,
    ClientUpdateRequest,
)
from .utils import check_api_errors, make_pihole_request


class PiHoleClients(BasePiHoleAPIClient):
    """Pi-hole Clients API client.

    Handles client management operations using the Clients endpoint.
    Uses a PiHoleClient instance for making authenticated requests.

    Clients may be described either by their IP addresses (IPv4 and IPv6 are supported),
    IP subnets (CIDR notation, like 192.168.2.0/24), their MAC addresses
    (like 12:34:56:78:9A:BC), by their hostnames (like localhost), or by the interface
    they are connected to (prefaced with a colon, like :eth0).

    Note that client recognition by IP addresses (incl. subnet ranges) is preferred over
    MAC address, host name or interface recognition as the two latter will only be
    available after some time. Furthermore, MAC address recognition only works for
    devices at most one networking hop away from your Pi-hole.

    Examples::

        from pihole_lib import PiHoleClient, PiHoleClients

        with PiHoleClient("http://192.168.1.100", password="secret") as client:
            clients = PiHoleClients(client)

            # Get all clients
            all_clients = clients.get_clients()
            print(f"Found {len(all_clients)} clients")

            # Add a new client
            clients.add_client(
                client="192.168.1.50",
                comment="John's laptop",
                groups=[0, 1]
            )

            # Get client suggestions
            suggestions = clients.get_client_suggestions()
            print(f"Found {len(suggestions)} unconfigured clients")

    """

    BASE_URL = "/api/clients"

    def get_clients(self, client: str | None = None) -> list[Client]:
        """Get Pi-hole clients.

        Retrieve clients configured in Pi-hole. Clients are devices that can be
        assigned to groups for different filtering policies. Authentication is required.

        Args:
            client: Optional specific client identifier to retrieve.

        Returns:
            List of Client objects.

        Raises:
            PiHoleConnectionError: Connection failed.
            PiHoleAuthenticationError: Authentication failed.
            PiHoleServerError: Server error.
            PiHoleAPIError: Other API errors.

        Examples::

            # Get all clients
            all_clients = clients.get_clients()

            # Get specific client by IP
            specific_client = clients.get_clients(client="192.168.1.50")
            if specific_client:
                client_info = specific_client[0]
                print(f"Client: {client_info.client}")
                print(f"Comment: {client_info.comment}")
                print(f"Groups: {client_info.groups}")

            # Get client by MAC address
            mac_client = clients.get_clients(client="12:34:56:78:9A:BC")

            # Get client by hostname
            hostname_client = clients.get_clients(client="laptop.local")

        """
        endpoint = self.BASE_URL
        if client:
            # URL encode the client identifier for safe transmission
            encoded_client = quote(client, safe="")
            endpoint = f"{self.BASE_URL}/{encoded_client}"

        response = make_pihole_request(
            self._client,
            "GET",
            endpoint,
        )

        response_data = response.json()
        clients_response = ClientsResponse.model_validate(response_data)
        return clients_response.clients

    def add_client(
        self,
        client: str,
        comment: str | None = None,
        groups: list[int] | None = None,
    ) -> list[Client]:
        """Add a new client to Pi-hole.

        Creates a new client in the clients object. Clients may be described either by
        their IP addresses (IPv4 and IPv6 are supported), IP subnets (CIDR notation,
        like 192.168.2.0/24), their MAC addresses (like 12:34:56:78:9A:BC), by their
        hostnames (like localhost), or by the interface they are connected to
        (prefaced with a colon, like :eth0).

        Args:
            client: Client identifier (IP, MAC, hostname, or interface).
            comment: Optional comment for this client.
            groups: Group IDs to assign the client to (defaults to [0]).

        Returns:
            List of Client objects containing the created client.

        Raises:
            PiHoleServerError: If Pi-hole reports an error (e.g., duplicate client).
            PiHoleConnectionError: Connection failed.
            PiHoleAuthenticationError: Authentication failed.

        Examples::

            # Add client by IP address
            new_clients = clients.add_client(
                client="192.168.1.50",
                comment="John's laptop",
                groups=[0, 1]
            )

            # Add client by MAC address
            new_clients = clients.add_client(
                client="12:34:56:78:9A:BC",
                comment="Smart TV"
            )

            # Add client by hostname
            new_clients = clients.add_client(
                client="laptop.local",
                comment="Development machine"
            )

            # Add client by subnet (CIDR notation)
            new_clients = clients.add_client(
                client="192.168.2.0/24",
                comment="Guest network"
            )

            # Add client by interface
            new_clients = clients.add_client(
                client=":eth0",
                comment="Ethernet interface clients"
            )

            if new_clients:
                print(f"Added client: {new_clients[0].client}")

        """
        request_data = ClientRequest(
            client=client,
            comment=comment,
            groups=groups or [0],  # Default group ID
        )

        response = make_pihole_request(
            self._client,
            "POST",
            self.BASE_URL,
            json=request_data.model_dump(exclude_none=True),
        )

        response_data = response.json()

        # Check for Pi-hole errors in the response
        check_api_errors(response_data, client, "add client")

        clients_response = ClientsResponse.model_validate(response_data)
        return clients_response.clients

    def update_client(
        self,
        client: str,
        comment: str | None = None,
        groups: list[int] | None = None,
    ) -> ClientsResponse:
        """Update an existing client in Pi-hole.

        Replace/update a client's properties. All required parameters must be provided
        to ensure properties are retained. Read-only fields (id, date_added) are
        preserved, and date_modified is automatically updated on success.

        Args:
            client: Client identifier to update.
            comment: Optional comment for this client.
            groups: Group IDs to assign the client to (defaults to [0]).

        Returns:
            ClientsResponse object containing the updated client and processing results.

        Raises:
            PiHoleConnectionError: Connection failed.
            PiHoleAuthenticationError: Authentication failed.
            PiHoleServerError: Server error or client not found.
            PiHoleAPIError: Other API errors.

        Examples::

            # Update a client's comment and groups
            response = clients.update_client(
                client="192.168.1.50",
                comment="Updated comment for John's laptop",
                groups=[0, 1, 2]
            )

            if response.processed and response.processed.errors:
                for error in response.processed.errors:
                    print(f"Error: {error.error}")
            else:
                updated_client = response.clients[0]
                print(f"Updated client: {updated_client.client}")
                print(f"New comment: {updated_client.comment}")
                print(f"Groups: {updated_client.groups}")

            # Update client by MAC address
            response = clients.update_client(
                client="12:34:56:78:9A:BC",
                comment="Updated Smart TV settings",
                groups=[0]
            )

        """
        request_data = ClientUpdateRequest(
            comment=comment,
            groups=groups or [0],
        )

        # URL encode the client identifier for safe transmission
        encoded_client = quote(client, safe="")
        endpoint = f"{self.BASE_URL}/{encoded_client}"

        response = make_pihole_request(
            self._client,
            "PUT",
            endpoint,
            json=request_data.model_dump(exclude_none=True),
        )

        response_data = response.json()

        # Check for Pi-hole errors in the response
        check_api_errors(response_data, client, "update client")

        return ClientsResponse.model_validate(response_data)

    def delete_client(self, client: str) -> bool:
        """Delete a client from Pi-hole.

        Args:
            client: Client identifier to delete.

        Returns:
            True if the client was successfully deleted.

        Raises:
            PiHoleConnectionError: Connection failed.
            PiHoleAuthenticationError: Authentication failed.
            PiHoleServerError: Server error or client not found.
            PiHoleAPIError: Other API errors.

        Examples::

            # Delete client by IP
            success = clients.delete_client("192.168.1.50")
            print(f"Deletion successful: {success}")

            # Delete client by MAC address
            success = clients.delete_client("12:34:56:78:9A:BC")

            # Delete client by hostname
            success = clients.delete_client("laptop.local")

        """
        # URL encode the client identifier for safe transmission
        encoded_client = quote(client, safe="")
        endpoint = f"{self.BASE_URL}/{encoded_client}"

        response = make_pihole_request(
            self._client,
            "DELETE",
            endpoint,
        )

        # Pi-hole returns 204 No Content on successful deletion
        return response.status_code == 204

    def batch_delete_clients(self, items: list[ClientBatchDeleteItem]) -> bool:
        """Delete multiple clients from Pi-hole.

        Args:
            items: List of ClientBatchDeleteItem objects specifying clients to delete.

        Returns:
            True if all clients were successfully deleted.

        Raises:
            PiHoleConnectionError: Connection failed.
            PiHoleAuthenticationError: Authentication failed.
            PiHoleServerError: Server error.
            PiHoleAPIError: Other API errors.

        Examples::

            from pihole_lib.models import ClientBatchDeleteItem

            # Delete multiple clients
            items_to_delete = [
                ClientBatchDeleteItem(item="192.168.1.50"),
                ClientBatchDeleteItem(item="12:34:56:78:9A:BC"),
                ClientBatchDeleteItem(item="laptop.local"),
            ]

            success = clients.batch_delete_clients(items_to_delete)
            print(f"Batch deletion successful: {success}")

        """
        # Convert ClientBatchDeleteItem objects to dictionaries
        items_data = [item.model_dump() for item in items]

        response = make_pihole_request(
            self._client,
            "POST",
            f"{self.BASE_URL}:batchDelete",
            json=items_data,
        )

        # Pi-hole returns 204 No Content on successful batch deletion
        return response.status_code == 204

    def get_client_suggestions(self) -> list[Client]:
        """Get client suggestions from Pi-hole.

        Returns a list of unconfigured clients that have been seen by Pi-hole.
        These are clients that have made DNS queries but are not yet configured
        in the clients database.

        Returns:
            List of Client objects representing unconfigured clients.

        Raises:
            PiHoleConnectionError: Connection failed.
            PiHoleAuthenticationError: Authentication failed.
            PiHoleServerError: Server error.
            PiHoleAPIError: Other API errors.

        Examples::

            # Get unconfigured clients
            suggestions = clients.get_client_suggestions()
            print(f"Found {len(suggestions)} unconfigured clients")

            for suggestion in suggestions:
                print(f"Suggested client: {suggestion.client}")
                if suggestion.name:
                    print(f"  Name: {suggestion.name}")
                print(f"  Last seen: {suggestion.date_modified}")

            # Add suggested clients to configuration
            for suggestion in suggestions[:5]:  # Add first 5 suggestions
                clients.add_client(
                    client=suggestion.client,
                    comment=f"Auto-added from suggestions: {suggestion.name or 'Unknown'}"
                )

        """
        endpoint = f"{self.BASE_URL}/_suggestions"

        response = make_pihole_request(
            self._client,
            "GET",
            endpoint,
        )

        response_data = response.json()
        suggestions_response = ClientSuggestionsResponse.model_validate(response_data)
        return suggestions_response.clients
