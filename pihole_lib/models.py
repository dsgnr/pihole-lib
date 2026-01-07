"""Data models for Pi-hole API responses."""

from enum import Enum

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

    version: str = Field(..., description="Version string")
    hash: str = Field(..., description="Git commit hash")


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

    local: str = Field(..., description="Local Docker version")
    remote: str = Field(..., description="Remote Docker version")


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
    """

    version: VersionDetails = Field(
        ..., description="Version details for all components"
    )


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
