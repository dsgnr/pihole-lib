"""Integration tests for PiHoleBackup against real Pi-hole."""

import tempfile
from pathlib import Path

import pytest

from pihole_lib import PiHoleBackup, PiHoleClient
from pihole_lib.exceptions import PiHoleAPIError, PiHoleConnectionError
from pihole_lib.models import TeleporterImportOptions

from .constants import (
    CONNECTION_FAILED_MESSAGE,
    PIHOLE_BASE_URL,
    PIHOLE_TEST_PASSWORD,
    TEST_INVALID_HOST_URL,
)


class TestPiHoleBackupExport:
    """Test backup export functionality against real Pi-hole."""

    def test_export_backup_success(self, pihole_container):
        """Should successfully export backup from Pi-hole."""
        with PiHoleClient(
            base_url=PIHOLE_BASE_URL, password=PIHOLE_TEST_PASSWORD, verify_ssl=False
        ) as client:
            backup_client = PiHoleBackup(client)

            with tempfile.TemporaryDirectory() as tmp_dir:
                result = backup_client.export_backup(tmp_dir)

                # Should return full path with timestamped filename
                assert result.startswith(tmp_dir)
                assert result.endswith("_UTC.zip")
                assert Path(result).exists()
                assert Path(result).stat().st_size > 0  # Should have content

    def test_export_backup_connection_error(self):
        """Network errors should raise connection error."""
        client = PiHoleClient(
            base_url=TEST_INVALID_HOST_URL,
            password=PIHOLE_TEST_PASSWORD,
            timeout=1,  # Short timeout
        )
        backup_client = PiHoleBackup(client)

        with tempfile.TemporaryDirectory() as tmp_dir:
            with pytest.raises(PiHoleConnectionError, match=CONNECTION_FAILED_MESSAGE):
                backup_client.export_backup(tmp_dir)

        client.close()

    def test_export_backup_creates_directory(self, pihole_container):
        """Should create parent directories if they don't exist."""
        with PiHoleClient(
            base_url=PIHOLE_BASE_URL, password=PIHOLE_TEST_PASSWORD, verify_ssl=False
        ) as client:
            backup_client = PiHoleBackup(client)

            with tempfile.TemporaryDirectory() as tmp_dir:
                backup_dir = Path(tmp_dir) / "subdir" / "backups"

                result = backup_client.export_backup(str(backup_dir))

                assert result.startswith(str(backup_dir))
                assert Path(result).exists()
                assert backup_dir.exists()

    def test_export_backup_invalid_path(self, pihole_container):
        """Should raise error for invalid backup paths."""
        with PiHoleClient(
            base_url=PIHOLE_BASE_URL, password=PIHOLE_TEST_PASSWORD, verify_ssl=False
        ) as client:
            backup_client = PiHoleBackup(client)

            # Try to write to a directory that can't be created (e.g., root-only path)
            invalid_path = "/root/cannot_create"

            with pytest.raises(PiHoleAPIError, match="Failed to save backup file"):
                backup_client.export_backup(invalid_path)


class TestPiHoleBackupImport:
    """Test backup import functionality against real Pi-hole."""

    def test_import_backup_file_not_found(self, pihole_container):
        """Should raise error when backup file doesn't exist."""
        with PiHoleClient(
            base_url=PIHOLE_BASE_URL, password=PIHOLE_TEST_PASSWORD, verify_ssl=False
        ) as client:
            backup_client = PiHoleBackup(client)

            with pytest.raises(PiHoleAPIError, match="Backup file not found"):
                backup_client.import_backup("/tmp/nonexistent_backup.zip")

    def test_import_backup_connection_error(self):
        """Network errors should raise connection error."""
        client = PiHoleClient(
            base_url=TEST_INVALID_HOST_URL,
            password=PIHOLE_TEST_PASSWORD,
            timeout=1,  # Short timeout
        )
        backup_client = PiHoleBackup(client)

        # Create a dummy backup file
        with tempfile.NamedTemporaryFile(suffix=".zip") as tmp_file:
            tmp_file.write(b"dummy backup content")
            tmp_file.flush()

            with pytest.raises(PiHoleConnectionError, match=CONNECTION_FAILED_MESSAGE):
                backup_client.import_backup(tmp_file.name)

        client.close()

    def test_import_backup_with_options(
        self, pihole_container, pihole_restart_isolation
    ):
        """Should handle import options correctly."""
        from .conftest import wait_for_pihole_restart

        with PiHoleClient(
            base_url=PIHOLE_BASE_URL, password=PIHOLE_TEST_PASSWORD, verify_ssl=False
        ) as client:
            backup_client = PiHoleBackup(client)

            with tempfile.TemporaryDirectory() as tmp_dir:
                try:
                    # Export backup
                    export_result = backup_client.export_backup(tmp_dir)
                    assert export_result.startswith(tmp_dir)
                    assert Path(export_result).exists()

                    # Import with specific options
                    import_options = TeleporterImportOptions(
                        config=True,
                        dhcp_leases=False,
                    )

                    result = backup_client.import_backup(export_result, import_options)

                    assert isinstance(result, list)
                    assert len(result) > 0  # Should have imported some files
                    assert all(isinstance(file, str) for file in result)

                    # Wait for Pi-hole to restart after import
                    wait_for_pihole_restart(client)

                finally:
                    # Clean up (tempfile.TemporaryDirectory handles this automatically)
                    pass


class TestPiHoleBackupWorkflows:
    """Test complete backup workflows with real Pi-hole."""

    def test_full_backup_restore_workflow(
        self, pihole_container, pihole_restart_isolation
    ):
        """Test complete backup and restore workflow."""
        from .conftest import wait_for_pihole_restart

        with PiHoleClient(
            base_url=PIHOLE_BASE_URL, password=PIHOLE_TEST_PASSWORD, verify_ssl=False
        ) as client:
            backup_client = PiHoleBackup(client)

            with tempfile.TemporaryDirectory() as tmp_dir:
                try:
                    # Step 1: Export backup
                    export_result = backup_client.export_backup(tmp_dir)
                    assert export_result.startswith(tmp_dir)
                    assert Path(export_result).exists()

                    # Step 2: Import the same backup (should work)
                    import_result = backup_client.import_backup(export_result)
                    assert isinstance(import_result, list)
                    assert len(import_result) > 0  # Should have processed something

                    # Wait for Pi-hole to restart after import
                    wait_for_pihole_restart(client)

                finally:
                    # Clean up (tempfile.TemporaryDirectory handles this automatically)
                    pass

    def test_backup_operations_efficiency(self, pihole_container):
        """Test backup operations work efficiently with proper session management."""
        with PiHoleClient(
            base_url=PIHOLE_BASE_URL, password=PIHOLE_TEST_PASSWORD, verify_ssl=False
        ) as client:
            backup_client = PiHoleBackup(client)

            with tempfile.TemporaryDirectory() as tmp_dir:
                try:
                    # Create backup and verify it works
                    result = backup_client.export_backup(tmp_dir)
                    assert result.startswith(tmp_dir)
                    assert Path(result).exists()
                    assert Path(result).stat().st_size > 0

                    # Verify session is properly managed
                    assert client._session is not None

                finally:
                    # Clean up (tempfile.TemporaryDirectory handles this automatically)
                    pass

    def test_constants_usage(self, pihole_container):
        """Test that the class uses the correct API endpoint constants."""
        with PiHoleClient(
            PIHOLE_BASE_URL, password=PIHOLE_TEST_PASSWORD, verify_ssl=False
        ) as client:
            backup = PiHoleBackup(client)
            assert backup.BASE_URL == "/api/teleporter"
