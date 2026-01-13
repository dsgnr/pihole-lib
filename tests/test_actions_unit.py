"""Unit tests for PiHoleActions."""

from unittest.mock import Mock, patch

import pytest

from pihole_lib import PiHoleActions
from tests.conftest import EXCEPTION_TEST_CASES, make_mock_response


@pytest.fixture
def actions_client(mock_client):
    """Create a PiHoleActions instance with mock client."""
    return PiHoleActions(mock_client)


class TestPiHoleActionsInit:
    """Test PiHoleActions initialization."""

    def test_init_with_client(self, mock_client):
        """Test initialization with a client."""
        actions = PiHoleActions(mock_client)
        assert actions._client is mock_client


class TestUpdateGravity:
    """Test update_gravity method."""

    @pytest.fixture
    def mock_gravity_response(self):
        """Create a mock streaming response for gravity update."""
        response = Mock()
        response.iter_lines.return_value = [
            "  [✓] DNS resolution is available",
            "  [i] Neutrino emissions detected...",
            "  [✓] Done.",
        ]
        return response

    @patch("pihole_lib.actions.make_pihole_request")
    def test_update_gravity_basic(
        self, mock_request, actions_client, mock_gravity_response
    ):
        """Test basic gravity update without color."""
        mock_request.return_value = mock_gravity_response

        lines = list(actions_client.update_gravity())

        mock_request.assert_called_once_with(
            actions_client._client,
            "POST",
            f"{actions_client.BASE_URL}/gravity",
            params=None,
            stream=True,
        )
        assert lines == [
            "  [✓] DNS resolution is available",
            "  [i] Neutrino emissions detected...",
            "  [✓] Done.",
        ]

    @pytest.mark.parametrize(
        "color,expected_params",
        [
            (True, {"color": "true"}),
            (False, None),
        ],
    )
    @patch("pihole_lib.actions.make_pihole_request")
    def test_update_gravity_color_param(
        self, mock_request, actions_client, color, expected_params
    ):
        """Test gravity update with color parameter variations."""
        mock_response = Mock()
        mock_response.iter_lines.return_value = ["  [✓] Done."]
        mock_request.return_value = mock_response

        list(actions_client.update_gravity(color=color))

        mock_request.assert_called_once_with(
            actions_client._client,
            "POST",
            f"{actions_client.BASE_URL}/gravity",
            params=expected_params,
            stream=True,
        )

    @pytest.mark.parametrize(
        "input_lines,expected_output",
        [
            ([], []),
            (["", "", ""], []),
            (["  [✓] Start", "", "  [✓] Done", ""], ["  [✓] Start", "  [✓] Done"]),
        ],
    )
    @patch("pihole_lib.actions.make_pihole_request")
    def test_update_gravity_filters_empty_lines(
        self, mock_request, actions_client, input_lines, expected_output
    ):
        """Test that empty lines are filtered from gravity output."""
        mock_response = Mock()
        mock_response.iter_lines.return_value = input_lines
        mock_request.return_value = mock_response

        lines = list(actions_client.update_gravity())
        assert lines == expected_output

    @pytest.mark.parametrize("exception_class,message", EXCEPTION_TEST_CASES)
    @patch("pihole_lib.actions.make_pihole_request")
    def test_update_gravity_exceptions(
        self, mock_request, actions_client, exception_class, message
    ):
        """Test gravity update exception handling."""
        mock_request.side_effect = exception_class(message)

        with pytest.raises(exception_class, match=message):
            list(actions_client.update_gravity())


class TestRestartDns:
    """Test restart_dns method."""

    @pytest.mark.parametrize(
        "status,expected_result",
        [
            ("success", True),
            ("error", False),
        ],
    )
    @patch("pihole_lib.actions.make_pihole_request")
    def test_restart_dns_status_handling(
        self, mock_request, actions_client, status, expected_result
    ):
        """Test DNS restart with various status responses."""
        mock_request.return_value = make_mock_response(
            json_data={"status": status, "took": 0.003}
        )

        result = actions_client.restart_dns()

        mock_request.assert_called_once_with(
            actions_client._client,
            "POST",
            f"{actions_client.BASE_URL}/restartdns",
        )
        assert result is expected_result

    @patch("pihole_lib.actions.make_pihole_request")
    def test_restart_dns_missing_status(self, mock_request, actions_client):
        """Test DNS restart with missing status field."""
        mock_request.return_value = make_mock_response(json_data={"took": 0.001})

        result = actions_client.restart_dns()
        assert result is False

    @pytest.mark.parametrize("exception_class,message", EXCEPTION_TEST_CASES)
    @patch("pihole_lib.actions.make_pihole_request")
    def test_restart_dns_exceptions(
        self, mock_request, actions_client, exception_class, message
    ):
        """Test DNS restart exception handling."""
        mock_request.side_effect = exception_class(message)

        with pytest.raises(exception_class, match=message):
            actions_client.restart_dns()


class TestFlushMethods:
    """Test flush_logs and flush_network methods."""

    @pytest.mark.parametrize(
        "method,endpoint",
        [
            ("flush_logs", "/flush/logs"),
            ("flush_network", "/flush/network"),
        ],
    )
    @pytest.mark.parametrize(
        "status,expected_result",
        [
            ("success", True),
            ("error", False),
        ],
    )
    @patch("pihole_lib.actions.make_pihole_request")
    def test_flush_methods(
        self, mock_request, actions_client, method, endpoint, status, expected_result
    ):
        """Test flush methods with various status responses."""
        mock_request.return_value = make_mock_response(
            json_data={"status": status, "took": 0.001}
        )

        result = getattr(actions_client, method)()

        mock_request.assert_called_once_with(
            actions_client._client,
            "POST",
            f"{actions_client.BASE_URL}{endpoint}",
        )
        assert result is expected_result

    @pytest.mark.parametrize("method", ["flush_logs", "flush_network"])
    @pytest.mark.parametrize(
        "exception_class,message", EXCEPTION_TEST_CASES[:2]
    )  # Test subset
    @patch("pihole_lib.actions.make_pihole_request")
    def test_flush_methods_exceptions(
        self, mock_request, actions_client, method, exception_class, message
    ):
        """Test flush methods exception handling."""
        mock_request.side_effect = exception_class(message)

        with pytest.raises(exception_class):
            getattr(actions_client, method)()
