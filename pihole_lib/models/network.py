"""Network models."""

from pydantic import Field

from pihole_lib.models.base import StrictModel, TimedResponse


class NetworkDeviceAddress(StrictModel):
    """Network device address information."""

    ip: str = Field(..., description="IP address")
    hostname: str | None = Field(None, description="Hostname associated with the IP")
    last_query: int = Field(
        ..., description="Unix timestamp of last query from this IP"
    )


class NetworkDevice(StrictModel):
    """Network device information."""

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


class NetworkDevicesResponse(TimedResponse):
    """Response for network devices endpoint."""

    devices: list[NetworkDevice] = Field(..., description="List of network devices")


class NetworkGateway(StrictModel):
    """Network gateway information."""

    family: str = Field(..., description="Address family (inet, inet6)")
    interface: str = Field(..., description="Network interface")
    address: str = Field(..., description="Gateway IP address")
    local: list[str] = Field(..., description="List of local IP addresses")


class NetworkGatewayResponse(TimedResponse):
    """Response for network gateway endpoint."""

    gateway: list[NetworkGateway] = Field(
        ..., description="List of gateway information"
    )


class NetworkGatewayDetailedResponse(TimedResponse):
    """Response for detailed network gateway endpoint."""

    gateway: list[NetworkGateway] = Field(
        ..., description="List of gateway information"
    )
    routes: list[dict] = Field(..., description="List of routing table entries")
    interfaces: list[dict] = Field(..., description="List of network interfaces")


class NetworkInterfaceStats(StrictModel):
    """Network interface statistics."""

    rx_bytes: dict[str, str | float] = Field(
        ..., description="Received bytes with value and unit"
    )
    tx_bytes: dict[str, str | float] = Field(
        ..., description="Transmitted bytes with value and unit"
    )
    bits: int = Field(..., description="Bit architecture (32 or 64)")


class NetworkInterfaceAddress(StrictModel):
    """Network interface address information."""

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


class NetworkInterface(StrictModel):
    """Network interface information."""

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


class NetworkInterfacesResponse(TimedResponse):
    """Response for network interfaces endpoint."""

    interfaces: list[NetworkInterface] = Field(
        ..., description="List of network interfaces"
    )


class NetworkRoute(StrictModel):
    """Network route information."""

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


class NetworkRoutesResponse(TimedResponse):
    """Response for network routes endpoint."""

    routes: list[NetworkRoute] = Field(..., description="List of network routes")


class NetworkDeviceDeleteResponse(TimedResponse):
    """Response for network device deletion."""

    pass
