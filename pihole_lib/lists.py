"""Pi-hole Lists API client."""

from typing import TYPE_CHECKING

from .models import AddListRequest, ListType, PiHoleList
from .utils import make_pihole_request

if TYPE_CHECKING:
    from .client import PiHoleClient


class PiHoleLists:
    """Pi-hole Lists API client.

    Handles domain list operations using the Lists endpoint.
    Uses a PiHoleClient instance for making authenticated requests.

    Examples:
        ```python
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
        ```
    """

    def __init__(self, client: "PiHoleClient") -> None:
        """Initialize a Pi-hole lists client.

        Args:
            client: PiHoleClient instance to use for requests.
        """
        self._client = client

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

        Examples:
            ```python
            # Get all lists
            all_lists = lists.get_lists()

            # Get only allow lists
            allow_lists = lists.get_lists(list_type=ListType.ALLOW)

            # Get specific list by name
            my_list = lists.get_lists(list_name="my_blocklist")
            ```
        """
        endpoint = "/api/lists"
        if list_name:
            endpoint += f"/{list_name}"

        params = {}
        if list_type:
            params["type"] = list_type.value

        response = make_pihole_request(
            self._client,
            "GET",
            endpoint,
            params=params if params else None,
        )

        response_data = response.json()
        return [PiHoleList(**list_data) for list_data in response_data["lists"]]

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
            List of PiHoleList objects returned by the API.

        Raises:
            PiHoleServerError: If Pi-hole reports an error (e.g., duplicate list).
            PiHoleConnectionError: Connection failed.
            PiHoleAuthenticationError: Authentication failed.

        Examples:
            ```python
            # Add a blocklist
            lists.add_list(
                address="https://example.com/domains.txt",
                list_type=ListType.BLOCK,
                comment="Ad servers"
            )

            # Add an allowlist
            lists.add_list(
                address="example.com",
                list_type=ListType.ALLOW
            )
            ```
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
            "/api/lists",
            params={"type": list_type.value},
            json=request_data.model_dump(exclude_none=True),
        )

        response_data = response.json()

        # Check for Pi-hole errors in the response
        processed = response_data.get("processed")
        if processed and processed.get("errors"):
            errors = processed["errors"]
            for error in errors:
                if error.get("item") == address:
                    error_msg = error.get("error", "Unknown error")
                    from .exceptions import PiHoleServerError

                    raise PiHoleServerError(
                        f"Failed to add list '{address}': {error_msg}"
                    )

        return [PiHoleList(**list_data) for list_data in response_data["lists"]]
