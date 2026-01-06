"""Data models for Pi-hole API responses."""

from typing import List, Optional

from pydantic import BaseModel, Field


class LoginInfo(BaseModel):
    """Pi-hole login page information.

    Attributes:
        https_port: HTTPS port of the Pi-hole webserver (0 if disabled).
        dns: Whether the DNS server is up and running. False only in failed state.
        took: Time in seconds it took to process the request.
    """

    https_port: int = Field(
        ..., description="HTTPS port of the Pi-hole webserver (0 if disabled)"
    )
    dns: bool = Field(..., description="Whether the DNS server is up and running")
    took: float = Field(
        ..., description="Time in seconds it took to process the request"
    )


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


class TeleporterImportResult(BaseModel):
    """Pi-hole Teleporter import result.

    Attributes:
        files: List of imported backup files/components.
        took: Time in seconds it took to process the request.
    """

    files: List[str] = Field(
        ..., description="List of imported backup files/components"
    )
    took: float = Field(
        ..., description="Time in seconds it took to process the request"
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


class AuthResponse(BaseModel):
    """Pi-hole authentication response.

    Attributes:
        session: Authentication session data.
        took: Request processing time in seconds.
    """

    session: PiHoleAuthSession = Field(..., description="Authentication session data")
    took: float = Field(..., description="Request processing time in seconds")
