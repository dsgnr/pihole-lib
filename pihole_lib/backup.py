"""Pi-hole Backup API client."""

from datetime import datetime, timezone
from pathlib import Path
from typing import TYPE_CHECKING, Optional

from .exceptions import (
    PiHoleAPIError,
)
from .models import TeleporterImportOptions, TeleporterImportResult
from .utils import make_pihole_request

if TYPE_CHECKING:
    from .client import PiHoleClient


class PiHoleBackup:
    """Pi-hole Backup API client.

    Handles backup and restore operations using the Teleporter endpoint.
    Uses a PiHoleClient instance for making authenticated requests.

    Examples:
        ```python
        from pihole_lib import PiHoleClient, PiHoleBackup

        # Create client and backup instance
        with PiHoleClient("http://192.168.1.100", password="secret") as client:
            backup = PiHoleBackup(client)

            # Export backup to directory (filename auto-generated with timestamp)
            backup_file = backup.export_backup("/path/to/backups")
            print(f"Backup saved to: {backup_file}")

            # Import backup (Pi-hole only accepts ZIP files)
            result = backup.import_backup("/path/to/backup.zip")
            print(f"Imported {len(result.files)} files in {result.took}s")
        ```
    """

    def __init__(self, client: "PiHoleClient") -> None:
        """Initialize a Pi-hole backup client.

        Args:
            client: PiHoleClient instance to use for requests.
        """
        self._client = client

    def _generate_backup_filename(self) -> str:
        """Generate a timestamped backup filename.

        Returns:
            Backup filename in format: pi-hole_pihole_teleporter_YYYY-MM-DD_HH-MM-SS_UTC.zip
        """
        timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d_%H-%M-%S")
        return f"pi-hole_pihole_teleporter_{timestamp}_UTC.zip"

    def export_backup(self, backup_dir: str) -> str:
        """Export Pi-hole settings to a backup file.

        Request an archived copy of your Pi-hole's current configuration.
        The backup file will be saved with a timestamped filename.
        Authentication is required for this endpoint.

        Args:
            backup_dir: Directory where the backup file should be saved.

        Returns:
            The full path to the created backup file.

        Raises:
            PiHoleConnectionError: Connection failed.
            PiHoleAuthenticationError: Authentication failed.
            PiHoleServerError: Server error.
            PiHoleAPIError: Other API errors.
        """
        response = make_pihole_request(
            self._client,
            "GET",
            "/api/teleporter",
        )

        # Generate timestamped filename and create full path
        try:
            backup_dir_obj = Path(backup_dir)
            backup_dir_obj.mkdir(parents=True, exist_ok=True)

            backup_filename = self._generate_backup_filename()
            backup_path = backup_dir_obj / backup_filename

            with open(backup_path, "wb") as f:
                f.write(response.content)

            return str(backup_path)
        except OSError as e:
            raise PiHoleAPIError(f"Failed to save backup file: {e}") from e

    def import_backup(
        self,
        file_path: str,
        import_options: Optional[TeleporterImportOptions] = None,
    ) -> TeleporterImportResult:
        """Import Pi-hole settings from a backup file.

        Upload a Pi-hole Teleporter archive to restore from it.
        Note that this will overwrite your current configuration and restart Pi-hole.
        Authentication is required for this endpoint.

        Args:
            file_path: Full path to the backup ZIP file to import.
            import_options: Options specifying which elements to restore.
                          If None, all items will be restored.

        Returns:
            TeleporterImportResult containing imported files and processing time.

        Raises:
            PiHoleConnectionError: Connection failed.
            PiHoleAuthenticationError: Authentication failed.
            PiHoleServerError: Server error.
            PiHoleAPIError: Other API errors, file not found, or invalid file type.
        """
        file_path_obj = Path(file_path)

        # Check if file is a ZIP file (Pi-hole only accepts ZIP format)
        if not file_path_obj.name.lower().endswith(".zip"):
            raise PiHoleAPIError(
                f"Invalid backup file format. Pi-hole only accepts ZIP files, "
                f"got: {file_path_obj.name}"
            )

        if not file_path_obj.exists():
            raise PiHoleAPIError(f"Backup file not found: {file_path}")

        # Handle import options - send as JSON if provided
        json_data = None
        if import_options:
            json_data = import_options.model_dump()

        # Prepare files for upload and make request
        with open(file_path_obj, "rb") as f:
            files = {"file": (file_path_obj.name, f, "application/zip")}

            response = make_pihole_request(
                self._client,
                "POST",
                "/api/teleporter",
                files=files,
                json=json_data,
            )

        response_data = response.json()
        return TeleporterImportResult(**response_data)
