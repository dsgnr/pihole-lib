"""Pi-hole API Python Library.

A Python library for interacting with Pi-hole through its API.
Handles authentication and session management.

Examples:
    ```python
    from pihole_lib import PiHoleClient, PiHoleInfo, PiHoleBackup, PiHoleLists, PiHoleActions, PiHoleConfig, ListType

    # For authenticated operations
    with PiHoleClient("http://192.168.1.100", password="secret") as client:
        # Configuration management
        config = PiHoleConfig(client)
        current_config = config.get_config()
        print(f"DNS upstreams: {current_config['dns']['upstreams']}")

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
from .config import PiHoleConfig
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
    ClientHeader,
    ClientInfo,
    ComponentVersion,
    DatabaseGroup,
    DatabaseInfo,
    DatabaseOwner,
    DatabaseUser,
    DockerVersion,
    FTLClientStats,
    FTLDatabaseStats,
    FTLDnsmasqStats,
    FTLInfo,
    FTLStats,
    HostDetails,
    HostDMI,
    HostDMIBios,
    HostDMIBoard,
    HostDMIProduct,
    HostDMISystem,
    HostInfo,
    HostUname,
    ListType,
    LoginInfo,
    PiHoleAuthSession,
    PiHoleList,
    TeleporterGravityOptions,
    TeleporterImportOptions,
    VersionDetails,
    VersionInfo,
    VersionLocal,
    VersionRemote,
)

__version__ = "0.1.0"
__author__ = "@dsgnr"

__all__ = [
    "PiHoleClient",
    "PiHoleInfo",
    "PiHoleBackup",
    "PiHoleLists",
    "PiHoleActions",
    "PiHoleConfig",
    "BasePiHoleAPIClient",
    "PiHoleAPIError",
    "PiHoleAuthenticationError",
    "PiHoleConnectionError",
    "PiHoleServerError",
    "AddListRequest",
    "ClientHeader",
    "ClientInfo",
    "DatabaseGroup",
    "DatabaseInfo",
    "DatabaseOwner",
    "DatabaseUser",
    "ListType",
    "LoginInfo",
    "PiHoleAuthSession",
    "PiHoleList",
    "TeleporterGravityOptions",
    "TeleporterImportOptions",
]
