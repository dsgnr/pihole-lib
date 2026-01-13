"""Pi-hole Lists API client."""

from pihole_lib.base import BasePiHoleAPIClient
from pihole_lib.models.lists import (
    AddListRequest,
    BatchDeleteItem,
    ListsResponse,
    ListType,
    PiHoleList,
    UpdateListRequest,
)
from pihole_lib.models.search import SearchResponse
from pihole_lib.utils import check_api_errors, make_pihole_request


class PiHoleLists(BasePiHoleAPIClient):
    """Pi-hole Lists API client.

    Handles domain list operations for blocklists and allowlists.

    Examples::

        from pihole_lib import PiHoleClient, ListType

        with PiHoleClient("http://192.168.1.100", password="secret") as client:
            # Get all lists
            all_lists = client.lists.get_lists()

            # Add a blocklist
            client.lists.add_list(
                address="https://example.com/domains.txt",
                list_type=ListType.BLOCK,
                comment="Ad servers"
            )

            # Search for domains
            results = client.lists.search_domains("example.com")

    """

    BASE_URL = "/api/lists"

    def get_lists(
        self,
        list_name: str | None = None,
        list_type: ListType | None = None,
    ) -> list[PiHoleList]:
        """Get Pi-hole domain lists.

        Args:
            list_name: Optional specific list name to retrieve.
            list_type: Optional list type filter (allow or block).

        Returns:
            List of PiHoleList objects.
        """
        endpoint = f"{self.BASE_URL}/{list_name}" if list_name else self.BASE_URL
        params = {"type": list_type.value} if list_type else None

        response = make_pihole_request(
            self._client,
            "GET",
            endpoint,
            params=params,
        )
        return ListsResponse.model_validate(response.json()).lists

    def add_list(
        self,
        address: str,
        list_type: ListType,
        comment: str | None = None,
        groups: list[int] | None = None,
        enabled: bool = True,
    ) -> list[PiHoleList]:
        """Add a new domain list to Pi-hole.

        Args:
            address: Address of the list.
            list_type: Type of list (ALLOW or BLOCK).
            comment: Optional comment for this list.
            groups: Group IDs to assign (defaults to [0]).
            enabled: Whether the list should be enabled (defaults to True).

        Returns:
            List of PiHoleList objects containing the created list.
        """
        request_data = AddListRequest(
            address=address,
            comment=comment,
            groups=groups or [0],
            enabled=enabled,
        )
        response = make_pihole_request(
            self._client,
            "POST",
            self.BASE_URL,
            params={"type": list_type.value},
            json=request_data.model_dump(exclude_none=True),
        )
        response_data = response.json()
        check_api_errors(response_data, address, "add list")
        return ListsResponse.model_validate(response_data).lists

    def delete_list(self, address: str, list_type: ListType) -> bool:
        """Delete a domain list from Pi-hole.

        Args:
            address: Address of the list to delete.
            list_type: Type of list (ALLOW or BLOCK).

        Returns:
            True if the list was successfully deleted.
        """
        response = make_pihole_request(
            self._client,
            "DELETE",
            f"{self.BASE_URL}/{address}",
            params={"type": list_type.value},
        )
        return bool(response.status_code == 204)

    def batch_delete_lists(self, items: list[BatchDeleteItem]) -> bool:
        """Delete multiple domain lists from Pi-hole.

        Args:
            items: List of BatchDeleteItem objects specifying lists to delete.

        Returns:
            True if all lists were successfully deleted.
        """
        items_data = [item.model_dump() for item in items]
        response = make_pihole_request(
            self._client,
            "POST",
            f"{self.BASE_URL}:batchDelete",
            json=items_data,
        )
        return bool(response.status_code == 204)

    def update_list(
        self,
        address: str,
        list_type: ListType,
        comment: str | None = None,
        groups: list[int] | None = None,
        enabled: bool = True,
    ) -> ListsResponse:
        """Update an existing domain list in Pi-hole.

        Args:
            address: Address of the list to update.
            list_type: Type of list (ALLOW or BLOCK).
            comment: Optional comment for this list.
            groups: Group IDs to assign (defaults to [0]).
            enabled: Whether the list should be enabled (defaults to True).

        Returns:
            ListsResponse with the updated list and processing results.
        """
        request_data = UpdateListRequest(
            comment=comment,
            type=list_type,
            groups=groups or [0],
            enabled=enabled,
        )
        response = make_pihole_request(
            self._client,
            "PUT",
            f"{self.BASE_URL}/{address}",
            params={"type": list_type.value},
            json=request_data.model_dump(exclude_none=True),
        )
        response_data = response.json()
        check_api_errors(response_data, address, "update list")
        return ListsResponse.model_validate(response_data)

    def search_domains(
        self,
        domain: str,
        partial: bool = False,
        max_results: int = 20,
        debug: bool = False,
    ) -> SearchResponse:
        """Search for domains in Pi-hole's lists.

        Args:
            domain: Domain (or part of domain) to search for.
            partial: Whether to enable partial matching (defaults to False).
            max_results: Maximum number of results (defaults to 20).
            debug: Whether to include debug information (defaults to False).

        Returns:
            SearchResponse with search results and metadata.
        """
        params = {"partial": partial, "N": max_results, "debug": debug}
        response = make_pihole_request(
            self._client,
            "GET",
            f"/api/search/{domain}",
            params=params,
        )
        return SearchResponse.model_validate(response.json())
