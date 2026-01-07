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
