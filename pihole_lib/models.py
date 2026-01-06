"""Data models for Pi-hole API responses."""

from typing import Optional

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
