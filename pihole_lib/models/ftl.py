"""FTL and database models."""

from pydantic import Field

from pihole_lib.models.base import StrictModel


class DatabaseUser(StrictModel):
    """Database file user information."""

    uid: int = Field(..., description="User ID")
    name: str = Field(..., description="User name")
    info: str = Field(..., description="Additional user information")


class DatabaseGroup(StrictModel):
    """Database file group information."""

    gid: int = Field(..., description="Group ID")
    name: str = Field(..., description="Group name")


class DatabaseOwner(StrictModel):
    """Database file ownership information."""

    user: DatabaseUser = Field(..., description="User information")
    group: DatabaseGroup = Field(..., description="Group information")


class DatabaseInfo(StrictModel):
    """Pi-hole database information."""

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


class FTLDatabaseStats(StrictModel):
    """FTL database statistics."""

    gravity: int = Field(..., description="Number of gravity domains")
    groups: int = Field(..., description="Number of groups")
    lists: int = Field(..., description="Number of lists")
    clients: int = Field(..., description="Number of clients")
    domains: dict = Field(..., description="Domain statistics")
    regex: dict = Field(..., description="Regex statistics")


class FTLClientStats(StrictModel):
    """FTL client statistics."""

    total: int = Field(..., description="Total number of clients")
    active: int = Field(..., description="Number of active clients")


class FTLDnsmasqStats(StrictModel):
    """FTL dnsmasq statistics."""

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


class FTLStats(StrictModel):
    """FTL statistics."""

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


class FTLInfo(StrictModel):
    """Pi-hole FTL information wrapper."""

    ftl: FTLStats = Field(..., description="FTL statistics and runtime information")
