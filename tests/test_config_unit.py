"""Unit tests for PiHoleConfig class."""

from unittest.mock import Mock, patch

import pytest

from pihole_lib import PiHoleClient, PiHoleConfig
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
            config_client.BASE_URL,
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
            "/api/config/dns",
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
            "/api/config/dns/upstreams",
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
            "/api/config/dhcp",
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
            "/api/config/webserver",
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


class TestUpdateConfig:
    """Test update_config method."""

    @patch("pihole_lib.config.make_pihole_request")
    def test_update_config_dns_success(self, mock_request, config_client):
        """Test successful DNS config update."""
        # Mock successful response
        mock_response = Mock()
        mock_response.json.return_value = {
            "config": {
                "dns": {
                    "upstreams": ["1.1.1.1", "1.0.0.1"],
                    "queryLogging": True,
                    "port": 53,
                }
            },
            "took": 0.005,
        }
        mock_request.return_value = mock_response

        # Test data
        config_update = {
            "dns": {
                "upstreams": ["1.1.1.1", "1.0.0.1"],
                "queryLogging": True,
            }
        }

        result = config_client.update_config(config_update)

        # Verify the request was made correctly
        mock_request.assert_called_once_with(
            config_client._client,
            "PATCH",
            "/api/config",
            params={"restart": True},
            json={"config": config_update},
        )

        # Verify the response
        assert isinstance(result, dict)
        assert result["dns"]["upstreams"] == ["1.1.1.1", "1.0.0.1"]
        assert result["dns"]["queryLogging"] is True

    @patch("pihole_lib.config.make_pihole_request")
    def test_update_config_dhcp_success(self, mock_request, config_client):
        """Test successful DHCP config update."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "config": {
                "dhcp": {
                    "active": True,
                    "start": "192.168.1.100",
                    "end": "192.168.1.200",
                    "router": "192.168.1.1",
                }
            },
            "took": 0.008,
        }
        mock_request.return_value = mock_response

        config_update = {
            "dhcp": {
                "active": True,
                "start": "192.168.1.100",
                "end": "192.168.1.200",
                "router": "192.168.1.1",
            }
        }

        result = config_client.update_config(config_update)

        mock_request.assert_called_once_with(
            config_client._client,
            "PATCH",
            "/api/config",
            params={"restart": True},
            json={"config": config_update},
        )

        assert result["dhcp"]["active"] is True
        assert result["dhcp"]["start"] == "192.168.1.100"

    @patch("pihole_lib.config.make_pihole_request")
    def test_update_config_no_restart(self, mock_request, config_client):
        """Test config update without restart."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "config": {"dns": {"upstreams": ["8.8.8.8"]}},
            "took": 0.003,
        }
        mock_request.return_value = mock_response

        config_update = {"dns": {"upstreams": ["8.8.8.8"]}}

        config_client.update_config(config_update, restart=False)

        mock_request.assert_called_once_with(
            config_client._client,
            "PATCH",
            "/api/config",
            params={"restart": False},
            json={"config": config_update},
        )

    @patch("pihole_lib.config.make_pihole_request")
    def test_update_config_multiple_sections(self, mock_request, config_client):
        """Test updating multiple config sections at once."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "config": {
                "dns": {"upstreams": ["1.1.1.1"], "port": 5353},
                "webserver": {"port": "8080o"},
            },
            "took": 0.010,
        }
        mock_request.return_value = mock_response

        config_update = {
            "dns": {"upstreams": ["1.1.1.1"], "port": 5353},
            "webserver": {"port": "8080o"},
        }

        result = config_client.update_config(config_update)

        mock_request.assert_called_once_with(
            config_client._client,
            "PATCH",
            "/api/config",
            params={"restart": True},
            json={"config": config_update},
        )

        assert result["dns"]["port"] == 5353
        assert result["webserver"]["port"] == "8080o"


class TestAddConfigItem:
    """Test add_config_item method."""

    @patch("pihole_lib.config.make_pihole_request")
    def test_add_config_item_success(self, mock_request, config_client):
        """Test successful config item addition."""
        mock_response = Mock()
        mock_response.status_code = 201
        mock_request.return_value = mock_response

        result = config_client.add_config_item("dns/upstreams", "1.1.1.1")

        mock_request.assert_called_once_with(
            config_client._client,
            "PUT",
            "/api/config/dns%2Fupstreams/1.1.1.1",
            params={"restart": True},
        )

        assert result is True

    @patch("pihole_lib.config.make_pihole_request")
    def test_add_config_item_no_restart(self, mock_request, config_client):
        """Test config item addition without restart."""
        mock_response = Mock()
        mock_response.status_code = 201
        mock_request.return_value = mock_response

        result = config_client.add_config_item(
            "dns/upstreams", "8.8.8.8", restart=False
        )

        mock_request.assert_called_once_with(
            config_client._client,
            "PUT",
            "/api/config/dns%2Fupstreams/8.8.8.8",
            params={"restart": False},
        )

        assert result is True

    @patch("pihole_lib.config.make_pihole_request")
    def test_add_config_item_with_special_chars(self, mock_request, config_client):
        """Test config item addition with special characters."""
        mock_response = Mock()
        mock_response.status_code = 201
        mock_request.return_value = mock_response

        # Test with spaces and special characters
        result = config_client.add_config_item(
            "dns/hosts", "192.168.1.10 myserver.local"
        )

        mock_request.assert_called_once_with(
            config_client._client,
            "PUT",
            "/api/config/dns%2Fhosts/192.168.1.10%20myserver.local",
            params={"restart": True},
        )

        assert result is True

    @patch("pihole_lib.config.make_pihole_request")
    def test_add_config_item_failure(self, mock_request, config_client):
        """Test config item addition failure."""
        mock_response = Mock()
        mock_response.status_code = 400
        mock_request.return_value = mock_response

        result = config_client.add_config_item("dns/upstreams", "invalid")

        assert result is False

    @patch("pihole_lib.config.make_pihole_request")
    def test_add_config_item_webserver_header(self, mock_request, config_client):
        """Test adding webserver header."""
        mock_response = Mock()
        mock_response.status_code = 201
        mock_request.return_value = mock_response

        result = config_client.add_config_item(
            "webserver/headers", "X-Custom-Header: MyValue"
        )

        mock_request.assert_called_once_with(
            config_client._client,
            "PUT",
            "/api/config/webserver%2Fheaders/X-Custom-Header%3A%20MyValue",
            params={"restart": True},
        )

        assert result is True


class TestRemoveConfigItem:
    """Test remove_config_item method."""

    @patch("pihole_lib.config.make_pihole_request")
    def test_remove_config_item_success(self, mock_request, config_client):
        """Test successful config item removal."""
        mock_response = Mock()
        mock_response.status_code = 204
        mock_request.return_value = mock_response

        result = config_client.remove_config_item("dns/upstreams", "8.8.8.8")

        mock_request.assert_called_once_with(
            config_client._client,
            "DELETE",
            "/api/config/dns%2Fupstreams/8.8.8.8",
            params={"restart": True},
        )

        assert result is True

    @patch("pihole_lib.config.make_pihole_request")
    def test_remove_config_item_no_restart(self, mock_request, config_client):
        """Test config item removal without restart."""
        mock_response = Mock()
        mock_response.status_code = 204
        mock_request.return_value = mock_response

        result = config_client.remove_config_item(
            "dns/upstreams", "1.1.1.1", restart=False
        )

        mock_request.assert_called_once_with(
            config_client._client,
            "DELETE",
            "/api/config/dns%2Fupstreams/1.1.1.1",
            params={"restart": False},
        )

        assert result is True

    @patch("pihole_lib.config.make_pihole_request")
    def test_remove_config_item_with_special_chars(self, mock_request, config_client):
        """Test config item removal with special characters."""
        mock_response = Mock()
        mock_response.status_code = 204
        mock_request.return_value = mock_response

        result = config_client.remove_config_item(
            "dns/hosts", "192.168.1.10 myserver.local"
        )

        mock_request.assert_called_once_with(
            config_client._client,
            "DELETE",
            "/api/config/dns%2Fhosts/192.168.1.10%20myserver.local",
            params={"restart": True},
        )

        assert result is True

    @patch("pihole_lib.config.make_pihole_request")
    def test_remove_config_item_failure(self, mock_request, config_client):
        """Test config item removal failure."""
        mock_response = Mock()
        mock_response.status_code = 404
        mock_request.return_value = mock_response

        result = config_client.remove_config_item("dns/upstreams", "nonexistent")

        assert result is False

    @patch("pihole_lib.config.make_pihole_request")
    def test_remove_config_item_dhcp_host(self, mock_request, config_client):
        """Test removing DHCP host entry."""
        mock_response = Mock()
        mock_response.status_code = 204
        mock_request.return_value = mock_response

        result = config_client.remove_config_item(
            "dhcp/hosts", "12:34:56:78:9A:BC,192.168.1.50,laptop"
        )

        mock_request.assert_called_once_with(
            config_client._client,
            "DELETE",
            "/api/config/dhcp%2Fhosts/12%3A34%3A56%3A78%3A9A%3ABC%2C192.168.1.50%2Claptop",
            params={"restart": True},
        )

        assert result is True
