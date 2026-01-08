"""Pi-hole Actions API client."""

from collections.abc import Iterator

from .base import BasePiHoleAPIClient
from .utils import make_pihole_request


class PiHoleActions(BasePiHoleAPIClient):
    """Pi-hole Actions API client.

    Handles action endpoints that perform operations on Pi-hole.
    Uses a PiHoleClient instance for making authenticated requests.

    Examples::

        from pihole_lib import PiHoleClient, PiHoleActions

        with PiHoleClient("http://192.168.1.100", password="secret") as client:
            actions = PiHoleActions(client)

            # Update gravity database with streaming output
            for line in actions.update_gravity():
                print(line.strip())

            # Update gravity with colored output
            for line in actions.update_gravity(color=True):
                print(line.strip())

            # Restart DNS service
            success = actions.restart_dns()
            print(f"DNS restart: {'success' if success else 'failed'}")

    """

    BASE_URL = "/api/action"

    def update_gravity(self, color: bool = False) -> Iterator[str]:
        """Update Pi-hole's gravity database (adlists).

        This endpoint triggers Pi-hole's gravity update process, which downloads
        and processes all configured adlists to update the blocking database.
        The output is streamed with chunked encoding.

        Args:
            color: Include ANSI color escape codes in the streamed output.
                  Defaults to False to prevent colored output for API consumers
                  that don't need formatting.

        Yields:
            Lines of output from the gravity update process.

        Raises:
            PiHoleConnectionError: Connection failed.
            PiHoleAuthenticationError: Authentication failed.
            PiHoleServerError: Server error.
            PiHoleAPIError: Other API errors.

        Examples::

            # Basic gravity update
            for line in actions.update_gravity():
                print(line.strip())

            # Gravity update with colored output
            for line in actions.update_gravity(color=True):
                print(line.strip())

        """
        params = {"color": "true"} if color else None

        response = make_pihole_request(
            self._client,
            "POST",
            f"{self.BASE_URL}/gravity",
            params=params,
            stream=True,
        )

        # Stream the response line by line
        for line in response.iter_lines(decode_unicode=True):
            if line:  # Skip empty lines
                yield line

    def restart_dns(self) -> bool:
        """Restart Pi-hole's DNS service (pihole-FTL).

        Returns:
            True if the restart was successful, False otherwise.

        Raises:
            PiHoleConnectionError: Connection failed.
            PiHoleAuthenticationError: Authentication failed.
            PiHoleServerError: Server error.
            PiHoleAPIError: Other API errors.

        Examples::

            # Restart DNS service
            success = actions.restart_dns()
            if success:
                print("DNS service restarted successfully")
            else:
                print("DNS restart failed")

        """
        response = make_pihole_request(
            self._client,
            "POST",
            f"{self.BASE_URL}/restartdns",
        )

        result = response.json()
        return result.get("status") == "success"  # type: ignore[no-any-return]

    def flush_logs(self) -> bool:
        """Flush Pi-hole's DNS logs.

        This endpoint flushes the DNS logs, including emptying the DNS log file
        and purging the most recent 24 hours from both the database and FTL's
        internal memory.

        Returns:
            True if the flush was successful, False otherwise.

        Raises:
            PiHoleConnectionError: Connection failed.
            PiHoleAuthenticationError: Authentication failed.
            PiHoleServerError: Server error.
            PiHoleAPIError: Other API errors.

        Examples::

            # Flush DNS logs
            success = actions.flush_logs()
            if success:
                print("DNS logs flushed successfully")
            else:
                print("DNS logs flush failed")

        """
        response = make_pihole_request(
            self._client,
            "POST",
            f"{self.BASE_URL}/flush/logs",
        )

        result = response.json()
        return result.get("status") == "success"  # type: ignore[no-any-return]

    def flush_network(self) -> bool:
        """Flush Pi-hole's network table.

        This endpoint flushes the network table, including removing both all
        known devices and their associated addresses.

        Returns:
            True if the flush was successful, False otherwise.

        Raises:
            PiHoleConnectionError: Connection failed.
            PiHoleAuthenticationError: Authentication failed.
            PiHoleServerError: Server error.
            PiHoleAPIError: Other API errors.

        Examples::

            # Flush network table
            success = actions.flush_network()
            if success:
                print("Network table flushed successfully")
            else:
                print("Network table flush failed")

        """
        response = make_pihole_request(
            self._client,
            "POST",
            f"{self.BASE_URL}/flush/network",
        )

        result = response.json()
        return result.get("status") == "success"  # type: ignore[no-any-return]
