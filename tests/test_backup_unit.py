"""Unit tests for PiHoleBackup."""

from unittest.mock import Mock, mock_open, patch

import pytest

from pihole_lib import PiHoleBackup
from pihole_lib.exceptions import PiHoleAPIError
from pihole_lib.models.teleporter import TeleporterImportOptions
from tests.conftest import make_client

TEST_BACKUP_CONTENT = b"test backup content"
TEST_IMPORTED_FILES = [
    "etc/pihole/pihole.toml",
    "etc/pihole/gravity.db->group",
    "etc/pihole/gravity.db->adlist",
    "etc/pihole/gravity.db->adlist_by_group",
]


class TestPiHoleBackupInit:
    """Test PiHoleBackup initialization."""

    def test_stores_client(self):
        """Test that backup client stores the provided client."""
        client = make_client()
        backup = PiHoleBackup(client)

        assert backup._client is client


class TestPiHoleBackupExport:
    """Test backup export functionality."""

    def test_generates_timestamped_filename(self):
        """Test that backup filename is properly timestamped."""
        backup = PiHoleBackup(make_client())

        filename = backup._generate_backup_filename()

        assert filename.startswith("pi-hole_pihole_teleporter_")
        assert filename.endswith("_UTC.zip")
        assert len(filename.split("_")) == 6

    @patch("pihole_lib.backup.make_pihole_request")
    @patch("pathlib.Path.mkdir")
    @patch("pathlib.Path.write_bytes")
    def test_export_success(self, mock_write, mock_mkdir, mock_request):
        """Test successful backup export."""
        backup = PiHoleBackup(make_client())
        mock_request.return_value = Mock(content=TEST_BACKUP_CONTENT)

        path = backup.export_backup("/tmp")

        assert path.startswith("/tmp/pi-hole_pihole_teleporter_")
        assert path.endswith("_UTC.zip")
        mock_request.assert_called_once_with(backup._client, "GET", backup.BASE_URL)
        mock_mkdir.assert_called_once()
        mock_write.assert_called_once_with(TEST_BACKUP_CONTENT)

    @patch("pihole_lib.backup.make_pihole_request")
    @patch("pathlib.Path.write_bytes", side_effect=OSError("Permission denied"))
    @patch("pathlib.Path.mkdir")
    def test_export_file_error(self, mock_mkdir, mock_write, mock_request):
        """Test export failure due to file system error."""
        backup = PiHoleBackup(make_client())
        mock_request.return_value = Mock(content=TEST_BACKUP_CONTENT)

        with pytest.raises(PiHoleAPIError, match="Failed to save backup file"):
            backup.export_backup("/tmp")

    def test_export_uses_client_properties(self):
        """Test that export uses client's timeout and SSL settings."""
        client = make_client(timeout=60, verify_ssl=False)
        backup = PiHoleBackup(client)

        assert backup._client.timeout == 60
        assert backup._client.verify_ssl is False


class TestPiHoleBackupImport:
    """Test backup import functionality."""

    @patch("pihole_lib.backup.make_pihole_request")
    @patch("pathlib.Path.exists", return_value=True)
    @patch("pathlib.Path.open", new_callable=mock_open, read_data=TEST_BACKUP_CONTENT)
    def test_import_success(self, mock_file, mock_exists, mock_request):
        """Test successful backup import."""
        backup = PiHoleBackup(make_client())
        mock_request.return_value = Mock(json=lambda: {"files": TEST_IMPORTED_FILES})

        result = backup.import_backup("/tmp/test.zip")

        assert result == TEST_IMPORTED_FILES
        mock_request.assert_called_once()

    @patch("pathlib.Path.exists", return_value=False)
    def test_import_file_not_found(self, mock_exists):
        """Test import failure when file doesn't exist."""
        backup = PiHoleBackup(make_client())

        with pytest.raises(PiHoleAPIError, match="Backup file not found"):
            backup.import_backup("/tmp/missing.zip")

    @patch("pihole_lib.backup.make_pihole_request")
    @patch("pathlib.Path.exists", return_value=True)
    @patch("pathlib.Path.open", new_callable=mock_open, read_data=TEST_BACKUP_CONTENT)
    def test_import_with_options(self, mock_file, mock_exists, mock_request):
        """Test import with custom options."""
        backup = PiHoleBackup(make_client())
        mock_request.return_value = Mock(json=lambda: {"files": TEST_IMPORTED_FILES})

        options = TeleporterImportOptions(config=False, dhcp_leases=True)
        result = backup.import_backup("/tmp/test.zip", options)

        assert result == TEST_IMPORTED_FILES
        assert mock_request.call_args.kwargs["json"] == options.model_dump()

    @pytest.mark.parametrize("extension", [".txt", ".tar", ".gz", ""])
    def test_import_invalid_extension(self, extension):
        """Test import failure with invalid file extension."""
        backup = PiHoleBackup(make_client())

        with patch("pathlib.Path.exists", return_value=True):
            with pytest.raises(PiHoleAPIError, match="Invalid backup file format"):
                backup.import_backup(f"/tmp/backup{extension}")

    def test_import_does_not_create_session_before_file_check(self):
        """Test that session is not created before file validation."""
        client = make_client()
        backup = PiHoleBackup(client)

        assert client._session is None

        with pytest.raises(PiHoleAPIError, match="Backup file not found"):
            backup.import_backup("/tmp/missing.zip")

        assert client._session is None
