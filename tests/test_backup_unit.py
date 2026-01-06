"""Unit tests for PiHoleBackup (no network calls)."""

from unittest.mock import Mock, mock_open, patch

import pytest

from pihole_lib import PiHoleBackup, PiHoleClient
from pihole_lib.constants import API_TELEPORTER
from pihole_lib.exceptions import PiHoleAPIError
from pihole_lib.models import TeleporterImportOptions

from .constants import (
    TEST_BACKUP_CONTENT,
    TEST_IMPORTED_FILES,
    TEST_LOCALHOST_URL,
    TEST_SECRET_PASSWORD,
)


class TestPiHoleBackupInit:
    """Test backup client initialization."""

    def test_init_with_client(self):
        """Backup client should initialize with a PiHoleClient."""
        client = PiHoleClient(TEST_LOCALHOST_URL, password=TEST_SECRET_PASSWORD)
        backup_client = PiHoleBackup(client)

        assert backup_client._client is client

    def test_init_stores_client_reference(self):
        """Backup client should store reference to the provided client."""
        client = PiHoleClient(TEST_LOCALHOST_URL, password=TEST_SECRET_PASSWORD)
        backup_client = PiHoleBackup(client)

        # Should be able to access client properties through the stored reference
        assert backup_client._client.base_url == TEST_LOCALHOST_URL
        assert backup_client._client._password == TEST_SECRET_PASSWORD


class TestPiHoleBackupExport:
    """Test backup export functionality (no network calls)."""

    def test_generate_backup_filename(self):
        """Should generate timestamped backup filename."""
        client = PiHoleClient(TEST_LOCALHOST_URL, password=TEST_SECRET_PASSWORD)
        backup_client = PiHoleBackup(client)

        filename = backup_client._generate_backup_filename()

        # Should match the expected pattern
        assert filename.startswith("pi-hole_pihole_teleporter_")
        assert filename.endswith("_UTC.zip")
        # Format: pi-hole_pihole_teleporter_YYYY-MM-DD_HH-MM-SS_UTC.zip
        # Split by '_': ['pi-hole', 'pihole', 'teleporter', 'YYYY-MM-DD', 'HH-MM-SS', 'UTC.zip']
        assert len(filename.split("_")) == 6

    def test_export_backup_uses_client_session(self):
        """export_backup should use the client through make_pihole_request."""
        client = PiHoleClient(TEST_LOCALHOST_URL, password=TEST_SECRET_PASSWORD)
        backup_client = PiHoleBackup(client)

        assert client._session is None

        # Mock the make_pihole_request to avoid network calls
        with patch("pihole_lib.backup.make_pihole_request") as mock_request:
            mock_response = Mock()
            mock_response.content = TEST_BACKUP_CONTENT
            mock_request.return_value = mock_response

            with patch("builtins.open", mock_open()):
                with patch("pathlib.Path.mkdir"):
                    backup_client.export_backup("/tmp")

        # Verify make_pihole_request was called with the client
        mock_request.assert_called_once_with(client, "GET", "/api/teleporter")

    @patch("pihole_lib.backup.make_pihole_request")
    @patch("pathlib.Path.write_bytes")
    @patch("pathlib.Path.mkdir")
    def test_export_backup_success(self, mock_mkdir, mock_write_bytes, mock_request):
        """Should successfully export backup with timestamped filename."""
        client = PiHoleClient(TEST_LOCALHOST_URL, password=TEST_SECRET_PASSWORD)
        backup_client = PiHoleBackup(client)

        # Mock successful response
        mock_response = Mock()
        mock_response.content = TEST_BACKUP_CONTENT
        mock_request.return_value = mock_response

        result = backup_client.export_backup("/tmp")

        # Should return full path with timestamped filename
        assert result.startswith("/tmp/pi-hole_pihole_teleporter_")
        assert result.endswith("_UTC.zip")

        mock_request.assert_called_once_with(client, "GET", API_TELEPORTER)

        # Should create directory and write file
        mock_mkdir.assert_called_once()
        mock_write_bytes.assert_called_once_with(TEST_BACKUP_CONTENT)

    @patch("pihole_lib.backup.make_pihole_request")
    @patch("pathlib.Path.write_bytes", side_effect=OSError("Permission denied"))
    @patch("pathlib.Path.mkdir")
    def test_export_backup_file_error(self, mock_mkdir, mock_write_bytes, mock_request):
        """Should raise PiHoleAPIError when file operations fail."""
        client = PiHoleClient(TEST_LOCALHOST_URL, password=TEST_SECRET_PASSWORD)
        client._ensure_session()
        backup_client = PiHoleBackup(client)

        mock_response = Mock()
        mock_response.content = TEST_BACKUP_CONTENT
        mock_request.return_value = mock_response

        with pytest.raises(PiHoleAPIError, match="Failed to save backup file"):
            backup_client.export_backup("/tmp")

    def test_export_backup_uses_client_properties(self):
        """export_backup should use client's base_url and timeout."""
        client = PiHoleClient(
            TEST_LOCALHOST_URL,
            password=TEST_SECRET_PASSWORD,
            timeout=60,
            verify_ssl=False,
        )
        backup_client = PiHoleBackup(client)

        # Verify backup client uses client properties
        assert backup_client._client.base_url == TEST_LOCALHOST_URL
        assert backup_client._client.timeout == 60
        assert backup_client._client.verify_ssl is False


class TestPiHoleBackupImport:
    """Test backup import functionality (no network calls)."""

    @patch("pihole_lib.backup.make_pihole_request")
    @patch("pathlib.Path.exists", return_value=True)
    @patch("pathlib.Path.open", new_callable=mock_open, read_data=TEST_BACKUP_CONTENT)
    def test_import_backup_success(self, mock_file, mock_exists, mock_request):
        """Should successfully import backup."""
        client = PiHoleClient(TEST_LOCALHOST_URL, password=TEST_SECRET_PASSWORD)
        backup_client = PiHoleBackup(client)

        # Mock successful response
        mock_response = Mock()
        mock_response.json.return_value = {
            "files": TEST_IMPORTED_FILES,
        }
        mock_request.return_value = mock_response

        result = backup_client.import_backup("/tmp/test.zip")

        assert isinstance(result, list)
        assert result == TEST_IMPORTED_FILES
        mock_request.assert_called_once_with(
            client,
            "POST",
            API_TELEPORTER,
            files={
                "file": (
                    "test.zip",
                    mock_file.return_value.__enter__.return_value,
                    "application/zip",
                )
            },
            json=None,
        )

    @patch("pathlib.Path.exists", return_value=False)
    def test_import_backup_file_not_found(self, mock_exists):
        """Should raise PiHoleAPIError when backup file doesn't exist."""
        client = PiHoleClient(TEST_LOCALHOST_URL, password=TEST_SECRET_PASSWORD)
        backup_client = PiHoleBackup(client)

        with pytest.raises(PiHoleAPIError, match="Backup file not found"):
            backup_client.import_backup("/tmp/nonexistent.zip")

    @patch("pihole_lib.backup.make_pihole_request")
    @patch("pathlib.Path.exists", return_value=True)
    @patch("pathlib.Path.open", new_callable=mock_open, read_data=TEST_BACKUP_CONTENT)
    def test_import_backup_with_options(self, mock_file, mock_exists, mock_request):
        """Should pass import options correctly."""
        client = PiHoleClient(TEST_LOCALHOST_URL, password=TEST_SECRET_PASSWORD)
        backup_client = PiHoleBackup(client)

        mock_response = Mock()
        mock_response.json.return_value = {
            "files": TEST_IMPORTED_FILES,
        }
        mock_request.return_value = mock_response

        import_options = TeleporterImportOptions(config=False, dhcp_leases=True)
        result = backup_client.import_backup("/tmp/test.zip", import_options)

        assert isinstance(result, list)
        assert result == TEST_IMPORTED_FILES
        # Verify that make_pihole_request was called with JSON containing the options
        call_args = mock_request.call_args
        json_data = call_args[1]["json"]
        assert json_data == import_options.model_dump()

    def test_import_backup_uses_client_session(self):
        """import_backup should use the client through make_pihole_request."""
        client = PiHoleClient(TEST_LOCALHOST_URL, password=TEST_SECRET_PASSWORD)
        backup_client = PiHoleBackup(client)

        assert client._session is None

        # This should fail due to file not found, but should call make_pihole_request
        with pytest.raises(PiHoleAPIError, match="Backup file not found"):
            backup_client.import_backup("/tmp/nonexistent.zip")

        # The session is not created because we never call make_pihole_request
        # (the method fails before that due to file not found)
        assert client._session is None

    def test_import_backup_invalid_file_format(self):
        """Should raise error for invalid file formats."""
        client = PiHoleClient(TEST_LOCALHOST_URL, password=TEST_SECRET_PASSWORD)
        backup_client = PiHoleBackup(client)

        # Mock file exists but has wrong extension
        with patch("pathlib.Path.exists", return_value=True):
            with pytest.raises(PiHoleAPIError, match="Invalid backup file format"):
                backup_client.import_backup("/tmp/backup.txt")
