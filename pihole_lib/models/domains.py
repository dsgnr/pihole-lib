"""Domain models."""

from enum import Enum

from pydantic import Field

from pihole_lib.models.base import StrictModel, TimedResponse


class DomainType(str, Enum):
    """Pi-hole domain types."""

    ALLOW = "allow"
    DENY = "deny"


class DomainKind(str, Enum):
    """Pi-hole domain kinds."""

    EXACT = "exact"
    REGEX = "regex"


class Domain(StrictModel):
    """Pi-hole domain entry."""

    domain: str = Field(..., description="The domain name or regex pattern")
    unicode: str = Field(..., description="Unicode representation of the domain")
    type: DomainType = Field(..., description="Type of domain")
    kind: DomainKind = Field(..., description="Kind of domain")
    comment: str | None = Field(
        None, description="User-provided free-text comment for this domain"
    )
    groups: list[int] = Field(..., description="Array of group IDs")
    enabled: bool = Field(True, description="Status of domain")
    id: int = Field(..., description="Database ID")
    date_added: int = Field(..., description="Unix timestamp of item addition")
    date_modified: int = Field(
        ..., description="Unix timestamp of last item modification"
    )


class DomainsResponse(TimedResponse):
    """Response for domains endpoints."""

    domains: list[Domain] = Field(..., description="List of domain entries")


class DomainRequest(StrictModel):
    """Request for adding/updating domains."""

    domain: str | None = Field(None, description="The domain name or regex pattern")
    type: DomainType | None = Field(None, description="Type of domain")
    kind: DomainKind | None = Field(None, description="Kind of domain")
    comment: str | None = Field(
        None, description="User-provided free-text comment for this domain"
    )
    groups: list[int] | None = Field(None, description="Array of group IDs")
    enabled: bool | None = Field(None, description="Status of domain")


class DomainBatchDeleteItem(StrictModel):
    """Item for batch domain deletion."""

    item: str = Field(..., description="Domain to delete")
    type: DomainType = Field(..., description="Type of domain to delete")
    kind: DomainKind = Field(..., description="Kind of domain to delete")


class DomainProcessedSuccess(StrictModel):
    """Successful domain processing result."""

    item: str = Field(..., description="The domain that was processed")


class DomainProcessedError(StrictModel):
    """Failed domain processing result."""

    item: str = Field(..., description="The domain that failed to process")
    error: str = Field(..., description="Error message")


class DomainProcessedResult(StrictModel):
    """Domain processing results."""

    success: list[DomainProcessedSuccess] = Field(
        ..., description="List of successfully processed domains"
    )
    errors: list[DomainProcessedError] = Field(
        ..., description="List of failed domain processing attempts"
    )


class DomainMutationResponse(TimedResponse):
    """Response for domain mutation operations."""

    domains: list[Domain] = Field(
        ..., description="List of domain entries after the operation"
    )
    processed: DomainProcessedResult = Field(..., description="Processing results")


class DomainBatchDeleteResponse(TimedResponse):
    """Response for batch domain deletion."""

    pass
