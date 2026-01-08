"""Pi-hole Stats API client."""

from typing import Any

from .base import BasePiHoleAPIClient
from .models import (
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
from .utils import make_pihole_request


class PiHoleStats(BasePiHoleAPIClient):
    """Pi-hole Stats API client.

    Handles statistics and history endpoints for Pi-hole data analysis.
    Uses a PiHoleClient instance for making requests.

    Examples::

        from pihole_lib import PiHoleClient, PiHoleStats

        # Create client and stats instance
        with PiHoleClient("http://192.168.1.100", password="secret") as client:
            stats = PiHoleStats(client)

            # Get activity graph data
            history = stats.get_history()

            # Get query statistics
            summary = stats.get_summary()

            # Get top domains
            top_domains = stats.get_top_domains(count=10)

    """

    BASE_URL = "/api"
    STATS_URL = f"{BASE_URL}/stats"
    HISTORY_URL = f"{BASE_URL}/history"
    DB_URL = f"{STATS_URL}/database"

    def get_history(self) -> HistoryResponse:
        """Get activity graph data.

        Request data needed to generate the total queries over time graph.
        The sum of the values in the individual data arrays may be smaller
        than the total number of queries for the corresponding timestamp.

        Returns:
            HistoryResponse: Activity graph data with timestamps and query counts.

        Raises:
            PiHoleConnectionError: Connection failed.
            PiHoleAuthenticationError: Authentication failed.
            PiHoleServerError: Server error.
            PiHoleAPIError: Other API errors.

        Examples::

            with PiHoleClient("http://192.168.1.100", password="secret") as client:
                stats = PiHoleStats(client)
                history = stats.get_history()

                for entry in history.history:
                    print(f"Time: {entry.timestamp}")
                    print(f"Total: {entry.total}, Blocked: {entry.blocked}")
                    print(f"Cached: {entry.cached}, Forwarded: {entry.forwarded}")

        """
        response = make_pihole_request(
            self._client,
            "GET",
            f"{self.HISTORY_URL}",
        )

        data = response.json()
        return HistoryResponse.model_validate(data)

    def get_client_history(self) -> ClientHistoryResponse:
        """Get per-client activity graph data.

        Request data needed to generate the "Client activity over last 24 hours" graph.
        This endpoint returns the top N clients, sorted by total number of queries
        within 24 hours. The last client returned is a special client that contains
        the total number of queries that were not sent by any of the other shown clients.

        Returns:
            ClientHistoryResponse: Per-client activity data with client mappings.

        Raises:
            PiHoleConnectionError: Connection failed.
            PiHoleAuthenticationError: Authentication failed.
            PiHoleServerError: Server error.
            PiHoleAPIError: Other API errors.

        Examples::

            with PiHoleClient("http://192.168.1.100", password="secret") as client:
                stats = PiHoleStats(client)
                client_history = stats.get_client_history()

                print(f"Client mappings: {client_history.clients}")
                for entry in client_history.history:
                    print(f"Time: {entry.timestamp}")
                    print(f"Client data: {entry.data}")

        """
        response = make_pihole_request(
            self._client,
            "GET",
            f"{self.HISTORY_URL}/clients",
        )

        data = response.json()
        return ClientHistoryResponse.model_validate(data)

    def get_database_history(
        self, from_timestamp: int, until_timestamp: int
    ) -> DatabaseHistoryResponse:
        """Get activity graph data from long-term database.

        Request long-term data needed to generate the activity graph.

        Args:
            from_timestamp: Unix timestamp from when the data should be requested.
            until_timestamp: Unix timestamp until when the data should be requested.

        Returns:
            DatabaseHistoryResponse: Long-term activity graph data.

        Raises:
            PiHoleConnectionError: Connection failed.
            PiHoleAuthenticationError: Authentication failed.
            PiHoleServerError: Server error.
            PiHoleAPIError: Other API errors.

        Examples::

            import time

            with PiHoleClient("http://192.168.1.100", password="secret") as client:
                stats = PiHoleStats(client)

                # Get data for the last 7 days
                now = int(time.time())
                week_ago = now - (7 * 24 * 60 * 60)

                history = stats.get_database_history(week_ago, now)
                print(f"Found {len(history.history)} entries")

        """
        params = {"from": from_timestamp, "until": until_timestamp}
        response = make_pihole_request(
            self._client,
            "GET",
            f"{self.HISTORY_URL}/database",
            params=params,
        )

        data = response.json()
        return DatabaseHistoryResponse.model_validate(data)

    def get_database_client_history(
        self, from_timestamp: int, until_timestamp: int
    ) -> DatabaseClientHistoryResponse:
        """Get per-client activity graph data from long-term database.

        Request long-term data needed to generate the client activity graph.

        Args:
            from_timestamp: Unix timestamp from when the data should be requested.
            until_timestamp: Unix timestamp until when the data should be requested.

        Returns:
            DatabaseClientHistoryResponse: Long-term per-client activity data.

        Raises:
            PiHoleConnectionError: Connection failed.
            PiHoleAuthenticationError: Authentication failed.
            PiHoleServerError: Server error.
            PiHoleAPIError: Other API errors.

        Examples::

            import time

            with PiHoleClient("http://192.168.1.100", password="secret") as client:
                stats = PiHoleStats(client)

                # Get client data for the last 30 days
                now = int(time.time())
                month_ago = now - (30 * 24 * 60 * 60)

                client_history = stats.get_database_client_history(month_ago, now)
                print(f"Client mappings: {client_history.clients}")

        """
        params = {"from": from_timestamp, "until": until_timestamp}
        response = make_pihole_request(
            self._client,
            "GET",
            f"{self.HISTORY_URL}/database/clients",
            params=params,
        )

        data = response.json()
        return DatabaseClientHistoryResponse.model_validate(data)

    # Query endpoints

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
        """Get query details.

        Request query details with optional filtering and pagination.
        By default, this returns the most recent 100 queries.

        Args:
            length: Number of queries to return (default: 100).
            cursor: Cursor for pagination (optional).
            from_timestamp: Only show queries from this timestamp on (optional).
            until_timestamp: Only show queries until this timestamp (optional).
            upstream: Only show queries sent to specific upstream (optional).
            domain: Only show queries for specific domains (optional).
            client: Only show queries for specific clients (optional).

        Returns:
            QueriesResponse: Query details with pagination information.

        Raises:
            PiHoleConnectionError: Connection failed.
            PiHoleAuthenticationError: Authentication failed.
            PiHoleServerError: Server error.
            PiHoleAPIError: Other API errors.

        Examples::

            with PiHoleClient("http://192.168.1.100", password="secret") as client:
                stats = PiHoleStats(client)

                # Get recent queries
                queries = stats.get_queries(length=50)
                print(f"Total records: {queries.records_total}")

                for query in queries.queries:
                    print(f"{query.timestamp}: {query.domain} -> {query.status}")

                # Get queries for specific domain
                domain_queries = stats.get_queries(domain="example.com")

                # Get blocked queries
                blocked_queries = stats.get_queries(upstream="blocklist")

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

        data = response.json()
        return QueriesResponse.model_validate(data)

    def get_query_suggestions(self) -> QuerySuggestionsResponse:
        """Get query filter suggestions.

        This endpoint provides suggestions for filters suitable to be used
        with the queries endpoint.

        Returns:
            QuerySuggestionsResponse: Available filter suggestions.

        Raises:
            PiHoleConnectionError: Connection failed.
            PiHoleAuthenticationError: Authentication failed.
            PiHoleServerError: Server error.
            PiHoleAPIError: Other API errors.

        Examples::

            with PiHoleClient("http://192.168.1.100", password="secret") as client:
                stats = PiHoleStats(client)
                suggestions = stats.get_query_suggestions()

                print(f"Available domains: {suggestions.suggestions.domain}")
                print(f"Available clients: {suggestions.suggestions.client_ip}")
                print(f"Available upstreams: {suggestions.suggestions.upstream}")
                print(f"Available types: {suggestions.suggestions.type}")

        """
        response = make_pihole_request(
            self._client,
            "GET",
            f"{self.BASE_URL}/queries/suggestions",
        )

        data = response.json()
        return QuerySuggestionsResponse.model_validate(data)

    # Stats endpoints

    def get_query_types(self) -> QueryTypesResponse:
        """Get query types statistics.

        Request query types breakdown for recent queries.

        Returns:
            QueryTypesResponse: Query types and their counts.

        Raises:
            PiHoleConnectionError: Connection failed.
            PiHoleAuthenticationError: Authentication failed.
            PiHoleServerError: Server error.
            PiHoleAPIError: Other API errors.

        Examples::

            with PiHoleClient("http://192.168.1.100", password="secret") as client:
                stats = PiHoleStats(client)
                query_types = stats.get_query_types()

                for query_type, count in query_types.types.items():
                    print(f"{query_type}: {count}")

        """
        response = make_pihole_request(
            self._client,
            "GET",
            f"{self.STATS_URL}/query_types",
        )

        data = response.json()
        return QueryTypesResponse.model_validate(data)

    def get_recent_blocked(self, count: int = 10) -> RecentBlockedResponse:
        """Get most recently blocked domains.

        Request most recently blocked domains.

        Args:
            count: Number of requested blocked domains (default: 10).

        Returns:
            RecentBlockedResponse: List of recently blocked domains.

        Raises:
            PiHoleConnectionError: Connection failed.
            PiHoleAuthenticationError: Authentication failed.
            PiHoleServerError: Server error.
            PiHoleAPIError: Other API errors.

        Examples::

            with PiHoleClient("http://192.168.1.100", password="secret") as client:
                stats = PiHoleStats(client)
                recent_blocked = stats.get_recent_blocked(count=20)

                print(f"Recently blocked domains:")
                for domain in recent_blocked.blocked:
                    print(f"  - {domain}")

        """
        params = {"count": count}
        response = make_pihole_request(
            self._client,
            "GET",
            f"{self.STATS_URL}/recent_blocked",
            params=params,
        )

        data = response.json()
        return RecentBlockedResponse.model_validate(data)

    def get_summary(self) -> SummaryResponse:
        """Get overview of Pi-hole activity.

        Request various query, system, and FTL properties.

        Returns:
            SummaryResponse: Comprehensive Pi-hole activity summary.

        Raises:
            PiHoleConnectionError: Connection failed.
            PiHoleAuthenticationError: Authentication failed.
            PiHoleServerError: Server error.
            PiHoleAPIError: Other API errors.

        Examples::

            with PiHoleClient("http://192.168.1.100", password="secret") as client:
                stats = PiHoleStats(client)
                summary = stats.get_summary()

                print(f"Total queries: {summary.queries.total}")
                print(f"Blocked queries: {summary.queries.blocked}")
                print(f"Percent blocked: {summary.queries.percent_blocked}%")
                print(f"Active clients: {summary.clients.active}")
                print(f"Domains on blocklists: {summary.gravity.domains_being_blocked}")

        """
        response = make_pihole_request(
            self._client,
            "GET",
            f"{self.STATS_URL}/summary",
        )

        data = response.json()
        return SummaryResponse.model_validate(data)

    def get_top_clients(
        self, blocked: bool | None = None, count: int = 10
    ) -> TopClientsResponse:
        """Get top clients.

        Request top clients by query count.

        Args:
            blocked: Return information about permitted (False) or blocked (True)
                    queries. If None, returns all queries (default: None).
            count: Number of requested items (default: 10).

        Returns:
            TopClientsResponse: Top clients and their query counts.

        Raises:
            PiHoleConnectionError: Connection failed.
            PiHoleAuthenticationError: Authentication failed.
            PiHoleServerError: Server error.
            PiHoleAPIError: Other API errors.

        Examples::

            with PiHoleClient("http://192.168.1.100", password="secret") as client:
                stats = PiHoleStats(client)

                # Get top clients by total queries
                top_clients = stats.get_top_clients(count=15)
                for client in top_clients.clients:
                    print(f"{client.name or client.ip}: {client.count} queries")

                # Get top clients by blocked queries
                blocked_clients = stats.get_top_clients(blocked=True, count=5)

        """
        params: dict[str, Any] = {"count": count}
        if blocked is not None:
            params["blocked"] = blocked

        response = make_pihole_request(
            self._client,
            "GET",
            f"{self.STATS_URL}/top_clients",
            params=params,
        )

        data = response.json()
        return TopClientsResponse.model_validate(data)

    def get_top_domains(
        self, blocked: bool | None = None, count: int = 10
    ) -> TopDomainsResponse:
        """Get top domains.

        Request top domains by query count.

        Args:
            blocked: Return information about permitted (False) or blocked (True)
                    queries. If None, returns all queries (default: None).
            count: Number of requested items (default: 10).

        Returns:
            TopDomainsResponse: Top domains and their query counts.

        Raises:
            PiHoleConnectionError: Connection failed.
            PiHoleAuthenticationError: Authentication failed.
            PiHoleServerError: Server error.
            PiHoleAPIError: Other API errors.

        Examples::

            with PiHoleClient("http://192.168.1.100", password="secret") as client:
                stats = PiHoleStats(client)

                # Get top domains by total queries
                top_domains = stats.get_top_domains(count=20)
                for domain in top_domains.domains:
                    print(f"{domain.domain}: {domain.count} queries")

                # Get top blocked domains
                blocked_domains = stats.get_top_domains(blocked=True, count=10)

        """
        params: dict[str, Any] = {"count": count}
        if blocked is not None:
            params["blocked"] = blocked

        response = make_pihole_request(
            self._client,
            "GET",
            f"{self.STATS_URL}/top_domains",
            params=params,
        )

        data = response.json()
        return TopDomainsResponse.model_validate(data)

    def get_upstreams(self) -> UpstreamsResponse:
        """Get metrics about Pi-hole's upstream destinations.

        Request upstream metrics including response times and query counts.

        Returns:
            UpstreamsResponse: Upstream server metrics and statistics.

        Raises:
            PiHoleConnectionError: Connection failed.
            PiHoleAuthenticationError: Authentication failed.
            PiHoleServerError: Server error.
            PiHoleAPIError: Other API errors.

        Examples::

            with PiHoleClient("http://192.168.1.100", password="secret") as client:
                stats = PiHoleStats(client)
                upstreams = stats.get_upstreams()

                print(f"Total queries: {upstreams.total_queries}")
                print(f"Forwarded queries: {upstreams.forwarded_queries}")

                for upstream in upstreams.upstreams:
                    print(f"{upstream.name} ({upstream.ip}:{upstream.port})")
                    print(f"  Queries: {upstream.count}")
                    if upstream.statistics:
                        print(f"  Response time: {upstream.statistics.response}ms")

        """
        response = make_pihole_request(
            self._client,
            "GET",
            f"{self.STATS_URL}/upstreams",
        )

        data = response.json()
        return UpstreamsResponse.model_validate(data)

    # Database stats endpoints

    def get_database_query_types(
        self, from_timestamp: int, until_timestamp: int
    ) -> QueryTypesResponse:
        """Get query types from long-term database.

        Request query types breakdown for a specific time range from the database.

        Args:
            from_timestamp: Unix timestamp from when the data should be requested.
            until_timestamp: Unix timestamp until when the data should be requested.

        Returns:
            QueryTypesResponse: Query types and their counts for the time range.

        Raises:
            PiHoleConnectionError: Connection failed.
            PiHoleAuthenticationError: Authentication failed.
            PiHoleServerError: Server error.
            PiHoleAPIError: Other API errors.

        Examples::

            import time

            with PiHoleClient("http://192.168.1.100", password="secret") as client:
                stats = PiHoleStats(client)

                # Get query types for the last 24 hours
                now = int(time.time())
                day_ago = now - (24 * 60 * 60)

                query_types = stats.get_database_query_types(day_ago, now)
                for query_type, count in query_types.types.items():
                    print(f"{query_type}: {count}")

        """
        params = {"from": from_timestamp, "until": until_timestamp}
        response = make_pihole_request(
            self._client,
            "GET",
            f"{self.DB_URL}/query_types",
            params=params,
        )

        data = response.json()
        return QueryTypesResponse.model_validate(data)

    def get_database_summary(
        self, from_timestamp: int, until_timestamp: int
    ) -> DatabaseSummaryResponse:
        """Get database content details.

        Request various database content details for a specific time range.

        Args:
            from_timestamp: Unix timestamp from when the data should be requested.
            until_timestamp: Unix timestamp until when the data should be requested.

        Returns:
            DatabaseSummaryResponse: Database summary statistics for the time range.

        Raises:
            PiHoleConnectionError: Connection failed.
            PiHoleAuthenticationError: Authentication failed.
            PiHoleServerError: Server error.
            PiHoleAPIError: Other API errors.

        Examples::

            import time

            with PiHoleClient("http://192.168.1.100", password="secret") as client:
                stats = PiHoleStats(client)

                # Get summary for the last week
                now = int(time.time())
                week_ago = now - (7 * 24 * 60 * 60)

                summary = stats.get_database_summary(week_ago, now)
                print(f"Total queries: {summary.sum_queries}")
                print(f"Blocked queries: {summary.sum_blocked}")
                print(f"Percent blocked: {summary.percent_blocked}%")
                print(f"Total clients: {summary.total_clients}")

        """
        params = {"from": from_timestamp, "until": until_timestamp}
        response = make_pihole_request(
            self._client,
            "GET",
            f"{self.DB_URL}/summary",
            params=params,
        )

        data = response.json()
        return DatabaseSummaryResponse.model_validate(data)

    def get_database_top_clients(
        self, from_timestamp: int, until_timestamp: int
    ) -> TopClientsResponse:
        """Get top clients from long-term database.

        Request top clients for a specific time range from the database.

        Args:
            from_timestamp: Unix timestamp from when the data should be requested.
            until_timestamp: Unix timestamp until when the data should be requested.

        Returns:
            TopClientsResponse: Top clients for the time range.

        Raises:
            PiHoleConnectionError: Connection failed.
            PiHoleAuthenticationError: Authentication failed.
            PiHoleServerError: Server error.
            PiHoleAPIError: Other API errors.

        Examples::

            import time

            with PiHoleClient("http://192.168.1.100", password="secret") as client:
                stats = PiHoleStats(client)

                # Get top clients for the last month
                now = int(time.time())
                month_ago = now - (30 * 24 * 60 * 60)

                top_clients = stats.get_database_top_clients(month_ago, now)
                for client in top_clients.clients:
                    print(f"{client.name or client.ip}: {client.count} queries")

        """
        params = {"from": from_timestamp, "until": until_timestamp}
        response = make_pihole_request(
            self._client,
            "GET",
            f"{self.DB_URL}/top_clients",
            params=params,
        )

        data = response.json()
        return TopClientsResponse.model_validate(data)

    def get_database_top_domains(
        self, from_timestamp: int, until_timestamp: int
    ) -> TopDomainsResponse:
        """Get top domains from long-term database.

        Request top domains for a specific time range from the database.

        Args:
            from_timestamp: Unix timestamp from when the data should be requested.
            until_timestamp: Unix timestamp until when the data should be requested.

        Returns:
            TopDomainsResponse: Top domains for the time range.

        Raises:
            PiHoleConnectionError: Connection failed.
            PiHoleAuthenticationError: Authentication failed.
            PiHoleServerError: Server error.
            PiHoleAPIError: Other API errors.

        Examples::

            import time

            with PiHoleClient("http://192.168.1.100", password="secret") as client:
                stats = PiHoleStats(client)

                # Get top domains for the last month
                now = int(time.time())
                month_ago = now - (30 * 24 * 60 * 60)

                top_domains = stats.get_database_top_domains(month_ago, now)
                for domain in top_domains.domains:
                    print(f"{domain.domain}: {domain.count} queries")

        """
        params = {"from": from_timestamp, "until": until_timestamp}
        response = make_pihole_request(
            self._client,
            "GET",
            f"{self.DB_URL}/top_domains",
            params=params,
        )

        data = response.json()
        return TopDomainsResponse.model_validate(data)

    def get_database_upstreams(
        self, from_timestamp: int, until_timestamp: int
    ) -> UpstreamsResponse:
        """Get metrics about Pi-hole's upstream destinations from long-term database.

        Request upstream metrics for a specific time range from the database.

        Args:
            from_timestamp: Unix timestamp from when the data should be requested.
            until_timestamp: Unix timestamp until when the data should be requested.

        Returns:
            UpstreamsResponse: Upstream server metrics for the time range.

        Raises:
            PiHoleConnectionError: Connection failed.
            PiHoleAuthenticationError: Authentication failed.
            PiHoleServerError: Server error.
            PiHoleAPIError: Other API errors.

        Examples::

            import time

            with PiHoleClient("http://192.168.1.100", password="secret") as client:
                stats = PiHoleStats(client)

                # Get upstream metrics for the last week
                now = int(time.time())
                week_ago = now - (7 * 24 * 60 * 60)

                upstreams = stats.get_database_upstreams(week_ago, now)
                print(f"Total queries: {upstreams.total_queries}")

                for upstream in upstreams.upstreams:
                    print(f"{upstream.name}: {upstream.count} queries")

        """
        params = {"from": from_timestamp, "until": until_timestamp}
        response = make_pihole_request(
            self._client,
            "GET",
            f"{self.DB_URL}/upstreams",
            params=params,
        )

        data = response.json()
        return UpstreamsResponse.model_validate(data)
