"""Pi-hole API Python Library.

A Python library for interacting with Pi-hole through its API.
Handles authentication and session management.

Examples:
    ```python
    from pihole_lib import PiHoleClient, ListType

    # Simplified usage with property access (recommended)
    with PiHoleClient("http://192.168.1.100", password="secret") as client:
        # Get system information
        login_info = client.info.get_login_info()
        print(f"Pi-hole version: {login_info.version}")

        # Configuration management
        current_config = client.config.get_config()
        print(f"DNS upstreams: {current_config['dns']['upstreams']}")

        # Update gravity database (adlists)
        for line in client.actions.update_gravity():
            print(line.strip())

        # Backup operations
        backup_file = client.backup.export_backup("/path/to/backups")
        print(f"Backup saved to: {backup_file}")

        # Lists operations
        all_lists = client.lists.get_lists()
        print(f"Found {len(all_lists)} lists")

        # Add a new blocklist
        client.lists.add_list(
            address="https://hosts-file.net/ad_servers.txt",
            list_type=ListType.BLOCK,
            comment="Ad servers blocklist"
        )

        # Groups operations
        all_groups = client.groups.get_groups()
        print(f"Found {len(all_groups.groups)} groups")

        # Create a new group
        new_group = client.groups.create_group(
            name="family_devices",
            comment="Devices for family members",
            enabled=True
        )

    # Alternative usage with explicit class imports
    from pihole_lib import PiHoleClient, PiHoleInfo, PiHoleBackup, PiHoleLists, PiHoleActions, PiHoleConfig

    with PiHoleClient("http://192.168.1.100", password="secret") as client:
        # Configuration management
        config = PiHoleConfig(client)
        current_config = config.get_config()
        print(f"DNS upstreams: {current_config['dns']['upstreams']}")

        # Actions operations
        actions = PiHoleActions(client)
        for line in actions.update_gravity():
            print(line.strip())

        # Get system information
        info = PiHoleInfo(client)
        login_info = info.get_login_info()

        # Backup operations
        backup = PiHoleBackup(client)
        backup_file = backup.export_backup("/path/to/backups")
        print(f"Backup saved to: {backup_file}")

        # Lists operations
        lists = PiHoleLists(client)
        all_lists = lists.get_lists()
        print(f"Found {len(all_lists)} lists")

        result_lists = lists.add_list(
            address="https://hosts-file.net/ad_servers.txt",
            list_type=ListType.BLOCK,
            comment="Ad servers blocklist"
        )
    ```
"""

from .actions import PiHoleActions
from .backup import PiHoleBackup
from .base import BasePiHoleAPIClient
from .client import PiHoleClient
from .config import PiHoleConfig
from .dhcp import PiHoleDHCP
from .dns import PiHoleDNS
from .exceptions import (
    PiHoleAPIError,
    PiHoleAuthenticationError,
    PiHoleConnectionError,
    PiHoleServerError,
)
from .groups import PiHoleGroups
from .info import PiHoleInfo
from .lists import PiHoleLists
from .models import (
    PADDCPU,
    PADDFTL,
    AddListRequest,
    ClientHeader,
    ClientInfo,
    ComponentVersion,
    DatabaseGroup,
    DatabaseInfo,
    DatabaseOwner,
    DatabaseUser,
    DHCPLease,
    DHCPLeasesInfo,
    DNSBlockingStatus,
    DNSConfig,
    DNSConfigInfo,
    DNSRecord,
    DockerVersion,
    FTLClientStats,
    FTLDatabaseStats,
    FTLDnsmasqStats,
    FTLInfo,
    FTLStats,
    Group,
    GroupProcessedError,
    GroupProcessedResult,
    GroupProcessedSuccess,
    GroupRequest,
    GroupsResponse,
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
    Message,
    MessagesCountInfo,
    MessagesInfo,
    PADDCache,
    PADDConfig,
    PADDCPULoad,
    PADDInfo,
    PADDInterface,
    PADDMemory,
    PADDMemoryRAM,
    PADDMemorySwap,
    PADDNetworkBytes,
    PADDNetworkInterface,
    PADDQueries,
    PADDSensors,
    PADDSystem,
    PADDVersion,
    PADDVersionComponent,
    PADDVersionDocker,
    PADDVersionInfo,
    PADDVersionRemote,
    PiHoleAuthSession,
    PiHoleList,
    SystemCPU,
    SystemCPULoad,
    SystemDetails,
    SystemFTL,
    SystemInfo,
    SystemMemory,
    SystemRAM,
    SystemSwap,
    TeleporterGravityOptions,
    TeleporterImportOptions,
    VersionDetails,
    VersionInfo,
    VersionLocal,
    VersionRemote,
)
from .padd import PiHolePADD

__version__ = "0.1.0"
__author__ = "@dsgnr"

__all__ = [
    "PiHoleClient",
    "PiHoleInfo",
    "PiHoleBackup",
    "PiHoleLists",
    "PiHoleActions",
    "PiHoleConfig",
    "PiHoleDHCP",
    "PiHoleDNS",
    "PiHoleGroups",
    "PiHolePADD",
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
    "DHCPLease",
    "DHCPLeasesInfo",
    "DNSBlockingStatus",
    "DNSConfig",
    "DNSConfigInfo",
    "DNSRecord",
    "Group",
    "GroupProcessedError",
    "GroupProcessedResult",
    "GroupProcessedSuccess",
    "GroupRequest",
    "GroupsResponse",
    "ListType",
    "LoginInfo",
    "PADDCache",
    "PADDConfig",
    "PADDCPULoad",
    "PADDCPU",
    "PADDFTL",
    "PADDInfo",
    "PADDInterface",
    "PADDMemory",
    "PADDMemoryRAM",
    "PADDMemorySwap",
    "PADDNetworkBytes",
    "PADDNetworkInterface",
    "PADDQueries",
    "PADDSensors",
    "PADDSystem",
    "PADDVersion",
    "PADDVersionComponent",
    "PADDVersionDocker",
    "PADDVersionInfo",
    "PADDVersionRemote",
    "PiHoleAuthSession",
    "PiHoleList",
    "TeleporterGravityOptions",
    "TeleporterImportOptions",
]
