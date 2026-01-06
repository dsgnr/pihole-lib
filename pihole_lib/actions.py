"""Pi-hole Actions API client."""

from collections.abc import Iterator
from typing import TYPE_CHECKING

from .base import BasePiHoleAPIClient
from .constants import API_ACTION_GRAVITY
from .utils import make_pihole_request

if TYPE_CHECKING:
    pass


class PiHoleActions(BasePiHoleAPIClient):
    """Pi-hole Actions API client.

    Handles action endpoints that perform operations on Pi-hole.
    Uses a PiHoleClient instance for making authenticated requests.

    Examples:
        ```python
        from pihole_lib import PiHoleClient, PiHoleActions

        with PiHoleClient("http://192.168.1.100", password="secret") as client:
            actions = PiHoleActions(client)

            # Update gravity database with streaming output
            for line in actions.update_gravity():
                print(line.strip())

            # Update gravity with colored output
            for line in actions.update_gravity(color=True):
                print(line.strip())
        ```
    """

    def update_gravity(self, color: bool = False) -> Iterator[str]:
        """Update Pi-hole's gravity database (adlists).

        This endpoint triggers Pi-hole's gravity update process, which downloads
        and processes all configured adlists to update the blocking database.
        The output is streamed with chunked encoding.

        Args:
            color: Include ANSI color escape codes in the streamed output.
                  Defaults to False to prevent colored output for API consumers
                  that don't need formatting.

        Yields:
            Lines of output from the gravity update process.

        Raises:
            PiHoleConnectionError: Connection failed.
            PiHoleAuthenticationError: Authentication failed.
            PiHoleServerError: Server error.
            PiHoleAPIError: Other API errors.

        Examples:
            ```python
            # Basic gravity update
            for line in actions.update_gravity():
                print(line.strip())

            # Gravity update with colored output
            for line in actions.update_gravity(color=True):
                print(line.strip())
            ```
        """
        params = {"color": "true"} if color else None

        response = make_pihole_request(
            self._client,
            "POST",
            API_ACTION_GRAVITY,
            params=params,
            stream=True,
        )

        # Stream the response line by line
        for line in response.iter_lines(decode_unicode=True):
            if line:  # Skip empty lines
                yield line
