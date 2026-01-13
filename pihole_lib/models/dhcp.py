"""DHCP models."""

from pydantic import Field

from pihole_lib.models.base import StrictModel


class DHCPLease(StrictModel):
    """DHCP lease information."""

    expires: int = Field(
        ..., description="Expiration time (0 = infinite lease, never expires)"
    )
    name: str = Field(..., description="Hostname")
    hwaddr: str = Field(..., description="Hardware (MAC) address")
    ip: str = Field(..., description="IP address")
    clientid: str = Field(..., description="Client ID")


class DHCPLeasesInfo(StrictModel):
    """DHCP leases information."""

    leases: list[DHCPLease] = Field(..., description="List of DHCP leases")
