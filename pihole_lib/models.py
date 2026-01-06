"""Data models for Pi-hole API responses."""

from enum import Enum
from typing import List, Optional

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
    comment: Optional[str] = Field(
        None, description="User-provided free-text comment for this list"
    )
    groups: List[int] = Field(..., description="Array of group IDs")
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
    message: Optional[str] = Field(None, description="Optional message from Pi-hole")
