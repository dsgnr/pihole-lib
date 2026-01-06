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
                            api_ready = True
                            break
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
