"""Search models."""

from pydantic import Field

from pihole_lib.models.base import StrictModel, TimedResponse
from pihole_lib.models.lists import PiHoleList


class SearchResultCounts(StrictModel):
    """Search result counts."""

    exact: int = Field(..., description="Number of exact matches")
    regex: int = Field(..., description="Number of regex matches")


class SearchGravityCounts(StrictModel):
    """Search gravity result counts."""

    allow: int = Field(..., description="Number of allow list matches")
    block: int = Field(..., description="Number of block list matches")


class SearchResults(StrictModel):
    """Search results summary."""

    domains: SearchResultCounts = Field(..., description="Domain search result counts")
    gravity: SearchGravityCounts = Field(
        ..., description="Gravity search result counts"
    )
    total: int = Field(..., description="Total number of results")


class SearchParameters(StrictModel):
    """Search parameters used."""

    N: int = Field(..., description="Maximum number of results returned")
    partial: bool = Field(..., description="Whether partial matching was used")
    domain: str = Field(..., description="Domain that was searched for")
    debug: bool = Field(..., description="Whether debug information was included")


class SearchData(StrictModel):
    """Search data container."""

    domains: list[PiHoleList] = Field(..., description="List of domain matches")
    gravity: list[PiHoleList] = Field(..., description="List of gravity matches")
    results: SearchResults = Field(..., description="Search result summary")
    parameters: SearchParameters = Field(..., description="Search parameters used")


class SearchResponse(TimedResponse):
    """Response for domain search operations."""

    search: SearchData = Field(..., description="Search data and results")
