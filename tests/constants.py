"""Shared constants for Pi-hole library tests."""

# Test configuration constants
PIHOLE_CONTAINER_NAME = "pihole-test"
DOCKER_COMPOSE_FILE = "tests/docker-compose.test.yml"
PIHOLE_BASE_URL = "http://localhost:8080"
PIHOLE_TEST_PASSWORD = "test-password-123"
PIHOLE_AUTH_ENDPOINT = "/api/auth"
PIHOLE_AUTH_URL = f"{PIHOLE_BASE_URL}{PIHOLE_AUTH_ENDPOINT}"

# Timeout constants (in seconds)
CONTAINER_STARTUP_TIMEOUT = 60
AUTH_TIMEOUT = 30
REQUEST_TIMEOUT = 5
POLL_INTERVAL = 3
FINAL_WAIT = 5

# HTTP status codes
HTTP_OK = 200

# Test URLs and hosts
TEST_LOCALHOST_URL = "http://localhost"
TEST_INVALID_HOST_URL = "http://definitely-not-a-real-host:9999"

# Test passwords
TEST_SECRET_PASSWORD = "secret"
TEST_WRONG_PASSWORD = "wrong-password"

# Test session data
TEST_SESSION_ID = "test-session-id"
TEST_INVALID_SESSION_ID = "invalid-session-id"

# Test model data
TEST_SID = "abc123def456"
TEST_CSRF_TOKEN = "csrf-token-here"
TEST_MESSAGE_CORRECT = "password correct"
TEST_MESSAGE_INCORRECT = "password incorrect"
TEST_VALIDITY_SECONDS = 1800

# Test exception messages
TEST_EXCEPTION_MESSAGE = "Test exception"
CONNECTION_FAILED_MESSAGE = "Connection failed"

# Info endpoint constants
PIHOLE_INFO_LOGIN_ENDPOINT = "/api/info/login"
PIHOLE_INFO_LOGIN_URL = f"{PIHOLE_BASE_URL}{PIHOLE_INFO_LOGIN_ENDPOINT}"

# Test login info data
TEST_HTTPS_PORT = 443
TEST_HTTPS_PORT_DISABLED = 0
TEST_DNS_STATUS_UP = True
TEST_DNS_STATUS_DOWN = False
TEST_REQUEST_TIME = 0.123456
