"""Test setup and fixtures for integration tests."""

from __future__ import annotations

import os
import subprocess
import time
from collections.abc import Iterator

import docker
import docker.errors
import pytest

from tests.constants import (
    AUTH_TIMEOUT,
    CONTAINER_STARTUP_TIMEOUT,
    DOCKER_COMPOSE_FILE,
    PIHOLE_BASE_URL,
    PIHOLE_CONTAINER_NAME,
    PIHOLE_TEST_PASSWORD,
    POLL_INTERVAL,
)

# Re-export shared fixtures from fixtures module
from tests.fixtures import (  # noqa: F401
    EXCEPTION_TEST_CASES,
    RETRY_ATTEMPTS,
    RETRY_DELAY,
    SAMPLE_CLIENT_DATA,
    SAMPLE_DHCP_LEASE_DATA,
    SAMPLE_GROUP_DATA,
    SAMPLE_LIST_DATA,
    exception_case,
    integration,
    make_client,
    make_created_response,
    make_error_response,
    make_mock_response,
    make_no_content_response,
    make_success_response,
    mock_client,
    real_client,
)


def project_root() -> str:
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def docker_compose(*args: str, check: bool = True) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["docker-compose", "-f", DOCKER_COMPOSE_FILE, *args],
        cwd=project_root(),
        check=check,
        capture_output=True,
        text=True,
    )


def wait_for_container_health(container) -> None:
    """Block until the Docker container becomes healthy."""
    elapsed = 0

    while elapsed < CONTAINER_STARTUP_TIMEOUT:
        container.reload()
        health = container.attrs.get("State", {}).get("Health", {})
        status = health.get("Status", "unknown")

        if status == "healthy":
            return

        if status == "unhealthy":
            logs = container.logs().decode()
            pytest.fail(f"Container became unhealthy:\n{logs}")

        time.sleep(POLL_INTERVAL)
        elapsed += POLL_INTERVAL

    logs = container.logs().decode()
    pytest.fail(
        f"Container did not become healthy within "
        f"{CONTAINER_STARTUP_TIMEOUT}s:\n{logs}"
    )


def is_dns_ready(client) -> bool:
    """Check if Pi-hole DNS service is ready."""
    try:
        from pihole_lib import PiHoleInfo

        info = PiHoleInfo(client)
        return info.get_login_info().dns
    except Exception:
        return False


def wait_for_pihole_restart(client, timeout: int = 120) -> None:
    """Wait for Pi-hole to restart and DNS to become available again."""
    from pihole_lib import PiHoleClient

    time.sleep(RETRY_DELAY)  # allow restart to begin
    start = time.time()

    while time.time() - start < timeout:
        try:
            temp_client = PiHoleClient(
                base_url=PIHOLE_BASE_URL,
                password=PIHOLE_TEST_PASSWORD,
                verify_ssl=False,
                timeout=10,
            )

            if is_dns_ready(temp_client):
                temp_client.close()

                # Reset original client session (restart invalidates it)
                client._session_id = None
                if client._session:
                    client._session.close()
                    client._session = None

                time.sleep(RETRY_DELAY)
                return

            temp_client.close()

        except Exception:
            pass  # expected during restart window

        time.sleep(RETRY_DELAY)

    raise RuntimeError(f"Pi-hole did not restart within {timeout} seconds")


@pytest.fixture
def pihole_restart_isolation(pihole_container):
    """Ensure spacing between tests that restart Pi-hole."""
    yield
    time.sleep(5)


@pytest.fixture(scope="session")
def docker_client() -> Iterator[docker.DockerClient]:
    """Provide a Docker client."""
    client = docker.from_env()
    try:
        yield client
    finally:
        client.close()


@pytest.fixture(scope="session")
def pihole_container(docker_client):
    """Start and manage the Pi-hole Docker container."""
    # if we are running in a CI like GitHub Actions,
    # we should assume we are using a service container.
    if os.getenv("IS_CI"):
        yield None
        return

    try:
        try:
            container = docker_client.containers.get(PIHOLE_CONTAINER_NAME)
            if container.status != "running":
                container.start()
        except docker.errors.NotFound:
            docker_compose("up", "-d")
            container = docker_client.containers.get(PIHOLE_CONTAINER_NAME)

        wait_for_container_health(container)
        yield container

    finally:
        docker_compose("down", check=False)


@pytest.fixture(scope="session")
def _pihole_client_instance(pihole_container):
    """Create a shared PiHoleClient for the test session."""
    from pihole_lib import PiHoleClient

    client = PiHoleClient(
        base_url=PIHOLE_BASE_URL,
        password=PIHOLE_TEST_PASSWORD,
        verify_ssl=False,
        timeout=AUTH_TIMEOUT,
    )

    try:
        yield client
    finally:
        client.close()


@pytest.fixture
def pihole_client(_pihole_client_instance):
    """Provide an authenticated PiHoleClient.

    Authentication may expire between tests (like when a config change restarts the server),
    so this ensures a valid session before each test.
    """
    client = _pihole_client_instance

    if not client.is_authenticated():
        client._ensure_session()
        client._authenticate()

    return client
