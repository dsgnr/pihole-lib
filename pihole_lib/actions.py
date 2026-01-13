"""Pi-hole Actions API client."""

from collections.abc import Iterator

from pihole_lib.base import BasePiHoleAPIClient
from pihole_lib.utils import make_pihole_request


class PiHoleActions(BasePiHoleAPIClient):
    """Pi-hole Actions API client.

    Handles action endpoints that perform operations on Pi-hole.

    Examples::

        from pihole_lib import PiHoleClient

        with PiHoleClient("http://192.168.1.100", password="secret") as client:
            # Update gravity database with streaming output
            for line in client.actions.update_gravity():
                print(line.strip())

            # Restart DNS service
            if client.actions.restart_dns():
                print("DNS restarted successfully")

    """

    BASE_URL = "/api/action"

    def update_gravity(self, color: bool = False) -> Iterator[str]:
        """Update Pi-hole's gravity database (adlists).

        Triggers Pi-hole's gravity update process, which downloads and processes
        all configured adlists. The output is streamed with chunked encoding.

        Args:
            color: Include ANSI color escape codes in output. Defaults to False.

        Yields:
            Lines of output from the gravity update process.
        """
        params = {"color": "true"} if color else None
        response = make_pihole_request(
            self._client,
            "POST",
            f"{self.BASE_URL}/gravity",
            params=params,
            stream=True,
        )

        for line in response.iter_lines(decode_unicode=True):
            if line:
                yield line

    def restart_dns(self) -> bool:
        """Restart Pi-hole's DNS service (pihole-FTL).

        Returns:
            True if the restart was successful.
        """
        response = make_pihole_request(
            self._client,
            "POST",
            f"{self.BASE_URL}/restartdns",
        )
        result: dict[str, str] = response.json()
        return result.get("status") == "success"

    def flush_logs(self) -> bool:
        """Flush Pi-hole's DNS logs.

        Empties the DNS log file and purges the most recent 24 hours
        from both the database and FTL's internal memory.

        Returns:
            True if the flush was successful.
        """
        response = make_pihole_request(
            self._client,
            "POST",
            f"{self.BASE_URL}/flush/logs",
        )
        result: dict[str, str] = response.json()
        return result.get("status") == "success"

    def flush_network(self) -> bool:
        """Flush Pi-hole's network table.

        Removes all known devices and their associated addresses.

        Returns:
            True if the flush was successful.
        """
        response = make_pihole_request(
            self._client,
            "POST",
            f"{self.BASE_URL}/flush/network",
        )
        result: dict[str, str] = response.json()
        return result.get("status") == "success"
