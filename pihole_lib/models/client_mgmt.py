"""Client management models."""

from pydantic import Field

from pihole_lib.models.base import StrictModel, TimedResponse


class Client(StrictModel):
    """Pi-hole client entry."""

    client: str = Field(
        ..., description="Client identifier (IP, MAC, hostname, or interface)"
    )
    name: str = Field(default="", description="Client name (hostname if available)")
    comment: str | None = Field(
        None, description="User-provided free-text comment for this client"
    )
    groups: list[int] = Field(..., description="Array of group IDs")
    id: int = Field(..., description="Database ID")
    date_added: int = Field(..., description="Unix timestamp of client addition")
    date_modified: int = Field(
        ..., description="Unix timestamp of last client modification"
    )


class ClientRequest(StrictModel):
    """Request model for creating or updating a client."""

    client: str | None = Field(
        None, description="Client identifier (IP, MAC, hostname, or interface)"
    )
    comment: str | None = Field(
        None, description="User-provided free-text comment for this client"
    )
    groups: list[int] = Field(default=[0], description="Array of group IDs")


class ClientUpdateRequest(StrictModel):
    """Request model for updating an existing client."""

    comment: str | None = Field(
        None, description="User-provided free-text comment for this client"
    )
    groups: list[int] = Field(..., description="Array of group IDs")


class ClientBatchDeleteItem(StrictModel):
    """Item for batch client deletion."""

    item: str = Field(..., description="Client identifier to delete")


class ClientProcessedSuccess(StrictModel):
    """Success item in client processing result."""

    item: str = Field(..., description="Client that was successfully processed")


class ClientProcessedError(StrictModel):
    """Error item in client processing result."""

    item: str = Field(..., description="Client that could not be processed")
    error: str = Field(..., description="Error message")


class ClientProcessedResult(StrictModel):
    """Processing result for client operations."""

    success: list[ClientProcessedSuccess] = Field(
        default_factory=list, description="Successfully processed clients"
    )
    errors: list[ClientProcessedError] = Field(
        default_factory=list, description="Processing errors"
    )


class ClientsResponse(TimedResponse):
    """Response model for client operations."""

    clients: list[Client] = Field(..., description="Array of client objects")
    processed: ClientProcessedResult | None = Field(
        None, description="Processing result"
    )


class ClientSuggestionsResponse(TimedResponse):
    """Response model for client suggestions."""

    clients: list[Client] = Field(
        ..., description="Array of unconfigured client suggestions"
    )
