"""Integration tests for PiHoleConfig class."""

import pytest

from pihole_lib import PiHoleClient, PiHoleConfig
from pihole_lib.exceptions import PiHoleAPIError

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


class TestPiHoleConfigUpdateIntegration:
    """Integration tests for PiHoleConfig update methods."""

    def test_update_config_dns_upstreams(self, pihole_container):
        """Test updating DNS upstreams configuration."""
        with PiHoleClient(
            PIHOLE_BASE_URL, password=PIHOLE_TEST_PASSWORD, verify_ssl=False
        ) as client:
            config = PiHoleConfig(client)

            # Get original configuration
            original_config = config.get_config("dns/upstreams")
            original_upstreams = original_config["dns"]["upstreams"]

            # Update with new upstreams
            new_upstreams = ["1.1.1.1", "1.0.0.1"]
            update_config = {"dns": {"upstreams": new_upstreams}}

            updated_config = config.update_config(update_config)

            # Verify the update was applied
            assert "dns" in updated_config
            assert updated_config["dns"]["upstreams"] == new_upstreams

            # Verify by getting config again
            current_config = config.get_config("dns/upstreams")
            assert current_config["dns"]["upstreams"] == new_upstreams

            # Restore original configuration
            restore_config = {"dns": {"upstreams": original_upstreams}}
            config.update_config(restore_config)

    def test_update_config_dns_query_logging(self, pihole_container):
        """Test updating DNS query logging configuration."""
        with PiHoleClient(
            PIHOLE_BASE_URL, password=PIHOLE_TEST_PASSWORD, verify_ssl=False
        ) as client:
            config = PiHoleConfig(client)

            # Get original configuration
            original_config = config.get_config("dns")
            original_logging = original_config["dns"]["queryLogging"]

            # Toggle query logging
            new_logging = not original_logging
            update_config = {"dns": {"queryLogging": new_logging}}

            updated_config = config.update_config(update_config)

            # Verify the update was applied
            assert updated_config["dns"]["queryLogging"] == new_logging

            # Restore original configuration
            restore_config = {"dns": {"queryLogging": original_logging}}
            config.update_config(restore_config)

    def test_update_config_no_restart(self, pihole_container):
        """Test updating configuration without restart."""
        with PiHoleClient(
            PIHOLE_BASE_URL, password=PIHOLE_TEST_PASSWORD, verify_ssl=False
        ) as client:
            config = PiHoleConfig(client)

            # Get original configuration
            original_config = config.get_config("dns/upstreams")
            original_upstreams = original_config["dns"]["upstreams"]

            # Update without restart
            new_upstreams = ["8.8.8.8", "8.8.4.4"]
            update_config = {"dns": {"upstreams": new_upstreams}}

            updated_config = config.update_config(update_config, restart=False)

            # Verify the update was applied
            assert updated_config["dns"]["upstreams"] == new_upstreams

            # Restore original configuration with restart
            restore_config = {"dns": {"upstreams": original_upstreams}}
            config.update_config(restore_config, restart=True)

    def test_update_config_multiple_sections(self, pihole_container):
        """Test updating multiple configuration sections at once."""
        with PiHoleClient(
            PIHOLE_BASE_URL, password=PIHOLE_TEST_PASSWORD, verify_ssl=False
        ) as client:
            config = PiHoleConfig(client)

            # Get original configurations
            original_dns = config.get_config("dns")
            original_upstreams = original_dns["dns"]["upstreams"]
            original_logging = original_dns["dns"]["queryLogging"]

            # Update multiple sections
            new_upstreams = ["9.9.9.9", "149.112.112.112"]
            new_logging = not original_logging

            update_config = {
                "dns": {
                    "upstreams": new_upstreams,
                    "queryLogging": new_logging,
                }
            }

            updated_config = config.update_config(update_config)

            # Verify both updates were applied
            assert updated_config["dns"]["upstreams"] == new_upstreams
            assert updated_config["dns"]["queryLogging"] == new_logging

            # Restore original configuration
            restore_config = {
                "dns": {
                    "upstreams": original_upstreams,
                    "queryLogging": original_logging,
                }
            }
            config.update_config(restore_config)


class TestPiHoleConfigItemManagementIntegration:
    """Integration tests for PiHoleConfig item management methods."""

    def test_add_remove_upstream_dns_server(self, pihole_container):
        """Test adding and removing upstream DNS servers."""
        with PiHoleClient(
            PIHOLE_BASE_URL, password=PIHOLE_TEST_PASSWORD, verify_ssl=False
        ) as client:
            config = PiHoleConfig(client)

            # Get original upstreams
            original_config = config.get_config("dns/upstreams")
            original_upstreams = original_config["dns"]["upstreams"]

            # Add a new upstream
            test_upstream = "1.1.1.1"
            if test_upstream not in original_upstreams:
                success = config.add_config_item("dns/upstreams", test_upstream)
                assert success is True

                # Verify it was added
                current_config = config.get_config("dns/upstreams")
                current_upstreams = current_config["dns"]["upstreams"]
                assert test_upstream in current_upstreams

                # Remove the upstream
                success = config.remove_config_item("dns/upstreams", test_upstream)
                assert success is True

                # Verify it was removed
                final_config = config.get_config("dns/upstreams")
                final_upstreams = final_config["dns"]["upstreams"]
                assert test_upstream not in final_upstreams

    def test_add_remove_dns_host_entry(self, pihole_container):
        """Test adding and removing DNS host entries."""
        with PiHoleClient(
            PIHOLE_BASE_URL, password=PIHOLE_TEST_PASSWORD, verify_ssl=False
        ) as client:
            config = PiHoleConfig(client)

            # Get original hosts
            original_config = config.get_config("dns")
            original_hosts = original_config["dns"]["hosts"]

            # Add a new host entry
            test_host = "192.168.1.100 testserver.local"
            if test_host not in original_hosts:
                success = config.add_config_item("dns/hosts", test_host)
                assert success is True

                # Verify it was added
                current_config = config.get_config("dns")
                current_hosts = current_config["dns"]["hosts"]
                assert test_host in current_hosts

                # Remove the host entry
                success = config.remove_config_item("dns/hosts", test_host)
                assert success is True

                # Verify it was removed
                final_config = config.get_config("dns")
                final_hosts = final_config["dns"]["hosts"]
                assert test_host not in final_hosts

    def test_add_remove_config_item_no_restart(self, pihole_container):
        """Test adding and removing config items without restart."""
        with PiHoleClient(
            PIHOLE_BASE_URL, password=PIHOLE_TEST_PASSWORD, verify_ssl=False
        ) as client:
            config = PiHoleConfig(client)

            # Get original upstreams
            original_config = config.get_config("dns/upstreams")
            original_upstreams = original_config["dns"]["upstreams"]

            # Add upstream without restart
            test_upstream = "8.8.8.8"
            if test_upstream not in original_upstreams:
                success = config.add_config_item(
                    "dns/upstreams", test_upstream, restart=False
                )
                assert success is True

                # Remove upstream without restart
                success = config.remove_config_item(
                    "dns/upstreams", test_upstream, restart=False
                )
                assert success is True

    def test_add_config_item_special_characters(self, pihole_container):
        """Test adding config items with special characters."""
        with PiHoleClient(
            PIHOLE_BASE_URL, password=PIHOLE_TEST_PASSWORD, verify_ssl=False
        ) as client:
            config = PiHoleConfig(client)

            # Test with host entry containing spaces
            test_host = "192.168.1.200 test-server.example.com"

            # Add the host entry
            success = config.add_config_item("dns/hosts", test_host)
            assert success is True

            # Verify it was added
            current_config = config.get_config("dns")
            current_hosts = current_config["dns"]["hosts"]
            assert test_host in current_hosts

            # Remove the host entry
            success = config.remove_config_item("dns/hosts", test_host)
            assert success is True

            # Verify it was removed
            final_config = config.get_config("dns")
            final_hosts = final_config["dns"]["hosts"]
            assert test_host not in final_hosts

    def test_remove_nonexistent_config_item(self, pihole_container):
        """Test removing a config item that doesn't exist."""
        with PiHoleClient(
            PIHOLE_BASE_URL, password=PIHOLE_TEST_PASSWORD, verify_ssl=False
        ) as client:
            config = PiHoleConfig(client)

            # Try to remove a non-existent upstream - should raise an exception
            with pytest.raises(PiHoleAPIError, match="Endpoint not found"):
                config.remove_config_item("dns/upstreams", "999.999.999.999")

    def test_config_with_property_access(self, pihole_container):
        """Test configuration management using property access on PiHoleClient."""
        with PiHoleClient(
            PIHOLE_BASE_URL, password=PIHOLE_TEST_PASSWORD, verify_ssl=False
        ) as client:
            # Get configuration using property access
            config_data = client.config.get_config()
            assert isinstance(config_data, dict)
            assert "dns" in config_data

            # Get DNS configuration
            dns_config = client.config.get_config("dns")
            assert "dns" in dns_config

            # Update configuration
            original_upstreams = dns_config["dns"]["upstreams"]
            new_upstreams = ["1.1.1.1", "1.0.0.1"]

            if original_upstreams != new_upstreams:
                update_config = {"dns": {"upstreams": new_upstreams}}
                updated_config = client.config.update_config(update_config)
                assert updated_config["dns"]["upstreams"] == new_upstreams

                # Restore original
                restore_config = {"dns": {"upstreams": original_upstreams}}
                client.config.update_config(restore_config)
