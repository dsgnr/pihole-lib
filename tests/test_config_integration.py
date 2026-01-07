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


class TestPiHoleConfigElementIntegration:
    """Integration tests for PiHoleConfig element filtering."""

    def test_get_config_dns_element(self, pihole_container):
        """Test DNS element retrieval against real Pi-hole instance."""
        with PiHoleClient(
            PIHOLE_BASE_URL, password=PIHOLE_TEST_PASSWORD, verify_ssl=False
        ) as client:
            config = PiHoleConfig(client)

            # Get DNS configuration only
            dns_config = config.get_config("dns")

            # Verify response structure
            assert isinstance(dns_config, dict)
            assert "dns" in dns_config

            # Should only contain DNS section
            dns_section = dns_config["dns"]
            assert isinstance(dns_section, dict)
            assert "upstreams" in dns_section
            assert "queryLogging" in dns_section
            assert "port" in dns_section

    def test_get_config_dns_upstreams_element(self, pihole_container):
        """Test DNS upstreams element retrieval against real Pi-hole instance."""
        with PiHoleClient(
            PIHOLE_BASE_URL, password=PIHOLE_TEST_PASSWORD, verify_ssl=False
        ) as client:
            config = PiHoleConfig(client)

            # Get DNS upstreams only
            upstreams_config = config.get_config("dns/upstreams")

            # Verify response structure
            assert isinstance(upstreams_config, dict)
            assert "dns" in upstreams_config
            assert "upstreams" in upstreams_config["dns"]

            # Verify data type
            upstreams = upstreams_config["dns"]["upstreams"]
            assert isinstance(upstreams, list)

    def test_get_config_dhcp_element(self, pihole_container):
        """Test DHCP element retrieval against real Pi-hole instance."""
        with PiHoleClient(
            PIHOLE_BASE_URL, password=PIHOLE_TEST_PASSWORD, verify_ssl=False
        ) as client:
            config = PiHoleConfig(client)

            # Get DHCP configuration only
            dhcp_config = config.get_config("dhcp")

            # Verify response structure
            assert isinstance(dhcp_config, dict)
            assert "dhcp" in dhcp_config

            # Should only contain DHCP section
            dhcp_section = dhcp_config["dhcp"]
            assert isinstance(dhcp_section, dict)
            assert "active" in dhcp_section

    def test_get_config_webserver_element(self, pihole_container):
        """Test webserver element retrieval against real Pi-hole instance."""
        with PiHoleClient(
            PIHOLE_BASE_URL, password=PIHOLE_TEST_PASSWORD, verify_ssl=False
        ) as client:
            config = PiHoleConfig(client)

            # Get webserver configuration only
            web_config = config.get_config("webserver")

            # Verify response structure
            assert isinstance(web_config, dict)
            assert "webserver" in web_config

            # Should only contain webserver section
            web_section = web_config["webserver"]
            assert isinstance(web_section, dict)
            assert "domain" in web_section

    def test_get_config_element_vs_full_consistency(self, pihole_container):
        """Test that element retrieval matches full config data."""
        with PiHoleClient(
            PIHOLE_BASE_URL, password=PIHOLE_TEST_PASSWORD, verify_ssl=False
        ) as client:
            config = PiHoleConfig(client)

            # Get full config and DNS element separately
            full_config = config.get_config()
            dns_element = config.get_config("dns")

            # Verify DNS section matches
            assert full_config["dns"] == dns_element["dns"]

            # Get DHCP element and verify it matches
            dhcp_element = config.get_config("dhcp")
            assert full_config["dhcp"] == dhcp_element["dhcp"]

    def test_constants_usage(self, pihole_container):
        """Test that the class uses the correct API endpoint constants."""
        with PiHoleClient(
            PIHOLE_BASE_URL, password=PIHOLE_TEST_PASSWORD, verify_ssl=False
        ) as client:
            config = PiHoleConfig(client)
            assert config.BASE_URL == "/api/config"
