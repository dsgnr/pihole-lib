"""Integration tests for PiHoleActions class."""

import pytest

from pihole_lib import PiHoleActions, PiHoleClient

from .constants import PIHOLE_BASE_URL, PIHOLE_TEST_PASSWORD


@pytest.mark.integration
class TestPiHoleActionsIntegration:
    """Integration tests for PiHoleActions class."""

    def test_update_gravity_basic(self, pihole_container):
        """Test basic gravity update against real Pi-hole instance."""
        with PiHoleClient(
            PIHOLE_BASE_URL, password=PIHOLE_TEST_PASSWORD, verify_ssl=False
        ) as client:
            actions = PiHoleActions(client)

            # Collect all output lines
            lines = list(actions.update_gravity())

            # Verify we got some output
            assert len(lines) > 0

            # Verify typical gravity update output patterns
            output_text = "\n".join(lines)
            assert "DNS resolution is available" in output_text
            assert "Done." in output_text

            # Verify no empty lines made it through
            assert all(line.strip() for line in lines)

    def test_update_gravity_with_color(self, pihole_container):
        """Test gravity update with color parameter against real Pi-hole instance."""
        with PiHoleClient(
            PIHOLE_BASE_URL, password=PIHOLE_TEST_PASSWORD, verify_ssl=False
        ) as client:
            actions = PiHoleActions(client)

            # Collect all output lines with color
            lines = list(actions.update_gravity(color=True))

            # Verify we got some output
            assert len(lines) > 0

            # Verify typical gravity update output patterns
            output_text = "\n".join(lines)
            assert "DNS resolution is available" in output_text
            assert "Done." in output_text

            # Verify no empty lines made it through
            assert all(line.strip() for line in lines)

    def test_update_gravity_without_color(self, pihole_container):
        """Test gravity update without color parameter against real Pi-hole instance."""
        with PiHoleClient(
            PIHOLE_BASE_URL, password=PIHOLE_TEST_PASSWORD, verify_ssl=False
        ) as client:
            actions = PiHoleActions(client)

            # Collect all output lines without color
            lines = list(actions.update_gravity(color=False))

            # Verify we got some output
            assert len(lines) > 0

            # Verify typical gravity update output patterns
            output_text = "\n".join(lines)
            assert "DNS resolution is available" in output_text
            assert "Done." in output_text

    def test_update_gravity_streaming_behavior(self, pihole_container):
        """Test that gravity update streams output progressively."""
        with PiHoleClient(
            PIHOLE_BASE_URL, password=PIHOLE_TEST_PASSWORD, verify_ssl=False
        ) as client:
            actions = PiHoleActions(client)

            # Test that we can iterate through the output
            line_count = 0
            for line in actions.update_gravity():
                assert isinstance(line, str)
                assert line.strip()  # No empty lines
                line_count += 1

                # Break early to test streaming behavior
                if line_count >= 3:
                    break

            # Verify we got at least some lines
            assert line_count >= 3

    def test_multiple_gravity_updates(self, pihole_container):
        """Test multiple consecutive gravity updates."""
        with PiHoleClient(
            PIHOLE_BASE_URL, password=PIHOLE_TEST_PASSWORD, verify_ssl=False
        ) as client:
            actions = PiHoleActions(client)

            # First update
            lines1 = list(actions.update_gravity())
            assert len(lines1) > 0

            # Second update (should work without issues)
            lines2 = list(actions.update_gravity())
            assert len(lines2) > 0

            # Both should have similar structure
            output1 = "\n".join(lines1)
            output2 = "\n".join(lines2)

            assert "DNS resolution is available" in output1
            assert "DNS resolution is available" in output2
            assert "Done." in output1
            assert "Done." in output2

    def test_restart_dns_basic(self, pihole_container):
        """Test basic DNS restart against real Pi-hole instance."""
        with PiHoleClient(
            PIHOLE_BASE_URL, password=PIHOLE_TEST_PASSWORD, verify_ssl=False
        ) as client:
            actions = PiHoleActions(client)

            # Restart DNS service
            result = actions.restart_dns()

            # Verify response
            assert isinstance(result, bool)
            assert result is True  # Should be successful

    def test_actions_combination(self, pihole_container):
        """Test using multiple action methods together."""
        with PiHoleClient(
            PIHOLE_BASE_URL, password=PIHOLE_TEST_PASSWORD, verify_ssl=False
        ) as client:
            actions = PiHoleActions(client)

            # Restart DNS first
            restart_result = actions.restart_dns()
            assert restart_result is True

            # Then update gravity (just get first few lines to avoid long wait)
            gravity_lines = []
            for i, line in enumerate(actions.update_gravity()):
                gravity_lines.append(line)
                if i >= 2:  # Just get first few lines
                    break

            assert len(gravity_lines) > 0
            assert all(isinstance(line, str) for line in gravity_lines)
