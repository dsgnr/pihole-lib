"""List models."""

from enum import Enum

from pydantic import Field

from pihole_lib.models.base import StrictModel, TimedResponse


class ListType(str, Enum):
    """Pi-hole list types."""

    ALLOW = "allow"
    BLOCK = "block"


class PiHoleList(StrictModel):
    """Pi-hole domain list."""

    address: str = Field(..., description="Address of the list")
    type: ListType = Field(..., description="Type of list")
    comment: str | None = Field(
        None, description="User-provided free-text comment for this list"
    )
    groups: list[int] = Field(..., description="Array of group IDs")
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


class AddListRequest(StrictModel):
    """Request model for adding a new Pi-hole list."""

    address: str = Field(..., description="Address of the list")
    comment: str | None = Field(None, description="Optional comment for this list")
    groups: list[int] = Field(default=[0], description="Array of group IDs")
    enabled: bool = Field(default=True, description="Whether the list is enabled")


class UpdateListRequest(StrictModel):
    """Request model for updating an existing Pi-hole list."""

    comment: str | None = Field(None, description="Optional comment for this list")
    type: ListType = Field(..., description="Type of list")
    groups: list[int] = Field(..., description="Array of group IDs")
    enabled: bool = Field(..., description="Whether the list is enabled")


class BatchDeleteItem(StrictModel):
    """Item for batch delete operation."""

    item: str = Field(..., description="Address of the list to delete")
    type: ListType = Field(..., description="Type of list")


class ListProcessedSuccess(StrictModel):
    """Success item in list processing result."""

    item: str = Field(..., description="List that was successfully processed")


class ListProcessedError(StrictModel):
    """Error item in list processing result."""

    item: str = Field(..., description="List that could not be processed")
    error: str = Field(..., description="Error message")


class ListProcessedResult(StrictModel):
    """Processing result for list operations."""

    success: list[ListProcessedSuccess] = Field(
        default_factory=list, description="Successfully processed lists"
    )
    errors: list[ListProcessedError] = Field(
        default_factory=list, description="Processing errors"
    )


class ListsResponse(TimedResponse):
    """Response model for list operations."""

    lists: list[PiHoleList] = Field(..., description="Array of list objects")
    processed: ListProcessedResult | None = Field(None, description="Processing result")
