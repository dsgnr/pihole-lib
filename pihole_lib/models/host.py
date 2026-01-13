"""Host system models."""

from pydantic import Field

from pihole_lib.models.base import StrictModel


class HostUname(StrictModel):
    """Host system uname information."""

    domainname: str = Field(..., description="Domain name")
    machine: str = Field(..., description="Machine hardware name")
    nodename: str = Field(..., description="Network node hostname")
    release: str = Field(..., description="Operating system release")
    sysname: str = Field(..., description="Operating system name")
    version: str = Field(..., description="Operating system version")


class HostDMIBios(StrictModel):
    """Host DMI BIOS information."""

    vendor: str | None = Field(None, description="BIOS vendor")


class HostDMIBoard(StrictModel):
    """Host DMI board information."""

    name: str | None = Field(None, description="Board name")
    vendor: str | None = Field(None, description="Board vendor")
    version: str | None = Field(None, description="Board version")


class HostDMIProduct(StrictModel):
    """Host DMI product information."""

    name: str | None = Field(None, description="Product name")
    family: str | None = Field(None, description="Product family")
    version: str | None = Field(None, description="Product version")


class HostDMISystem(StrictModel):
    """Host DMI system information."""

    vendor: str | None = Field(None, description="System vendor")


class HostDMI(StrictModel):
    """Host DMI/SMBIOS information."""

    bios: HostDMIBios = Field(..., description="BIOS information")
    board: HostDMIBoard = Field(..., description="Board information")
    product: HostDMIProduct = Field(..., description="Product information")
    sys: HostDMISystem = Field(..., description="System information")


class HostDetails(StrictModel):
    """Host system details."""

    uname: HostUname = Field(..., description="System uname information")
    model: str | None = Field(None, description="Hardware model")
    dmi: HostDMI = Field(..., description="DMI/SMBIOS information")


class HostInfo(StrictModel):
    """Pi-hole host system information wrapper."""

    host: HostDetails = Field(..., description="Host system details")
