"""Unit tests for PiHoleDNS."""

from unittest.mock import Mock, patch

import pytest

from pihole_lib import PiHoleDNS
from pihole_lib.exceptions import PiHoleAPIError
from pihole_lib.models.dns import DNSBlockingStatus, DNSConfig
from tests.conftest import make_mock_response


@pytest.fixture
def dns_client(mock_client):
    """Create a PiHoleDNS instance for testing."""
    return PiHoleDNS(mock_client)


@pytest.fixture
def mock_dns_config_data():
    """Sample DNS configuration data."""
    return {
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


class TestPiHoleDNSGetConfig:
    """Test DNS configuration retrieval."""

    @patch("pihole_lib.dns.PiHoleConfig")
    def test_get_config_success(
        self, mock_config_class, dns_client, mock_client, mock_dns_config_data
    ):
        """Test successful DNS configuration retrieval."""
        mock_config_instance = Mock()
        mock_config_class.return_value = mock_config_instance
        mock_config_instance.get_config.return_value = mock_dns_config_data

        result = dns_client.get_config()

        mock_config_class.assert_called_once_with(mock_client)
        mock_config_instance.get_config.assert_called_once_with("dns")
        assert isinstance(result, DNSConfig)
        assert result.upstreams == ["8.8.8.8", "8.8.4.4"]
        assert len(result.records) == 2
        assert result.blocking_active is True

    @patch("pihole_lib.dns.PiHoleConfig")
    def test_get_config_api_error(self, mock_config_class, dns_client):
        """Test DNS configuration retrieval with API error."""
        mock_config_instance = Mock()
        mock_config_class.return_value = mock_config_instance
        mock_config_instance.get_config.side_effect = PiHoleAPIError(
            "API request failed"
        )

        with pytest.raises(PiHoleAPIError, match="API request failed"):
            dns_client.get_config()


class TestPiHoleDNSGetRecords:
    """Test DNS records retrieval."""

    @patch("pihole_lib.dns.PiHoleConfig")
    def test_get_records_success(
        self, mock_config_class, dns_client, mock_dns_config_data
    ):
        """Test successful DNS records retrieval."""
        mock_config_instance = Mock()
        mock_config_class.return_value = mock_config_instance
        mock_config_instance.get_config.return_value = mock_dns_config_data

        result = dns_client.get_records()

        assert len(result) == 2
        a_records = [r for r in result if r.record_type == "A"]
        cname_records = [r for r in result if r.record_type == "CNAME"]
        assert len(a_records) == 1
        assert len(cname_records) == 1

    @pytest.mark.parametrize(
        "record_type,expected_count",
        [
            ("A", 1),
            ("CNAME", 1),
        ],
    )
    @patch("pihole_lib.dns.PiHoleConfig")
    def test_get_records_filter(
        self,
        mock_config_class,
        dns_client,
        mock_dns_config_data,
        record_type,
        expected_count,
    ):
        """Test DNS records retrieval with type filtering."""
        mock_config_instance = Mock()
        mock_config_class.return_value = mock_config_instance
        mock_config_instance.get_config.return_value = mock_dns_config_data

        result = dns_client.get_records(record_type=record_type)

        assert len(result) == expected_count
        for record in result:
            assert record.record_type == record_type

    @patch("pihole_lib.dns.PiHoleConfig")
    def test_get_records_invalid_type(self, mock_config_class, dns_client):
        """Test DNS records retrieval with invalid type parameter."""
        with pytest.raises(ValueError, match="Invalid record type 'INVALID'"):
            dns_client.get_records(record_type="INVALID")


class TestPiHoleDNSRecordOperations:
    """Test DNS record add/remove operations."""

    @pytest.mark.parametrize(
        "method,record_type,domain,target,endpoint_suffix,status_code,expected_result",
        [
            # Add operations - success returns 201
            (
                "add_a_record",
                "A",
                "server.local",
                "192.168.1.100",
                "hosts/192.168.1.100%20server.local",
                201,
                True,
            ),
            (
                "add_a_record",
                "A",
                "server.local",
                "192.168.1.100",
                "hosts/192.168.1.100%20server.local",
                400,
                False,
            ),
            (
                "add_a_record",
                "A",
                "server.local",
                "192.168.1.100",
                "hosts/192.168.1.100%20server.local",
                404,
                False,
            ),
            (
                "add_cname_record",
                "CNAME",
                "www.local",
                "server.local",
                "cnameRecords/www.local%2Cserver.local",
                201,
                True,
            ),
            (
                "add_cname_record",
                "CNAME",
                "www.local",
                "server.local",
                "cnameRecords/www.local%2Cserver.local",
                400,
                False,
            ),
            (
                "add_cname_record",
                "CNAME",
                "www.local",
                "server.local",
                "cnameRecords/www.local%2Cserver.local",
                404,
                False,
            ),
            # Remove operations - success returns 204
            (
                "remove_a_record",
                "A",
                "server.local",
                "192.168.1.100",
                "hosts/192.168.1.100%20server.local",
                204,
                True,
            ),
            (
                "remove_a_record",
                "A",
                "server.local",
                "192.168.1.100",
                "hosts/192.168.1.100%20server.local",
                400,
                False,
            ),
            (
                "remove_a_record",
                "A",
                "server.local",
                "192.168.1.100",
                "hosts/192.168.1.100%20server.local",
                404,
                False,
            ),
            (
                "remove_cname_record",
                "CNAME",
                "www.local",
                "server.local",
                "cnameRecords/www.local%2Cserver.local",
                204,
                True,
            ),
            (
                "remove_cname_record",
                "CNAME",
                "www.local",
                "server.local",
                "cnameRecords/www.local%2Cserver.local",
                400,
                False,
            ),
            (
                "remove_cname_record",
                "CNAME",
                "www.local",
                "server.local",
                "cnameRecords/www.local%2Cserver.local",
                404,
                False,
            ),
        ],
    )
    @patch("pihole_lib.dns.make_pihole_request")
    def test_record_operations(
        self,
        mock_request,
        dns_client,
        mock_client,
        method,
        record_type,
        domain,
        target,
        endpoint_suffix,
        status_code,
        expected_result,
    ):
        """Test record add/remove operations with various responses."""
        mock_request.return_value = make_mock_response(status_code=status_code)

        result = getattr(dns_client, method)(domain, target)

        assert result is expected_result

    @patch("pihole_lib.dns.make_pihole_request")
    def test_add_a_record_api_error(self, mock_request, dns_client):
        """Test A record addition with API error."""
        mock_request.side_effect = PiHoleAPIError("Invalid domain")

        with pytest.raises(PiHoleAPIError, match="Invalid domain"):
            dns_client.add_a_record("invalid..domain", "192.168.1.100")


class TestPiHoleDNSBlockingStatus:
    """Test DNS blocking status operations."""

    @patch("pihole_lib.dns.make_pihole_request")
    def test_get_blocking_status_success(self, mock_request, dns_client, mock_client):
        """Test successful DNS blocking status retrieval."""
        mock_request.return_value = make_mock_response(
            json_data={
                "blocking": "enabled",
                "timer": None,
                "took": 0.001,
            }
        )

        result = dns_client.get_blocking_status()

        mock_request.assert_called_once_with(
            mock_client, "GET", f"{dns_client.BASE_URL}/blocking"
        )
        assert isinstance(result, DNSBlockingStatus)
        assert result.blocking == "enabled"
        assert result.timer is None

    @pytest.mark.parametrize(
        "blocking,timer,expected_json",
        [
            (True, None, {"blocking": True}),
            (False, None, {"blocking": False}),
            (False, 600, {"blocking": False, "timer": 600}),
            (True, 3600, {"blocking": True, "timer": 3600}),
        ],
    )
    @patch("pihole_lib.dns.make_pihole_request")
    def test_set_blocking_status(
        self, mock_request, dns_client, blocking, timer, expected_json
    ):
        """Test setting DNS blocking status with various parameters."""
        mock_request.return_value = make_mock_response(
            json_data={
                "blocking": "enabled" if blocking else "disabled",
                "timer": timer,
                "took": 0.002,
            }
        )

        result = dns_client.set_blocking_status(blocking=blocking, timer=timer)

        mock_request.assert_called_once_with(
            dns_client._client,
            "POST",
            f"{dns_client.BASE_URL}/blocking",
            json=expected_json,
        )
        assert isinstance(result, DNSBlockingStatus)

    @pytest.mark.parametrize(
        "method,blocking,timer",
        [
            ("enable_blocking", True, None),
            ("enable_blocking", True, 3600),
            ("disable_blocking", False, None),
            ("disable_blocking", False, 300),
        ],
    )
    @patch("pihole_lib.dns.make_pihole_request")
    def test_convenience_methods(
        self, mock_request, dns_client, method, blocking, timer
    ):
        """Test enable_blocking and disable_blocking convenience methods."""
        mock_request.return_value = make_mock_response(
            json_data={
                "blocking": "enabled" if blocking else "disabled",
                "timer": timer,
                "took": 0.001,
            }
        )

        if timer:
            result = getattr(dns_client, method)(timer=timer)
        else:
            result = getattr(dns_client, method)()

        assert isinstance(result, DNSBlockingStatus)


class TestPiHoleDNSInheritance:
    """Test class inheritance and constants."""

    def test_inheritance(self, dns_client):
        """Test that PiHoleDNS inherits from BasePiHoleAPIClient."""
        from pihole_lib.base import BasePiHoleAPIClient

        assert isinstance(dns_client, BasePiHoleAPIClient)

    def test_constants(self, dns_client):
        """Test that the class uses correct API endpoint constants."""
        assert dns_client.BASE_URL == "/api/dns"
        assert dns_client.CONFIG_URL == "/api/config/dns"
