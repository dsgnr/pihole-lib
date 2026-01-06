"""Pi-hole API Python Library.

A Python library for interacting with Pi-hole through its API.
Handles authentication and session management.

Examples:
    ```python
    from pihole_lib import PiHoleClient, PiHoleInfo

    # For authenticated operations
    with PiHoleClient("http://192.168.1.100", password="secret") as client:
        # Client is authenticated and ready for API operations
        pass

    # For information that doesn't require authentication
    with PiHoleInfo("http://192.168.1.100") as info:
        login_info = info.get_login_info()
        print(f"HTTPS Port: {login_info.https_port}")
    ```
"""

from .client import PiHoleClient
from .exceptions import (
    PiHoleAPIError,
    PiHoleAuthenticationError,
    PiHoleConnectionError,
    PiHoleServerError,
)
from .info import PiHoleInfo
from .models import AuthResponse, LoginInfo, PiHoleAuthSession

__version__ = "0.1.0"
__author__ = "@dsgnr"

__all__ = [
    "PiHoleClient",
    "PiHoleInfo",
    "PiHoleAPIError",
    "PiHoleAuthenticationError",
    "PiHoleConnectionError",
    "PiHoleServerError",
    "AuthResponse",
    "LoginInfo",
    "PiHoleAuthSession",
]
