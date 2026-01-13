"""Pi-hole Backup API client."""

from datetime import datetime, timezone
from pathlib import Path

from pihole_lib.base import BasePiHoleAPIClient
from pihole_lib.exceptions import PiHoleAPIError
from pihole_lib.models.teleporter import TeleporterImportOptions
from pihole_lib.utils import make_pihole_request


class PiHoleBackup(BasePiHoleAPIClient):
    """Pi-hole Backup API client.

    Handles backup and restore operations using the Teleporter endpoint.

    Examples::

        from pihole_lib import PiHoleClient

        with PiHoleClient("http://192.168.1.100", password="secret") as client:
            # Export backup
            backup_file = client.backup.export_backup("/path/to/backups")
            print(f"Backup saved to: {backup_file}")

            # Import backup
            imported_files = client.backup.import_backup("/path/to/backup.zip")
            print(f"Imported {len(imported_files)} files")

    """

    BASE_URL = "/api/teleporter"
    _ZIP_EXT = ".zip"
    _MIME_ZIP = "application/zip"

    def _generate_backup_filename(self) -> str:
        """Generate a timestamped backup filename."""
        timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d_%H-%M-%S")
        return f"pi-hole_pihole_teleporter_{timestamp}_UTC{self._ZIP_EXT}"

    def export_backup(self, backup_dir: str) -> str:
        """Export Pi-hole settings to a backup file.

        Args:
            backup_dir: Directory where the backup file should be saved.

        Returns:
            The full path to the created backup file.
        """
        response = make_pihole_request(self._client, "GET", self.BASE_URL)

        try:
            backup_path = Path(backup_dir)
            backup_path.mkdir(parents=True, exist_ok=True)
            backup_file = backup_path / self._generate_backup_filename()
            backup_file.write_bytes(response.content)
            return str(backup_file)
        except OSError as e:
            raise PiHoleAPIError(f"Failed to save backup file: {e}") from e

    def import_backup(
        self,
        file_path: str,
        import_options: TeleporterImportOptions | None = None,
    ) -> list[str]:
        """Import Pi-hole settings from a backup file.

        Note: This will overwrite your current configuration and restart Pi-hole.

        Args:
            file_path: Full path to the backup ZIP file to import.
            import_options: Options specifying which elements to restore.
                          If None, all items will be restored.

        Returns:
            List of imported backup files/components.
        """
        file_path_obj = Path(file_path)

        if not file_path_obj.name.lower().endswith(self._ZIP_EXT):
            raise PiHoleAPIError(
                f"Invalid backup file format. Pi-hole only accepts ZIP files, "
                f"got: {file_path_obj.name}"
            )

        if not file_path_obj.exists():
            raise PiHoleAPIError(f"Backup file not found: {file_path}")

        json_data = import_options.model_dump() if import_options else None

        with file_path_obj.open("rb") as f:
            files = {"file": (file_path_obj.name, f, self._MIME_ZIP)}
            response = make_pihole_request(
                self._client,
                "POST",
                self.BASE_URL,
                files=files,
                json=json_data,
            )

        result: dict[str, list[str]] = response.json()
        return list(result["files"])
