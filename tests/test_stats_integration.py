"""Integration tests for PiHoleStats."""

import time

from pihole_lib import PiHoleStats
from tests.conftest import integration


@integration
class TestPiHoleStatsIntegration:
    """Integration tests for PiHoleStats class."""

    def test_get_history(self, pihole_client):
        """Should return activity graph data."""
        stats = PiHoleStats(pihole_client)
        history = stats.get_history()

        # Should have history data structure
        assert hasattr(history, "history")
        assert hasattr(history, "took")
        assert isinstance(history.history, list)
        assert isinstance(history.took, float)

        # Each history entry should have required fields
        for entry in history.history:
            assert hasattr(entry, "timestamp")
            assert hasattr(entry, "total")
            assert hasattr(entry, "cached")
            assert hasattr(entry, "blocked")
            assert hasattr(entry, "forwarded")
            assert isinstance(entry.timestamp, int)
            assert isinstance(entry.total, int)
            assert isinstance(entry.cached, int)
            assert isinstance(entry.blocked, int)
            assert isinstance(entry.forwarded, int)

    def test_get_client_history(self, pihole_client):
        """Should return per-client activity data."""
        stats = PiHoleStats(pihole_client)
        client_history = stats.get_client_history()

        # Should have client history data structure
        assert hasattr(client_history, "history")
        assert hasattr(client_history, "clients")
        assert hasattr(client_history, "took")
        assert isinstance(client_history.history, list)
        assert isinstance(client_history.clients, dict)
        assert isinstance(client_history.took, float)

        # Each history entry should have required fields
        for entry in client_history.history:
            assert hasattr(entry, "timestamp")
            assert hasattr(entry, "data")
            assert isinstance(entry.timestamp, int)
            assert isinstance(entry.data, dict)

    def test_get_database_history(self, pihole_client):
        """Should return database activity data for time range."""
        stats = PiHoleStats(pihole_client)

        # Get data for the last 24 hours
        now = int(time.time())
        day_ago = now - (24 * 60 * 60)

        history = stats.get_database_history(day_ago, now)

        # Should have database history data structure
        assert hasattr(history, "history")
        assert hasattr(history, "took")
        assert isinstance(history.history, list)
        assert isinstance(history.took, float)

    def test_get_database_client_history(self, pihole_client):
        """Should return database client activity data for time range."""
        stats = PiHoleStats(pihole_client)

        # Get data for the last 24 hours
        now = int(time.time())
        day_ago = now - (24 * 60 * 60)

        client_history = stats.get_database_client_history(day_ago, now)

        # Should have database client history data structure
        assert hasattr(client_history, "history")
        assert hasattr(client_history, "clients")
        assert hasattr(client_history, "took")
        assert isinstance(client_history.history, list)
        assert isinstance(client_history.clients, dict)
        assert isinstance(client_history.took, float)

    def test_get_queries(self, pihole_client):
        """Should return query details."""
        stats = PiHoleStats(pihole_client)
        queries = stats.get_queries(length=10)

        # Should have queries data structure
        assert hasattr(queries, "queries")
        assert hasattr(queries, "cursor")
        assert hasattr(queries, "records_total")
        assert hasattr(queries, "records_filtered")
        assert hasattr(queries, "draw")
        assert hasattr(queries, "took")
        assert isinstance(queries.queries, list)
        assert isinstance(queries.cursor, int)
        assert isinstance(queries.records_total, int)
        assert isinstance(queries.records_filtered, int)
        assert isinstance(queries.draw, int)
        assert isinstance(queries.took, float)

    def test_get_query_suggestions(self, pihole_client):
        """Should return query filter suggestions."""
        stats = PiHoleStats(pihole_client)
        suggestions = stats.get_query_suggestions()

        # Should have suggestions data structure
        assert hasattr(suggestions, "suggestions")
        assert hasattr(suggestions, "took")
        assert isinstance(suggestions.took, float)

        # Suggestions should have required fields
        assert hasattr(suggestions.suggestions, "domain")
        assert hasattr(suggestions.suggestions, "client_ip")
        assert hasattr(suggestions.suggestions, "client_name")
        assert hasattr(suggestions.suggestions, "upstream")
        assert hasattr(suggestions.suggestions, "type")
        assert hasattr(suggestions.suggestions, "status")
        assert isinstance(suggestions.suggestions.domain, list)
        assert isinstance(suggestions.suggestions.client_ip, list)
        assert isinstance(suggestions.suggestions.client_name, list)
        assert isinstance(suggestions.suggestions.upstream, list)
        assert isinstance(suggestions.suggestions.type, list)
        assert isinstance(suggestions.suggestions.status, list)

    def test_get_query_types(self, pihole_client):
        """Should return query types statistics."""
        stats = PiHoleStats(pihole_client)
        query_types = stats.get_query_types()

        # Should have query types data structure
        assert hasattr(query_types, "types")
        assert hasattr(query_types, "took")
        assert isinstance(query_types.types, dict)
        assert isinstance(query_types.took, float)

        # Should have common query types
        assert "A" in query_types.types
        assert "AAAA" in query_types.types
        assert isinstance(query_types.types["A"], int)
        assert isinstance(query_types.types["AAAA"], int)

    def test_get_recent_blocked(self, pihole_client):
        """Should return recently blocked domains."""
        stats = PiHoleStats(pihole_client)
        recent_blocked = stats.get_recent_blocked(count=5)

        # Should have recent blocked data structure
        assert hasattr(recent_blocked, "blocked")
        assert hasattr(recent_blocked, "took")
        assert isinstance(recent_blocked.blocked, list)
        assert isinstance(recent_blocked.took, float)

    def test_get_summary(self, pihole_client):
        """Should return Pi-hole activity summary."""
        stats = PiHoleStats(pihole_client)
        summary = stats.get_summary()

        # Should have summary data structure
        assert hasattr(summary, "queries")
        assert hasattr(summary, "clients")
        assert hasattr(summary, "gravity")
        assert hasattr(summary, "took")
        assert isinstance(summary.took, float)

        # Queries should have required fields
        assert hasattr(summary.queries, "total")
        assert hasattr(summary.queries, "blocked")
        assert hasattr(summary.queries, "percent_blocked")
        assert hasattr(summary.queries, "unique_domains")
        assert hasattr(summary.queries, "forwarded")
        assert hasattr(summary.queries, "cached")
        assert hasattr(summary.queries, "frequency")
        assert hasattr(summary.queries, "types")
        assert hasattr(summary.queries, "status")
        assert isinstance(summary.queries.total, int)
        assert isinstance(summary.queries.blocked, int)
        assert isinstance(summary.queries.percent_blocked, float)
        assert isinstance(summary.queries.types, dict)
        assert isinstance(summary.queries.status, dict)

        # Clients should have required fields
        assert hasattr(summary.clients, "total")
        assert hasattr(summary.clients, "active")
        assert isinstance(summary.clients.total, int)
        assert isinstance(summary.clients.active, int)

        # Gravity should have required fields
        assert hasattr(summary.gravity, "domains_being_blocked")
        assert hasattr(summary.gravity, "last_update")
        assert isinstance(summary.gravity.domains_being_blocked, int)
        assert isinstance(summary.gravity.last_update, int)

    def test_get_top_clients(self, pihole_client):
        """Should return top clients."""
        stats = PiHoleStats(pihole_client)
        top_clients = stats.get_top_clients(count=5)

        # Should have top clients data structure
        assert hasattr(top_clients, "clients")
        assert hasattr(top_clients, "total_queries")
        assert hasattr(top_clients, "blocked_queries")
        assert hasattr(top_clients, "took")
        assert isinstance(top_clients.clients, list)
        assert isinstance(top_clients.total_queries, int)
        assert isinstance(top_clients.blocked_queries, int)
        assert isinstance(top_clients.took, float)

        # Each client should have required fields
        for client in top_clients.clients:
            assert hasattr(client, "ip")
            assert hasattr(client, "name")
            assert hasattr(client, "count")
            assert isinstance(client.ip, str)
            assert isinstance(client.count, int)

    def test_get_top_domains(self, pihole_client):
        """Should return top domains."""
        stats = PiHoleStats(pihole_client)
        top_domains = stats.get_top_domains(count=5)

        # Should have top domains data structure
        assert hasattr(top_domains, "domains")
        assert hasattr(top_domains, "total_queries")
        assert hasattr(top_domains, "blocked_queries")
        assert hasattr(top_domains, "took")
        assert isinstance(top_domains.domains, list)
        assert isinstance(top_domains.total_queries, int)
        assert isinstance(top_domains.blocked_queries, int)
        assert isinstance(top_domains.took, float)

        # Each domain should have required fields
        for domain in top_domains.domains:
            assert hasattr(domain, "domain")
            assert hasattr(domain, "count")
            assert isinstance(domain.domain, str)
            assert isinstance(domain.count, int)

    def test_get_upstreams(self, pihole_client):
        """Should return upstream server metrics."""
        stats = PiHoleStats(pihole_client)
        upstreams = stats.get_upstreams()

        # Should have upstreams data structure
        assert hasattr(upstreams, "upstreams")
        assert hasattr(upstreams, "total_queries")
        assert hasattr(upstreams, "forwarded_queries")
        assert hasattr(upstreams, "took")
        assert isinstance(upstreams.upstreams, list)
        assert isinstance(upstreams.total_queries, int)
        assert isinstance(upstreams.forwarded_queries, int)
        assert isinstance(upstreams.took, float)

        # Each upstream should have required fields
        for upstream in upstreams.upstreams:
            assert hasattr(upstream, "ip")
            assert hasattr(upstream, "name")
            assert hasattr(upstream, "port")
            assert hasattr(upstream, "count")
            assert isinstance(upstream.ip, str)
            assert isinstance(upstream.name, str)
            assert isinstance(upstream.port, int)
            assert isinstance(upstream.count, int)

    def test_get_database_query_types(self, pihole_client):
        """Should return database query types for time range."""
        stats = PiHoleStats(pihole_client)

        # Get data for the last 24 hours
        now = int(time.time())
        day_ago = now - (24 * 60 * 60)

        query_types = stats.get_database_query_types(day_ago, now)

        # Should have query types data structure
        assert hasattr(query_types, "types")
        assert hasattr(query_types, "took")
        assert isinstance(query_types.types, dict)
        assert isinstance(query_types.took, float)

    def test_get_database_summary(self, pihole_client):
        """Should return database summary for time range."""
        stats = PiHoleStats(pihole_client)

        # Get data for the last 24 hours
        now = int(time.time())
        day_ago = now - (24 * 60 * 60)

        summary = stats.get_database_summary(day_ago, now)

        # Should have database summary data structure
        assert hasattr(summary, "sum_queries")
        assert hasattr(summary, "sum_blocked")
        assert hasattr(summary, "percent_blocked")
        assert hasattr(summary, "total_clients")
        assert hasattr(summary, "took")
        assert isinstance(summary.sum_queries, int)
        assert isinstance(summary.sum_blocked, int)
        assert isinstance(summary.percent_blocked, float)
        assert isinstance(summary.total_clients, int)
        assert isinstance(summary.took, float)

    def test_get_database_top_clients(self, pihole_client):
        """Should return database top clients for time range."""
        stats = PiHoleStats(pihole_client)

        # Get data for the last 24 hours
        now = int(time.time())
        day_ago = now - (24 * 60 * 60)

        top_clients = stats.get_database_top_clients(day_ago, now)

        # Should have top clients data structure
        assert hasattr(top_clients, "clients")
        assert hasattr(top_clients, "total_queries")
        assert hasattr(top_clients, "blocked_queries")
        assert hasattr(top_clients, "took")
        assert isinstance(top_clients.clients, list)
        assert isinstance(top_clients.total_queries, int)
        assert isinstance(top_clients.blocked_queries, int)
        assert isinstance(top_clients.took, float)

    def test_get_database_top_domains(self, pihole_client):
        """Should return database top domains for time range."""
        stats = PiHoleStats(pihole_client)

        # Get data for the last 24 hours
        now = int(time.time())
        day_ago = now - (24 * 60 * 60)

        top_domains = stats.get_database_top_domains(day_ago, now)

        # Should have top domains data structure
        assert hasattr(top_domains, "domains")
        assert hasattr(top_domains, "total_queries")
        assert hasattr(top_domains, "blocked_queries")
        assert hasattr(top_domains, "took")
        assert isinstance(top_domains.domains, list)
        assert isinstance(top_domains.total_queries, int)
        assert isinstance(top_domains.blocked_queries, int)
        assert isinstance(top_domains.took, float)

    def test_get_database_upstreams(self, pihole_client):
        """Should return database upstream metrics for time range."""
        stats = PiHoleStats(pihole_client)

        # Get data for the last 24 hours
        now = int(time.time())
        day_ago = now - (24 * 60 * 60)

        upstreams = stats.get_database_upstreams(day_ago, now)

        # Should have upstreams data structure
        assert hasattr(upstreams, "upstreams")
        assert hasattr(upstreams, "total_queries")
        assert hasattr(upstreams, "forwarded_queries")
        assert hasattr(upstreams, "took")
        assert isinstance(upstreams.upstreams, list)
        assert isinstance(upstreams.total_queries, int)
        assert isinstance(upstreams.forwarded_queries, int)
        assert isinstance(upstreams.took, float)

    def test_stats_via_client_property(self, pihole_client):
        """Should access stats via client property."""
        # Test property access
        summary = pihole_client.stats.get_summary()

        # Should have summary data structure
        assert hasattr(summary, "queries")
        assert hasattr(summary, "clients")
        assert hasattr(summary, "gravity")
        assert hasattr(summary, "took")
        assert isinstance(summary.took, float)
