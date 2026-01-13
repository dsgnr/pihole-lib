"""Base classes for Pi-hole API clients."""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pihole_lib.client import PiHoleClient


class BasePiHoleAPIClient:
    """Base class for Pi-hole API clients.

    Provides common functionality for all API client classes.
    """

    __slots__ = ("_client",)

    # Subclasses should override this
    BASE_URL: str = ""

    def __init__(self, client: "PiHoleClient") -> None:
        """Initialize the API client.

        Args:
            client: PiHoleClient instance to use for requests.
        """
        self._client = client
