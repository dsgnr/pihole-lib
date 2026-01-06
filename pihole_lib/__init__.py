"""Pi-hole API Python Library.

A Python library for interacting with Pi-hole through its API.
Handles authentication and session management.

Examples:
    ```python
    from pihole_lib import PiHoleClient, PiHoleInfo, PiHoleBackup, PiHoleLists

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

        # Lists operations
        lists = PiHoleLists(client)
        all_lists = lists.get_lists()
        print(f"Found {len(all_lists)} lists")
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
from .lists import PiHoleLists
from .models import (
    ListType,
    LoginInfo,
    PiHoleAuthSession,
    PiHoleList,
    TeleporterGravityOptions,
    TeleporterImportOptions,
)

__version__ = "0.1.0"
__author__ = "@dsgnr"

__all__ = [
    "PiHoleClient",
    "PiHoleInfo",
    "PiHoleBackup",
    "PiHoleLists",
    "PiHoleAPIError",
    "PiHoleAuthenticationError",
    "PiHoleConnectionError",
    "PiHoleServerError",
    "ListType",
    "LoginInfo",
    "PiHoleAuthSession",
    "PiHoleList",
    "TeleporterGravityOptions",
    "TeleporterImportOptions",
]
