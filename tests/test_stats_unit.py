"""Unit tests for Pi-hole Stats API client."""

import time
from unittest.mock import Mock, patch

import pytest

from pihole_lib import PiHoleClient, PiHoleStats
from pihole_lib.exceptions import (
    PiHoleAPIError,
    PiHoleAuthenticationError,
    PiHoleConnectionError,
    PiHoleServerError,
)
from tests.constants import (
    PIHOLE_BASE_URL,
    TEST_SESSION_ID,
)


class TestPiHoleStatsUnit:
    """Unit tests for PiHoleStats class."""

    @pytest.fixture
    def mock_client(self):
        """Create a mock PiHoleClient."""
        client = Mock(spec=PiHoleClient)
        client.base_url = PIHOLE_BASE_URL
        client.get_session_id.return_value = TEST_SESSION_ID
        return client

    @pytest.fixture
    def stats_client(self, mock_client):
        """Create a PiHoleStats instance with mock client."""
        return PiHoleStats(mock_client)

    def test_init(self, mock_client):
        """Should initialize with client."""
        stats = PiHoleStats(mock_client)
        assert stats._client == mock_client

    def test_get_history_success(self, stats_client, mock_client):
        """Should return history data on success."""
        # Mock successful response
        mock_response = Mock()
        mock_response.json.return_value = {
            "history": [
                {
                    "timestamp": 1767717900,
                    "total": 100,
                    "cached": 20,
                    "blocked": 30,
                    "forwarded": 50,
                }
            ],
            "took": 0.001,
        }

        with patch("pihole_lib.stats.make_pihole_request", return_value=mock_response):
            result = stats_client.get_history()

            assert len(result.history) == 1
            assert result.history[0].timestamp == 1767717900
            assert result.history[0].total == 100
            assert result.history[0].cached == 20
            assert result.history[0].blocked == 30
            assert result.history[0].forwarded == 50
            assert result.took == 0.001

    def test_get_client_history_success(self, stats_client, mock_client):
        """Should return client history data on success."""
        # Mock successful response
        mock_response = Mock()
        mock_response.json.return_value = {
            "history": [
                {
                    "timestamp": 1767717900,
                    "data": {"192.168.1.100": 50, "others": 10},
                }
            ],
            "clients": {"192.168.1.100": "client1"},
            "took": 0.001,
        }

        with patch("pihole_lib.stats.make_pihole_request", return_value=mock_response):
            result = stats_client.get_client_history()

            assert len(result.history) == 1
            assert result.history[0].timestamp == 1767717900
            assert result.history[0].data == {"192.168.1.100": 50, "others": 10}
            assert result.clients == {"192.168.1.100": "client1"}
            assert result.took == 0.001

    def test_get_database_history_success(self, stats_client, mock_client):
        """Should return database history data on success."""
        # Mock successful response
        mock_response = Mock()
        mock_response.json.return_value = {
            "history": [],
            "took": 0.001,
        }

        with patch("pihole_lib.stats.make_pihole_request", return_value=mock_response):
            now = int(time.time())
            day_ago = now - (24 * 60 * 60)
            result = stats_client.get_database_history(day_ago, now)

            assert result.history == []
            assert result.took == 0.001

    def test_get_queries_success(self, stats_client, mock_client):
        """Should return queries data on success."""
        # Mock successful response
        mock_response = Mock()
        mock_response.json.return_value = {
            "queries": [],
            "cursor": -1,
            "recordsTotal": 0,
            "recordsFiltered": 0,
            "draw": 0,
            "took": 0.001,
        }

        with patch("pihole_lib.stats.make_pihole_request", return_value=mock_response):
            result = stats_client.get_queries(length=50)

            assert result.queries == []
            assert result.cursor == -1
            assert result.records_total == 0
            assert result.records_filtered == 0
            assert result.draw == 0
            assert result.took == 0.001

    def test_get_query_suggestions_success(self, stats_client, mock_client):
        """Should return query suggestions on success."""
        # Mock successful response
        mock_response = Mock()
        mock_response.json.return_value = {
            "suggestions": {
                "domain": ["example.com"],
                "client_ip": ["192.168.1.100"],
                "client_name": ["client1"],
                "upstream": ["blocklist", "cache"],
                "type": ["A", "AAAA"],
                "status": ["FORWARDED", "BLOCKED"],
            },
            "took": 0.001,
        }

        with patch("pihole_lib.stats.make_pihole_request", return_value=mock_response):
            result = stats_client.get_query_suggestions()

            assert result.suggestions.domain == ["example.com"]
            assert result.suggestions.client_ip == ["192.168.1.100"]
            assert result.suggestions.upstream == ["blocklist", "cache"]
            assert result.took == 0.001

    def test_get_query_types_success(self, stats_client, mock_client):
        """Should return query types on success."""
        # Mock successful response
        mock_response = Mock()
        mock_response.json.return_value = {
            "types": {"A": 100, "AAAA": 50, "PTR": 10},
            "took": 0.001,
        }

        with patch("pihole_lib.stats.make_pihole_request", return_value=mock_response):
            result = stats_client.get_query_types()

            assert result.types == {"A": 100, "AAAA": 50, "PTR": 10}
            assert result.took == 0.001

    def test_get_recent_blocked_success(self, stats_client, mock_client):
        """Should return recent blocked domains on success."""
        # Mock successful response
        mock_response = Mock()
        mock_response.json.return_value = {
            "blocked": ["ads.example.com", "tracker.example.com"],
            "took": 0.001,
        }

        with patch("pihole_lib.stats.make_pihole_request", return_value=mock_response):
            result = stats_client.get_recent_blocked(count=5)

            assert result.blocked == ["ads.example.com", "tracker.example.com"]
            assert result.took == 0.001

    def test_get_summary_success(self, stats_client, mock_client):
        """Should return summary data on success."""
        # Mock successful response
        mock_response = Mock()
        mock_response.json.return_value = {
            "queries": {
                "total": 1000,
                "blocked": 200,
                "percent_blocked": 20.0,
                "unique_domains": 100,
                "forwarded": 600,
                "cached": 200,
                "frequency": 10.5,
                "types": {"A": 500, "AAAA": 300},
                "status": {"FORWARDED": 600, "BLOCKED": 200},
                "replies": {"IP": 600, "NXDOMAIN": 200},
            },
            "clients": {"total": 10, "active": 5},
            "gravity": {"domains_being_blocked": 50000, "last_update": 1767804656},
            "took": 0.001,
        }

        with patch("pihole_lib.stats.make_pihole_request", return_value=mock_response):
            result = stats_client.get_summary()

            assert result.queries.total == 1000
            assert result.queries.blocked == 200
            assert result.queries.percent_blocked == 20.0
            assert result.clients.total == 10
            assert result.clients.active == 5
            assert result.gravity.domains_being_blocked == 50000
            assert result.took == 0.001

    def test_get_top_clients_success(self, stats_client, mock_client):
        """Should return top clients on success."""
        # Mock successful response
        mock_response = Mock()
        mock_response.json.return_value = {
            "clients": [
                {"ip": "192.168.1.100", "name": "client1", "count": 100},
                {"ip": "192.168.1.101", "name": None, "count": 50},
            ],
            "total_queries": 1000,
            "blocked_queries": 200,
            "took": 0.001,
        }

        with patch("pihole_lib.stats.make_pihole_request", return_value=mock_response):
            result = stats_client.get_top_clients(count=5)

            assert len(result.clients) == 2
            assert result.clients[0].ip == "192.168.1.100"
            assert result.clients[0].name == "client1"
            assert result.clients[0].count == 100
            assert result.clients[1].name is None
            assert result.total_queries == 1000
            assert result.blocked_queries == 200
            assert result.took == 0.001

    def test_get_top_domains_success(self, stats_client, mock_client):
        """Should return top domains on success."""
        # Mock successful response
        mock_response = Mock()
        mock_response.json.return_value = {
            "domains": [
                {"domain": "example.com", "count": 100},
                {"domain": "google.com", "count": 50},
            ],
            "total_queries": 1000,
            "blocked_queries": 200,
            "took": 0.001,
        }

        with patch("pihole_lib.stats.make_pihole_request", return_value=mock_response):
            result = stats_client.get_top_domains(count=5, blocked=False)

            assert len(result.domains) == 2
            assert result.domains[0].domain == "example.com"
            assert result.domains[0].count == 100
            assert result.domains[1].domain == "google.com"
            assert result.domains[1].count == 50
            assert result.total_queries == 1000
            assert result.blocked_queries == 200
            assert result.took == 0.001

    def test_get_upstreams_success(self, stats_client, mock_client):
        """Should return upstreams data on success."""
        # Mock successful response
        mock_response = Mock()
        mock_response.json.return_value = {
            "upstreams": [
                {
                    "ip": "8.8.8.8",
                    "name": "google-dns",
                    "port": 53,
                    "count": 500,
                    "statistics": {"response": 25.5, "variance": 5.2},
                },
                {
                    "ip": "blocklist",
                    "name": "blocklist",
                    "port": -1,
                    "count": 200,
                    "statistics": None,
                },
            ],
            "total_queries": 1000,
            "forwarded_queries": 700,
            "took": 0.001,
        }

        with patch("pihole_lib.stats.make_pihole_request", return_value=mock_response):
            result = stats_client.get_upstreams()

            assert len(result.upstreams) == 2
            assert result.upstreams[0].ip == "8.8.8.8"
            assert result.upstreams[0].name == "google-dns"
            assert result.upstreams[0].port == 53
            assert result.upstreams[0].count == 500
            assert result.upstreams[0].statistics.response == 25.5
            assert result.upstreams[1].statistics is None
            assert result.total_queries == 1000
            assert result.forwarded_queries == 700
            assert result.took == 0.001

    def test_connection_error(self, stats_client, mock_client):
        """Should raise PiHoleConnectionError on connection failure."""
        with patch(
            "pihole_lib.stats.make_pihole_request",
            side_effect=PiHoleConnectionError("Connection failed"),
        ):
            with pytest.raises(PiHoleConnectionError):
                stats_client.get_summary()

    def test_authentication_error(self, stats_client, mock_client):
        """Should raise PiHoleAuthenticationError on auth failure."""
        with patch(
            "pihole_lib.stats.make_pihole_request",
            side_effect=PiHoleAuthenticationError("Authentication failed"),
        ):
            with pytest.raises(PiHoleAuthenticationError):
                stats_client.get_summary()

    def test_server_error(self, stats_client, mock_client):
        """Should raise PiHoleServerError on server error."""
        with patch(
            "pihole_lib.stats.make_pihole_request",
            side_effect=PiHoleServerError("Server error"),
        ):
            with pytest.raises(PiHoleServerError):
                stats_client.get_summary()

    def test_api_error(self, stats_client, mock_client):
        """Should raise PiHoleAPIError on other API errors."""
        with patch(
            "pihole_lib.stats.make_pihole_request",
            side_effect=PiHoleAPIError("API error"),
        ):
            with pytest.raises(PiHoleAPIError):
                stats_client.get_summary()
