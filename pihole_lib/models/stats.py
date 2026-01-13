"""Statistics and history models."""

from pydantic import Field

from pihole_lib.models.base import StrictModel, TimedResponse


class HistoryEntry(StrictModel):
    """History entry for activity graph data."""

    timestamp: int = Field(..., description="Unix timestamp")
    total: int = Field(..., description="Total number of queries")
    cached: int = Field(..., description="Number of cached queries")
    blocked: int = Field(..., description="Number of blocked queries")
    forwarded: int = Field(..., description="Number of forwarded queries")


class HistoryResponse(TimedResponse):
    """Response for history endpoints."""

    history: list[HistoryEntry] = Field(..., description="List of history entries")


class ClientHistoryEntry(StrictModel):
    """Client history entry for per-client activity data."""

    timestamp: int = Field(..., description="Unix timestamp")
    data: dict[str, int] = Field(
        ..., description="Dictionary mapping client IPs/names to query counts"
    )


class ClientHistoryResponse(TimedResponse):
    """Response for client history endpoints."""

    history: list[ClientHistoryEntry] = Field(
        ..., description="List of client history entries"
    )
    clients: dict[str, str] = Field(
        ..., description="Dictionary mapping client IPs to names"
    )


class DatabaseHistoryResponse(TimedResponse):
    """Response for database history endpoints."""

    history: list[HistoryEntry] = Field(..., description="List of history entries")


class DatabaseClientHistoryResponse(TimedResponse):
    """Response for database client history endpoints."""

    history: list[ClientHistoryEntry] = Field(
        ..., description="List of client history entries"
    )
    clients: dict[str, str] = Field(
        ..., description="Dictionary mapping client IPs to names"
    )


class QueryEntry(StrictModel):
    """Individual query entry."""

    timestamp: int = Field(..., description="Unix timestamp of the query")
    type: str = Field(..., description="Query type (A, AAAA, etc.)")
    domain: str = Field(..., description="Queried domain")
    client: str = Field(..., description="Client IP or name")
    status: str = Field(..., description="Query status (FORWARDED, BLOCKED, etc.)")
    destination: str = Field(..., description="Upstream destination or action")
    reply_type: str = Field(..., description="Type of reply")
    response_time: float = Field(..., description="Response time in milliseconds")
    dnssec: str = Field(..., description="DNSSEC status")


class QueriesResponse(TimedResponse):
    """Response for queries endpoint."""

    queries: list[QueryEntry] = Field(..., description="List of query entries")
    cursor: int = Field(..., description="Cursor for pagination")
    records_total: int = Field(
        ..., alias="recordsTotal", description="Total number of records"
    )
    records_filtered: int = Field(
        ..., alias="recordsFiltered", description="Number of filtered records"
    )
    draw: int = Field(..., description="Draw counter for DataTables")


class QuerySuggestions(StrictModel):
    """Query filter suggestions."""

    domain: list[str] = Field(..., description="List of domain suggestions")
    client_ip: list[str] = Field(..., description="List of client IP suggestions")
    client_name: list[str] = Field(..., description="List of client name suggestions")
    upstream: list[str] = Field(..., description="List of upstream suggestions")
    type: list[str] = Field(..., description="List of query type suggestions")
    status: list[str] = Field(..., description="List of status suggestions")


class QuerySuggestionsResponse(TimedResponse):
    """Response for query suggestions endpoint."""

    suggestions: QuerySuggestions = Field(..., description="Query filter suggestions")


class QueryTypesResponse(TimedResponse):
    """Response for query types endpoints."""

    types: dict[str, int] = Field(
        ..., description="Dictionary mapping query types to counts"
    )


class DatabaseSummaryResponse(TimedResponse):
    """Response for database summary endpoint."""

    sum_queries: int = Field(..., description="Total number of queries")
    sum_blocked: int = Field(..., description="Total number of blocked queries")
    percent_blocked: float = Field(..., description="Percentage of queries blocked")
    total_clients: int = Field(..., description="Total number of clients")


class TopClient(StrictModel):
    """Top client entry."""

    ip: str = Field(..., description="Client IP address")
    name: str | None = Field(None, description="Client name")
    count: int = Field(..., description="Number of queries")


class TopClientsResponse(TimedResponse):
    """Response for top clients endpoints."""

    clients: list[TopClient] = Field(..., description="List of top clients")
    total_queries: int = Field(..., description="Total number of queries")
    blocked_queries: int = Field(..., description="Total number of blocked queries")


class TopDomain(StrictModel):
    """Top domain entry."""

    domain: str = Field(..., description="Domain name")
    count: int = Field(..., description="Number of queries")


class TopDomainsResponse(TimedResponse):
    """Response for top domains endpoints."""

    domains: list[TopDomain] = Field(..., description="List of top domains")
    total_queries: int = Field(..., description="Total number of queries")
    blocked_queries: int = Field(..., description="Total number of blocked queries")


class UpstreamStatistics(StrictModel):
    """Upstream server statistics."""

    response: float = Field(..., description="Average response time")
    variance: float = Field(..., description="Response time variance")


class UpstreamServer(StrictModel):
    """Upstream server information."""

    ip: str = Field(..., description="Server IP address or identifier")
    name: str = Field(..., description="Server name")
    port: int = Field(..., description="Server port (-1 for special entries)")
    count: int = Field(..., description="Number of queries sent to this upstream")
    statistics: UpstreamStatistics | None = Field(
        None, description="Response time statistics"
    )


class UpstreamsResponse(TimedResponse):
    """Response for upstreams endpoints."""

    upstreams: list[UpstreamServer] = Field(..., description="List of upstream servers")
    total_queries: int = Field(..., description="Total number of queries")
    forwarded_queries: int = Field(..., description="Number of forwarded queries")


class RecentBlockedResponse(TimedResponse):
    """Response for recent blocked domains endpoint."""

    blocked: list[str] = Field(..., description="List of recently blocked domains")


class SummaryQueries(StrictModel):
    """Summary queries information."""

    total: int = Field(..., description="Total number of queries")
    blocked: int = Field(..., description="Number of blocked queries")
    percent_blocked: float = Field(..., description="Percentage of queries blocked")
    unique_domains: int = Field(..., description="Number of unique domains")
    forwarded: int = Field(..., description="Number of forwarded queries")
    cached: int = Field(..., description="Number of cached queries")
    frequency: float = Field(..., description="Query frequency")
    types: dict[str, int] = Field(
        ..., description="Dictionary of query types and counts"
    )
    status: dict[str, int] = Field(
        ..., description="Dictionary of query statuses and counts"
    )
    replies: dict[str, int] = Field(
        ..., description="Dictionary of reply types and counts"
    )


class SummaryClients(StrictModel):
    """Summary clients information."""

    total: int = Field(..., description="Total number of clients")
    active: int = Field(..., description="Number of active clients")


class SummaryGravity(StrictModel):
    """Summary gravity information."""

    domains_being_blocked: int = Field(
        ..., description="Number of domains on blocklists"
    )
    last_update: int = Field(..., description="Last gravity update timestamp")


class SummaryResponse(TimedResponse):
    """Response for summary endpoint."""

    queries: SummaryQueries = Field(..., description="Query statistics")
    clients: SummaryClients = Field(..., description="Client statistics")
    gravity: SummaryGravity = Field(..., description="Gravity statistics")
