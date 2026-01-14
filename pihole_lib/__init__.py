"""Pi-hole API Python Library.

A Python library for interacting with Pi-hole through its API.
Handles authentication and session management.

"""

from pihole_lib.actions import PiHoleActions
from pihole_lib.backup import PiHoleBackup
from pihole_lib.base import BasePiHoleAPIClient
from pihole_lib.client import PiHoleClient
from pihole_lib.clients import PiHoleClients
from pihole_lib.config import PiHoleConfig
from pihole_lib.dhcp import PiHoleDHCP
from pihole_lib.dns import PiHoleDNS
from pihole_lib.domains import PiHoleDomains
from pihole_lib.exceptions import (
    PiHoleAPIError,
    PiHoleAuthenticationError,
    PiHoleConnectionError,
    PiHoleServerError,
)
from pihole_lib.groups import PiHoleGroups
from pihole_lib.info import PiHoleInfo
from pihole_lib.lists import PiHoleLists

# Core/Generic models
from pihole_lib.models.base import (
    ProcessedError,
    ProcessedResult,
    ProcessedSuccess,
)

# Client management models
from pihole_lib.models.client_mgmt import (
    Client,
    ClientBatchDeleteItem,
    ClientProcessedError,
    ClientProcessedResult,
    ClientProcessedSuccess,
    ClientRequest,
    ClientsResponse,
    ClientSuggestionsResponse,
    ClientUpdateRequest,
)

# DHCP models
from pihole_lib.models.dhcp import (
    DHCPLease,
    DHCPLeasesInfo,
)

# DNS models
from pihole_lib.models.dns import (
    DNSBlockingStatus,
    DNSConfig,
    DNSConfigInfo,
    DNSRecord,
)

# Enums
# Domain models
from pihole_lib.models.domains import (
    Domain,
    DomainBatchDeleteItem,
    DomainBatchDeleteResponse,
    DomainKind,
    DomainMutationResponse,
    DomainProcessedError,
    DomainProcessedResult,
    DomainProcessedSuccess,
    DomainRequest,
    DomainsResponse,
    DomainType,
)

# Database models
from pihole_lib.models.ftl import (
    DatabaseGroup,
    DatabaseInfo,
    DatabaseOwner,
    DatabaseUser,
    FTLClientStats,
    FTLDatabaseStats,
    FTLDnsmasqStats,
    FTLInfo,
    FTLStats,
)

# Group models
from pihole_lib.models.groups import (
    Group,
    GroupProcessedError,
    GroupProcessedResult,
    GroupProcessedSuccess,
    GroupRequest,
    GroupsResponse,
)

# Host models
from pihole_lib.models.host import (
    HostDetails,
    HostDMI,
    HostDMIBios,
    HostDMIBoard,
    HostDMIProduct,
    HostDMISystem,
    HostInfo,
    HostUname,
)

# List models
from pihole_lib.models.lists import (
    AddListRequest,
    BatchDeleteItem,
    ListProcessedError,
    ListProcessedResult,
    ListProcessedSuccess,
    ListsResponse,
    ListType,
    PiHoleList,
    UpdateListRequest,
)

# Message models
from pihole_lib.models.messages import (
    Message,
    MessagesCountInfo,
    MessagesInfo,
)

# Network models
from pihole_lib.models.network import (
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
)

# PADD models
from pihole_lib.models.padd import (
    PADDCache,
    PADDConfig,
    PADDInfo,
    PADDInterface,
    PADDMemory,
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
)

# Search models
from pihole_lib.models.search import (
    SearchData,
    SearchGravityCounts,
    SearchParameters,
    SearchResponse,
    SearchResultCounts,
    SearchResults,
)

# Auth models
from pihole_lib.models.session import (
    ClientHeader,
    ClientInfo,
    LoginInfo,
    PiHoleAuthSession,
)

# History/Stats models
from pihole_lib.models.stats import (
    ClientHistoryEntry,
    ClientHistoryResponse,
    DatabaseClientHistoryResponse,
    DatabaseHistoryResponse,
    DatabaseSummaryResponse,
    HistoryEntry,
    HistoryResponse,
    QueriesResponse,
    QueryEntry,
    QuerySuggestions,
    QuerySuggestionsResponse,
    QueryTypesResponse,
    RecentBlockedResponse,
    SummaryClients,
    SummaryGravity,
    SummaryQueries,
    SummaryResponse,
    TopClient,
    TopClientsResponse,
    TopDomain,
    TopDomainsResponse,
    UpstreamServer,
    UpstreamsResponse,
    UpstreamStatistics,
)

# System resource models
# NetworkBytes is in system.py
from pihole_lib.models.system import (
    CPULoad,
    CPUStats,
    FTLResourceUsage,
    Memory,
    MemoryStats,
    NetworkBytes,
    RAMStats,
    SystemDetails,
    SystemInfo,
)

# Teleporter models
from pihole_lib.models.teleporter import (
    TeleporterGravityOptions,
    TeleporterImportOptions,
)

# Version models
from pihole_lib.models.version import (
    ComponentVersion,
    DockerVersion,
    VersionDetails,
    VersionInfo,
    VersionLocal,
    VersionRemote,
)
from pihole_lib.network import PiHoleNetwork
from pihole_lib.padd import PiHolePADD
from pihole_lib.stats import PiHoleStats

__version__ = "0.1.0"
__author__ = "@dsgnr"

__all__ = [
    # Client classes
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
    "PiHoleClients",
    "BasePiHoleAPIClient",
    # Exceptions
    "PiHoleAPIError",
    "PiHoleAuthenticationError",
    "PiHoleConnectionError",
    "PiHoleServerError",
    # Core/Generic models
    "ProcessedSuccess",
    "ProcessedError",
    "ProcessedResult",
    # Enums
    "ListType",
    "DomainType",
    "DomainKind",
    # System resource models
    "RAMStats",
    "MemoryStats",
    "Memory",
    "CPULoad",
    "CPUStats",
    "FTLResourceUsage",
    "SystemDetails",
    "SystemInfo",
    # Version models
    "VersionLocal",
    "VersionRemote",
    "ComponentVersion",
    "DockerVersion",
    "VersionDetails",
    "VersionInfo",
    # Auth models
    "LoginInfo",
    "PiHoleAuthSession",
    # Client request info
    "ClientHeader",
    "ClientInfo",
    # Database models
    "DatabaseUser",
    "DatabaseGroup",
    "DatabaseOwner",
    "DatabaseInfo",
    # FTL models
    "FTLDatabaseStats",
    "FTLClientStats",
    "FTLDnsmasqStats",
    "FTLStats",
    "FTLInfo",
    # Host models
    "HostUname",
    "HostDMIBios",
    "HostDMIBoard",
    "HostDMIProduct",
    "HostDMISystem",
    "HostDMI",
    "HostDetails",
    "HostInfo",
    # List models
    "PiHoleList",
    "AddListRequest",
    "UpdateListRequest",
    "BatchDeleteItem",
    "ListProcessedSuccess",
    "ListProcessedError",
    "ListProcessedResult",
    "ListsResponse",
    # Search models
    "SearchResultCounts",
    "SearchGravityCounts",
    "SearchResults",
    "SearchParameters",
    "SearchData",
    "SearchResponse",
    # Message models
    "Message",
    "MessagesInfo",
    "MessagesCountInfo",
    # DHCP models
    "DHCPLease",
    "DHCPLeasesInfo",
    # PADD models
    "PADDQueries",
    "PADDCache",
    "PADDMemory",
    "PADDSystem",
    "NetworkBytes",
    "PADDNetworkBytes",
    "PADDNetworkInterface",
    "PADDInterface",
    "PADDVersionComponent",
    "PADDVersionRemote",
    "PADDVersionInfo",
    "PADDVersionDocker",
    "PADDVersion",
    "PADDConfig",
    "PADDSensors",
    "PADDInfo",
    # DNS models
    "DNSRecord",
    "DNSConfig",
    "DNSConfigInfo",
    "DNSBlockingStatus",
    # Group models
    "Group",
    "GroupRequest",
    "GroupProcessedSuccess",
    "GroupProcessedError",
    "GroupProcessedResult",
    "GroupsResponse",
    # History/Stats models
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
    # Domain models
    "Domain",
    "DomainsResponse",
    "DomainRequest",
    "DomainBatchDeleteItem",
    "DomainProcessedSuccess",
    "DomainProcessedError",
    "DomainProcessedResult",
    "DomainMutationResponse",
    "DomainBatchDeleteResponse",
    # Network models
    "NetworkDeviceAddress",
    "NetworkDevice",
    "NetworkDevicesResponse",
    "NetworkGateway",
    "NetworkGatewayResponse",
    "NetworkGatewayDetailedResponse",
    "NetworkInterfaceStats",
    "NetworkInterfaceAddress",
    "NetworkInterface",
    "NetworkInterfacesResponse",
    "NetworkRoute",
    "NetworkRoutesResponse",
    "NetworkDeviceDeleteResponse",
    # Client management models
    "Client",
    "ClientRequest",
    "ClientUpdateRequest",
    "ClientBatchDeleteItem",
    "ClientProcessedSuccess",
    "ClientProcessedError",
    "ClientProcessedResult",
    "ClientsResponse",
    "ClientSuggestionsResponse",
    # Teleporter models
    "TeleporterGravityOptions",
    "TeleporterImportOptions",
]
