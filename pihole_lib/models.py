"""Data models for Pi-hole API responses."""

from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class ListType(str, Enum):
    """Pi-hole list types."""

    ALLOW = "allow"
    BLOCK = "block"


class PiHoleList(BaseModel):
    """Pi-hole domain list.

    Attributes:
        address: Address of the list.
        type: Type of list (allow or block).
        comment: User-provided free-text comment for this list.
        groups: Array of group IDs.
        enabled: Status of domain.
        id: Database ID.
        date_added: Unix timestamp of item addition.
        date_modified: Unix timestamp of last item modification.
        date_updated: Unix timestamp of last update of list content.
        number: Number of VALID domains on this list.
        invalid_domains: Number of INVALID domains on this list.
        abp_entries: Number of ABP entries on this list.
        status: List status.
    """

    address: str = Field(..., description="Address of the list")
    type: ListType = Field(..., description="Type of list")
    comment: str | None = Field(
        None, description="User-provided free-text comment for this list"
    )
    groups: list[int] = Field(..., description="Array of group IDs")
    enabled: bool = Field(True, description="Status of domain")
    id: int = Field(..., description="Database ID")
    date_added: int = Field(..., description="Unix timestamp of item addition")
    date_modified: int = Field(
        ..., description="Unix timestamp of last item modification"
    )
    date_updated: int = Field(
        ..., description="Unix timestamp of last update of list content"
    )
    number: int = Field(..., description="Number of VALID domains on this list")
    invalid_domains: int = Field(
        ..., description="Number of INVALID domains on this list"
    )
    abp_entries: int = Field(..., description="Number of ABP entries on this list")
    status: int = Field(..., description="List status")


class LoginInfo(BaseModel):
    """Pi-hole login page information.

    Attributes:
        https_port: HTTPS port of the Pi-hole webserver (0 if disabled).
        dns: Whether the DNS server is up and running. False only in failed state.
    """

    https_port: int = Field(
        ..., description="HTTPS port of the Pi-hole webserver (0 if disabled)"
    )
    dns: bool = Field(..., description="Whether the DNS server is up and running")


class ClientHeader(BaseModel):
    """HTTP header from client request.

    Attributes:
        name: Header name.
        value: Header value.
    """

    name: str = Field(..., description="Header name")
    value: str = Field(..., description="Header value")


class ClientInfo(BaseModel):
    """Pi-hole client request information.

    Attributes:
        remote_addr: Client's remote IP address.
        http_version: HTTP version used by client.
        method: HTTP method used.
        headers: List of HTTP headers sent by client.
    """

    remote_addr: str = Field(..., description="Client's remote IP address")
    http_version: str = Field(..., description="HTTP version used by client")
    method: str = Field(..., description="HTTP method used")
    headers: list[ClientHeader] = Field(..., description="HTTP headers sent by client")


class DatabaseUser(BaseModel):
    """Database file user information.

    Attributes:
        uid: User ID.
        name: User name.
        info: Additional user information.
    """

    uid: int = Field(..., description="User ID")
    name: str = Field(..., description="User name")
    info: str = Field(..., description="Additional user information")


class DatabaseGroup(BaseModel):
    """Database file group information.

    Attributes:
        gid: Group ID.
        name: Group name.
    """

    gid: int = Field(..., description="Group ID")
    name: str = Field(..., description="Group name")


class DatabaseOwner(BaseModel):
    """Database file ownership information.

    Attributes:
        user: User information.
        group: Group information.
    """

    user: DatabaseUser = Field(..., description="User information")
    group: DatabaseGroup = Field(..., description="Group information")


class DatabaseInfo(BaseModel):
    """Pi-hole database information.

    Attributes:
        size: Database file size in bytes.
        type: File type description.
        mode: File permissions.
        atime: Last access time (Unix timestamp).
        mtime: Last modification time (Unix timestamp).
        ctime: Creation time (Unix timestamp).
        owner: File ownership information.
        queries: Number of queries in memory.
        earliest_timestamp: Earliest query timestamp in memory.
        queries_disk: Number of queries on disk.
        earliest_timestamp_disk: Earliest query timestamp on disk.
        sqlite_version: SQLite version.
    """

    size: int = Field(..., description="Database file size in bytes")
    type: str = Field(..., description="File type description")
    mode: str = Field(..., description="File permissions")
    atime: int = Field(..., description="Last access time (Unix timestamp)")
    mtime: int = Field(..., description="Last modification time (Unix timestamp)")
    ctime: int = Field(..., description="Creation time (Unix timestamp)")
    owner: DatabaseOwner = Field(..., description="File ownership information")
    queries: int = Field(..., description="Number of queries in memory")
    earliest_timestamp: int = Field(
        ..., description="Earliest query timestamp in memory"
    )
    queries_disk: int = Field(..., description="Number of queries on disk")
    earliest_timestamp_disk: int = Field(
        ..., description="Earliest query timestamp on disk"
    )
    sqlite_version: str = Field(..., description="SQLite version")


class FTLDatabaseStats(BaseModel):
    """FTL database statistics.

    Attributes:
        gravity: Number of gravity domains.
        groups: Number of groups.
        lists: Number of lists.
        clients: Number of clients.
        domains: Domain statistics (allowed/denied).
        regex: Regex statistics (allowed/denied).
    """

    gravity: int = Field(..., description="Number of gravity domains")
    groups: int = Field(..., description="Number of groups")
    lists: int = Field(..., description="Number of lists")
    clients: int = Field(..., description="Number of clients")
    domains: dict = Field(..., description="Domain statistics")
    regex: dict = Field(..., description="Regex statistics")


class FTLClientStats(BaseModel):
    """FTL client statistics.

    Attributes:
        total: Total number of clients.
        active: Number of active clients.
    """

    total: int = Field(..., description="Total number of clients")
    active: int = Field(..., description="Number of active clients")


class FTLDnsmasqStats(BaseModel):
    """FTL dnsmasq statistics.

    Attributes:
        dns_cache_inserted: DNS cache insertions.
        dns_cache_live_freed: DNS cache live freed.
        dns_queries_forwarded: DNS queries forwarded.
        dns_auth_answered: DNS authoritative answers.
        dns_local_answered: DNS local answers.
        dns_stale_answered: DNS stale answers.
        dns_unanswered: DNS unanswered queries.
        dnssec_max_crypto_use: DNSSEC max crypto use.
        dnssec_max_sig_fail: DNSSEC max signature failures.
        dnssec_max_work: DNSSEC max work.
        bootp: BOOTP requests.
        pxe: PXE requests.
        dhcp_ack: DHCP ACK messages.
        dhcp_decline: DHCP decline messages.
        dhcp_discover: DHCP discover messages.
        dhcp_inform: DHCP inform messages.
        dhcp_nak: DHCP NAK messages.
        dhcp_offer: DHCP offer messages.
        dhcp_release: DHCP release messages.
        dhcp_request: DHCP request messages.
        noanswer: No answer queries.
        leases_allocated_4: IPv4 leases allocated.
        leases_pruned_4: IPv4 leases pruned.
        leases_allocated_6: IPv6 leases allocated.
        leases_pruned_6: IPv6 leases pruned.
        tcp_connections: TCP connections.
        dhcp_leasequery: DHCP lease queries.
        dhcp_lease_unassigned: DHCP unassigned leases.
        dhcp_lease_actve: DHCP active leases.
        dhcp_lease_unknown: DHCP unknown leases.
    """

    dns_cache_inserted: int = Field(..., description="DNS cache insertions")
    dns_cache_live_freed: int = Field(..., description="DNS cache live freed")
    dns_queries_forwarded: int = Field(..., description="DNS queries forwarded")
    dns_auth_answered: int = Field(..., description="DNS authoritative answers")
    dns_local_answered: int = Field(..., description="DNS local answers")
    dns_stale_answered: int = Field(..., description="DNS stale answers")
    dns_unanswered: int = Field(..., description="DNS unanswered queries")
    dnssec_max_crypto_use: int = Field(..., description="DNSSEC max crypto use")
    dnssec_max_sig_fail: int = Field(..., description="DNSSEC max signature failures")
    dnssec_max_work: int = Field(..., description="DNSSEC max work")
    bootp: int = Field(..., description="BOOTP requests")
    pxe: int = Field(..., description="PXE requests")
    dhcp_ack: int = Field(..., description="DHCP ACK messages")
    dhcp_decline: int = Field(..., description="DHCP decline messages")
    dhcp_discover: int = Field(..., description="DHCP discover messages")
    dhcp_inform: int = Field(..., description="DHCP inform messages")
    dhcp_nak: int = Field(..., description="DHCP NAK messages")
    dhcp_offer: int = Field(..., description="DHCP offer messages")
    dhcp_release: int = Field(..., description="DHCP release messages")
    dhcp_request: int = Field(..., description="DHCP request messages")
    noanswer: int = Field(..., description="No answer queries")
    leases_allocated_4: int = Field(..., description="IPv4 leases allocated")
    leases_pruned_4: int = Field(..., description="IPv4 leases pruned")
    leases_allocated_6: int = Field(..., description="IPv6 leases allocated")
    leases_pruned_6: int = Field(..., description="IPv6 leases pruned")
    tcp_connections: int = Field(..., description="TCP connections")
    dhcp_leasequery: int = Field(..., description="DHCP lease queries")
    dhcp_lease_unassigned: int = Field(..., description="DHCP unassigned leases")
    dhcp_lease_actve: int = Field(..., description="DHCP active leases")
    dhcp_lease_unknown: int = Field(..., description="DHCP unknown leases")


class FTLStats(BaseModel):
    """FTL statistics subset.

    Attributes:
        database: Database statistics.
        privacy_level: Privacy level.
        query_frequency: Query frequency.
        clients: Client statistics.
        pid: Process ID of FTL.
        uptime: FTL uptime in seconds.
        mem_percent: Memory usage percentage.
        cpu_percent: CPU usage percentage.
        allow_destructive: Whether destructive operations are allowed.
        dnsmasq: Dnsmasq statistics.
    """

    database: FTLDatabaseStats = Field(..., description="Database statistics")
    privacy_level: int = Field(..., description="Privacy level")
    query_frequency: int = Field(..., description="Query frequency")
    clients: FTLClientStats = Field(..., description="Client statistics")
    pid: int = Field(..., description="Process ID of FTL")
    uptime: float = Field(..., description="FTL uptime in seconds")
    mem_percent: float = Field(..., alias="%mem", description="Memory usage percentage")
    cpu_percent: float = Field(..., alias="%cpu", description="CPU usage percentage")
    allow_destructive: bool = Field(
        ..., description="Whether destructive operations are allowed"
    )
    dnsmasq: FTLDnsmasqStats = Field(..., description="Dnsmasq statistics")


class HostUname(BaseModel):
    """Host system uname information.

    Attributes:
        domainname: Domain name.
        machine: Machine hardware name.
        nodename: Network node hostname.
        release: Operating system release.
        sysname: Operating system name.
        version: Operating system version.
    """

    domainname: str = Field(..., description="Domain name")
    machine: str = Field(..., description="Machine hardware name")
    nodename: str = Field(..., description="Network node hostname")
    release: str = Field(..., description="Operating system release")
    sysname: str = Field(..., description="Operating system name")
    version: str = Field(..., description="Operating system version")


class HostDMIBios(BaseModel):
    """Host DMI BIOS information.

    Attributes:
        vendor: BIOS vendor.
    """

    vendor: str | None = Field(None, description="BIOS vendor")


class HostDMIBoard(BaseModel):
    """Host DMI board information.

    Attributes:
        name: Board name.
        vendor: Board vendor.
        version: Board version.
    """

    name: str | None = Field(None, description="Board name")
    vendor: str | None = Field(None, description="Board vendor")
    version: str | None = Field(None, description="Board version")


class HostDMIProduct(BaseModel):
    """Host DMI product information.

    Attributes:
        name: Product name.
        family: Product family.
        version: Product version.
    """

    name: str | None = Field(None, description="Product name")
    family: str | None = Field(None, description="Product family")
    version: str | None = Field(None, description="Product version")


class HostDMISystem(BaseModel):
    """Host DMI system information.

    Attributes:
        vendor: System vendor.
    """

    vendor: str | None = Field(None, description="System vendor")


class HostDMI(BaseModel):
    """Host DMI/SMBIOS information.

    Attributes:
        bios: BIOS information.
        board: Board information.
        product: Product information.
        sys: System information.
    """

    bios: HostDMIBios = Field(..., description="BIOS information")
    board: HostDMIBoard = Field(..., description="Board information")
    product: HostDMIProduct = Field(..., description="Product information")
    sys: HostDMISystem = Field(..., description="System information")


class HostDetails(BaseModel):
    """Host system details.

    Attributes:
        uname: System uname information.
        model: Hardware model.
        dmi: DMI/SMBIOS information.
    """

    uname: HostUname = Field(..., description="System uname information")
    model: str | None = Field(None, description="Hardware model")
    dmi: HostDMI = Field(..., description="DMI/SMBIOS information")


class HostInfo(BaseModel):
    """Pi-hole host system information.

    Attributes:
        host: Host system details.
    """

    host: HostDetails = Field(..., description="Host system details")


class VersionLocal(BaseModel):
    """Local version information.

    Attributes:
        version: Version string.
        branch: Git branch (optional).
        hash: Git commit hash.
        date: Build date (optional).
    """

    version: str = Field(..., description="Version string")
    branch: str | None = Field(None, description="Git branch")
    hash: str = Field(..., description="Git commit hash")
    date: str | None = Field(None, description="Build date")


class VersionRemote(BaseModel):
    """Remote version information.

    Attributes:
        version: Version string.
        hash: Git commit hash.
    """

    version: str | None = Field(None, description="Version string")
    hash: str | None = Field(None, description="Git commit hash")


class ComponentVersion(BaseModel):
    """Component version information.

    Attributes:
        local: Local version information.
        remote: Remote version information.
    """

    local: VersionLocal = Field(..., description="Local version information")
    remote: VersionRemote = Field(..., description="Remote version information")


class DockerVersion(BaseModel):
    """Docker version information.

    Attributes:
        local: Local Docker version.
        remote: Remote Docker version.
    """

    local: str | None = Field(None, description="Local Docker version")
    remote: str | None = Field(None, description="Remote Docker version")


class VersionDetails(BaseModel):
    """Pi-hole version details.

    Attributes:
        core: Pi-hole core version information.
        web: Pi-hole web interface version information.
        ftl: FTL version information.
        docker: Docker image version information.
    """

    core: ComponentVersion = Field(..., description="Pi-hole core version information")
    web: ComponentVersion = Field(
        ..., description="Pi-hole web interface version information"
    )
    ftl: ComponentVersion = Field(..., description="FTL version information")
    docker: DockerVersion = Field(..., description="Docker image version information")


class VersionInfo(BaseModel):
    """Pi-hole version information.

    Attributes:
        version: Version details for all components.
        took: Time taken to process the request.
    """

    version: VersionDetails = Field(
        ..., description="Version details for all components"
    )
    took: float = Field(..., description="Time taken to process the request")


class FTLInfo(BaseModel):
    """Pi-hole FTL (Faster Than Light) information.

    Attributes:
        ftl: FTL statistics and runtime information.
    """

    ftl: FTLStats = Field(..., description="FTL statistics and runtime information")


class TeleporterGravityOptions(BaseModel):
    """Teleporter gravity database import options.

    Attributes:
        group: Whether to import groups.
        adlist: Whether to import adlists.
        adlist_by_group: Whether to import adlist-group associations.
        domainlist: Whether to import domain lists.
        domainlist_by_group: Whether to import domainlist-group associations.
        client: Whether to import clients.
        client_by_group: Whether to import client-group associations.
    """

    group: bool = Field(default=True, description="Whether to import groups")
    adlist: bool = Field(default=True, description="Whether to import adlists")
    adlist_by_group: bool = Field(
        default=True, description="Whether to import adlist-group associations"
    )
    domainlist: bool = Field(default=True, description="Whether to import domain lists")
    domainlist_by_group: bool = Field(
        default=True, description="Whether to import domainlist-group associations"
    )
    client: bool = Field(default=True, description="Whether to import clients")
    client_by_group: bool = Field(
        default=True, description="Whether to import client-group associations"
    )


class TeleporterImportOptions(BaseModel):
    """Pi-hole Teleporter import options.

    Attributes:
        config: Whether to import configuration files.
        dhcp_leases: Whether to import DHCP leases.
        gravity: Gravity database import options.
    """

    config: bool = Field(
        default=True, description="Whether to import configuration files"
    )
    dhcp_leases: bool = Field(default=True, description="Whether to import DHCP leases")
    gravity: TeleporterGravityOptions = Field(
        default_factory=lambda: TeleporterGravityOptions(),
        description="Gravity database import options",
    )


class AddListRequest(BaseModel):
    """Request model for adding a new Pi-hole list.

    Attributes:
        address: Address of the list (URL, IP, MAC address, hostname, or interface).
        comment: Optional user-provided comment for this list.
        groups: Array of group IDs (defaults to [0] for default group).
        enabled: Whether the list should be enabled (defaults to True).
    """

    address: str = Field(..., description="Address of the list")
    comment: str | None = Field(None, description="Optional comment for this list")
    groups: list[int] = Field(default=[0], description="Array of group IDs")
    enabled: bool = Field(default=True, description="Whether the list is enabled")


class UpdateListRequest(BaseModel):
    """Request model for updating an existing Pi-hole list.

    Attributes:
        comment: Optional user-provided comment for this list.
        type: Type of list (allow or block).
        groups: Array of group IDs.
        enabled: Whether the list should be enabled.
    """

    comment: str | None = Field(None, description="Optional comment for this list")
    type: ListType = Field(..., description="Type of list")
    groups: list[int] = Field(..., description="Array of group IDs")
    enabled: bool = Field(..., description="Whether the list is enabled")


class BatchDeleteItem(BaseModel):
    """Item for batch delete operation.

    Attributes:
        item: Address of the list to delete.
        type: Type of list (allow or block).
    """

    item: str = Field(..., description="Address of the list to delete")
    type: ListType = Field(..., description="Type of list")


class ListProcessedSuccess(BaseModel):
    """Success item in list processing result.

    Attributes:
        item: List that was successfully processed.
    """

    item: str = Field(..., description="List that was successfully processed")


class ListProcessedError(BaseModel):
    """Error item in list processing result.

    Attributes:
        item: List that could not be processed.
        error: Error message.
    """

    item: str = Field(..., description="List that could not be processed")
    error: str = Field(..., description="Error message")


class ListProcessedResult(BaseModel):
    """Processing result for list operations.

    Attributes:
        success: Array of lists that were successfully processed.
        errors: Array of errors that occurred during processing.
    """

    success: list[ListProcessedSuccess] = Field(
        default_factory=list, description="Successfully processed lists"
    )
    errors: list[ListProcessedError] = Field(
        default_factory=list, description="Processing errors"
    )


class ListsResponse(BaseModel):
    """Response model for list operations.

    Attributes:
        lists: Array of list objects.
        processed: Processing result (null for GET operations).
        took: Time in seconds it took to process the request.
    """

    lists: list[PiHoleList] = Field(..., description="Array of list objects")
    processed: ListProcessedResult | None = Field(None, description="Processing result")
    took: float = Field(
        ..., description="Time in seconds it took to process the request"
    )


class SearchResultCounts(BaseModel):
    """Search result counts.

    Attributes:
        exact: Number of exact matches.
        regex: Number of regex matches.
    """

    exact: int = Field(..., description="Number of exact matches")
    regex: int = Field(..., description="Number of regex matches")


class SearchGravityCounts(BaseModel):
    """Search gravity result counts.

    Attributes:
        allow: Number of allow list matches.
        block: Number of block list matches.
    """

    allow: int = Field(..., description="Number of allow list matches")
    block: int = Field(..., description="Number of block list matches")


class SearchResults(BaseModel):
    """Search results summary.

    Attributes:
        domains: Domain search result counts.
        gravity: Gravity search result counts.
        total: Total number of results.
    """

    domains: SearchResultCounts = Field(..., description="Domain search result counts")
    gravity: SearchGravityCounts = Field(
        ..., description="Gravity search result counts"
    )
    total: int = Field(..., description="Total number of results")


class SearchParameters(BaseModel):
    """Search parameters used.

    Attributes:
        N: Maximum number of results returned.
        partial: Whether partial matching was used.
        domain: Domain that was searched for.
        debug: Whether debug information was included.
    """

    N: int = Field(..., description="Maximum number of results returned")
    partial: bool = Field(..., description="Whether partial matching was used")
    domain: str = Field(..., description="Domain that was searched for")
    debug: bool = Field(..., description="Whether debug information was included")


class SearchData(BaseModel):
    """Search data container.

    Attributes:
        domains: List of domain matches.
        gravity: List of gravity matches.
        results: Search result summary.
        parameters: Search parameters used.
    """

    domains: list[PiHoleList] = Field(..., description="List of domain matches")
    gravity: list[PiHoleList] = Field(..., description="List of gravity matches")
    results: SearchResults = Field(..., description="Search result summary")
    parameters: SearchParameters = Field(..., description="Search parameters used")


class SearchResponse(BaseModel):
    """Response for domain search operations.

    Attributes:
        search: Search data and results.
        took: Time taken to process the request.
    """

    search: SearchData = Field(..., description="Search data and results")
    took: float = Field(..., description="Time taken to process the request")


class PiHoleAuthSession(BaseModel):
    """Pi-hole authentication session data.

    Attributes:
        valid: Whether session is valid.
        totp: Whether two-factor auth is enabled.
        sid: Session ID token.
        csrf: CSRF protection token.
        validity: Session duration in seconds.
        message: Optional message from Pi-hole.
    """

    valid: bool = Field(..., description="Whether session is valid")
    totp: bool = Field(..., description="Whether two-factor auth is enabled")
    sid: str = Field(..., description="Session ID token")
    csrf: str = Field(..., description="CSRF protection token")
    validity: int = Field(..., description="Session duration in seconds")
    message: str | None = Field(None, description="Optional message from Pi-hole")


class SystemRAM(BaseModel):
    """System RAM information.

    Attributes:
        total: Total RAM in KB.
        free: Free RAM in KB.
        used: Used RAM in KB.
        available: Available RAM in KB.
        percent_used: Percentage of RAM used.
    """

    total: int = Field(..., description="Total RAM in KB")
    free: int = Field(..., description="Free RAM in KB")
    used: int = Field(..., description="Used RAM in KB")
    available: int = Field(..., description="Available RAM in KB")
    percent_used: float = Field(
        ..., alias="%used", description="Percentage of RAM used"
    )


class SystemSwap(BaseModel):
    """System swap information.

    Attributes:
        total: Total swap in KB.
        free: Free swap in KB.
        used: Used swap in KB.
        percent_used: Percentage of swap used.
    """

    total: int = Field(..., description="Total swap in KB")
    free: int = Field(..., description="Free swap in KB")
    used: int = Field(..., description="Used swap in KB")
    percent_used: float = Field(
        ..., alias="%used", description="Percentage of swap used"
    )


class SystemMemory(BaseModel):
    """System memory information.

    Attributes:
        ram: RAM information.
        swap: Swap information.
    """

    ram: SystemRAM = Field(..., description="RAM information")
    swap: SystemSwap = Field(..., description="Swap information")


class SystemCPULoad(BaseModel):
    """System CPU load information.

    Attributes:
        raw: Raw load averages (1, 5, 15 minutes).
        percent: Load averages as percentages.
    """

    raw: list[float] = Field(..., description="Raw load averages (1, 5, 15 minutes)")
    percent: list[float] = Field(..., description="Load averages as percentages")


class SystemCPU(BaseModel):
    """System CPU information.

    Attributes:
        nprocs: Number of CPU cores.
        percent_cpu: CPU usage percentage.
        load: Load average information.
    """

    nprocs: int = Field(..., description="Number of CPU cores")
    percent_cpu: float = Field(..., alias="%cpu", description="CPU usage percentage")
    load: SystemCPULoad = Field(..., description="Load average information")


class SystemFTL(BaseModel):
    """System FTL resource usage.

    Attributes:
        percent_mem: FTL memory usage percentage.
        percent_cpu: FTL CPU usage percentage.
    """

    percent_mem: float = Field(
        ..., alias="%mem", description="FTL memory usage percentage"
    )
    percent_cpu: float = Field(
        ..., alias="%cpu", description="FTL CPU usage percentage"
    )


class SystemDetails(BaseModel):
    """System details.

    Attributes:
        uptime: System uptime in seconds.
        memory: Memory information.
        procs: Number of processes.
        cpu: CPU information.
        ftl: FTL resource usage.
    """

    uptime: int = Field(..., description="System uptime in seconds")
    memory: SystemMemory = Field(..., description="Memory information")
    procs: int = Field(..., description="Number of processes")
    cpu: SystemCPU = Field(..., description="CPU information")
    ftl: SystemFTL = Field(..., description="FTL resource usage")


class SystemInfo(BaseModel):
    """Pi-hole system information.

    Attributes:
        system: System details.
    """

    system: SystemDetails = Field(..., description="System details")


class Message(BaseModel):
    """Pi-hole system message.

    Attributes:
        id: Message ID (integer).
        timestamp: Message timestamp (Unix timestamp).
        type: Message type (e.g., 'info', 'warning', 'error').
        plain: Plain text message content.
        html: HTML-formatted message content.
    """

    id: int = Field(..., description="Message ID (integer)")
    timestamp: int = Field(..., description="Message timestamp (Unix timestamp)")
    type: str = Field(..., description="Message type")
    plain: str = Field(..., description="Plain text message content")
    html: str = Field(..., description="HTML-formatted message content")


class MessagesInfo(BaseModel):
    """Pi-hole messages information.

    Attributes:
        messages: List of system messages.
    """

    messages: list[Message] = Field(..., description="List of system messages")


class MessagesCountInfo(BaseModel):
    """Pi-hole messages count information.

    Attributes:
        count: Number of system messages.
    """

    count: int = Field(..., description="Number of system messages")


class DHCPLease(BaseModel):
    """DHCP lease information.

    Attributes:
        expires: Expiration time (0 = infinite lease, never expires).
        name: Hostname.
        hwaddr: Hardware (MAC) address.
        ip: IP address.
        clientid: Client ID.
    """

    expires: int = Field(..., description="Expiration time (0 = infinite lease)")
    name: str = Field(..., description="Hostname")
    hwaddr: str = Field(..., description="Hardware (MAC) address")
    ip: str = Field(..., description="IP address")
    clientid: str = Field(..., description="Client ID")


class DHCPLeasesInfo(BaseModel):
    """DHCP leases information.

    Attributes:
        leases: List of DHCP leases.
    """

    leases: list[DHCPLease] = Field(..., description="List of DHCP leases")


class PADDQueries(BaseModel):
    """PADD queries information.

    Attributes:
        total: Total number of queries.
        blocked: Number of blocked queries.
        percent_blocked: Percentage of queries that were blocked.
    """

    total: int = Field(..., description="Total number of queries")
    blocked: int = Field(..., description="Number of blocked queries")
    percent_blocked: float = Field(..., description="Percentage of queries blocked")


class PADDCache(BaseModel):
    """PADD cache information.

    Attributes:
        size: Cache size limit.
        inserted: Number of entries inserted into cache.
        evicted: Number of entries evicted from cache.
    """

    size: int = Field(..., description="Cache size limit")
    inserted: int = Field(..., description="Number of entries inserted")
    evicted: int = Field(..., description="Number of entries evicted")


class PADDMemoryRAM(BaseModel):
    """PADD RAM memory information.

    Attributes:
        total: Total RAM in KB.
        free: Free RAM in KB.
        used: Used RAM in KB.
        available: Available RAM in KB.
        percent_used: Percentage of RAM used.
    """

    total: int = Field(..., description="Total RAM in KB")
    free: int = Field(..., description="Free RAM in KB")
    used: int = Field(..., description="Used RAM in KB")
    available: int = Field(..., description="Available RAM in KB")
    percent_used: float = Field(
        ..., alias="%used", description="Percentage of RAM used"
    )


class PADDMemorySwap(BaseModel):
    """PADD swap memory information.

    Attributes:
        total: Total swap in KB.
        free: Free swap in KB.
        used: Used swap in KB.
        percent_used: Percentage of swap used.
    """

    total: int = Field(..., description="Total swap in KB")
    free: int = Field(..., description="Free swap in KB")
    used: int = Field(..., description="Used swap in KB")
    percent_used: float = Field(
        ..., alias="%used", description="Percentage of swap used"
    )


class PADDMemory(BaseModel):
    """PADD memory information.

    Attributes:
        ram: RAM information.
        swap: Swap information.
    """

    ram: PADDMemoryRAM = Field(..., description="RAM information")
    swap: PADDMemorySwap = Field(..., description="Swap information")


class PADDCPULoad(BaseModel):
    """PADD CPU load information.

    Attributes:
        raw: Raw load averages (1, 5, 15 minutes).
        percent: Load averages as percentages.
    """

    raw: list[float] = Field(..., description="Raw load averages")
    percent: list[float] = Field(..., description="Load averages as percentages")


class PADDCPU(BaseModel):
    """PADD CPU information.

    Attributes:
        nprocs: Number of CPU cores.
        percent_cpu: CPU usage percentage.
        load: Load average information.
    """

    nprocs: int = Field(..., description="Number of CPU cores")
    percent_cpu: float = Field(..., alias="%cpu", description="CPU usage percentage")
    load: PADDCPULoad = Field(..., description="Load average information")


class PADDFTL(BaseModel):
    """PADD FTL resource usage.

    Attributes:
        percent_mem: FTL memory usage percentage.
        percent_cpu: FTL CPU usage percentage.
    """

    percent_mem: float = Field(
        ..., alias="%mem", description="FTL memory usage percentage"
    )
    percent_cpu: float = Field(
        ..., alias="%cpu", description="FTL CPU usage percentage"
    )


class PADDSystem(BaseModel):
    """PADD system information.

    Attributes:
        uptime: System uptime in seconds.
        memory: Memory information.
        procs: Number of processes.
        cpu: CPU information.
        ftl: FTL resource usage.
    """

    uptime: int = Field(..., description="System uptime in seconds")
    memory: PADDMemory = Field(..., description="Memory information")
    procs: int = Field(..., description="Number of processes")
    cpu: PADDCPU = Field(..., description="CPU information")
    ftl: PADDFTL = Field(..., description="FTL resource usage")


class PADDNetworkBytes(BaseModel):
    """PADD network bytes information.

    Attributes:
        value: Byte value.
        unit: Unit (e.g., 'K', 'M', 'G').
    """

    value: float = Field(..., description="Byte value")
    unit: str = Field(..., description="Unit")


class PADDNetworkInterface(BaseModel):
    """PADD network interface information.

    Attributes:
        addr: IP address (can be None).
        rx_bytes: Received bytes information (optional).
        tx_bytes: Transmitted bytes information (optional).
        num_addrs: Number of addresses.
        name: Interface name.
        gw_addr: Gateway address (can be None).
    """

    addr: str | None = Field(None, description="IP address")
    rx_bytes: PADDNetworkBytes | None = Field(None, description="Received bytes")
    tx_bytes: PADDNetworkBytes | None = Field(None, description="Transmitted bytes")
    num_addrs: int = Field(..., description="Number of addresses")
    name: str = Field(..., description="Interface name")
    gw_addr: str | None = Field(None, description="Gateway address")


class PADDInterface(BaseModel):
    """PADD interface information.

    Attributes:
        v4: IPv4 interface information.
        v6: IPv6 interface information.
    """

    v4: PADDNetworkInterface = Field(..., description="IPv4 interface")
    v6: PADDNetworkInterface = Field(..., description="IPv6 interface")


class PADDVersionComponent(BaseModel):
    """PADD version component information.

    Attributes:
        version: Version string.
        branch: Git branch (optional).
        hash: Git commit hash.
        date: Build date (optional).
    """

    version: str = Field(..., description="Version string")
    branch: str | None = Field(None, description="Git branch")
    hash: str = Field(..., description="Git commit hash")
    date: str | None = Field(None, description="Build date")


class PADDVersionRemote(BaseModel):
    """PADD remote version information.

    Attributes:
        version: Version string.
        hash: Git commit hash.
    """

    version: str = Field(..., description="Version string")
    hash: str = Field(..., description="Git commit hash")


class PADDVersionInfo(BaseModel):
    """PADD version component info.

    Attributes:
        local: Local version information.
        remote: Remote version information.
    """

    local: PADDVersionComponent = Field(..., description="Local version")
    remote: PADDVersionRemote = Field(..., description="Remote version")


class PADDVersionDocker(BaseModel):
    """PADD Docker version information.

    Attributes:
        local: Local Docker version.
        remote: Remote Docker version.
    """

    local: str = Field(..., description="Local Docker version")
    remote: str = Field(..., description="Remote Docker version")


class PADDVersion(BaseModel):
    """PADD version information.

    Attributes:
        core: Pi-hole core version.
        web: Pi-hole web version.
        ftl: FTL version.
        docker: Docker version.
    """

    core: PADDVersionInfo = Field(..., description="Pi-hole core version")
    web: PADDVersionInfo = Field(..., description="Pi-hole web version")
    ftl: PADDVersionInfo = Field(..., description="FTL version")
    docker: PADDVersionDocker = Field(..., description="Docker version")


class PADDConfig(BaseModel):
    """PADD configuration information.

    Attributes:
        dhcp_active: Whether DHCP is active.
        dhcp_start: DHCP start address.
        dhcp_end: DHCP end address.
        dhcp_ipv6: Whether DHCP IPv6 is enabled.
        dns_domain: DNS domain.
        dns_port: DNS port.
        dns_num_upstreams: Number of upstream DNS servers.
        dns_dnssec: Whether DNSSEC is enabled.
        dns_revServer_active: Whether reverse DNS server is active.
        privacy_level: Privacy level setting.
    """

    dhcp_active: bool = Field(..., description="Whether DHCP is active")
    dhcp_start: str = Field(..., description="DHCP start address")
    dhcp_end: str = Field(..., description="DHCP end address")
    dhcp_ipv6: bool = Field(..., description="Whether DHCP IPv6 is enabled")
    dns_domain: str = Field(..., description="DNS domain")
    dns_port: int = Field(..., description="DNS port")
    dns_num_upstreams: int = Field(..., description="Number of upstream DNS servers")
    dns_dnssec: bool = Field(..., description="Whether DNSSEC is enabled")
    dns_revServer_active: bool = Field(
        ..., description="Whether reverse DNS server is active"
    )
    privacy_level: int = Field(..., description="Privacy level setting")


class PADDSensors(BaseModel):
    """PADD sensors information.

    Attributes:
        cpu_temp: CPU temperature (can be None).
        hot_limit: Hot temperature limit.
        unit: Temperature unit.
    """

    cpu_temp: float | None = Field(None, description="CPU temperature")
    hot_limit: int = Field(..., description="Hot temperature limit")
    unit: str = Field(..., description="Temperature unit")


class PADDInfo(BaseModel):
    """Pi-hole PADD (Pi-hole API Dashboard Data) information.

    This contains comprehensive dashboard data including statistics,
    system information, network details, and configuration.

    Attributes:
        active_clients: Number of active clients.
        gravity_size: Size of gravity database.
        top_domain: Top queried domain (can be None).
        top_blocked: Top blocked domain (can be None).
        top_client: Top client (can be None).
        recent_blocked: Recently blocked domain (can be None).
        blocking: Blocking status ('enabled' or 'disabled').
        queries: Query statistics.
        cache: Cache information.
        system: System resource information.
        node_name: Node/hostname.
        host_model: Host model (can be None).
        iface: Network interface information.
        version: Version information for all components.
        config: Configuration summary.
        percent_mem: Memory usage percentage.
        percent_cpu: CPU usage percentage.
        pid: Process ID.
        sensors: Temperature sensor information.
    """

    active_clients: int = Field(..., description="Number of active clients")
    gravity_size: int = Field(..., description="Size of gravity database")
    top_domain: str | None = Field(None, description="Top queried domain")
    top_blocked: str | None = Field(None, description="Top blocked domain")
    top_client: str | None = Field(None, description="Top client")
    recent_blocked: str | None = Field(None, description="Recently blocked domain")
    blocking: str = Field(..., description="Blocking status")
    queries: PADDQueries = Field(..., description="Query statistics")
    cache: PADDCache = Field(..., description="Cache information")
    system: PADDSystem = Field(..., description="System information")
    node_name: str = Field(..., description="Node/hostname")
    host_model: str | None = Field(None, description="Host model")
    iface: PADDInterface = Field(..., description="Network interface information")
    version: PADDVersion = Field(..., description="Version information")
    config: PADDConfig = Field(..., description="Configuration summary")
    percent_mem: float = Field(..., alias="%mem", description="Memory usage percentage")
    percent_cpu: float = Field(..., alias="%cpu", description="CPU usage percentage")
    pid: int = Field(..., description="Process ID")
    sensors: PADDSensors = Field(..., description="Temperature sensor information")


class DNSRecord(BaseModel):
    """DNS record information."""

    domain: str
    """Domain name."""

    target: str
    """Target (IP address for A records, domain for CNAME records)."""

    record_type: str
    """Record type ('A' or 'CNAME')."""


class DNSConfig(BaseModel):
    """DNS configuration information."""

    upstreams: list[str]
    """List of upstream DNS servers."""

    records: list[DNSRecord]
    """List of custom DNS records (A records and CNAME records)."""

    port: int
    """DNS port number."""

    query_logging: bool = Field(alias="queryLogging")
    """Whether DNS query logging is enabled."""

    dnssec: bool
    """Whether DNSSEC validation is enabled."""

    blocking: dict[str, Any]
    """DNS blocking configuration."""

    @property
    def blocking_active(self) -> bool:
        """Whether DNS blocking is active."""
        return bool(self.blocking.get("active", False))

    @property
    def hosts(self) -> list[DNSRecord]:
        """List of A records (host entries)."""
        return [record for record in self.records if record.record_type == "A"]

    @property
    def cname_records(self) -> list[DNSRecord]:
        """List of CNAME records."""
        return [record for record in self.records if record.record_type == "CNAME"]

    @classmethod
    def from_raw_config(cls, raw_config: dict[str, Any]) -> "DNSConfig":
        """Create DNSConfig from raw API response.

        Args:
            raw_config: Raw DNS configuration from API

        Returns:
            DNSConfig object with parsed DNS records
        """
        records = []

        # Parse hosts (format: "ip domain")
        for host_entry in raw_config.get("hosts", []):
            if " " in host_entry:
                ip, domain = host_entry.split(" ", 1)
                records.append(DNSRecord(domain=domain, target=ip, record_type="A"))

        # Parse CNAME records (format: "domain,target")
        for cname_entry in raw_config.get("cnameRecords", []):
            if "," in cname_entry:
                domain, target = cname_entry.split(",", 1)
                records.append(
                    DNSRecord(domain=domain, target=target, record_type="CNAME")
                )

        # Create the config with parsed records
        return cls(
            upstreams=raw_config.get("upstreams", []),
            records=records,
            port=raw_config.get("port", 53),
            queryLogging=raw_config.get("queryLogging", False),
            dnssec=raw_config.get("dnssec", False),
            blocking=raw_config.get("blocking", {}),
        )


class DNSConfigInfo(BaseModel):
    """DNS configuration response information."""

    config: dict
    """DNS configuration data (raw dict to handle nested structure)."""


class DNSBlockingStatus(BaseModel):
    """DNS blocking status information."""

    blocking: str
    """Blocking status ('enabled' or 'disabled')."""

    timer: int | None
    """Timer for temporary disable (seconds remaining, None if permanent)."""

    took: float
    """Time taken to process the request in seconds."""


class Group(BaseModel):
    """Pi-hole group information.

    Attributes:
        name: Group name.
        comment: User-provided free-text comment for this group.
        enabled: Status of group.
        id: Database ID.
        date_added: Unix timestamp of group addition.
        date_modified: Unix timestamp of last group modification.
    """

    name: str = Field(..., description="Group name")
    comment: str | None = Field(
        None, description="User-provided free-text comment for this group"
    )
    enabled: bool = Field(True, description="Status of group")
    id: int = Field(..., description="Database ID")
    date_added: int = Field(..., description="Unix timestamp of group addition")
    date_modified: int = Field(
        ..., description="Unix timestamp of last group modification"
    )


class GroupRequest(BaseModel):
    """Request model for creating or updating a group.

    Attributes:
        name: Group name.
        comment: User-provided free-text comment for this group.
        enabled: Status of group.
    """

    name: str = Field(..., description="Group name")
    comment: str | None = Field(
        None, description="User-provided free-text comment for this group"
    )
    enabled: bool = Field(True, description="Status of group")


class GroupProcessedSuccess(BaseModel):
    """Success item in group processing result.

    Attributes:
        item: Group that was successfully processed.
    """

    item: str = Field(..., description="Group that was successfully processed")


class GroupProcessedError(BaseModel):
    """Error item in group processing result.

    Attributes:
        item: Group that could not be processed.
        error: Error message.
    """

    item: str = Field(..., description="Group that could not be processed")
    error: str = Field(..., description="Error message")


class GroupProcessedResult(BaseModel):
    """Processing result for group operations.

    Attributes:
        success: Array of groups that were successfully processed.
        errors: Array of errors that occurred during processing.
    """

    success: list[GroupProcessedSuccess] = Field(
        default_factory=list, description="Successfully processed groups"
    )
    errors: list[GroupProcessedError] = Field(
        default_factory=list, description="Processing errors"
    )


class GroupsResponse(BaseModel):
    """Response model for group operations.

    Attributes:
        groups: Array of group objects.
        processed: Processing result (null for GET operations).
        took: Time in seconds it took to process the request.
    """

    groups: list[Group] = Field(..., description="Array of group objects")
    processed: GroupProcessedResult | None = Field(
        None, description="Processing result"
    )
    took: float = Field(
        ..., description="Time in seconds it took to process the request"
    )


# History and Stats Models


class HistoryEntry(BaseModel):
    """History entry for activity graph data.

    Attributes:
        timestamp: Unix timestamp.
        total: Total number of queries.
        cached: Number of cached queries.
        blocked: Number of blocked queries.
        forwarded: Number of forwarded queries.
    """

    timestamp: int = Field(..., description="Unix timestamp")
    total: int = Field(..., description="Total number of queries")
    cached: int = Field(..., description="Number of cached queries")
    blocked: int = Field(..., description="Number of blocked queries")
    forwarded: int = Field(..., description="Number of forwarded queries")


class HistoryResponse(BaseModel):
    """Response for history endpoints.

    Attributes:
        history: List of history entries.
        took: Time taken to process the request.
    """

    history: list[HistoryEntry] = Field(..., description="List of history entries")
    took: float = Field(..., description="Time taken to process the request")


class ClientHistoryEntry(BaseModel):
    """Client history entry for per-client activity data.

    Attributes:
        timestamp: Unix timestamp.
        data: Dictionary mapping client IPs/names to query counts.
    """

    timestamp: int = Field(..., description="Unix timestamp")
    data: dict[str, int] = Field(
        ..., description="Dictionary mapping client IPs/names to query counts"
    )


class ClientHistoryResponse(BaseModel):
    """Response for client history endpoints.

    Attributes:
        history: List of client history entries.
        clients: Dictionary mapping client IPs to names.
        took: Time taken to process the request.
    """

    history: list[ClientHistoryEntry] = Field(
        ..., description="List of client history entries"
    )
    clients: dict[str, str] = Field(
        ..., description="Dictionary mapping client IPs to names"
    )
    took: float = Field(..., description="Time taken to process the request")


class DatabaseHistoryResponse(BaseModel):
    """Response for database history endpoints.

    Attributes:
        history: List of history entries (empty if no data).
        took: Time taken to process the request.
    """

    history: list[HistoryEntry] = Field(..., description="List of history entries")
    took: float = Field(..., description="Time taken to process the request")


class DatabaseClientHistoryResponse(BaseModel):
    """Response for database client history endpoints.

    Attributes:
        history: List of client history entries (empty if no data).
        clients: Dictionary mapping client IPs to names.
        took: Time taken to process the request.
    """

    history: list[ClientHistoryEntry] = Field(
        ..., description="List of client history entries"
    )
    clients: dict[str, str] = Field(
        ..., description="Dictionary mapping client IPs to names"
    )
    took: float = Field(..., description="Time taken to process the request")


class QueryEntry(BaseModel):
    """Individual query entry.

    Attributes:
        timestamp: Unix timestamp of the query.
        type: Query type (A, AAAA, etc.).
        domain: Queried domain.
        client: Client IP or name.
        status: Query status (FORWARDED, BLOCKED, etc.).
        destination: Upstream destination or action.
        reply_type: Type of reply.
        response_time: Response time in milliseconds.
        dnssec: DNSSEC status.
    """

    timestamp: int = Field(..., description="Unix timestamp of the query")
    type: str = Field(..., description="Query type")
    domain: str = Field(..., description="Queried domain")
    client: str = Field(..., description="Client IP or name")
    status: str = Field(..., description="Query status")
    destination: str = Field(..., description="Upstream destination or action")
    reply_type: str = Field(..., description="Type of reply")
    response_time: float = Field(..., description="Response time in milliseconds")
    dnssec: str = Field(..., description="DNSSEC status")


class QueriesResponse(BaseModel):
    """Response for queries endpoint.

    Attributes:
        queries: List of query entries.
        cursor: Cursor for pagination.
        records_total: Total number of records.
        records_filtered: Number of filtered records.
        draw: Draw counter for DataTables.
        took: Time taken to process the request.
    """

    queries: list[QueryEntry] = Field(..., description="List of query entries")
    cursor: int = Field(..., description="Cursor for pagination")
    records_total: int = Field(
        ..., alias="recordsTotal", description="Total number of records"
    )
    records_filtered: int = Field(
        ..., alias="recordsFiltered", description="Number of filtered records"
    )
    draw: int = Field(..., description="Draw counter for DataTables")
    took: float = Field(..., description="Time taken to process the request")


class QuerySuggestions(BaseModel):
    """Query filter suggestions.

    Attributes:
        domain: List of domain suggestions.
        client_ip: List of client IP suggestions.
        client_name: List of client name suggestions.
        upstream: List of upstream suggestions.
        type: List of query type suggestions.
        status: List of status suggestions.
    """

    domain: list[str] = Field(..., description="List of domain suggestions")
    client_ip: list[str] = Field(..., description="List of client IP suggestions")
    client_name: list[str] = Field(..., description="List of client name suggestions")
    upstream: list[str] = Field(..., description="List of upstream suggestions")
    type: list[str] = Field(..., description="List of query type suggestions")
    status: list[str] = Field(..., description="List of status suggestions")


class QuerySuggestionsResponse(BaseModel):
    """Response for query suggestions endpoint.

    Attributes:
        suggestions: Query filter suggestions.
        took: Time taken to process the request.
    """

    suggestions: QuerySuggestions = Field(..., description="Query filter suggestions")
    took: float = Field(..., description="Time taken to process the request")


class QueryTypesResponse(BaseModel):
    """Response for query types endpoints.

    Attributes:
        types: Dictionary mapping query types to counts.
        took: Time taken to process the request.
    """

    types: dict[str, int] = Field(
        ..., description="Dictionary mapping query types to counts"
    )
    took: float = Field(..., description="Time taken to process the request")


class DatabaseSummaryResponse(BaseModel):
    """Response for database summary endpoint.

    Attributes:
        sum_queries: Total number of queries.
        sum_blocked: Total number of blocked queries.
        percent_blocked: Percentage of queries blocked.
        total_clients: Total number of clients.
        took: Time taken to process the request.
    """

    sum_queries: int = Field(..., description="Total number of queries")
    sum_blocked: int = Field(..., description="Total number of blocked queries")
    percent_blocked: float = Field(..., description="Percentage of queries blocked")
    total_clients: int = Field(..., description="Total number of clients")
    took: float = Field(..., description="Time taken to process the request")


class TopClient(BaseModel):
    """Top client entry.

    Attributes:
        ip: Client IP address.
        name: Client name (if available).
        count: Number of queries.
    """

    ip: str = Field(..., description="Client IP address")
    name: str | None = Field(None, description="Client name")
    count: int = Field(..., description="Number of queries")


class TopClientsResponse(BaseModel):
    """Response for top clients endpoints.

    Attributes:
        clients: List of top clients.
        total_queries: Total number of queries.
        blocked_queries: Total number of blocked queries.
        took: Time taken to process the request.
    """

    clients: list[TopClient] = Field(..., description="List of top clients")
    total_queries: int = Field(..., description="Total number of queries")
    blocked_queries: int = Field(..., description="Total number of blocked queries")
    took: float = Field(..., description="Time taken to process the request")


class TopDomain(BaseModel):
    """Top domain entry.

    Attributes:
        domain: Domain name.
        count: Number of queries.
    """

    domain: str = Field(..., description="Domain name")
    count: int = Field(..., description="Number of queries")


class TopDomainsResponse(BaseModel):
    """Response for top domains endpoints.

    Attributes:
        domains: List of top domains.
        total_queries: Total number of queries.
        blocked_queries: Total number of blocked queries.
        took: Time taken to process the request.
    """

    domains: list[TopDomain] = Field(..., description="List of top domains")
    total_queries: int = Field(..., description="Total number of queries")
    blocked_queries: int = Field(..., description="Total number of blocked queries")
    took: float = Field(..., description="Time taken to process the request")


class UpstreamStatistics(BaseModel):
    """Upstream server statistics.

    Attributes:
        response: Average response time.
        variance: Response time variance.
    """

    response: float = Field(..., description="Average response time")
    variance: float = Field(..., description="Response time variance")


class UpstreamServer(BaseModel):
    """Upstream server information.

    Attributes:
        ip: Server IP address or identifier.
        name: Server name.
        port: Server port (-1 for special entries).
        count: Number of queries sent to this upstream.
        statistics: Response time statistics (optional).
    """

    ip: str = Field(..., description="Server IP address or identifier")
    name: str = Field(..., description="Server name")
    port: int = Field(..., description="Server port")
    count: int = Field(..., description="Number of queries sent to this upstream")
    statistics: UpstreamStatistics | None = Field(
        None, description="Response time statistics"
    )


class UpstreamsResponse(BaseModel):
    """Response for upstreams endpoints.

    Attributes:
        upstreams: List of upstream servers.
        total_queries: Total number of queries.
        forwarded_queries: Number of forwarded queries.
        took: Time taken to process the request.
    """

    upstreams: list[UpstreamServer] = Field(..., description="List of upstream servers")
    total_queries: int = Field(..., description="Total number of queries")
    forwarded_queries: int = Field(..., description="Number of forwarded queries")
    took: float = Field(..., description="Time taken to process the request")


class RecentBlockedResponse(BaseModel):
    """Response for recent blocked domains endpoint.

    Attributes:
        blocked: List of recently blocked domains.
        took: Time taken to process the request.
    """

    blocked: list[str] = Field(..., description="List of recently blocked domains")
    took: float = Field(..., description="Time taken to process the request")


class SummaryQueries(BaseModel):
    """Summary queries information.

    Attributes:
        total: Total number of queries.
        blocked: Number of blocked queries.
        percent_blocked: Percentage of queries blocked.
        unique_domains: Number of unique domains.
        forwarded: Number of forwarded queries.
        cached: Number of cached queries.
        frequency: Query frequency.
        types: Dictionary of query types and counts.
        status: Dictionary of query statuses and counts.
        replies: Dictionary of reply types and counts.
    """

    total: int = Field(..., description="Total number of queries")
    blocked: int = Field(..., description="Number of blocked queries")
    percent_blocked: float = Field(..., description="Percentage of queries blocked")
    unique_domains: int = Field(..., description="Number of unique domains")
    forwarded: int = Field(..., description="Number of forwarded queries")
    cached: int = Field(..., description="Number of cached queries")
    frequency: float = Field(..., description="Query frequency")
    types: dict[str, int] = Field(
        ..., description="Dictionary of query types and counts"
    )
    status: dict[str, int] = Field(
        ..., description="Dictionary of query statuses and counts"
    )
    replies: dict[str, int] = Field(
        ..., description="Dictionary of reply types and counts"
    )


class SummaryClients(BaseModel):
    """Summary clients information.

    Attributes:
        total: Total number of clients.
        active: Number of active clients.
    """

    total: int = Field(..., description="Total number of clients")
    active: int = Field(..., description="Number of active clients")


class SummaryGravity(BaseModel):
    """Summary gravity information.

    Attributes:
        domains_being_blocked: Number of domains on blocklists.
        last_update: Last gravity update timestamp.
    """

    domains_being_blocked: int = Field(
        ..., description="Number of domains on blocklists"
    )
    last_update: int = Field(..., description="Last gravity update timestamp")


class SummaryResponse(BaseModel):
    """Response for summary endpoint.

    Attributes:
        queries: Query statistics.
        clients: Client statistics.
        gravity: Gravity statistics.
        took: Time taken to process the request.
    """

    queries: SummaryQueries = Field(..., description="Query statistics")
    clients: SummaryClients = Field(..., description="Client statistics")
    gravity: SummaryGravity = Field(..., description="Gravity statistics")
    took: float = Field(..., description="Time taken to process the request")


class DomainType(str, Enum):
    """Pi-hole domain types."""

    ALLOW = "allow"
    DENY = "deny"


class DomainKind(str, Enum):
    """Pi-hole domain kinds."""

    EXACT = "exact"
    REGEX = "regex"


class Domain(BaseModel):
    """Pi-hole domain entry.

    Attributes:
        domain: The domain name or regex pattern.
        unicode: Unicode representation of the domain.
        type: Type of domain (allow or deny).
        kind: Kind of domain (exact or regex).
        comment: User-provided free-text comment for this domain.
        groups: Array of group IDs.
        enabled: Status of domain.
        id: Database ID.
        date_added: Unix timestamp of item addition.
        date_modified: Unix timestamp of last item modification.
    """

    domain: str = Field(..., description="The domain name or regex pattern")
    unicode: str = Field(..., description="Unicode representation of the domain")
    type: DomainType = Field(..., description="Type of domain")
    kind: DomainKind = Field(..., description="Kind of domain")
    comment: str | None = Field(
        None, description="User-provided free-text comment for this domain"
    )
    groups: list[int] = Field(..., description="Array of group IDs")
    enabled: bool = Field(True, description="Status of domain")
    id: int = Field(..., description="Database ID")
    date_added: int = Field(..., description="Unix timestamp of item addition")
    date_modified: int = Field(
        ..., description="Unix timestamp of last item modification"
    )


class DomainsResponse(BaseModel):
    """Response for domains endpoints.

    Attributes:
        domains: List of domain entries.
        took: Time taken to process the request.
    """

    domains: list[Domain] = Field(..., description="List of domain entries")
    took: float = Field(..., description="Time taken to process the request")


class DomainRequest(BaseModel):
    """Request for adding/updating domains.

    Attributes:
        domain: The domain name or regex pattern.
        type: Type of domain (allow or deny). Used for moving domains.
        kind: Kind of domain (exact or regex). Used for moving domains.
        comment: User-provided free-text comment for this domain.
        groups: Array of group IDs.
        enabled: Status of domain.
    """

    domain: str | None = Field(None, description="The domain name or regex pattern")
    type: DomainType | None = Field(None, description="Type of domain")
    kind: DomainKind | None = Field(None, description="Kind of domain")
    comment: str | None = Field(
        None, description="User-provided free-text comment for this domain"
    )
    groups: list[int] | None = Field(None, description="Array of group IDs")
    enabled: bool | None = Field(None, description="Status of domain")


class DomainBatchDeleteItem(BaseModel):
    """Item for batch domain deletion.

    Attributes:
        item: Domain to delete.
        type: Type of domain to delete.
        kind: Kind of domain to delete.
    """

    item: str = Field(..., description="Domain to delete")
    type: DomainType = Field(..., description="Type of domain to delete")
    kind: DomainKind = Field(..., description="Kind of domain to delete")


class DomainProcessedSuccess(BaseModel):
    """Successful domain processing result.

    Attributes:
        item: The domain that was processed.
    """

    item: str = Field(..., description="The domain that was processed")


class DomainProcessedError(BaseModel):
    """Failed domain processing result.

    Attributes:
        item: The domain that failed to process.
        error: Error message.
    """

    item: str = Field(..., description="The domain that failed to process")
    error: str = Field(..., description="Error message")


class DomainProcessedResult(BaseModel):
    """Domain processing results.

    Attributes:
        success: List of successfully processed domains.
        errors: List of failed domain processing attempts.
    """

    success: list[DomainProcessedSuccess] = Field(
        ..., description="List of successfully processed domains"
    )
    errors: list[DomainProcessedError] = Field(
        ..., description="List of failed domain processing attempts"
    )


class DomainMutationResponse(BaseModel):
    """Response for domain mutation operations (add, update, delete).

    Attributes:
        domains: List of domain entries after the operation.
        processed: Processing results.
        took: Time taken to process the request.
    """

    domains: list[Domain] = Field(
        ..., description="List of domain entries after the operation"
    )
    processed: DomainProcessedResult = Field(..., description="Processing results")
    took: float = Field(..., description="Time taken to process the request")


class DomainBatchDeleteResponse(BaseModel):
    """Response for batch domain deletion.

    Attributes:
        took: Time taken to process the request.
    """

    took: float = Field(..., description="Time taken to process the request")


# Network models


class NetworkDeviceAddress(BaseModel):
    """Network device address information.

    Attributes:
        ip: IP address.
        hostname: Hostname associated with the IP.
        last_query: Unix timestamp of last query from this IP.
    """

    ip: str = Field(..., description="IP address")
    hostname: str | None = Field(None, description="Hostname associated with the IP")
    last_query: int = Field(
        ..., description="Unix timestamp of last query from this IP"
    )


class NetworkDevice(BaseModel):
    """Network device information.

    Attributes:
        id: Device ID.
        hwaddr: Hardware (MAC) address.
        interface: Network interface.
        name: Device name.
        first_seen: Unix timestamp when device was first seen.
        last_query: Unix timestamp of last query from this device.
        num_queries: Total number of queries from this device.
        addresses: List of IP addresses associated with this device.
    """

    id: int = Field(..., description="Device ID")
    hwaddr: str = Field(..., description="Hardware (MAC) address")
    interface: str = Field(..., description="Network interface")
    name: str = Field(..., description="Device name")
    first_seen: int = Field(
        ..., description="Unix timestamp when device was first seen"
    )
    last_query: int = Field(
        ..., description="Unix timestamp of last query from this device"
    )
    num_queries: int = Field(
        ..., description="Total number of queries from this device"
    )
    addresses: list[NetworkDeviceAddress] = Field(
        ..., description="List of IP addresses associated with this device"
    )


class NetworkDevicesResponse(BaseModel):
    """Response for network devices endpoint.

    Attributes:
        devices: List of network devices.
        took: Time taken to process the request.
    """

    devices: list[NetworkDevice] = Field(..., description="List of network devices")
    took: float = Field(..., description="Time taken to process the request")


class NetworkGateway(BaseModel):
    """Network gateway information.

    Attributes:
        family: Address family (inet, inet6).
        interface: Network interface.
        address: Gateway IP address.
        local: List of local IP addresses.
    """

    family: str = Field(..., description="Address family (inet, inet6)")
    interface: str = Field(..., description="Network interface")
    address: str = Field(..., description="Gateway IP address")
    local: list[str] = Field(..., description="List of local IP addresses")


class NetworkGatewayResponse(BaseModel):
    """Response for network gateway endpoint.

    Attributes:
        gateway: List of gateway information.
        took: Time taken to process the request.
    """

    gateway: list[NetworkGateway] = Field(
        ..., description="List of gateway information"
    )
    took: float = Field(..., description="Time taken to process the request")


class NetworkGatewayDetailedResponse(BaseModel):
    """Response for detailed network gateway endpoint.

    Attributes:
        gateway: List of gateway information.
        routes: List of routing table entries.
        interfaces: List of network interfaces.
        took: Time taken to process the request.
    """

    gateway: list[NetworkGateway] = Field(
        ..., description="List of gateway information"
    )
    routes: list[dict] = Field(..., description="List of routing table entries")
    interfaces: list[dict] = Field(..., description="List of network interfaces")
    took: float = Field(..., description="Time taken to process the request")


class NetworkInterfaceStats(BaseModel):
    """Network interface statistics.

    Attributes:
        rx_bytes: Received bytes with value and unit.
        tx_bytes: Transmitted bytes with value and unit.
        bits: Bit architecture (32 or 64).
    """

    rx_bytes: dict[str, str | float] = Field(
        ..., description="Received bytes with value and unit"
    )
    tx_bytes: dict[str, str | float] = Field(
        ..., description="Transmitted bytes with value and unit"
    )
    bits: int = Field(..., description="Bit architecture (32 or 64)")


class NetworkInterfaceAddress(BaseModel):
    """Network interface address information.

    Attributes:
        family: Address family (inet, inet6).
        scope: Address scope.
        flags: List of address flags.
        prefixlen: Prefix length.
        address: IP address.
        address_type: Type of address.
        local: Local address.
        local_type: Type of local address.
        broadcast: Broadcast address (optional).
        broadcast_type: Type of broadcast address (optional).
        label: Interface label (optional).
        prefered: Preferred lifetime.
        valid: Valid lifetime.
        cstamp: Creation timestamp.
        tstamp: Timestamp.
    """

    family: str = Field(..., description="Address family (inet, inet6)")
    scope: str = Field(..., description="Address scope")
    flags: list[str] = Field(..., description="List of address flags")
    prefixlen: int = Field(..., description="Prefix length")
    address: str = Field(..., description="IP address")
    address_type: str = Field(..., description="Type of address")
    local: str | None = Field(None, description="Local address")
    local_type: str | None = Field(None, description="Type of local address")
    broadcast: str | None = Field(None, description="Broadcast address")
    broadcast_type: str | None = Field(None, description="Type of broadcast address")
    label: str | None = Field(None, description="Interface label")
    prefered: int = Field(..., description="Preferred lifetime")
    valid: int = Field(..., description="Valid lifetime")
    cstamp: float = Field(..., description="Creation timestamp")
    tstamp: float = Field(..., description="Timestamp")


class NetworkInterface(BaseModel):
    """Network interface information.

    Attributes:
        name: Interface name.
        speed: Interface speed (optional).
        type: Interface type.
        flags: List of interface flags.
        state: Interface state.
        carrier: Carrier status.
        proto_down: Protocol down status.
        address: Hardware address.
        broadcast: Broadcast address.
        perm_address: Permanent address (optional).
        stats: Interface statistics.
        addresses: List of IP addresses (optional).
    """

    name: str = Field(..., description="Interface name")
    speed: int | None = Field(None, description="Interface speed")
    type: str = Field(..., description="Interface type")
    flags: list[str] = Field(..., description="List of interface flags")
    state: str = Field(..., description="Interface state")
    carrier: bool = Field(..., description="Carrier status")
    proto_down: bool = Field(..., description="Protocol down status")
    address: str = Field(..., description="Hardware address")
    broadcast: str = Field(..., description="Broadcast address")
    perm_address: str | None = Field(None, description="Permanent address")
    stats: NetworkInterfaceStats = Field(..., description="Interface statistics")
    addresses: list[NetworkInterfaceAddress] | None = Field(
        None, description="List of IP addresses"
    )


class NetworkInterfacesResponse(BaseModel):
    """Response for network interfaces endpoint.

    Attributes:
        interfaces: List of network interfaces.
        took: Time taken to process the request.
    """

    interfaces: list[NetworkInterface] = Field(
        ..., description="List of network interfaces"
    )
    took: float = Field(..., description="Time taken to process the request")


class NetworkRoute(BaseModel):
    """Network route information.

    Attributes:
        table: Routing table ID.
        family: Address family (inet, inet6).
        protocol: Routing protocol.
        scope: Route scope.
        type: Route type.
        flags: List of route flags.
        gateway: Gateway address (optional).
        oif: Output interface.
        dst: Destination address.
        prefsrc: Preferred source address (optional).
        priority: Route priority (optional).
        pref: Route preference (optional).
    """

    table: int = Field(..., description="Routing table ID")
    family: str = Field(..., description="Address family (inet, inet6)")
    protocol: str = Field(..., description="Routing protocol")
    scope: str = Field(..., description="Route scope")
    type: str = Field(..., description="Route type")
    flags: list[str] = Field(..., description="List of route flags")
    gateway: str | None = Field(None, description="Gateway address")
    oif: str = Field(..., description="Output interface")
    dst: str = Field(..., description="Destination address")
    prefsrc: str | None = Field(None, description="Preferred source address")
    priority: int | None = Field(None, description="Route priority")
    pref: int | None = Field(None, description="Route preference")


class NetworkRoutesResponse(BaseModel):
    """Response for network routes endpoint.

    Attributes:
        routes: List of network routes.
        took: Time taken to process the request.
    """

    routes: list[NetworkRoute] = Field(..., description="List of network routes")
    took: float = Field(..., description="Time taken to process the request")


class NetworkDeviceDeleteResponse(BaseModel):
    """Response for network device deletion.

    Attributes:
        took: Time taken to process the request.
    """

    took: float = Field(..., description="Time taken to process the request")


# Client Management Models


class Client(BaseModel):
    """Pi-hole client entry.

    Attributes:
        client: Client identifier (IP, MAC, hostname, or interface).
        name: Client name (hostname if available).
        comment: User-provided free-text comment for this client.
        groups: Array of group IDs.
        id: Database ID.
        date_added: Unix timestamp of client addition.
        date_modified: Unix timestamp of last client modification.
    """

    client: str = Field(..., description="Client identifier")
    name: str = Field(default="", description="Client name")
    comment: str | None = Field(
        None, description="User-provided free-text comment for this client"
    )
    groups: list[int] = Field(..., description="Array of group IDs")
    id: int = Field(..., description="Database ID")
    date_added: int = Field(..., description="Unix timestamp of client addition")
    date_modified: int = Field(
        ..., description="Unix timestamp of last client modification"
    )


class ClientRequest(BaseModel):
    """Request model for creating or updating a client.

    Attributes:
        client: Client identifier (IP, MAC, hostname, or interface).
        comment: User-provided free-text comment for this client.
        groups: Array of group IDs.
    """

    client: str | None = Field(None, description="Client identifier")
    comment: str | None = Field(
        None, description="User-provided free-text comment for this client"
    )
    groups: list[int] = Field(default=[0], description="Array of group IDs")


class ClientUpdateRequest(BaseModel):
    """Request model for updating an existing client.

    Attributes:
        comment: User-provided free-text comment for this client.
        groups: Array of group IDs.
    """

    comment: str | None = Field(
        None, description="User-provided free-text comment for this client"
    )
    groups: list[int] = Field(..., description="Array of group IDs")


class ClientBatchDeleteItem(BaseModel):
    """Item for batch client deletion.

    Attributes:
        item: Client identifier to delete.
    """

    item: str = Field(..., description="Client identifier to delete")


class ClientProcessedSuccess(BaseModel):
    """Success item in client processing result.

    Attributes:
        item: Client that was successfully processed.
    """

    item: str = Field(..., description="Client that was successfully processed")


class ClientProcessedError(BaseModel):
    """Error item in client processing result.

    Attributes:
        item: Client that could not be processed.
        error: Error message.
    """

    item: str = Field(..., description="Client that could not be processed")
    error: str = Field(..., description="Error message")


class ClientProcessedResult(BaseModel):
    """Processing result for client operations.

    Attributes:
        success: Array of clients that were successfully processed.
        errors: Array of errors that occurred during processing.
    """

    success: list[ClientProcessedSuccess] = Field(
        default_factory=list, description="Successfully processed clients"
    )
    errors: list[ClientProcessedError] = Field(
        default_factory=list, description="Processing errors"
    )


class ClientsResponse(BaseModel):
    """Response model for client operations.

    Attributes:
        clients: Array of client objects.
        processed: Processing result (null for GET operations).
        took: Time in seconds it took to process the request.
    """

    clients: list[Client] = Field(..., description="Array of client objects")
    processed: ClientProcessedResult | None = Field(
        None, description="Processing result"
    )
    took: float = Field(
        ..., description="Time in seconds it took to process the request"
    )


class ClientSuggestionsResponse(BaseModel):
    """Response model for client suggestions.

    Attributes:
        clients: Array of unconfigured client suggestions.
        took: Time in seconds it took to process the request.
    """

    clients: list[Client] = Field(
        ..., description="Array of unconfigured client suggestions"
    )
    took: float = Field(
        ..., description="Time in seconds it took to process the request"
    )
