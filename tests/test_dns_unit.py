"""Unit tests for PiHoleDNS class."""

from unittest.mock import Mock, patch

import pytest

from pihole_lib import PiHoleClient, PiHoleDNS
from pihole_lib.exceptions import PiHoleAPIError
from pihole_lib.models import DNSBlockingStatus, DNSConfig


class TestPiHoleDNS:
    """Test cases for PiHoleDNS class."""

    @pytest.fixture
    def mock_client(self):
        """Create a mock PiHoleClient for testing."""
        client = Mock(spec=PiHoleClient)
        client.base_url = "http://localhost"
        client._session = Mock()
        return client

    @pytest.fixture
    def dns_client(self, mock_client):
        """Create a PiHoleDNS instance for testing."""
        return PiHoleDNS(mock_client)

    @patch("pihole_lib.dns.PiHoleConfig")
    def test_get_config_success(self, mock_config_class, dns_client, mock_client):
        """Test successful DNS configuration retrieval."""
        # Mock PiHoleConfig instance and its get_config method
        mock_config_instance = Mock()
        mock_config_class.return_value = mock_config_instance

        # Mock response data from PiHoleConfig.get_config("dns")
        mock_config_data = {
            "dns": {
                "upstreams": ["8.8.8.8", "8.8.4.4"],
                "hosts": ["192.168.1.100 server.local"],
                "cnameRecords": ["www.local,server.local"],
                "port": 53,
                "queryLogging": True,
                "blocking": {"active": True},
                "dnssec": False,
            }
        }
        mock_config_instance.get_config.return_value = mock_config_data

        # Call method
        result = dns_client.get_config()

        # Verify PiHoleConfig was instantiated with the client
        mock_config_class.assert_called_once_with(mock_client)

        # Verify get_config was called with "dns"
        mock_config_instance.get_config.assert_called_once_with("dns")

        # Verify result
        assert isinstance(result, DNSConfig)
        assert result.upstreams == ["8.8.8.8", "8.8.4.4"]
        assert len(result.records) == 2  # 1 A + 1 CNAME
        assert len(result.hosts) == 1  # A records only
        assert len(result.cname_records) == 1  # CNAME records only

        # Check A record
        a_record = result.hosts[0]
        assert a_record.domain == "server.local"
        assert a_record.target == "192.168.1.100"
        assert a_record.record_type == "A"

        # Check CNAME record
        cname_record = result.cname_records[0]
        assert cname_record.domain == "www.local"
        assert cname_record.target == "server.local"
        assert cname_record.record_type == "CNAME"

        assert result.port == 53
        assert result.query_logging is True
        assert result.blocking == {"active": True}
        assert result.blocking_active is True
        assert result.dnssec is False

    @patch("pihole_lib.dns.PiHoleConfig")
    def test_get_config_api_error(self, mock_config_class, dns_client):
        """Test DNS configuration retrieval with API error."""
        # Mock PiHoleConfig instance
        mock_config_instance = Mock()
        mock_config_class.return_value = mock_config_instance

        # Mock API error
        mock_config_instance.get_config.side_effect = PiHoleAPIError(
            "API request failed"
        )

        # Call method and expect exception
        with pytest.raises(PiHoleAPIError, match="API request failed"):
            dns_client.get_config()

    @patch("pihole_lib.dns.PiHoleConfig")
    def test_get_records_success(self, mock_config_class, dns_client, mock_client):
        """Test successful DNS records retrieval."""
        # Mock PiHoleConfig instance
        mock_config_instance = Mock()
        mock_config_class.return_value = mock_config_instance

        # Mock config data with records
        mock_config_data = {
            "dns": {
                "upstreams": ["8.8.8.8"],
                "hosts": ["192.168.1.100 server.local", "192.168.1.101 nas.local"],
                "cnameRecords": ["www.local,server.local", "files.local,nas.local"],
                "port": 53,
                "queryLogging": True,
                "blocking": {"active": True},
                "dnssec": False,
            }
        }
        mock_config_instance.get_config.return_value = mock_config_data

        # Call method
        result = dns_client.get_records()

        # Verify result
        assert len(result) == 4

        # Check A records
        a_records = [r for r in result if r.record_type == "A"]
        assert len(a_records) == 2
        assert a_records[0].domain == "server.local"
        assert a_records[0].target == "192.168.1.100"
        assert a_records[1].domain == "nas.local"
        assert a_records[1].target == "192.168.1.101"

        # Check CNAME records
        cname_records = [r for r in result if r.record_type == "CNAME"]
        assert len(cname_records) == 2
        assert cname_records[0].domain == "www.local"
        assert cname_records[0].target == "server.local"
        assert cname_records[1].domain == "files.local"
        assert cname_records[1].target == "nas.local"

    @patch("pihole_lib.dns.PiHoleConfig")
    def test_get_records_empty(self, mock_config_class, dns_client):
        """Test DNS records retrieval with no records."""
        # Mock PiHoleConfig instance
        mock_config_instance = Mock()
        mock_config_class.return_value = mock_config_instance

        # Mock empty config data
        mock_config_data = {
            "dns": {
                "upstreams": ["8.8.8.8"],
                "hosts": [],
                "cnameRecords": [],
                "port": 53,
                "queryLogging": True,
                "blocking": {"active": True},
                "dnssec": False,
            }
        }
        mock_config_instance.get_config.return_value = mock_config_data

        # Call method
        result = dns_client.get_records()

        # Verify result
        assert len(result) == 0

    @patch("pihole_lib.dns.PiHoleConfig")
    def test_get_records_filter_a_records(self, mock_config_class, dns_client):
        """Test DNS records retrieval filtered for A records only."""
        # Mock PiHoleConfig instance
        mock_config_instance = Mock()
        mock_config_class.return_value = mock_config_instance

        # Mock config data with records
        mock_config_data = {
            "dns": {
                "upstreams": ["8.8.8.8"],
                "hosts": ["192.168.1.100 server.local", "192.168.1.101 nas.local"],
                "cnameRecords": ["www.local,server.local", "files.local,nas.local"],
                "port": 53,
                "queryLogging": True,
                "blocking": {"active": True},
                "dnssec": False,
            }
        }
        mock_config_instance.get_config.return_value = mock_config_data

        # Call method with A record filter
        result = dns_client.get_records(record_type="A")

        # Verify result - should only contain A records
        assert len(result) == 2
        for record in result:
            assert record.record_type == "A"

        # Check specific A records
        assert result[0].domain == "server.local"
        assert result[0].target == "192.168.1.100"
        assert result[1].domain == "nas.local"
        assert result[1].target == "192.168.1.101"

    @patch("pihole_lib.dns.PiHoleConfig")
    def test_get_records_filter_cname_records(self, mock_config_class, dns_client):
        """Test DNS records retrieval filtered for CNAME records only."""
        # Mock PiHoleConfig instance
        mock_config_instance = Mock()
        mock_config_class.return_value = mock_config_instance

        # Mock config data with records
        mock_config_data = {
            "dns": {
                "upstreams": ["8.8.8.8"],
                "hosts": ["192.168.1.100 server.local", "192.168.1.101 nas.local"],
                "cnameRecords": ["www.local,server.local", "files.local,nas.local"],
                "port": 53,
                "queryLogging": True,
                "blocking": {"active": True},
                "dnssec": False,
            }
        }
        mock_config_instance.get_config.return_value = mock_config_data

        # Call method with CNAME record filter
        result = dns_client.get_records(record_type="CNAME")

        # Verify result - should only contain CNAME records
        assert len(result) == 2
        for record in result:
            assert record.record_type == "CNAME"

        # Check specific CNAME records
        assert result[0].domain == "www.local"
        assert result[0].target == "server.local"
        assert result[1].domain == "files.local"
        assert result[1].target == "nas.local"

    @patch("pihole_lib.dns.PiHoleConfig")
    def test_get_records_invalid_type(self, mock_config_class, dns_client):
        """Test DNS records retrieval with invalid type parameter."""
        # Mock PiHoleConfig instance (not needed for this test but required for setup)
        mock_config_instance = Mock()
        mock_config_class.return_value = mock_config_instance

        # Call method with invalid type and expect ValueError
        with pytest.raises(ValueError, match="Invalid record type 'INVALID'"):
            dns_client.get_records(record_type="INVALID")

    @patch("pihole_lib.dns.PiHoleConfig")
    def test_get_records_filter_empty_results(self, mock_config_class, dns_client):
        """Test DNS records retrieval with filter when no records of that type exist."""
        # Mock PiHoleConfig instance
        mock_config_instance = Mock()
        mock_config_class.return_value = mock_config_instance

        # Mock config data with only A records
        mock_config_data = {
            "dns": {
                "upstreams": ["8.8.8.8"],
                "hosts": ["192.168.1.100 server.local"],
                "cnameRecords": [],  # No CNAME records
                "port": 53,
                "queryLogging": True,
                "blocking": {"active": True},
                "dnssec": False,
            }
        }
        mock_config_instance.get_config.return_value = mock_config_data

        # Call method with CNAME filter - should return empty list
        result = dns_client.get_records(record_type="CNAME")

        # Verify result
        assert len(result) == 0

    @patch("pihole_lib.dns.make_pihole_request")
    def test_add_a_record_success(self, mock_request, dns_client, mock_client):
        """Test successful A record addition."""
        # Mock successful response (201 Created)
        mock_response = Mock()
        mock_response.status_code = 201
        mock_request.return_value = mock_response

        # Call method
        result = dns_client.add_a_record("server.local", "192.168.1.100")

        # Verify request was made correctly
        mock_request.assert_called_once_with(
            mock_client,
            "PUT",
            f"{dns_client.CONFIG_URL}/hosts/192.168.1.100%20server.local",
        )

        # Verify result
        assert result is True

    @patch("pihole_lib.dns.make_pihole_request")
    def test_add_a_record_failure(self, mock_request, dns_client):
        """Test A record addition failure."""
        # Mock failure response (400 Bad Request)
        mock_response = Mock()
        mock_response.status_code = 400
        mock_request.return_value = mock_response

        # Call method
        result = dns_client.add_a_record("server.local", "192.168.1.100")

        # Verify result
        assert result is False

    @patch("pihole_lib.dns.make_pihole_request")
    def test_add_a_record_api_error(self, mock_request, dns_client):
        """Test A record addition with API error."""
        # Mock API error
        mock_request.side_effect = PiHoleAPIError("Invalid domain")

        # Call method and expect exception
        with pytest.raises(PiHoleAPIError, match="Invalid domain"):
            dns_client.add_a_record("invalid..domain", "192.168.1.100")

    @patch("pihole_lib.dns.make_pihole_request")
    def test_remove_a_record_success(self, mock_request, dns_client, mock_client):
        """Test successful A record removal."""
        # Mock successful response (204 No Content)
        mock_response = Mock()
        mock_response.status_code = 204
        mock_request.return_value = mock_response

        # Call method
        result = dns_client.remove_a_record("server.local", "192.168.1.100")

        # Verify request was made correctly
        mock_request.assert_called_once_with(
            mock_client,
            "DELETE",
            f"{dns_client.CONFIG_URL}/hosts/192.168.1.100%20server.local",
        )

        # Verify result
        assert result is True

    @patch("pihole_lib.dns.make_pihole_request")
    def test_remove_a_record_not_found(self, mock_request, dns_client):
        """Test A record removal when record not found."""
        # Mock 404 response for not found record
        mock_response = Mock()
        mock_response.status_code = 404
        mock_request.return_value = mock_response

        # Call method
        result = dns_client.remove_a_record("nonexistent.local", "192.168.1.999")

        # Verify result
        assert result is False

    @patch("pihole_lib.dns.make_pihole_request")
    def test_add_cname_record_success(self, mock_request, dns_client, mock_client):
        """Test successful CNAME record addition."""
        # Mock successful response (201 Created)
        mock_response = Mock()
        mock_response.status_code = 201
        mock_request.return_value = mock_response

        # Call method
        result = dns_client.add_cname_record("www.local", "server.local")

        # Verify request was made correctly
        mock_request.assert_called_once_with(
            mock_client,
            "PUT",
            f"{dns_client.CONFIG_URL}/cnameRecords/www.local%2Cserver.local",
        )

        # Verify result
        assert result is True

    @patch("pihole_lib.dns.make_pihole_request")
    def test_add_cname_record_failure(self, mock_request, dns_client):
        """Test CNAME record addition failure."""
        # Mock failure response (400 Bad Request)
        mock_response = Mock()
        mock_response.status_code = 400
        mock_request.return_value = mock_response

        # Call method
        result = dns_client.add_cname_record("www.local", "server.local")

        # Verify result
        assert result is False

    @patch("pihole_lib.dns.make_pihole_request")
    def test_remove_cname_record_success(self, mock_request, dns_client, mock_client):
        """Test successful CNAME record removal."""
        # Mock successful response (204 No Content)
        mock_response = Mock()
        mock_response.status_code = 204
        mock_request.return_value = mock_response

        # Call method
        result = dns_client.remove_cname_record("www.local", "server.local")

        # Verify request was made correctly
        mock_request.assert_called_once_with(
            mock_client,
            "DELETE",
            f"{dns_client.CONFIG_URL}/cnameRecords/www.local%2Cserver.local",
        )

        # Verify result
        assert result is True

    @patch("pihole_lib.dns.make_pihole_request")
    def test_remove_cname_record_not_found(self, mock_request, dns_client):
        """Test CNAME record removal when record not found."""
        # Mock 404 response for not found record
        mock_response = Mock()
        mock_response.status_code = 404
        mock_request.return_value = mock_response

        # Call method
        result = dns_client.remove_cname_record("nonexistent.local", "target.local")

        # Verify result
        assert result is False

    @patch("pihole_lib.dns.make_pihole_request")
    def test_get_blocking_status_success(self, mock_request, dns_client, mock_client):
        """Test successful DNS blocking status retrieval."""
        # Mock response data
        mock_response_data = {
            "blocking": "enabled",
            "timer": None,
            "took": 0.001,
        }
        mock_request.return_value.json.return_value = mock_response_data

        # Call method
        result = dns_client.get_blocking_status()

        # Verify request was made correctly
        mock_request.assert_called_once_with(
            mock_client,
            "GET",
            f"{dns_client.BASE_URL}/blocking",
        )

        # Verify result
        assert isinstance(result, DNSBlockingStatus)
        assert result.blocking == "enabled"
        assert result.timer is None
        assert result.took == 0.001

    @patch("pihole_lib.dns.make_pihole_request")
    def test_get_blocking_status_with_timer(self, mock_request, dns_client):
        """Test DNS blocking status retrieval with timer."""
        # Mock response data with timer
        mock_response_data = {
            "blocking": "disabled",
            "timer": 300,
            "took": 0.001,
        }
        mock_request.return_value.json.return_value = mock_response_data

        # Call method
        result = dns_client.get_blocking_status()

        # Verify result
        assert isinstance(result, DNSBlockingStatus)
        assert result.blocking == "disabled"
        assert result.timer == 300
        assert result.took == 0.001

    @patch("pihole_lib.dns.make_pihole_request")
    def test_get_blocking_status_api_error(self, mock_request, dns_client):
        """Test DNS blocking status retrieval with API error."""
        # Mock API error
        mock_request.side_effect = PiHoleAPIError("API request failed")

        # Call method and expect exception
        with pytest.raises(PiHoleAPIError, match="API request failed"):
            dns_client.get_blocking_status()

    @patch("pihole_lib.dns.make_pihole_request")
    def test_set_blocking_status_enable(self, mock_request, dns_client):
        """Test enabling DNS blocking."""
        # Mock response
        mock_response = Mock()
        mock_response.json.return_value = {
            "blocking": "enabled",
            "timer": None,
            "took": 0.002,
        }
        mock_request.return_value = mock_response

        # Call method
        result = dns_client.set_blocking_status(blocking=True)

        # Verify API call
        mock_request.assert_called_once_with(
            dns_client._client,
            "POST",
            f"{dns_client.BASE_URL}/blocking",
            json={"blocking": True},
        )

        # Verify result
        assert isinstance(result, DNSBlockingStatus)
        assert result.blocking == "enabled"
        assert result.timer is None
        assert result.took == 0.002

    @patch("pihole_lib.dns.make_pihole_request")
    def test_set_blocking_status_disable_with_timer(self, mock_request, dns_client):
        """Test disabling DNS blocking with timer."""
        # Mock response
        mock_response = Mock()
        mock_response.json.return_value = {
            "blocking": "disabled",
            "timer": 600,
            "took": 0.003,
        }
        mock_request.return_value = mock_response

        # Call method
        result = dns_client.set_blocking_status(blocking=False, timer=600)

        # Verify API call
        mock_request.assert_called_once_with(
            dns_client._client,
            "POST",
            f"{dns_client.BASE_URL}/blocking",
            json={"blocking": False, "timer": 600},
        )

        # Verify result
        assert isinstance(result, DNSBlockingStatus)
        assert result.blocking == "disabled"
        assert result.timer == 600
        assert result.took == 0.003

    @patch("pihole_lib.dns.make_pihole_request")
    def test_enable_blocking(self, mock_request, dns_client):
        """Test enable_blocking convenience method."""
        # Mock response
        mock_response = Mock()
        mock_response.json.return_value = {
            "blocking": "enabled",
            "timer": None,
            "took": 0.001,
        }
        mock_request.return_value = mock_response

        # Call method
        result = dns_client.enable_blocking()

        # Verify API call
        mock_request.assert_called_once_with(
            dns_client._client,
            "POST",
            f"{dns_client.BASE_URL}/blocking",
            json={"blocking": True},
        )

        # Verify result
        assert isinstance(result, DNSBlockingStatus)
        assert result.blocking == "enabled"
        assert result.timer is None

    @patch("pihole_lib.dns.make_pihole_request")
    def test_enable_blocking_with_timer(self, mock_request, dns_client):
        """Test enable_blocking with timer."""
        # Mock response
        mock_response = Mock()
        mock_response.json.return_value = {
            "blocking": "enabled",
            "timer": 3600,
            "took": 0.001,
        }
        mock_request.return_value = mock_response

        # Call method
        result = dns_client.enable_blocking(timer=3600)

        # Verify API call
        mock_request.assert_called_once_with(
            dns_client._client,
            "POST",
            f"{dns_client.BASE_URL}/blocking",
            json={"blocking": True, "timer": 3600},
        )

        # Verify result
        assert isinstance(result, DNSBlockingStatus)
        assert result.blocking == "enabled"
        assert result.timer == 3600

    @patch("pihole_lib.dns.make_pihole_request")
    def test_disable_blocking(self, mock_request, dns_client):
        """Test disable_blocking convenience method."""
        # Mock response
        mock_response = Mock()
        mock_response.json.return_value = {
            "blocking": "disabled",
            "timer": None,
            "took": 0.001,
        }
        mock_request.return_value = mock_response

        # Call method
        result = dns_client.disable_blocking()

        # Verify API call
        mock_request.assert_called_once_with(
            dns_client._client,
            "POST",
            f"{dns_client.BASE_URL}/blocking",
            json={"blocking": False},
        )

        # Verify result
        assert isinstance(result, DNSBlockingStatus)
        assert result.blocking == "disabled"
        assert result.timer is None

    @patch("pihole_lib.dns.make_pihole_request")
    def test_disable_blocking_with_timer(self, mock_request, dns_client):
        """Test disable_blocking with timer."""
        # Mock response
        mock_response = Mock()
        mock_response.json.return_value = {
            "blocking": "disabled",
            "timer": 300,
            "took": 0.001,
        }
        mock_request.return_value = mock_response

        # Call method
        result = dns_client.disable_blocking(timer=300)

        # Verify API call
        mock_request.assert_called_once_with(
            dns_client._client,
            "POST",
            f"{dns_client.BASE_URL}/blocking",
            json={"blocking": False, "timer": 300},
        )

        # Verify result
        assert isinstance(result, DNSBlockingStatus)
        assert result.blocking == "disabled"
        assert result.timer == 300

    def test_inheritance(self, dns_client):
        """Test that PiHoleDNS inherits from BasePiHoleAPIClient."""
        from pihole_lib.base import BasePiHoleAPIClient

        assert isinstance(dns_client, BasePiHoleAPIClient)

    @patch("pihole_lib.dns.make_pihole_request")
    def test_url_encoding(self, mock_request, dns_client, mock_client):
        """Test that special characters in domains/IPs are properly URL encoded."""
        # Mock successful response
        mock_response = Mock()
        mock_response.status_code = 201
        mock_request.return_value = mock_response

        # Test with domain containing special characters
        dns_client.add_a_record("test-server.local", "192.168.1.100")

        # Verify URL encoding
        mock_request.assert_called_with(
            mock_client,
            "PUT",
            f"{dns_client.CONFIG_URL}/hosts/192.168.1.100%20test-server.local",
        )

        # Reset mock
        mock_request.reset_mock()

        # Test CNAME with special characters
        dns_client.add_cname_record("www-test.local", "server-test.local")

        # Verify URL encoding for CNAME
        mock_request.assert_called_with(
            mock_client,
            "PUT",
            f"{dns_client.CONFIG_URL}/cnameRecords/www-test.local%2Cserver-test.local",
        )
