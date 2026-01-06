"""Test setup and fixtures."""

import os
import subprocess
import time

import docker
import docker.errors
import pytest
import requests

from .constants import (
    AUTH_TIMEOUT,
    CONTAINER_STARTUP_TIMEOUT,
    DOCKER_COMPOSE_FILE,
    FINAL_WAIT,
    HTTP_OK,
    PIHOLE_AUTH_URL,
    PIHOLE_CONTAINER_NAME,
    PIHOLE_TEST_PASSWORD,
    POLL_INTERVAL,
    REQUEST_TIMEOUT,
)


def is_dns_ready(client) -> bool:
    """Check if Pi-hole DNS service is ready.

    Args:
        client: PiHoleClient instance to check.

    Returns:
        True if DNS service is up and running, False otherwise.
    """
    try:
        from pihole_lib import PiHoleInfo

        info = PiHoleInfo(client)
        login_info = info.get_login_info()
        return login_info.dns
    except Exception:
        return False


def wait_for_pihole_restart(client, timeout: int = 120) -> None:
    """Wait for Pi-hole to restart after backup import.

    Args:
        client: PiHoleClient instance to check.
        timeout: Maximum time to wait in seconds.

    Raises:
        Exception: If Pi-hole doesn't come back up within timeout.
    """
    from pihole_lib import PiHoleClient

    from .constants import PIHOLE_BASE_URL

    # Wait longer for the restart to begin
    time.sleep(5)

    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            # Create a new client since the old session is invalid after restart
            temp_client = PiHoleClient(
                base_url=PIHOLE_BASE_URL,
                password=PIHOLE_TEST_PASSWORD,
                timeout=10,  # Longer timeout for readiness check
                verify_ssl=False,
            )

            if is_dns_ready(temp_client):
                # Pi-hole is back up and DNS is ready
                temp_client.close()

                # Invalidate the original client's session since Pi-hole restarted
                client._session_id = None
                if client._session:
                    client._session.close()
                    client._session = None

                # Give it a bit more time to fully stabilize
                time.sleep(3)
                return

            temp_client.close()

        except Exception:
            # Expected during restart
            pass

        time.sleep(3)  # Wait longer between checks

    raise Exception(f"Pi-hole did not restart within {timeout} seconds")


@pytest.fixture
def pihole_restart_isolation(pihole_container):
    """Ensure proper isolation between tests that cause Pi-hole restarts."""
    yield
    # After test completion, wait a bit to ensure Pi-hole is stable
    # before the next test runs
    time.sleep(5)


@pytest.fixture(scope="session")
def docker_client():
    """Get a Docker client for tests."""
    client = docker.from_env()
    yield client
    client.close()


@pytest.fixture(scope="session")
def pihole_container(docker_client):
    """Start a Pi-hole container for testing."""
    container = None

    def cleanup_container():
        """Cleanup function to ensure container is always removed."""
        try:
            test_dir = os.path.dirname(os.path.abspath(__file__))
            project_dir = os.path.dirname(test_dir)

            subprocess.run(
                ["docker-compose", "-f", DOCKER_COMPOSE_FILE, "down"],
                cwd=project_dir,
                check=False,
                capture_output=True,  # Suppress output unless there's an error
            )
        except Exception as e:
            print(f"Warning: Failed to clean up Docker container: {e}")

    # Register cleanup to run even if tests fail
    import atexit

    atexit.register(cleanup_container)

    try:
        # Check if container already exists
        try:
            container = docker_client.containers.get(PIHOLE_CONTAINER_NAME)
            if container.status != "running":
                container.start()
        except docker.errors.NotFound:
            # Start new container using docker-compose
            test_dir = os.path.dirname(os.path.abspath(__file__))
            project_dir = os.path.dirname(test_dir)

            # Start container with docker-compose
            subprocess.run(
                ["docker-compose", "-f", DOCKER_COMPOSE_FILE, "up", "-d"],
                cwd=project_dir,
                check=True,
            )

            # Get the container
            container = docker_client.containers.get(PIHOLE_CONTAINER_NAME)

        # Wait for container to be ready by testing the API directly
        max_wait = CONTAINER_STARTUP_TIMEOUT
        wait_time = 0
        api_ready = False

        while wait_time < max_wait and not api_ready:
            container.reload()
            if container.status == "running":
                # Test if Pi-hole API is responding
                try:
                    # Test authentication first
                    auth_response = requests.post(
                        PIHOLE_AUTH_URL,
                        json={"password": PIHOLE_TEST_PASSWORD},
                        timeout=REQUEST_TIMEOUT,
                    )
                    if auth_response.status_code == HTTP_OK:
                        auth_data = auth_response.json()
                        if auth_data.get("session", {}).get("valid"):
                            # Also check if DNS service is ready
                            try:
                                from pihole_lib import PiHoleClient

                                from .constants import PIHOLE_BASE_URL

                                # Create a temporary client to check DNS status
                                temp_client = PiHoleClient(
                                    base_url=PIHOLE_BASE_URL,
                                    password=PIHOLE_TEST_PASSWORD,
                                    verify_ssl=False,
                                    timeout=5,  # Short timeout for readiness check
                                )

                                # Check if DNS is ready
                                if is_dns_ready(temp_client):
                                    api_ready = True
                                    temp_client.close()
                                    break
                                else:
                                    temp_client.close()
                                    print("DNS not ready yet, waiting...")
                            except Exception as e:
                                print(f"DNS check failed: {e}")
                                pass
                except Exception:
                    pass

            time.sleep(POLL_INTERVAL)
            wait_time += POLL_INTERVAL

        if not api_ready:
            # Get logs for debugging
            logs = container.logs().decode("utf-8")
            pytest.fail(
                f"Pi-hole API failed to start within {max_wait}s. Logs:\n{logs}"
            )

        # Give it a bit more time to fully initialize
        time.sleep(FINAL_WAIT)

        yield container

    finally:
        # Cleanup: Stop and remove the container
        cleanup_container()


@pytest.fixture(scope="session")
def pihole_session(pihole_container):
    """Create a reusable Pi-hole session to avoid rate limiting."""
    # Wait for the container to be ready first
    _ = pihole_container

    session = requests.Session()
    session.verify = False

    # Authenticate once for the entire test session
    auth_response = session.post(
        PIHOLE_AUTH_URL,
        json={"password": PIHOLE_TEST_PASSWORD},
        timeout=AUTH_TIMEOUT,
    )

    if auth_response.status_code != HTTP_OK:
        pytest.fail(f"Failed to authenticate: {auth_response.status_code}")

    auth_data = auth_response.json()
    session_info = auth_data.get("session", {})

    if not session_info.get("valid"):
        pytest.fail("Authentication failed - invalid session")

    session_id = session_info.get("sid")
    if not session_id:
        pytest.fail("No session ID received")

    # Store session ID for cleanup
    session.headers.update({"X-FTL-SID": session_id})

    yield session, session_id

    # Clean up session
    try:
        session.delete(PIHOLE_AUTH_URL, timeout=REQUEST_TIMEOUT)
    except Exception:
        pass
    finally:
        session.close()
