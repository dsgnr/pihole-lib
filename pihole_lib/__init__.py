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

        # Domain operations
        all_domains = client.domains.get_domains()
        print(f"Found {len(all_domains)} domains")

        # Add a new domain
        client.domains.add_domain(
            domain="badsite.com",
            domain_type=DomainType.DENY,
            domain_kind=DomainKind.EXACT,
            comment="Blocked site"
        )

        # Network operations
        devices = client.network.get_devices()
        print(f"Found {len(devices.devices)} network devices")

        gateway = client.network.get_gateway()
        interfaces = client.network.get_interfaces()
        routes = client.network.get_routes()

    # Alternative usage with explicit class imports
    from pihole_lib import PiHoleClient, PiHoleInfo, PiHoleBackup, PiHoleLists, PiHoleActions, PiHoleConfig, PiHoleDomains, PiHoleNetwork

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

        # Domain operations
        domains = PiHoleDomains(client)
        all_domains = domains.get_domains()
        print(f"Found {len(all_domains)} domains")

        # Network operations
        network = PiHoleNetwork(client)
        devices = network.get_devices()
        gateway = network.get_gateway()
        interfaces = network.get_interfaces()
        routes = network.get_routes()
    ```
"""

from .actions import PiHoleActions
from .backup import PiHoleBackup
from .base import BasePiHoleAPIClient
from .client import PiHoleClient
from .config import PiHoleConfig
from .dhcp import PiHoleDHCP
from .dns import PiHoleDNS
from .domains import PiHoleDomains
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
    BatchDeleteItem,
    ClientHeader,
    ClientHistoryEntry,
    ClientHistoryResponse,
    ClientInfo,
    ComponentVersion,
    DatabaseClientHistoryResponse,
    DatabaseGroup,
    DatabaseHistoryResponse,
    DatabaseInfo,
    DatabaseOwner,
    DatabaseSummaryResponse,
    DatabaseUser,
    DHCPLease,
    DHCPLeasesInfo,
    DNSBlockingStatus,
    DNSConfig,
    DNSConfigInfo,
    DNSRecord,
    DockerVersion,
    Domain,
    DomainBatchDeleteItem,
    DomainKind,
    DomainMutationResponse,
    DomainProcessedError,
    DomainProcessedResult,
    DomainProcessedSuccess,
    DomainRequest,
    DomainsResponse,
    DomainType,
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
    HistoryEntry,
    HistoryResponse,
    HostDetails,
    HostDMI,
    HostDMIBios,
    HostDMIBoard,
    HostDMIProduct,
    HostDMISystem,
    HostInfo,
    HostUname,
    ListProcessedError,
    ListProcessedResult,
    ListProcessedSuccess,
    ListsResponse,
    ListType,
    LoginInfo,
    Message,
    MessagesCountInfo,
    MessagesInfo,
    NetworkDevice,
    NetworkDeviceAddress,
    NetworkDeviceDeleteResponse,
    NetworkDevicesResponse,
    NetworkGateway,
    NetworkGatewayDetailedResponse,
    NetworkGatewayResponse,
    NetworkInterface,
    NetworkInterfaceAddress,
    NetworkInterfacesResponse,
    NetworkInterfaceStats,
    NetworkRoute,
    NetworkRoutesResponse,
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
    QueriesResponse,
    QueryEntry,
    QuerySuggestions,
    QuerySuggestionsResponse,
    QueryTypesResponse,
    RecentBlockedResponse,
    SearchData,
    SearchGravityCounts,
    SearchParameters,
    SearchResponse,
    SearchResultCounts,
    SearchResults,
    SummaryClients,
    SummaryGravity,
    SummaryQueries,
    SummaryResponse,
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
    TopClient,
    TopClientsResponse,
    TopDomain,
    TopDomainsResponse,
    UpdateListRequest,
    UpstreamServer,
    UpstreamsResponse,
    UpstreamStatistics,
    VersionDetails,
    VersionInfo,
    VersionLocal,
    VersionRemote,
)
from .network import PiHoleNetwork
from .padd import PiHolePADD
from .stats import PiHoleStats

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
    "PiHoleDomains",
    "PiHoleGroups",
    "PiHoleNetwork",
    "PiHolePADD",
    "PiHoleStats",
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
    "Domain",
    "DomainBatchDeleteItem",
    "DomainKind",
    "DomainMutationResponse",
    "DomainProcessedError",
    "DomainProcessedResult",
    "DomainProcessedSuccess",
    "DomainRequest",
    "DomainsResponse",
    "DomainType",
    "Group",
    "GroupProcessedError",
    "GroupProcessedResult",
    "GroupProcessedSuccess",
    "GroupRequest",
    "GroupsResponse",
    "HistoryEntry",
    "HistoryResponse",
    "ClientHistoryEntry",
    "ClientHistoryResponse",
    "DatabaseHistoryResponse",
    "DatabaseClientHistoryResponse",
    "QueryEntry",
    "QueriesResponse",
    "QuerySuggestions",
    "QuerySuggestionsResponse",
    "QueryTypesResponse",
    "DatabaseSummaryResponse",
    "TopClient",
    "TopClientsResponse",
    "TopDomain",
    "TopDomainsResponse",
    "UpstreamStatistics",
    "UpstreamServer",
    "UpstreamsResponse",
    "RecentBlockedResponse",
    "SummaryQueries",
    "SummaryClients",
    "SummaryGravity",
    "SummaryResponse",
    "UpdateListRequest",
    "BatchDeleteItem",
    "ListProcessedSuccess",
    "ListProcessedError",
    "ListProcessedResult",
    "ListsResponse",
    "SearchResultCounts",
    "SearchGravityCounts",
    "SearchResults",
    "SearchParameters",
    "SearchData",
    "SearchResponse",
    "ListType",
    "LoginInfo",
    "NetworkDevice",
    "NetworkDeviceAddress",
    "NetworkDeviceDeleteResponse",
    "NetworkDevicesResponse",
    "NetworkGateway",
    "NetworkGatewayDetailedResponse",
    "NetworkGatewayResponse",
    "NetworkInterface",
    "NetworkInterfaceAddress",
    "NetworkInterfacesResponse",
    "NetworkInterfaceStats",
    "NetworkRoute",
    "NetworkRoutesResponse",
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
