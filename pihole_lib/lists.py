"""Pi-hole Lists API client."""


from .base import BasePiHoleAPIClient
from .models import (
    AddListRequest,
    BatchDeleteItem,
    ListsResponse,
    ListType,
    PiHoleList,
    SearchResponse,
    UpdateListRequest,
)
from .utils import check_api_errors, make_pihole_request


class PiHoleLists(BasePiHoleAPIClient):
    """Pi-hole Lists API client.

    Handles domain list operations using the Lists endpoint.
    Uses a PiHoleClient instance for making authenticated requests.

    Examples::

        from pihole_lib import PiHoleClient, PiHoleLists, ListType

        with PiHoleClient("http://192.168.1.100", password="secret") as client:
            lists = PiHoleLists(client)

            # Get all lists
            all_lists = lists.get_lists()
            print(f"Found {len(all_lists)} lists")

            # Add a new list
            lists.add_list(
                address="https://hosts-file.net/ad_servers.txt",
                list_type=ListType.BLOCK,
                comment="Ad servers"
            )

    """

    BASE_URL = "/api/lists"

    def get_lists(
        self,
        list_name: str | None = None,
        list_type: ListType | None = None,
    ) -> list[PiHoleList]:
        """Get Pi-hole domain lists.

        Retrieve domain lists configured in Pi-hole. Lists are collections of domain names
        that are blocked or allowed. Authentication is required.

        Args:
            list_name: Optional specific list name to retrieve.
            list_type: Optional list type filter ("allow" or "block").

        Returns:
            List of PiHoleList objects.

        Raises:
            PiHoleConnectionError: Connection failed.
            PiHoleAuthenticationError: Authentication failed.
            PiHoleServerError: Server error.
            PiHoleAPIError: Other API errors.

        Examples::

            # Get all lists
            all_lists = lists.get_lists()

            # Get only allow lists
            allow_lists = lists.get_lists(list_type=ListType.ALLOW)

            # Get specific list by name
            specific_lists = lists.get_lists(list_name="my_blocklist")
            if specific_lists:
                my_list = specific_lists[0]

        """
        endpoint = f"{self.BASE_URL}/{list_name}" if list_name else self.BASE_URL
        params = {"type": list_type.value} if list_type else None

        response = make_pihole_request(
            self._client,
            "GET",
            endpoint,
            params=params,
        )

        response_data = response.json()
        lists_response = ListsResponse.model_validate(response_data)
        return lists_response.lists

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
            list_type: Type of list (ListType.ALLOW or ListType.BLOCK).
            comment: Optional comment for this list.
            groups: Group IDs to assign the list to (defaults to [0]).
            enabled: Whether the list should be enabled (defaults to True).

        Returns:
            List of PiHoleList objects containing the created list.

        Raises:
            PiHoleServerError: If Pi-hole reports an error (e.g., duplicate list).
            PiHoleConnectionError: Connection failed.
            PiHoleAuthenticationError: Authentication failed.

        Examples::

            # Add a blocklist
            new_lists = lists.add_list(
                address="https://example.com/domains.txt",
                list_type=ListType.BLOCK,
                comment="Ad servers"
            )

            if new_lists:
                print(f"Added list: {new_lists[0].address}")

            # Add an allowlist
            new_lists = lists.add_list(
                address="example.com",
                list_type=ListType.ALLOW
            )

        """
        request_data = AddListRequest(
            address=address,
            comment=comment,
            groups=groups or [0],  # Default group ID
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

        # Check for Pi-hole errors in the response
        check_api_errors(response_data, address, "add list")

        lists_response = ListsResponse.model_validate(response_data)
        return lists_response.lists

    def delete_list(self, address: str, list_type: ListType) -> bool:
        """Delete a domain list from Pi-hole.

        Args:
            address: Address of the list to delete.
            list_type: Type of list (ListType.ALLOW or ListType.BLOCK).

        Returns:
            True if the list was successfully deleted or raises.

        Raises:
            PiHoleConnectionError: Connection failed.
            PiHoleAuthenticationError: Authentication failed.
            PiHoleServerError: Server error or list not found.
            PiHoleAPIError: Other API errors.

        Examples::

            # Delete a blocklist
            success = lists.delete_list(
                address="https://example.com/domains.txt",
                list_type=ListType.BLOCK
            )
            print(f"Deletion successful: {success}")

            # Delete an allowlist
            success = lists.delete_list(
                address="example.com",
                list_type=ListType.ALLOW
            )

        """
        endpoint = f"{self.BASE_URL}/{address}"
        params = {"type": list_type.value}

        response = make_pihole_request(
            self._client,
            "DELETE",
            endpoint,
            params=params,
        )

        # Pi-hole returns 204 No Content on successful deletion
        return response.status_code == 204

    def batch_delete_lists(self, items: list[BatchDeleteItem]) -> bool:
        """Delete multiple domain lists from Pi-hole.

        Args:
            items: List of BatchDeleteItem objects specifying lists to delete.

        Returns:
            True if all lists were successfully deleted.

        Raises:
            PiHoleConnectionError: Connection failed.
            PiHoleAuthenticationError: Authentication failed.
            PiHoleServerError: Server error.
            PiHoleAPIError: Other API errors.

        Examples::

            from pihole_lib.models import BatchDeleteItem

            # Delete multiple lists
            items_to_delete = [
                BatchDeleteItem(item="example.com", type=ListType.ALLOW),
                BatchDeleteItem(item="ads.example.com", type=ListType.BLOCK),
            ]

            success = lists.batch_delete_lists(items_to_delete)
            print(f"Batch deletion successful: {success}")

        """
        # Convert BatchDeleteItem objects to dictionaries
        items_data = [item.model_dump() for item in items]

        response = make_pihole_request(
            self._client,
            "POST",
            f"{self.BASE_URL}:batchDelete",
            json=items_data,
        )

        # Pi-hole returns 204 No Content on successful batch deletion
        return response.status_code == 204

    def update_list(
        self,
        address: str,
        list_type: ListType,
        comment: str | None = None,
        groups: list[int] | None = None,
        enabled: bool = True,
    ) -> ListsResponse:
        """Update an existing domain list in Pi-hole.

        Replace/update a list's properties. All required parameters must be provided
        to ensure properties are retained. Read-only fields (id, date_added) are
        preserved, and date_modified is automatically updated on success.

        Args:
            address: Address of the list to update.
            list_type: Type of list (ListType.ALLOW or ListType.BLOCK).
            comment: Optional comment for this list.
            groups: Group IDs to assign the list to (defaults to [0]).
            enabled: Whether the list should be enabled (defaults to True).

        Returns:
            ListsResponse object containing the updated list and processing results.

        Raises:
            PiHoleConnectionError: Connection failed.
            PiHoleAuthenticationError: Authentication failed.
            PiHoleServerError: Server error or list not found.
            PiHoleAPIError: Other API errors.

        Examples::

            # Update a list's comment and disable it
            response = lists.update_list(
                address="example.com",
                list_type=ListType.ALLOW,
                comment="Updated comment",
                groups=[0, 1],
                enabled=False
            )

            if response.processed and response.processed.errors:
                for error in response.processed.errors:
                    print(f"Error: {error.error}")
            else:
                updated_list = response.lists[0]
                print(f"Updated list: {updated_list.address}")
                print(f"New comment: {updated_list.comment}")
                print(f"Enabled: {updated_list.enabled}")

        """
        request_data = UpdateListRequest(
            comment=comment,
            type=list_type,
            groups=groups or [0],
            enabled=enabled,
        )

        endpoint = f"{self.BASE_URL}/{address}"
        params = {"type": list_type.value}

        response = make_pihole_request(
            self._client,
            "PUT",
            endpoint,
            params=params,
            json=request_data.model_dump(exclude_none=True),
        )

        response_data = response.json()

        # Check for Pi-hole errors in the response
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

        Search for domains in Pi-hole's domain lists. The specified domain is
        automatically converted to lowercase. International domain names (IDNs)
        are internally converted to punycode before matching.

        Args:
            domain: Domain (or part of domain) to search for.
            partial: Whether to enable partial matching (defaults to False).
            max_results: Maximum number of results to return (defaults to 20).
            debug: Whether to include debug information (defaults to False).

        Returns:
            SearchResponse object containing search results and metadata.

        Raises:
            PiHoleConnectionError: Connection failed.
            PiHoleAuthenticationError: Authentication failed.
            PiHoleServerError: Server error.
            PiHoleAPIError: Other API errors.

        Examples::

            # Exact search
            response = lists.search_domains("example.com")
            print(f"Found {response.search.results.total} results")

            for domain_match in response.search.domains:
                print(f"Domain: {domain_match.address} ({domain_match.type})")

            for gravity_match in response.search.gravity:
                print(f"Gravity: {gravity_match.address} ({gravity_match.type})")

            # Partial search with more results
            response = lists.search_domains(
                domain="example",
                partial=True,
                max_results=50,
                debug=True
            )

            print(f"Search parameters: {response.search.parameters}")
            print(f"Domain matches: {response.search.results.domains.exact}")
            print(f"Gravity matches: {response.search.results.gravity.block}")

        """
        endpoint = f"/api/search/{domain}"
        params = {
            "partial": partial,
            "N": max_results,
            "debug": debug,
        }

        response = make_pihole_request(
            self._client,
            "GET",
            endpoint,
            params=params,
        )

        response_data = response.json()
        return SearchResponse.model_validate(response_data)
