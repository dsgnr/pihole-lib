"""Pi-hole Stats API client."""

from typing import Any

from pihole_lib.base import BasePiHoleAPIClient
from pihole_lib.models.stats import (
    ClientHistoryResponse,
    DatabaseClientHistoryResponse,
    DatabaseHistoryResponse,
    DatabaseSummaryResponse,
    HistoryResponse,
    QueriesResponse,
    QuerySuggestionsResponse,
    QueryTypesResponse,
    RecentBlockedResponse,
    SummaryResponse,
    TopClientsResponse,
    TopDomainsResponse,
    UpstreamsResponse,
)
from pihole_lib.utils import make_pihole_request


class PiHoleStats(BasePiHoleAPIClient):
    """Pi-hole Stats API client.

    Handles statistics and history endpoints for Pi-hole data analysis.

    Examples::

        from pihole_lib import PiHoleClient

        with PiHoleClient("http://192.168.1.100", password="secret") as client:
            # Get activity history
            history = client.stats.get_history()

            # Get summary
            summary = client.stats.get_summary()
            print(f"Total queries: {summary.queries.total}")

            # Get top domains
            top_domains = client.stats.get_top_domains(count=10)

    """

    BASE_URL = "/api"

    def get_history(self) -> HistoryResponse:
        """Get activity graph data.

        Returns:
            HistoryResponse with timestamps and query counts.
        """
        response = make_pihole_request(
            self._client,
            "GET",
            f"{self.BASE_URL}/history",
        )
        return HistoryResponse.model_validate(response.json())

    def get_client_history(self) -> ClientHistoryResponse:
        """Get per-client activity graph data.

        Returns:
            ClientHistoryResponse with per-client activity data.
        """
        response = make_pihole_request(
            self._client,
            "GET",
            f"{self.BASE_URL}/history/clients",
        )
        return ClientHistoryResponse.model_validate(response.json())

    def get_database_history(
        self, from_timestamp: int, until_timestamp: int
    ) -> DatabaseHistoryResponse:
        """Get activity graph data from long-term database.

        Args:
            from_timestamp: Unix timestamp from when to request data.
            until_timestamp: Unix timestamp until when to request data.

        Returns:
            DatabaseHistoryResponse with long-term activity data.
        """
        params = {"from": from_timestamp, "until": until_timestamp}
        response = make_pihole_request(
            self._client,
            "GET",
            f"{self.BASE_URL}/history/database",
            params=params,
        )
        return DatabaseHistoryResponse.model_validate(response.json())

    def get_database_client_history(
        self, from_timestamp: int, until_timestamp: int
    ) -> DatabaseClientHistoryResponse:
        """Get per-client activity data from long-term database.

        Args:
            from_timestamp: Unix timestamp from when to request data.
            until_timestamp: Unix timestamp until when to request data.

        Returns:
            DatabaseClientHistoryResponse with long-term per-client data.
        """
        params = {"from": from_timestamp, "until": until_timestamp}
        response = make_pihole_request(
            self._client,
            "GET",
            f"{self.BASE_URL}/history/database/clients",
            params=params,
        )
        return DatabaseClientHistoryResponse.model_validate(response.json())

    def get_queries(
        self,
        length: int = 100,
        cursor: int | None = None,
        from_timestamp: int | None = None,
        until_timestamp: int | None = None,
        upstream: str | None = None,
        domain: str | None = None,
        client: str | None = None,
    ) -> QueriesResponse:
        """Get query details with optional filtering.

        Args:
            length: Number of queries to return (default: 100).
            cursor: Cursor for pagination (optional).
            from_timestamp: Only show queries from this timestamp (optional).
            until_timestamp: Only show queries until this timestamp (optional).
            upstream: Filter by specific upstream (optional).
            domain: Filter by specific domain (optional).
            client: Filter by specific client (optional).

        Returns:
            QueriesResponse with query details and pagination info.
        """
        params: dict[str, Any] = {"length": length}
        if cursor is not None:
            params["cursor"] = cursor
        if from_timestamp is not None:
            params["from"] = from_timestamp
        if until_timestamp is not None:
            params["until"] = until_timestamp
        if upstream is not None:
            params["upstream"] = upstream
        if domain is not None:
            params["domain"] = domain
        if client is not None:
            params["client"] = client

        response = make_pihole_request(
            self._client,
            "GET",
            f"{self.BASE_URL}/queries",
            params=params,
        )
        return QueriesResponse.model_validate(response.json())

    def get_query_suggestions(self) -> QuerySuggestionsResponse:
        """Get query filter suggestions.

        Returns:
            QuerySuggestionsResponse with available filter suggestions.
        """
        response = make_pihole_request(
            self._client,
            "GET",
            f"{self.BASE_URL}/queries/suggestions",
        )
        return QuerySuggestionsResponse.model_validate(response.json())

    def get_query_types(self) -> QueryTypesResponse:
        """Get query types statistics.

        Returns:
            QueryTypesResponse with query types and counts.
        """
        response = make_pihole_request(
            self._client,
            "GET",
            f"{self.BASE_URL}/stats/query_types",
        )
        return QueryTypesResponse.model_validate(response.json())

    def get_recent_blocked(self, count: int = 10) -> RecentBlockedResponse:
        """Get most recently blocked domains.

        Args:
            count: Number of blocked domains to return (default: 10).

        Returns:
            RecentBlockedResponse with recently blocked domains.
        """
        response = make_pihole_request(
            self._client,
            "GET",
            f"{self.BASE_URL}/stats/recent_blocked",
            params={"count": count},
        )
        return RecentBlockedResponse.model_validate(response.json())

    def get_summary(self) -> SummaryResponse:
        """Get overview of Pi-hole activity.

        Returns:
            SummaryResponse with comprehensive activity summary.
        """
        response = make_pihole_request(
            self._client,
            "GET",
            f"{self.BASE_URL}/stats/summary",
        )
        return SummaryResponse.model_validate(response.json())

    def get_top_clients(
        self, blocked: bool | None = None, count: int = 10
    ) -> TopClientsResponse:
        """Get top clients by query count.

        Args:
            blocked: Filter by permitted (False) or blocked (True) queries.
            count: Number of clients to return (default: 10).

        Returns:
            TopClientsResponse with top clients and query counts.
        """
        params: dict[str, Any] = {"count": count}
        if blocked is not None:
            params["blocked"] = blocked

        response = make_pihole_request(
            self._client,
            "GET",
            f"{self.BASE_URL}/stats/top_clients",
            params=params,
        )
        return TopClientsResponse.model_validate(response.json())

    def get_top_domains(
        self, blocked: bool | None = None, count: int = 10
    ) -> TopDomainsResponse:
        """Get top domains by query count.

        Args:
            blocked: Filter by permitted (False) or blocked (True) queries.
            count: Number of domains to return (default: 10).

        Returns:
            TopDomainsResponse with top domains and query counts.
        """
        params: dict[str, Any] = {"count": count}
        if blocked is not None:
            params["blocked"] = blocked

        response = make_pihole_request(
            self._client,
            "GET",
            f"{self.BASE_URL}/stats/top_domains",
            params=params,
        )
        return TopDomainsResponse.model_validate(response.json())

    def get_upstreams(self) -> UpstreamsResponse:
        """Get metrics about upstream destinations.

        Returns:
            UpstreamsResponse with upstream server metrics.
        """
        response = make_pihole_request(
            self._client,
            "GET",
            f"{self.BASE_URL}/stats/upstreams",
        )
        return UpstreamsResponse.model_validate(response.json())

    # Database stats endpoints

    def get_database_query_types(
        self, from_timestamp: int, until_timestamp: int
    ) -> QueryTypesResponse:
        """Get query types from long-term database.

        Args:
            from_timestamp: Unix timestamp from when to request data.
            until_timestamp: Unix timestamp until when to request data.

        Returns:
            QueryTypesResponse with query types for the time range.
        """
        params = {"from": from_timestamp, "until": until_timestamp}
        response = make_pihole_request(
            self._client,
            "GET",
            f"{self.BASE_URL}/stats/database/query_types",
            params=params,
        )
        return QueryTypesResponse.model_validate(response.json())

    def get_database_summary(
        self, from_timestamp: int, until_timestamp: int
    ) -> DatabaseSummaryResponse:
        """Get database content details for a time range.

        Args:
            from_timestamp: Unix timestamp from when to request data.
            until_timestamp: Unix timestamp until when to request data.

        Returns:
            DatabaseSummaryResponse with summary statistics.
        """
        params = {"from": from_timestamp, "until": until_timestamp}
        response = make_pihole_request(
            self._client,
            "GET",
            f"{self.BASE_URL}/stats/database/summary",
            params=params,
        )
        return DatabaseSummaryResponse.model_validate(response.json())

    def get_database_top_clients(
        self, from_timestamp: int, until_timestamp: int
    ) -> TopClientsResponse:
        """Get top clients from long-term database.

        Args:
            from_timestamp: Unix timestamp from when to request data.
            until_timestamp: Unix timestamp until when to request data.

        Returns:
            TopClientsResponse with top clients for the time range.
        """
        params = {"from": from_timestamp, "until": until_timestamp}
        response = make_pihole_request(
            self._client,
            "GET",
            f"{self.BASE_URL}/stats/database/top_clients",
            params=params,
        )
        return TopClientsResponse.model_validate(response.json())

    def get_database_top_domains(
        self, from_timestamp: int, until_timestamp: int
    ) -> TopDomainsResponse:
        """Get top domains from long-term database.

        Args:
            from_timestamp: Unix timestamp from when to request data.
            until_timestamp: Unix timestamp until when to request data.

        Returns:
            TopDomainsResponse with top domains for the time range.
        """
        params = {"from": from_timestamp, "until": until_timestamp}
        response = make_pihole_request(
            self._client,
            "GET",
            f"{self.BASE_URL}/stats/database/top_domains",
            params=params,
        )
        return TopDomainsResponse.model_validate(response.json())

    def get_database_upstreams(
        self, from_timestamp: int, until_timestamp: int
    ) -> UpstreamsResponse:
        """Get upstream metrics from long-term database.

        Args:
            from_timestamp: Unix timestamp from when to request data.
            until_timestamp: Unix timestamp until when to request data.

        Returns:
            UpstreamsResponse with upstream metrics for the time range.
        """
        params = {"from": from_timestamp, "until": until_timestamp}
        response = make_pihole_request(
            self._client,
            "GET",
            f"{self.BASE_URL}/stats/database/upstreams",
            params=params,
        )
        return UpstreamsResponse.model_validate(response.json())
