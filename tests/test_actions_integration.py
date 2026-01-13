"""Integration tests for PiHoleActions."""

import pytest

from pihole_lib import PiHoleActions
from tests.conftest import integration


@integration
class TestPiHoleActions:
    """Integration tests for PiHoleActions against a real Pi-hole instance."""

    @staticmethod
    def _assert_gravity_output(lines):
        """Common assertions for gravity update output."""
        assert lines, "Expected gravity update to produce output"
        output = "\n".join(lines)
        assert "DNS resolution is available" in output
        assert "Done." in output
        assert all(line.strip() for line in lines), "Empty lines found in output"

    @pytest.mark.parametrize("color", [False, True])
    def test_update_gravity(self, pihole_client, color):
        """Gravity update with and without color."""
        actions = PiHoleActions(pihole_client)
        lines = list(actions.update_gravity(color=color))
        self._assert_gravity_output(lines)

    def test_update_gravity_streaming(self, pihole_client):
        """Verify gravity output is streamed progressively."""
        actions = PiHoleActions(pihole_client)
        received = []

        for line in actions.update_gravity():
            assert isinstance(line, str)
            assert line.strip()
            received.append(line)
            if len(received) >= 3:
                break

        assert len(received) >= 3, "Expected streamed output, got too few lines"

    @pytest.mark.parametrize("method", ["restart_dns", "flush_logs", "flush_network"])
    def test_action_methods(self, pihole_client, method):
        """Test action methods return True on success."""
        actions = PiHoleActions(pihole_client)
        result = getattr(actions, method)()
        assert result is True

    def test_base_url_constant(self, pihole_client):
        """Ensure correct API base path is used."""
        actions = PiHoleActions(pihole_client)
        assert actions.BASE_URL == "/api/action"
