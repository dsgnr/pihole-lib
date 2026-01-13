"""Pi-hole Clients API client."""

from urllib.parse import quote

from pihole_lib.base import BasePiHoleAPIClient
from pihole_lib.models.client_mgmt import (
    Client,
    ClientBatchDeleteItem,
    ClientRequest,
    ClientsResponse,
    ClientSuggestionsResponse,
    ClientUpdateRequest,
)
from pihole_lib.utils import check_api_errors, make_pihole_request


class PiHoleClients(BasePiHoleAPIClient):
    """Pi-hole Clients API client.

    Handles client management operations. Clients can be identified by IP address,
    MAC address, hostname, or interface.

    Examples::

        from pihole_lib import PiHoleClient

        with PiHoleClient("http://192.168.1.100", password="secret") as client:
            # Get all clients
            all_clients = client.clients.get_clients()

            # Add a new client
            client.clients.add_client(
                client="192.168.1.50",
                comment="John's laptop",
                groups=[0, 1]
            )

            # Get client suggestions
            suggestions = client.clients.get_client_suggestions()

    """

    BASE_URL = "/api/clients"

    def get_clients(self, client: str | None = None) -> list[Client]:
        """Get Pi-hole clients.

        Args:
            client: Optional specific client identifier to retrieve.

        Returns:
            List of Client objects.
        """
        endpoint = self.BASE_URL
        if client:
            encoded_client = quote(client, safe="")
            endpoint = f"{self.BASE_URL}/{encoded_client}"

        response = make_pihole_request(self._client, "GET", endpoint)
        return ClientsResponse.model_validate(response.json()).clients

    def add_client(
        self,
        client: str,
        comment: str | None = None,
        groups: list[int] | None = None,
    ) -> list[Client]:
        """Add a new client to Pi-hole.

        Args:
            client: Client identifier (IP, MAC, hostname, or interface).
            comment: Optional comment for this client.
            groups: Group IDs to assign (defaults to [0]).

        Returns:
            List of Client objects containing the created client.
        """
        request_data = ClientRequest(
            client=client,
            comment=comment,
            groups=groups or [0],
        )
        response = make_pihole_request(
            self._client,
            "POST",
            self.BASE_URL,
            json=request_data.model_dump(exclude_none=True),
        )
        response_data = response.json()
        check_api_errors(response_data, client, "add client")
        return ClientsResponse.model_validate(response_data).clients

    def update_client(
        self,
        client: str,
        comment: str | None = None,
        groups: list[int] | None = None,
    ) -> ClientsResponse:
        """Update an existing client in Pi-hole.

        Args:
            client: Client identifier to update.
            comment: Optional comment for this client.
            groups: Group IDs to assign (defaults to [0]).

        Returns:
            ClientsResponse with the updated client and processing results.
        """
        request_data = ClientUpdateRequest(
            comment=comment,
            groups=groups or [0],
        )
        encoded_client = quote(client, safe="")
        response = make_pihole_request(
            self._client,
            "PUT",
            f"{self.BASE_URL}/{encoded_client}",
            json=request_data.model_dump(exclude_none=True),
        )
        response_data = response.json()
        check_api_errors(response_data, client, "update client")
        return ClientsResponse.model_validate(response_data)

    def delete_client(self, client: str) -> bool:
        """Delete a client from Pi-hole.

        Args:
            client: Client identifier to delete.

        Returns:
            True if the client was successfully deleted.
        """
        encoded_client = quote(client, safe="")
        response = make_pihole_request(
            self._client,
            "DELETE",
            f"{self.BASE_URL}/{encoded_client}",
        )
        return bool(response.status_code == 204)

    def batch_delete_clients(self, items: list[ClientBatchDeleteItem]) -> bool:
        """Delete multiple clients from Pi-hole.

        Args:
            items: List of ClientBatchDeleteItem objects.

        Returns:
            True if all clients were successfully deleted.
        """
        items_data = [item.model_dump() for item in items]
        response = make_pihole_request(
            self._client,
            "POST",
            f"{self.BASE_URL}:batchDelete",
            json=items_data,
        )
        return bool(response.status_code == 204)

    def get_client_suggestions(self) -> list[Client]:
        """Get client suggestions from Pi-hole.

        Returns unconfigured clients that have been seen by Pi-hole.

        Returns:
            List of Client objects representing unconfigured clients.
        """
        response = make_pihole_request(
            self._client,
            "GET",
            f"{self.BASE_URL}/_suggestions",
        )
        return ClientSuggestionsResponse.model_validate(response.json()).clients
