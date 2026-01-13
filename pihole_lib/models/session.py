"""Authentication and session models."""

from pydantic import Field

from pihole_lib.models.base import StrictModel


class LoginInfo(StrictModel):
    """Pi-hole login page information."""

    https_port: int = Field(
        ..., description="HTTPS port of the Pi-hole webserver (0 if disabled)"
    )
    dns: bool = Field(..., description="Whether the DNS server is up and running")


class PiHoleAuthSession(StrictModel):
    """Pi-hole authentication session data."""

    valid: bool = Field(..., description="Whether session is valid")
    totp: bool = Field(..., description="Whether two-factor auth is enabled")
    sid: str = Field(..., description="Session ID token")
    csrf: str = Field(..., description="CSRF protection token")
    validity: int = Field(..., description="Session duration in seconds")
    message: str | None = Field(None, description="Optional message from Pi-hole")


class ClientHeader(StrictModel):
    """HTTP header from client request."""

    name: str = Field(..., description="Header name")
    value: str = Field(..., description="Header value")


class ClientInfo(StrictModel):
    """Pi-hole client request information."""

    remote_addr: str = Field(..., description="Client's remote IP address")
    http_version: str = Field(..., description="HTTP version used by client")
    method: str = Field(..., description="HTTP method used")
    headers: list[ClientHeader] = Field(..., description="HTTP headers sent by client")
