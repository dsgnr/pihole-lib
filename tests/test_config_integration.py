"""Integration tests for PiHoleConfig class."""

import pytest

from pihole_lib import PiHoleClient, PiHoleConfig

from .constants import PIHOLE_BASE_URL, PIHOLE_TEST_PASSWORD


@pytest.mark.integration
class TestPiHoleConfigIntegration:
    """Integration tests for PiHoleConfig class."""

    def test_get_config_basic(self, pihole_container):
        """Test basic config retrieval against real Pi-hole instance."""
        with PiHoleClient(
            PIHOLE_BASE_URL, password=PIHOLE_TEST_PASSWORD, verify_ssl=False
        ) as client:
            config = PiHoleConfig(client)

            # Get configuration
            config_data = config.get_config()

            # Verify response structure
            assert isinstance(config_data, dict)

            # Verify expected top-level sections exist
            expected_sections = ["dns", "dhcp", "webserver", "files", "misc"]
            for section in expected_sections:
                assert section in config_data, f"Missing section: {section}"

    def test_get_config_dns_section(self, pihole_container):
        """Test DNS configuration section against real Pi-hole instance."""
        with PiHoleClient(
            PIHOLE_BASE_URL, password=PIHOLE_TEST_PASSWORD, verify_ssl=False
        ) as client:
            config = PiHoleConfig(client)

            config_data = config.get_config()
            dns_config = config_data["dns"]

            # Verify DNS section structure
            assert isinstance(dns_config, dict)
            assert "upstreams" in dns_config
            assert "queryLogging" in dns_config
            assert "port" in dns_config

            # Verify data types
            assert isinstance(dns_config["upstreams"], list)
            assert isinstance(dns_config["queryLogging"], bool)
            assert isinstance(dns_config["port"], int)

            # Verify reasonable values
            assert dns_config["port"] > 0
            assert len(dns_config["upstreams"]) >= 0

    def test_get_config_dhcp_section(self, pihole_container):
        """Test DHCP configuration section against real Pi-hole instance."""
        with PiHoleClient(
            PIHOLE_BASE_URL, password=PIHOLE_TEST_PASSWORD, verify_ssl=False
        ) as client:
            config = PiHoleConfig(client)

            config_data = config.get_config()
            dhcp_config = config_data["dhcp"]

            # Verify DHCP section structure
            assert isinstance(dhcp_config, dict)
            assert "active" in dhcp_config

            # Verify data types
            assert isinstance(dhcp_config["active"], bool)

    def test_get_config_webserver_section(self, pihole_container):
        """Test webserver configuration section against real Pi-hole instance."""
        with PiHoleClient(
            PIHOLE_BASE_URL, password=PIHOLE_TEST_PASSWORD, verify_ssl=False
        ) as client:
            config = PiHoleConfig(client)

            config_data = config.get_config()
            web_config = config_data["webserver"]

            # Verify webserver section structure
            assert isinstance(web_config, dict)
            assert "domain" in web_config

            # Verify data types
            assert isinstance(web_config["domain"], str)
            assert len(web_config["domain"]) > 0

    def test_get_config_data_access_patterns(self, pihole_container):
        """Test common data access patterns with real Pi-hole config."""
        with PiHoleClient(
            PIHOLE_BASE_URL, password=PIHOLE_TEST_PASSWORD, verify_ssl=False
        ) as client:
            config = PiHoleConfig(client)

            config_data = config.get_config()

            # Test safe access patterns that should work with any Pi-hole config
            dns_upstreams = config_data.get("dns", {}).get("upstreams", [])
            assert isinstance(dns_upstreams, list)

            dhcp_active = config_data.get("dhcp", {}).get("active", False)
            assert isinstance(dhcp_active, bool)

            web_domain = config_data.get("webserver", {}).get("domain", "")
            assert isinstance(web_domain, str)
