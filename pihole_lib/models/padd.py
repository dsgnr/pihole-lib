"""PADD (Pi-hole API Dashboard Data) models."""

from pydantic import Field

from pihole_lib.models.base import StrictModel
from pihole_lib.models.system import CPUStats, FTLResourceUsage, MemoryStats, RAMStats


class PADDQueries(StrictModel):
    """PADD queries information."""

    total: int = Field(..., description="Total number of queries")
    blocked: int = Field(..., description="Number of blocked queries")
    percent_blocked: float = Field(..., description="Percentage of queries blocked")


class PADDCache(StrictModel):
    """PADD cache information."""

    size: int = Field(..., description="Cache size limit")
    inserted: int = Field(..., description="Number of entries inserted")
    evicted: int = Field(..., description="Number of entries evicted")


class PADDMemory(StrictModel):
    """PADD memory information."""

    ram: RAMStats = Field(..., description="RAM information")
    swap: MemoryStats = Field(..., description="Swap information")


class PADDSystem(StrictModel):
    """PADD system information."""

    uptime: int = Field(..., description="System uptime in seconds")
    memory: PADDMemory = Field(..., description="Memory information")
    procs: int = Field(..., description="Number of processes")
    cpu: CPUStats = Field(..., description="CPU information")
    ftl: FTLResourceUsage = Field(..., description="FTL resource usage")


class PADDNetworkBytes(StrictModel):
    """PADD network bytes information."""

    value: float = Field(..., description="Byte value")
    unit: str = Field(..., description="Unit")


class PADDNetworkInterface(StrictModel):
    """PADD network interface information."""

    addr: str | None = Field(None, description="IP address")
    rx_bytes: PADDNetworkBytes | None = Field(None, description="Received bytes")
    tx_bytes: PADDNetworkBytes | None = Field(None, description="Transmitted bytes")
    num_addrs: int = Field(..., description="Number of addresses")
    name: str = Field(..., description="Interface name")
    gw_addr: str | None = Field(None, description="Gateway address")


class PADDInterface(StrictModel):
    """PADD interface information."""

    v4: PADDNetworkInterface = Field(..., description="IPv4 interface")
    v6: PADDNetworkInterface = Field(..., description="IPv6 interface")


class PADDVersionComponent(StrictModel):
    """PADD version component information."""

    version: str = Field(..., description="Version string")
    branch: str | None = Field(None, description="Git branch")
    hash: str = Field(..., description="Git commit hash")
    date: str | None = Field(None, description="Build date")


class PADDVersionRemote(StrictModel):
    """PADD remote version information."""

    version: str = Field(..., description="Version string")
    hash: str = Field(..., description="Git commit hash")


class PADDVersionInfo(StrictModel):
    """PADD version component info."""

    local: PADDVersionComponent = Field(..., description="Local version")
    remote: PADDVersionRemote = Field(..., description="Remote version")


class PADDVersionDocker(StrictModel):
    """PADD Docker version information."""

    local: str = Field(..., description="Local Docker version")
    remote: str = Field(..., description="Remote Docker version")


class PADDVersion(StrictModel):
    """PADD version information."""

    core: PADDVersionInfo = Field(..., description="Pi-hole core version")
    web: PADDVersionInfo = Field(..., description="Pi-hole web version")
    ftl: PADDVersionInfo = Field(..., description="FTL version")
    docker: PADDVersionDocker = Field(..., description="Docker version")


class PADDConfig(StrictModel):
    """PADD configuration information."""

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


class PADDSensors(StrictModel):
    """PADD sensors information."""

    cpu_temp: float | None = Field(None, description="CPU temperature")
    hot_limit: int = Field(..., description="Hot temperature limit")
    unit: str = Field(..., description="Temperature unit")


class PADDInfo(StrictModel):
    """Pi-hole PADD (Pi-hole API Dashboard Data) information."""

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
