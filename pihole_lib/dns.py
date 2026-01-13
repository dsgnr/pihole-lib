"""Pi-hole DNS management."""

from urllib.parse import quote

from pihole_lib.base import BasePiHoleAPIClient
from pihole_lib.config import PiHoleConfig
from pihole_lib.models.dns import DNSBlockingStatus, DNSConfig, DNSRecord
from pihole_lib.utils import make_pihole_request


class PiHoleDNS(BasePiHoleAPIClient):
    """Pi-hole DNS management client.

    Provides methods to manage custom DNS records, retrieve DNS configuration,
    and control DNS blocking status.

    Examples::

        from pihole_lib import PiHoleClient

        with PiHoleClient("http://192.168.1.100", password="secret") as client:
            # Get DNS configuration
            config = client.dns.get_config()
            print(f"Upstream servers: {config.upstreams}")

            # Manage DNS records
            client.dns.add_a_record("server.local", "192.168.1.100")
            client.dns.add_cname_record("www.local", "server.local")

            # Control blocking
            client.dns.disable_blocking(timer=300)  # 5 minutes
            client.dns.enable_blocking()

    """

    BASE_URL = "/api/dns"
    CONFIG_URL = "/api/config/dns"

    def get_config(self) -> DNSConfig:
        """Get Pi-hole DNS configuration.

        Returns:
            DNSConfig with upstream servers, custom records, and settings.
        """
        config_client = PiHoleConfig(self._client)
        dns_config = config_client.get_config("dns")["dns"]
        return DNSConfig.from_raw_config(dns_config)

    def get_records(self, record_type: str | None = None) -> list[DNSRecord]:
        """Get all custom DNS records.

        Args:
            record_type: Filter by "A" or "CNAME", or None for all records.

        Returns:
            List of DNSRecord objects.

        Raises:
            ValueError: If an invalid record type is specified.
        """
        if record_type is not None and record_type not in ("A", "CNAME"):
            raise ValueError(
                f"Invalid record type '{record_type}'. Must be 'A', 'CNAME', or None."
            )

        config = self.get_config()
        if record_type is None:
            return config.records
        return [r for r in config.records if r.record_type == record_type]

    def add_a_record(self, domain: str, ip: str) -> bool:
        """Add a custom A record.

        Args:
            domain: Domain name (e.g., "server.local").
            ip: IPv4 address (e.g., "192.168.1.100").

        Returns:
            True if the record was added successfully.
        """
        record_value = quote(f"{ip} {domain}", safe="")
        response = make_pihole_request(
            self._client,
            "PUT",
            f"{self.CONFIG_URL}/hosts/{record_value}",
        )
        return bool(response.status_code == 201)

    def remove_a_record(self, domain: str, ip: str) -> bool:
        """Remove a custom A record.

        Args:
            domain: Domain name of the record to remove.
            ip: IPv4 address of the record to remove.

        Returns:
            True if the record was removed successfully.
        """
        record_value = quote(f"{ip} {domain}", safe="")
        response = make_pihole_request(
            self._client,
            "DELETE",
            f"{self.CONFIG_URL}/hosts/{record_value}",
        )
        return bool(response.status_code == 204)

    def add_cname_record(self, domain: str, target: str) -> bool:
        """Add a custom CNAME record.

        Args:
            domain: Source domain name (the alias).
            target: Target domain name.

        Returns:
            True if the record was added successfully.
        """
        record_value = quote(f"{domain},{target}", safe="")
        response = make_pihole_request(
            self._client,
            "PUT",
            f"{self.CONFIG_URL}/cnameRecords/{record_value}",
        )
        return bool(response.status_code == 201)

    def remove_cname_record(self, domain: str, target: str) -> bool:
        """Remove a custom CNAME record.

        Args:
            domain: Source domain name of the record to remove.
            target: Target domain name of the record to remove.

        Returns:
            True if the record was removed successfully.
        """
        record_value = quote(f"{domain},{target}", safe="")
        response = make_pihole_request(
            self._client,
            "DELETE",
            f"{self.CONFIG_URL}/cnameRecords/{record_value}",
        )
        return bool(response.status_code == 204)

    def get_blocking_status(self) -> DNSBlockingStatus:
        """Get DNS blocking status.

        Returns:
            DNSBlockingStatus with current blocking state and timer info.
        """
        response = make_pihole_request(
            self._client,
            "GET",
            f"{self.BASE_URL}/blocking",
        )
        return DNSBlockingStatus.model_validate(response.json())

    def set_blocking_status(
        self, blocking: bool = True, timer: int | None = None
    ) -> DNSBlockingStatus:
        """Change DNS blocking status.

        Args:
            blocking: Whether to enable (True) or disable (False) blocking.
            timer: Optional timer in seconds. Status reverts after timer expires.

        Returns:
            DNSBlockingStatus with updated state.
        """
        payload: dict[str, bool | int] = {"blocking": blocking}
        if timer is not None:
            payload["timer"] = timer

        response = make_pihole_request(
            self._client,
            "POST",
            f"{self.BASE_URL}/blocking",
            json=payload,
        )
        return DNSBlockingStatus.model_validate(response.json())

    def enable_blocking(self, timer: int | None = None) -> DNSBlockingStatus:
        """Enable DNS blocking.

        Args:
            timer: Optional timer in seconds to auto-disable after.

        Returns:
            DNSBlockingStatus with updated state.
        """
        return self.set_blocking_status(blocking=True, timer=timer)

    def disable_blocking(self, timer: int | None = None) -> DNSBlockingStatus:
        """Disable DNS blocking.

        Args:
            timer: Optional timer in seconds to auto-enable after.

        Returns:
            DNSBlockingStatus with updated state.
        """
        return self.set_blocking_status(blocking=False, timer=timer)
