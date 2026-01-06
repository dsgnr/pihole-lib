"""Pi-hole API Python Library.

A Python library for interacting with Pi-hole through its API.
Handles authentication and session management.

Examples:
    ```python
    from pihole_lib import PiHoleClient, PiHoleInfo, PiHoleBackup

    # For authenticated operations
    with PiHoleClient("http://192.168.1.100", password="secret") as client:
        # Client is authenticated and ready for API operations

        # Get system information
        info = PiHoleInfo(client)
        login_info = info.get_login_info()

        # Backup operations
        backup = PiHoleBackup(client)
        backup_file = backup.export_backup("/path/to/backups")  # Directory path
        print(f"Backup saved to: {backup_file}")  # Timestamped filename
    ```
"""

from .backup import PiHoleBackup
from .client import PiHoleClient
from .exceptions import (
    PiHoleAPIError,
    PiHoleAuthenticationError,
    PiHoleConnectionError,
    PiHoleServerError,
)
from .info import PiHoleInfo
from .models import (
    AuthResponse,
    LoginInfo,
    PiHoleAuthSession,
    TeleporterGravityOptions,
    TeleporterImportOptions,
    TeleporterImportResult,
)

__version__ = "0.1.0"
__author__ = "@dsgnr"

__all__ = [
    "PiHoleClient",
    "PiHoleInfo",
    "PiHoleBackup",
    "PiHoleAPIError",
    "PiHoleAuthenticationError",
    "PiHoleConnectionError",
    "PiHoleServerError",
    "AuthResponse",
    "LoginInfo",
    "PiHoleAuthSession",
    "TeleporterGravityOptions",
    "TeleporterImportOptions",
    "TeleporterImportResult",
]
