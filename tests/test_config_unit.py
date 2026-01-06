"""Unit tests for PiHoleConfig class."""

from unittest.mock import Mock, patch

import pytest

from pihole_lib import PiHoleClient, PiHoleConfig
from pihole_lib.constants import API_CONFIG
from pihole_lib.exceptions import (
    PiHoleAPIError,
    PiHoleAuthenticationError,
    PiHoleConnectionError,
    PiHoleServerError,
)

from .constants import TEST_LOCALHOST_URL


@pytest.fixture
def mock_client():
    """Create a mock PiHoleClient for testing."""
    client = Mock(spec=PiHoleClient)
    client.base_url = TEST_LOCALHOST_URL
    client.timeout = 30
    client.verify_ssl = True
    client._session_id = "test-session-id"
    return client


@pytest.fixture
def config_client(mock_client):
    """Create a PiHoleConfig instance with mock client."""
    return PiHoleConfig(mock_client)


class TestPiHoleConfigInit:
    """Test PiHoleConfig initialization."""

    def test_init_with_client(self, mock_client):
        """Test initialization with a client."""
        config = PiHoleConfig(mock_client)
        assert config._client is mock_client


class TestGetConfig:
    """Test get_config method."""

    @patch("pihole_lib.config.make_pihole_request")
    def test_get_config_full_success(self, mock_request, config_client):
        """Test successful full config retrieval."""
        # Mock successful response with sample config data
        mock_response = Mock()
        mock_response.json.return_value = {
            "config": {
                "dns": {
                    "upstreams": ["8.8.8.8", "8.8.4.4"],
                    "queryLogging": True,
                    "port": 53,
                },
                "dhcp": {"active": False, "start": "", "end": ""},
                "webserver": {"domain": "pi.hole", "port": "80o,443os"},
            },
            "took": 0.001,
        }
        mock_request.return_value = mock_response

        # Call the method without element (full config)
        result = config_client.get_config()

        # Verify the request was made correctly
        mock_request.assert_called_once_with(
            config_client._client,
            "GET",
            API_CONFIG,
        )

        # Verify the response structure
        assert isinstance(result, dict)
        assert "dns" in result
        assert "dhcp" in result
        assert "webserver" in result

        # Verify specific values
        assert result["dns"]["upstreams"] == ["8.8.8.8", "8.8.4.4"]
        assert result["dns"]["queryLogging"] is True
        assert result["dhcp"]["active"] is False
        assert result["webserver"]["domain"] == "pi.hole"

    @patch("pihole_lib.config.make_pihole_request")
    def test_get_config_element_dns_success(self, mock_request, config_client):
        """Test successful DNS config element retrieval."""
        # Mock successful response with DNS config data
        mock_response = Mock()
        mock_response.json.return_value = {
            "config": {
                "dns": {
                    "upstreams": ["8.8.8.8", "8.8.4.4"],
                    "queryLogging": True,
                    "port": 53,
                    "CNAMEdeepInspect": True,
                }
            },
            "took": 0.001,
        }
        mock_request.return_value = mock_response

        # Call the method with DNS element
        result = config_client.get_config("dns")

        # Verify the request was made correctly
        mock_request.assert_called_once_with(
            config_client._client,
            "GET",
            f"{API_CONFIG}/dns",
        )

        # Verify the response structure
        assert isinstance(result, dict)
        assert "dns" in result
        assert result["dns"]["upstreams"] == ["8.8.8.8", "8.8.4.4"]
        assert result["dns"]["queryLogging"] is True
        assert result["dns"]["port"] == 53

    @patch("pihole_lib.config.make_pihole_request")
    def test_get_config_element_dns_upstreams_success(
        self, mock_request, config_client
    ):
        """Test successful DNS upstreams config element retrieval."""
        # Mock successful response with DNS upstreams only
        mock_response = Mock()
        mock_response.json.return_value = {
            "config": {"dns": {"upstreams": ["1.1.1.1", "1.0.0.1"]}},
            "took": 0.001,
        }
        mock_request.return_value = mock_response

        # Call the method with DNS upstreams element
        result = config_client.get_config("dns/upstreams")

        # Verify the request was made correctly
        mock_request.assert_called_once_with(
            config_client._client,
            "GET",
            f"{API_CONFIG}/dns/upstreams",
        )

        # Verify the response structure
        assert isinstance(result, dict)
        assert "dns" in result
        assert "upstreams" in result["dns"]
        assert result["dns"]["upstreams"] == ["1.1.1.1", "1.0.0.1"]

    @patch("pihole_lib.config.make_pihole_request")
    def test_get_config_element_dhcp_success(self, mock_request, config_client):
        """Test successful DHCP config element retrieval."""
        # Mock successful response with DHCP config data
        mock_response = Mock()
        mock_response.json.return_value = {
            "config": {
                "dhcp": {
                    "active": True,
                    "start": "192.168.1.100",
                    "end": "192.168.1.200",
                    "router": "192.168.1.1",
                    "leaseTime": "24h",
                }
            },
            "took": 0.001,
        }
        mock_request.return_value = mock_response

        # Call the method with DHCP element
        result = config_client.get_config("dhcp")

        # Verify the request was made correctly
        mock_request.assert_called_once_with(
            config_client._client,
            "GET",
            f"{API_CONFIG}/dhcp",
        )

        # Verify the response structure
        assert isinstance(result, dict)
        assert "dhcp" in result
        assert result["dhcp"]["active"] is True
        assert result["dhcp"]["start"] == "192.168.1.100"
        assert result["dhcp"]["leaseTime"] == "24h"

    @patch("pihole_lib.config.make_pihole_request")
    def test_get_config_element_webserver_success(self, mock_request, config_client):
        """Test successful webserver config element retrieval."""
        # Mock successful response with webserver config data
        mock_response = Mock()
        mock_response.json.return_value = {
            "config": {
                "webserver": {
                    "domain": "pihole.local",
                    "port": "80o,443os",
                    "threads": 50,
                }
            },
            "took": 0.001,
        }
        mock_request.return_value = mock_response

        # Call the method with webserver element
        result = config_client.get_config("webserver")

        # Verify the request was made correctly
        mock_request.assert_called_once_with(
            config_client._client,
            "GET",
            f"{API_CONFIG}/webserver",
        )

        # Verify the response structure
        assert isinstance(result, dict)
        assert "webserver" in result
        assert result["webserver"]["domain"] == "pihole.local"
        assert result["webserver"]["threads"] == 50

    @patch("pihole_lib.config.make_pihole_request")
    def test_get_config_minimal_response(self, mock_request, config_client):
        """Test config retrieval with minimal response."""
        # Mock minimal response
        mock_response = Mock()
        mock_response.json.return_value = {
            "config": {"dns": {"upstreams": []}, "dhcp": {"active": False}}
        }
        mock_request.return_value = mock_response

        result = config_client.get_config()

        assert isinstance(result, dict)
        assert "dns" in result
        assert "dhcp" in result
        assert result["dns"]["upstreams"] == []
        assert result["dhcp"]["active"] is False

    @patch("pihole_lib.config.make_pihole_request")
    def test_get_config_connection_error(self, mock_request, config_client):
        """Test config retrieval with connection error."""
        mock_request.side_effect = PiHoleConnectionError("Connection failed")

        with pytest.raises(PiHoleConnectionError, match="Connection failed"):
            config_client.get_config()

    @patch("pihole_lib.config.make_pihole_request")
    def test_get_config_element_connection_error(self, mock_request, config_client):
        """Test config element retrieval with connection error."""
        mock_request.side_effect = PiHoleConnectionError("Connection failed")

        with pytest.raises(PiHoleConnectionError, match="Connection failed"):
            config_client.get_config("dns")

    @patch("pihole_lib.config.make_pihole_request")
    def test_get_config_authentication_error(self, mock_request, config_client):
        """Test config retrieval with authentication error."""
        mock_request.side_effect = PiHoleAuthenticationError("Invalid credentials")

        with pytest.raises(PiHoleAuthenticationError, match="Invalid credentials"):
            config_client.get_config()

    @patch("pihole_lib.config.make_pihole_request")
    def test_get_config_element_authentication_error(self, mock_request, config_client):
        """Test config element retrieval with authentication error."""
        mock_request.side_effect = PiHoleAuthenticationError("Invalid credentials")

        with pytest.raises(PiHoleAuthenticationError, match="Invalid credentials"):
            config_client.get_config("dhcp")

    @patch("pihole_lib.config.make_pihole_request")
    def test_get_config_server_error(self, mock_request, config_client):
        """Test config retrieval with server error."""
        mock_request.side_effect = PiHoleServerError("Server error: 500")

        with pytest.raises(PiHoleServerError, match="Server error: 500"):
            config_client.get_config()

    @patch("pihole_lib.config.make_pihole_request")
    def test_get_config_element_server_error(self, mock_request, config_client):
        """Test config element retrieval with server error."""
        mock_request.side_effect = PiHoleServerError("Server error: 500")

        with pytest.raises(PiHoleServerError, match="Server error: 500"):
            config_client.get_config("webserver")

    @patch("pihole_lib.config.make_pihole_request")
    def test_get_config_api_error(self, mock_request, config_client):
        """Test config retrieval with API error."""
        mock_request.side_effect = PiHoleAPIError("Bad request")

        with pytest.raises(PiHoleAPIError, match="Bad request"):
            config_client.get_config()

    @patch("pihole_lib.config.make_pihole_request")
    def test_get_config_element_api_error(self, mock_request, config_client):
        """Test config element retrieval with API error."""
        mock_request.side_effect = PiHoleAPIError("Bad request")

        with pytest.raises(PiHoleAPIError, match="Bad request"):
            config_client.get_config("invalid/element")

    @patch("pihole_lib.config.make_pihole_request")
    def test_get_config_complex_structure(self, mock_request, config_client):
        """Test config retrieval with complex nested structure."""
        # Mock response with complex nested data
        mock_response = Mock()
        mock_response.json.return_value = {
            "config": {
                "dns": {
                    "upstreams": ["1.1.1.1", "1.0.0.1"],
                    "cache": {"size": 10000, "optimizer": 3600},
                    "blocking": {"active": True, "mode": "NULL"},
                },
                "webserver": {
                    "session": {"timeout": 1800, "restore": True},
                    "tls": {"cert": "/etc/pihole/tls.pem", "validity": 47},
                },
            }
        }
        mock_request.return_value = mock_response

        result = config_client.get_config()

        # Verify nested structure access
        assert result["dns"]["cache"]["size"] == 10000
        assert result["dns"]["blocking"]["active"] is True
        assert result["webserver"]["session"]["timeout"] == 1800
        assert result["webserver"]["tls"]["cert"] == "/etc/pihole/tls.pem"
