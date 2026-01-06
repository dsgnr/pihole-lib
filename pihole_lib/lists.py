"""Pi-hole Lists API client."""

from typing import TYPE_CHECKING

from .models import ListType, PiHoleList
from .utils import make_pihole_request

if TYPE_CHECKING:
    from .client import PiHoleClient


class PiHoleLists:
    """Pi-hole Lists API client.

    Handles domain list operations using the Lists endpoint.
    Uses a PiHoleClient instance for making authenticated requests.

    Examples:
        ```python
        from pihole_lib import PiHoleClient, PiHoleLists

        # Create client and lists instance
        with PiHoleClient("http://192.168.1.100", password="secret") as client:
            lists = PiHoleLists(client)

            # Get all lists
            all_lists = lists.get_lists()
            print(f"Found {len(all_lists)} lists")

            # Get only block lists
            block_lists = lists.get_lists(list_type=ListType.BLOCK)
            print(f"Found {len(block_lists)} block lists")

            # Get specific list
            specific_list = lists.get_lists(list_name="my_list")
            if specific_list:
                print(f"List: {specific_list[0].address}")
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

        Retrieve domain lists configured in Pi-hole. Lists are collections of domains
        that are blocked or allowed for ad filtering. Authentication is required.

        Args:
            list_name: Optional specific list name to retrieve. If provided,
                      only the list with this exact name will be returned.
            list_type: Optional list type filter ("allow" or "block").
                      If provided, only lists of this type will be returned.

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
        # Build endpoint path
        endpoint = "/api/lists"
        if list_name:
            endpoint += f"/{list_name}"

        # Build query parameters
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
        # Return the lists directly instead of wrapped in a response object
        return [PiHoleList(**list_data) for list_data in response_data["lists"]]
