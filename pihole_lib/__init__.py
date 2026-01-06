"""Pi-hole API Python Library.

A Python library for interacting with Pi-hole through its API.
Handles authentication and session management.

Examples:
    ```python
    from pihole_lib import PiHoleClient, PiHoleInfo, PiHoleBackup, PiHoleLists, PiHoleActions, ListType

    # For authenticated operations
    with PiHoleClient("http://192.168.1.100", password="secret") as client:
        # Actions operations
        actions = PiHoleActions(client)

        # Update gravity database (adlists)
        for line in actions.update_gravity():
            print(line.strip())

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

        # Get existing lists
        all_lists = lists.get_lists()
        print(f"Found {len(all_lists)} lists")

        # Add a new blocklist
        result_lists = lists.add_list(
            address="https://hosts-file.net/ad_servers.txt",
            list_type=ListType.BLOCK,
            comment="Ad servers blocklist"
        )
        print(f"Added list")
    ```
"""

from .actions import PiHoleActions
from .backup import PiHoleBackup
from .base import BasePiHoleAPIClient
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
    AddListRequest,
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
    "PiHoleActions",
    "BasePiHoleAPIClient",
    "PiHoleAPIError",
    "PiHoleAuthenticationError",
    "PiHoleConnectionError",
    "PiHoleServerError",
    "AddListRequest",
    "ListType",
    "LoginInfo",
    "PiHoleAuthSession",
    "PiHoleList",
    "TeleporterGravityOptions",
    "TeleporterImportOptions",
]
