"""Message models."""

from pydantic import Field

from pihole_lib.models.base import StrictModel


class Message(StrictModel):
    """Pi-hole system message."""

    id: int = Field(..., description="Message ID")
    timestamp: int = Field(..., description="Message timestamp (Unix timestamp)")
    type: str = Field(
        ..., description="Message type (e.g., 'info', 'warning', 'error')"
    )
    plain: str = Field(..., description="Plain text message content")
    html: str = Field(..., description="HTML-formatted message content")


class MessagesInfo(StrictModel):
    """Pi-hole messages information."""

    messages: list[Message] = Field(..., description="List of system messages")


class MessagesCountInfo(StrictModel):
    """Pi-hole messages count information."""

    count: int = Field(..., description="Number of system messages")
