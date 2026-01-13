"""Shared test fixtures and utilities for Pi-hole library tests."""

from __future__ import annotations

from typing import Any
from unittest.mock import Mock

import pytest

from pihole_lib import PiHoleClient
from pihole_lib.exceptions import (
    PiHoleAPIError,
    PiHoleAuthenticationError,
    PiHoleConnectionError,
    PiHoleServerError,
)
from tests.constants import (
    PIHOLE_BASE_URL,
    TEST_LOCALHOST_URL,
    TEST_SECRET_PASSWORD,
    TEST_SESSION_ID,
)

RETRY_ATTEMPTS = 3
RETRY_DELAY = 5  # seconds

# Decorator for integration tests - applies flaky retry behavior
integration = pytest.mark.flaky(reruns=RETRY_ATTEMPTS, reruns_delay=RETRY_DELAY)


@pytest.fixture
def mock_client() -> Mock:
    """Create a mock PiHoleClient for unit testing."""
    client = Mock(spec=PiHoleClient)
    client.base_url = PIHOLE_BASE_URL
    client.timeout = 30
    client.verify_ssl = True
    client._session_id = TEST_SESSION_ID
    client._session = Mock()
    return client


@pytest.fixture
def real_client() -> PiHoleClient:
    """Create a real PiHoleClient instance (not connected)."""
    return PiHoleClient(TEST_LOCALHOST_URL, password=TEST_SECRET_PASSWORD)


def make_client(**kwargs) -> PiHoleClient:
    """Factory function to create PiHoleClient instances with defaults."""
    return PiHoleClient(
        TEST_LOCALHOST_URL,
        password=TEST_SECRET_PASSWORD,
        **kwargs,
    )


def make_mock_response(
    json_data: dict[str, Any] | None = None,
    status_code: int = 200,
    content: bytes | None = None,
) -> Mock:
    """Create a mock HTTP response."""
    response = Mock()
    response.status_code = status_code
    if json_data is not None:
        response.json.return_value = json_data
    if content is not None:
        response.content = content
    return response


def make_success_response(json_data: dict[str, Any]) -> Mock:
    """Create a successful mock response with JSON data."""
    return make_mock_response(json_data=json_data, status_code=200)


def make_created_response(json_data: dict[str, Any] | None = None) -> Mock:
    """Create a 201 Created mock response."""
    return make_mock_response(json_data=json_data, status_code=201)


def make_no_content_response() -> Mock:
    """Create a 204 No Content mock response."""
    return make_mock_response(status_code=204)


def make_error_response(status_code: int = 400) -> Mock:
    """Create an error mock response."""
    return make_mock_response(status_code=status_code)


EXCEPTION_TEST_CASES = [
    (PiHoleConnectionError, "Connection failed"),
    (PiHoleAuthenticationError, "Invalid credentials"),
    (PiHoleServerError, "Server error: 500"),
    (PiHoleAPIError, "Bad request"),
]


def get_exception_test_ids() -> list[str]:
    """Get test IDs for exception test cases."""
    return ["connection", "auth", "server", "api"]


@pytest.fixture(params=EXCEPTION_TEST_CASES, ids=get_exception_test_ids())
def exception_case(request):
    """Parameterized fixture for testing exception handling."""
    return request.param


SAMPLE_LIST_DATA = {
    "address": "https://example.com/blocklist.txt",
    "type": "block",
    "comment": "Test blocklist",
    "groups": [0],
    "enabled": True,
    "id": 1,
    "date_added": 1640995200,
    "date_modified": 1640995200,
    "date_updated": 1640995200,
    "number": 1000,
    "invalid_domains": 5,
    "abp_entries": 0,
    "status": 1,
}

SAMPLE_CLIENT_DATA = {
    "client": "192.168.1.100",
    "name": "laptop",
    "comment": "Test client",
    "groups": [0],
    "id": 1,
    "date_added": 1640995200,
    "date_modified": 1640995200,
}

SAMPLE_GROUP_DATA = {
    "name": "Default",
    "comment": "The default group",
    "enabled": True,
    "id": 0,
    "date_added": 1594670974,
    "date_modified": 1611157897,
}

SAMPLE_DHCP_LEASE_DATA = {
    "expires": 1640995200,
    "name": "laptop",
    "hwaddr": "aa:bb:cc:dd:ee:ff",
    "ip": "192.168.1.100",
    "clientid": "01:aa:bb:cc:dd:ee:ff",
}
