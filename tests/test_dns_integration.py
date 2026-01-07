"""Integration tests for PiHoleDNS class."""

import pytest

from pihole_lib import PiHoleClient, PiHoleDNS
from pihole_lib.exceptions import PiHoleAPIError
from pihole_lib.models import DNSBlockingStatus, DNSConfig, DNSRecord
from tests.constants import PIHOLE_BASE_URL, PIHOLE_TEST_PASSWORD


class TestPiHoleDNSIntegration:
    """Integration test cases for PiHoleDNS class."""

    @pytest.fixture
    def dns_client(self):
        """Create a PiHoleDNS instance for integration testing."""
        client = PiHoleClient(
            PIHOLE_BASE_URL, password=PIHOLE_TEST_PASSWORD, verify_ssl=False
        )
        client.__enter__()  # Authenticate
        dns = PiHoleDNS(client)
        yield dns
        client.__exit__(None, None, None)  # Clean up

    def test_get_config_integration(self, dns_client):
        """Test DNS configuration retrieval against real Pi-hole instance."""
        # Get DNS configuration
        result = dns_client.get_config()

        # Verify result structure
        assert isinstance(result, DNSConfig)
        assert hasattr(result, "upstreams")
        assert hasattr(result, "hosts")
        assert hasattr(result, "cname_records")
        assert hasattr(result, "port")
        assert hasattr(result, "query_logging")
        assert hasattr(result, "blocking")
        assert hasattr(result, "dnssec")

        # Validate data types
        assert isinstance(result.upstreams, list)
        assert isinstance(result.hosts, list)
        assert isinstance(result.cname_records, list)
        assert isinstance(result.port, int)
        assert isinstance(result.query_logging, bool)
        assert isinstance(result.blocking, dict)
        assert isinstance(result.dnssec, bool)

        # Verify reasonable values
        assert result.port > 0
        assert len(result.upstreams) > 0

        # Test blocking_active property
        assert isinstance(result.blocking_active, bool)

        # Verify all records are DNSRecord objects
        assert isinstance(result.records, list)
        for record in result.records:
            assert isinstance(record, DNSRecord)
            assert hasattr(record, "domain")
            assert hasattr(record, "target")
            assert hasattr(record, "record_type")
            assert isinstance(record.domain, str)
            assert isinstance(record.target, str)
            assert isinstance(record.record_type, str)
            assert record.record_type in ["A", "CNAME"]

        # Verify backward compatibility properties
        for host in result.hosts:
            assert isinstance(host, DNSRecord)
            assert host.record_type == "A"

        for cname in result.cname_records:
            assert isinstance(cname, DNSRecord)
            assert cname.record_type == "CNAME"

    def test_get_records_integration(self, dns_client):
        """Test DNS records retrieval against real Pi-hole instance."""
        # Get DNS records
        result = dns_client.get_records()

        # Verify result structure
        assert isinstance(result, list)

        # Each record should be a DNSRecord
        for record in result:
            assert isinstance(record, DNSRecord)
            assert hasattr(record, "domain")
            assert hasattr(record, "target")
            assert hasattr(record, "record_type")

            # Validate data types
            assert isinstance(record.domain, str)
            assert isinstance(record.target, str)
            assert isinstance(record.record_type, str)

            # Validate record type
            assert record.record_type in ["A", "CNAME"]

    def test_get_records_filter_integration(self, dns_client):
        """Test DNS records retrieval with type filtering against real Pi-hole instance."""
        # Get all records first
        all_records = dns_client.get_records()

        # Get A records only
        a_records = dns_client.get_records(record_type="A")

        # Get CNAME records only
        cname_records = dns_client.get_records(record_type="CNAME")

        # Verify filtering works correctly
        assert isinstance(a_records, list)
        assert isinstance(cname_records, list)

        # All A records should have record_type "A"
        for record in a_records:
            assert record.record_type == "A"

        # All CNAME records should have record_type "CNAME"
        for record in cname_records:
            assert record.record_type == "CNAME"

        # Combined filtered results should equal all records
        assert len(a_records) + len(cname_records) == len(all_records)

        # Verify that filtering doesn't change the actual record data
        all_a_records = [r for r in all_records if r.record_type == "A"]
        all_cname_records = [r for r in all_records if r.record_type == "CNAME"]

        assert len(a_records) == len(all_a_records)
        assert len(cname_records) == len(all_cname_records)

    def test_get_records_invalid_type_integration(self, dns_client):
        """Test DNS records retrieval with invalid type parameter."""
        # Test invalid type parameter
        with pytest.raises(ValueError, match="Invalid record type 'INVALID'"):
            dns_client.get_records(record_type="INVALID")

    def test_get_blocking_status_integration(self, dns_client):
        """Test DNS blocking status retrieval against real Pi-hole instance."""
        # Get blocking status
        result = dns_client.get_blocking_status()

        # Verify result structure
        assert isinstance(result, DNSBlockingStatus)
        assert hasattr(result, "blocking")
        assert hasattr(result, "timer")
        assert hasattr(result, "took")

        # Validate data types
        assert isinstance(result.blocking, str)
        assert result.timer is None or isinstance(result.timer, int)
        assert isinstance(result.took, float)

        # Validate blocking status
        assert result.blocking in ["enabled", "disabled"]

    def test_a_record_operations_integration(self, dns_client):
        """Test A record add/remove operations against real Pi-hole instance."""
        test_domain = "test-integration.local"
        test_ip = "192.168.99.100"

        try:
            # Add A record
            add_result = dns_client.add_a_record(test_domain, test_ip)
            assert add_result is True

            # Verify record was added by getting all records
            records = dns_client.get_records()
            a_records = [
                r for r in records if r.record_type == "A" and r.domain == test_domain
            ]
            assert len(a_records) == 1
            assert a_records[0].target == test_ip

        finally:
            # Clean up - remove the test record
            remove_result = dns_client.remove_a_record(test_domain, test_ip)
            assert remove_result is True

            # Verify record was removed
            records = dns_client.get_records()
            a_records = [
                r for r in records if r.record_type == "A" and r.domain == test_domain
            ]
            assert len(a_records) == 0

    def test_cname_record_operations_integration(self, dns_client):
        """Test CNAME record add/remove operations against real Pi-hole instance."""
        test_domain = "test-cname-integration.local"
        test_target = "target-integration.local"

        try:
            # Add CNAME record
            add_result = dns_client.add_cname_record(test_domain, test_target)
            assert add_result is True

            # Verify record was added by getting all records
            records = dns_client.get_records()
            cname_records = [
                r
                for r in records
                if r.record_type == "CNAME" and r.domain == test_domain
            ]
            assert len(cname_records) == 1
            assert cname_records[0].target == test_target

        finally:
            # Clean up - remove the test record
            remove_result = dns_client.remove_cname_record(test_domain, test_target)
            assert remove_result is True

            # Verify record was removed
            records = dns_client.get_records()
            cname_records = [
                r
                for r in records
                if r.record_type == "CNAME" and r.domain == test_domain
            ]
            assert len(cname_records) == 0

    def test_remove_nonexistent_records_integration(self, dns_client):
        """Test removing non-existent records against real Pi-hole instance."""
        # Try to remove non-existent A record
        try:
            result = dns_client.remove_a_record("nonexistent.local", "192.168.99.999")
            # Should return False for non-existent record
            assert result is False
        except PiHoleAPIError:
            # Pi-hole may return 404 for non-existent records, which is also acceptable
            pass

        # Try to remove non-existent CNAME record
        try:
            result = dns_client.remove_cname_record("nonexistent.local", "target.local")
            # Should return False for non-existent record
            assert result is False
        except PiHoleAPIError:
            # Pi-hole may return 404 for non-existent records, which is also acceptable
            pass

    def test_multiple_record_operations_integration(self, dns_client):
        """Test multiple record operations in sequence."""
        test_records = [
            ("test1.local", "192.168.99.101", "A"),
            ("test2.local", "192.168.99.102", "A"),
            ("alias1.local", "test1.local", "CNAME"),
            ("alias2.local", "test2.local", "CNAME"),
        ]

        try:
            # Add all test records
            for domain, target, record_type in test_records:
                if record_type == "A":
                    result = dns_client.add_a_record(domain, target)
                else:  # CNAME
                    result = dns_client.add_cname_record(domain, target)
                assert result is True

            # Verify all records were added
            records = dns_client.get_records()
            for domain, target, record_type in test_records:
                matching_records = [
                    r
                    for r in records
                    if r.domain == domain
                    and r.target == target
                    and r.record_type == record_type
                ]
                assert len(matching_records) == 1

        finally:
            # Clean up all test records
            for domain, target, record_type in test_records:
                if record_type == "A":
                    dns_client.remove_a_record(domain, target)
                else:  # CNAME
                    dns_client.remove_cname_record(domain, target)

    def test_dns_client_combination_integration(self, dns_client):
        """Test using DNS client with other operations."""
        # Get initial state
        initial_config = dns_client.get_config()
        initial_records = dns_client.get_records()
        initial_blocking = dns_client.get_blocking_status()

        # Verify we can get all information
        assert isinstance(initial_config, DNSConfig)
        assert isinstance(initial_records, list)
        assert isinstance(initial_blocking, DNSBlockingStatus)

        # Test that configuration is consistent
        config_hosts = initial_config.hosts
        config_cnames = initial_config.cname_records

        # Count records from get_records()
        a_record_count = len([r for r in initial_records if r.record_type == "A"])
        cname_record_count = len(
            [r for r in initial_records if r.record_type == "CNAME"]
        )

        # Should match configuration
        assert a_record_count == len(config_hosts)
        assert cname_record_count == len(config_cnames)

    def test_blocking_control_integration(self, dns_client):
        """Test DNS blocking control against real Pi-hole instance."""
        # Get initial blocking status
        initial_status = dns_client.get_blocking_status()
        assert isinstance(initial_status, DNSBlockingStatus)

        # Store initial state to restore later
        initial_blocking = initial_status.blocking == "enabled"

        try:
            # Test enabling blocking (should work regardless of current state)
            enabled_status = dns_client.enable_blocking()
            assert isinstance(enabled_status, DNSBlockingStatus)
            assert enabled_status.blocking == "enabled"
            assert enabled_status.timer is None  # Should be permanent

            # Verify status was actually changed
            current_status = dns_client.get_blocking_status()
            assert current_status.blocking == "enabled"

            # Test disabling blocking with timer (5 seconds)
            disabled_status = dns_client.disable_blocking(timer=5)
            assert isinstance(disabled_status, DNSBlockingStatus)
            assert disabled_status.blocking == "disabled"
            assert disabled_status.timer == 5

            # Verify status was actually changed
            current_status = dns_client.get_blocking_status()
            assert current_status.blocking == "disabled"
            assert isinstance(current_status.timer, int)
            assert current_status.timer <= 5  # Should be counting down

            # Test canceling timer by enabling permanently
            enabled_status = dns_client.enable_blocking()
            assert isinstance(enabled_status, DNSBlockingStatus)
            assert enabled_status.blocking == "enabled"
            assert enabled_status.timer is None  # Timer should be canceled

            # Test set_blocking_status directly
            disabled_status = dns_client.set_blocking_status(blocking=False, timer=3)
            assert isinstance(disabled_status, DNSBlockingStatus)
            assert disabled_status.blocking == "disabled"
            assert disabled_status.timer == 3

        finally:
            # Restore initial state
            if initial_blocking:
                dns_client.enable_blocking()
            else:
                dns_client.disable_blocking()

    def test_blocking_convenience_methods_integration(self, dns_client):
        """Test blocking convenience methods against real Pi-hole instance."""
        # Get initial state
        initial_status = dns_client.get_blocking_status()
        initial_blocking = initial_status.blocking == "enabled"

        try:
            # Test enable_blocking convenience method
            result = dns_client.enable_blocking()
            assert isinstance(result, DNSBlockingStatus)
            assert result.blocking == "enabled"

            # Test disable_blocking convenience method
            result = dns_client.disable_blocking()
            assert isinstance(result, DNSBlockingStatus)
            assert result.blocking == "disabled"

            # Test enable_blocking with timer
            result = dns_client.enable_blocking(timer=2)
            assert isinstance(result, DNSBlockingStatus)
            assert result.blocking == "enabled"
            assert result.timer == 2

            # Test disable_blocking with timer
            result = dns_client.disable_blocking(timer=2)
            assert isinstance(result, DNSBlockingStatus)
            assert result.blocking == "disabled"
            assert result.timer == 2

        finally:
            # Restore initial state
            if initial_blocking:
                dns_client.enable_blocking()
            else:
                dns_client.disable_blocking()

    def test_constants_usage(self, dns_client):
        """Test that the class uses the correct API endpoint constants."""
        assert dns_client.BASE_URL == "/api/dns"
        assert dns_client.CONFIG_URL == "/api/config/dns"
