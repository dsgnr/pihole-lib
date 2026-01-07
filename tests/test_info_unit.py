"""Unit tests for PiHoleInfo (no network calls)."""

from unittest.mock import Mock, patch

from pihole_lib import PiHoleClient, PiHoleInfo

from .constants import (
    TEST_LOCALHOST_URL,
    TEST_SECRET_PASSWORD,
)


class TestPiHoleInfoInit:
    """Test info client initialization."""

    def test_init_with_client(self):
        """Info client should initialize with a PiHoleClient."""
        client = PiHoleClient(TEST_LOCALHOST_URL, password=TEST_SECRET_PASSWORD)
        info_client = PiHoleInfo(client)

        assert info_client._client is client

    def test_init_stores_client_reference(self):
        """Info client should store reference to the provided client."""
        client = PiHoleClient(TEST_LOCALHOST_URL, password=TEST_SECRET_PASSWORD)
        info_client = PiHoleInfo(client)

        # Should be able to access client properties through the stored reference
        assert info_client._client.base_url == TEST_LOCALHOST_URL
        assert info_client._client._password == TEST_SECRET_PASSWORD


class TestPiHoleInfoLoginInfo:
    """Test info client login info functionality (no network calls)."""

    def test_get_login_info_uses_client_session(self):
        """get_login_info should use the client's session."""
        client = PiHoleClient(TEST_LOCALHOST_URL, password=TEST_SECRET_PASSWORD)
        info_client = PiHoleInfo(client)

        assert client._session is None

        # This would fail in real usage due to no network, but we're testing
        # that it ensures the client has a session
        try:
            info_client.get_login_info()
        except Exception:
            # Expected to fail due to no network, but client session should be created
            pass

        assert client._session is not None


class TestPiHoleInfoClientInfo:
    """Test info client get_client_info functionality (no network calls)."""

    @patch("pihole_lib.info.make_pihole_request")
    def test_get_client_info_success(self, mock_request):
        """Should successfully get client info."""
        client = PiHoleClient(TEST_LOCALHOST_URL, password=TEST_SECRET_PASSWORD)
        info_client = PiHoleInfo(client)

        mock_response = Mock()
        mock_response.json.return_value = {
            "remote_addr": "192.168.1.100",
            "http_version": "1.1",
            "method": "GET",
            "headers": [
                {"name": "Host", "value": "localhost:8080"},
                {"name": "User-Agent", "value": "python-requests/2.32.5"},
            ],
            "took": 0.001,
        }
        mock_request.return_value = mock_response

        result = info_client.get_client_info()

        # Verify the request was made correctly
        mock_request.assert_called_once_with(
            client,
            "GET",
            "/api/info/client",
        )

        # Verify the response structure
        assert result.remote_addr == "192.168.1.100"
        assert result.http_version == "1.1"
        assert result.method == "GET"
        assert len(result.headers) == 2
        assert result.headers[0].name == "Host"
        assert result.headers[0].value == "localhost:8080"
        assert result.headers[1].name == "User-Agent"
        assert result.headers[1].value == "python-requests/2.32.5"

    @patch("pihole_lib.info.make_pihole_request")
    def test_get_client_info_empty_headers(self, mock_request):
        """Should handle empty headers list."""
        client = PiHoleClient(TEST_LOCALHOST_URL, password=TEST_SECRET_PASSWORD)
        info_client = PiHoleInfo(client)

        mock_response = Mock()
        mock_response.json.return_value = {
            "remote_addr": "127.0.0.1",
            "http_version": "2.0",
            "method": "POST",
            "headers": [],
            "took": 0.001,
        }
        mock_request.return_value = mock_response

        result = info_client.get_client_info()

        assert result.remote_addr == "127.0.0.1"
        assert result.http_version == "2.0"
        assert result.method == "POST"
        assert len(result.headers) == 0


class TestPiHoleInfoDatabaseInfo:
    """Test info client get_database_info functionality (no network calls)."""

    @patch("pihole_lib.info.make_pihole_request")
    def test_get_database_info_success(self, mock_request):
        """Should successfully get database info."""
        client = PiHoleClient(TEST_LOCALHOST_URL, password=TEST_SECRET_PASSWORD)
        info_client = PiHoleInfo(client)

        mock_response = Mock()
        mock_response.json.return_value = {
            "size": 90112,
            "type": "Regular file",
            "mode": "rw-r-----",
            "atime": 1767779556,
            "mtime": 1767779556,
            "ctime": 1767779556,
            "owner": {
                "user": {"uid": 1000, "name": "pihole", "info": ""},
                "group": {"gid": 1000, "name": "pihole"},
            },
            "queries": 0,
            "earliest_timestamp": 0,
            "queries_disk": 0,
            "earliest_timestamp_disk": 0,
            "sqlite_version": "3.51.0",
            "took": 0.001,
        }
        mock_request.return_value = mock_response

        result = info_client.get_database_info()

        # Verify the request was made correctly
        mock_request.assert_called_once_with(
            client,
            "GET",
            "/api/info/database",
        )

        # Verify the response structure
        assert result.size == 90112
        assert result.type == "Regular file"
        assert result.mode == "rw-r-----"
        assert result.atime == 1767779556
        assert result.mtime == 1767779556
        assert result.ctime == 1767779556
        assert result.owner.user.uid == 1000
        assert result.owner.user.name == "pihole"
        assert result.owner.user.info == ""
        assert result.owner.group.gid == 1000
        assert result.owner.group.name == "pihole"
        assert result.queries == 0
        assert result.earliest_timestamp == 0
        assert result.queries_disk == 0
        assert result.earliest_timestamp_disk == 0
        assert result.sqlite_version == "3.51.0"

    @patch("pihole_lib.info.make_pihole_request")
    def test_get_database_info_with_queries(self, mock_request):
        """Should handle database info with queries."""
        client = PiHoleClient(TEST_LOCALHOST_URL, password=TEST_SECRET_PASSWORD)
        info_client = PiHoleInfo(client)

        mock_response = Mock()
        mock_response.json.return_value = {
            "size": 1048576,
            "type": "Regular file",
            "mode": "rw-r--r--",
            "atime": 1767779556,
            "mtime": 1767779556,
            "ctime": 1767779556,
            "owner": {
                "user": {"uid": 999, "name": "ftl", "info": "FTL user"},
                "group": {"gid": 999, "name": "ftl"},
            },
            "queries": 1000,
            "earliest_timestamp": 1767700000,
            "queries_disk": 5000,
            "earliest_timestamp_disk": 1767600000,
            "sqlite_version": "3.45.0",
            "took": 0.002,
        }
        mock_request.return_value = mock_response

        result = info_client.get_database_info()

        assert result.size == 1048576
        assert result.queries == 1000
        assert result.earliest_timestamp == 1767700000
        assert result.queries_disk == 5000
        assert result.earliest_timestamp_disk == 1767600000
        assert result.owner.user.name == "ftl"
        assert result.owner.user.info == "FTL user"
        assert result.sqlite_version == "3.45.0"

    def test_get_login_info_uses_client_properties(self):
        """get_login_info should use client's base_url and timeout."""
        client = PiHoleClient(
            TEST_LOCALHOST_URL,
            password=TEST_SECRET_PASSWORD,
            timeout=60,
            verify_ssl=False,
        )
        info_client = PiHoleInfo(client)

        # Verify info client uses client properties
        assert info_client._client.base_url == TEST_LOCALHOST_URL
        assert info_client._client.timeout == 60
        assert info_client._client.verify_ssl is False
