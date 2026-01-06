"""Pi-hole Info API client."""

from typing import TYPE_CHECKING

from .models import LoginInfo
from .utils import make_pihole_request

if TYPE_CHECKING:
    from .client import PiHoleClient


class PiHoleInfo:
    """Pi-hole Info API client.

    Handles information endpoints that don't require authentication.
    Uses a PiHoleClient instance for making requests.

    Examples:
        ```python
        from pihole_lib import PiHoleClient, PiHoleInfo

        # Create client and info instance
        client = PiHoleClient("http://192.168.1.100", password="secret")
        info = PiHoleInfo(client)
        login_info = info.get_login_info()
        client.close()

        # Or within client context
        with PiHoleClient("http://192.168.1.100", password="secret") as client:
            info = PiHoleInfo(client)
            login_info = info.get_login_info()
        ```
    """

    def __init__(self, client: "PiHoleClient") -> None:
        """Initialize a Pi-hole info client.

        Args:
            client: PiHoleClient instance to use for requests.
        """
        self._client = client

    def get_login_info(self) -> LoginInfo:
        """Get login page related information.

        This API hook returns information used on the login page to possibly
        display messages/warnings.

        Returns:
            LoginInfo: Login page information including HTTPS port, DNS status,
                      and request processing time.

        Raises:
            PiHoleConnectionError: Connection failed.
            PiHoleServerError: Server error.
            PiHoleAPIError: Other API errors.
        """
        response = make_pihole_request(
            self._client,
            "GET",
            "/api/info/login",
        )

        data = response.json()
        return LoginInfo(**data)
