"""Group models."""

from pydantic import Field

from pihole_lib.models.base import StrictModel, TimedResponse


class Group(StrictModel):
    """Pi-hole group information."""

    name: str = Field(..., description="Group name")
    comment: str | None = Field(
        None, description="User-provided free-text comment for this group"
    )
    enabled: bool = Field(True, description="Status of group")
    id: int = Field(..., description="Database ID")
    date_added: int = Field(..., description="Unix timestamp of group addition")
    date_modified: int = Field(
        ..., description="Unix timestamp of last group modification"
    )


class GroupRequest(StrictModel):
    """Request model for creating or updating a group."""

    name: str = Field(..., description="Group name")
    comment: str | None = Field(
        None, description="User-provided free-text comment for this group"
    )
    enabled: bool = Field(True, description="Status of group")


class GroupProcessedSuccess(StrictModel):
    """Success item in group processing result."""

    item: str = Field(..., description="Group that was successfully processed")


class GroupProcessedError(StrictModel):
    """Error item in group processing result."""

    item: str = Field(..., description="Group that could not be processed")
    error: str = Field(..., description="Error message")


class GroupProcessedResult(StrictModel):
    """Processing result for group operations."""

    success: list[GroupProcessedSuccess] = Field(
        default_factory=list, description="Successfully processed groups"
    )
    errors: list[GroupProcessedError] = Field(
        default_factory=list, description="Processing errors"
    )


class GroupsResponse(TimedResponse):
    """Response model for group operations."""

    groups: list[Group] = Field(..., description="Array of group objects")
    processed: GroupProcessedResult | None = Field(
        None, description="Processing result"
    )
