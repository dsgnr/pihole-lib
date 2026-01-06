"""Pi-hole API Python Library.

A Python library for interacting with Pi-hole through its API.
Handles authentication and session management.

Examples:
    ```python
    from pihole_lib import PiHoleClient

    with PiHoleClient("http://192.168.1.100", password="secret") as client:
        # Client is authenticated and ready for API operations
        pass
    ```
"""

from .client import PiHoleClient
from .exceptions import (
    PiHoleAPIError,
    PiHoleAuthenticationError,
    PiHoleConnectionError,
    PiHoleServerError,
)
from .models import AuthResponse, PiHoleAuthSession

__version__ = "0.1.0"
__author__ = "@dsgnr"

__all__ = [
    "PiHoleClient",
    "PiHoleAPIError",
    "PiHoleAuthenticationError",
    "PiHoleConnectionError",
    "PiHoleServerError",
    "AuthResponse",
    "PiHoleAuthSession",
]
