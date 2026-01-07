"""Pi-hole DNS management."""

from urllib.parse import quote

from .base import BasePiHoleAPIClient
from .config import PiHoleConfig
from .models import DNSBlockingStatus, DNSConfig, DNSRecord
from .utils import make_pihole_request


class PiHoleDNS(BasePiHoleAPIClient):
    """Pi-hole DNS management client.

    This class provides methods to interact with Pi-hole's DNS functionality,
    including managing custom DNS records (A records and CNAME records),
    retrieving DNS configuration, and controlling DNS blocking status.

    Uses a PiHoleClient instance for making authenticated requests.

    Examples:
        ```python
        from pihole_lib import PiHoleClient, PiHoleDNS

        with PiHoleClient("http://192.168.1.100", password="secret") as client:
            dns = PiHoleDNS(client)

            # Get DNS configuration
            config = dns.get_config()
            print(f"Upstream servers: {config.config.upstreams}")

            # Get custom DNS records
            records = dns.get_records()
            for record in records:
                print(f"{record.record_type}: {record.domain} -> {record.target}")

            # Add custom A record
            success = dns.add_a_record("server.local", "192.168.1.100")
            print(f"A record added: {success}")

            # Add CNAME record
            success = dns.add_cname_record("www.local", "server.local")
            print(f"CNAME record added: {success}")

            # Check blocking status
            status = dns.get_blocking_status()
            print(f"Blocking: {status.blocking}")

            # Disable blocking for 5 minutes
            status = dns.disable_blocking(timer=300)
            print(f"Blocking disabled for {status.timer} seconds")

            # Re-enable blocking permanently
            status = dns.enable_blocking()
            print(f"Blocking enabled: {status.blocking}")
        ```
    """

    BASE_URL = "/api/dns"
    CONFIG_URL = "/api/config/dns"

    def get_config(self) -> DNSConfig:
        """Get Pi-hole DNS configuration.

        Returns:
            DNSConfig: Complete DNS configuration information including
            upstream servers, custom records, and settings.

        Raises:
            PiHoleConnectionError: If connection to Pi-hole fails.
            PiHoleAuthenticationError: If authentication fails.
            PiHoleAPIError: If the API request fails.

        Examples:
            ```python
            # Get DNS configuration
            config = dns.get_config()
            print(f"Upstream servers: {config.upstreams}")
            print(f"DNS port: {config.port}")
            print(f"Query logging: {config.query_logging}")
            print(f"DNSSEC: {config.dnssec}")
            print(f"Blocking active: {config.blocking_active}")

            # Access all DNS records
            for record in config.records:
                print(f"{record.record_type}: {record.domain} -> {record.target}")

            # Access A records only (backward compatibility)
            for host in config.hosts:
                print(f"A: {host.domain} -> {host.target}")

            # Access CNAME records only (backward compatibility)
            for cname in config.cname_records:
                print(f"CNAME: {cname.domain} -> {cname.target}")
            ```
        """
        # Use PiHoleConfig to get DNS configuration
        config_client = PiHoleConfig(self._client)
        config_data = config_client.get_config("dns")

        # Extract DNS configuration from the response
        dns_config = config_data["dns"]

        # Create DNSConfig object with parsed records
        return DNSConfig.from_raw_config(dns_config)

    def get_records(self, record_type: str | None = None) -> list[DNSRecord]:
        """Get all custom DNS records (A records and CNAME records).

        Args:
            record_type: Optional record type filter. Use "A" for A records only,
                 "CNAME" for CNAME records only, or None for all records.

        Returns:
            List of DNSRecord objects containing domain, target, and record type.
            If record_type is specified, only records of that type are returned.

        Raises:
            PiHoleConnectionError: If connection to Pi-hole fails.
            PiHoleAuthenticationError: If authentication fails.
            PiHoleAPIError: If the API request fails.
            ValueError: If an invalid record type is specified.

        Examples:
            ```python
            # Get all custom DNS records
            records = dns.get_records()
            for record in records:
                print(f"{record.record_type}: {record.domain} -> {record.target}")

            # Get only A records
            a_records = dns.get_records(record_type="A")
            for record in a_records:
                print(f"A: {record.domain} -> {record.target}")

            # Get only CNAME records
            cname_records = dns.get_records(record_type="CNAME")
            for record in cname_records:
                print(f"CNAME: {record.domain} -> {record.target}")
            ```
        """
        # Validate record_type parameter
        if record_type is not None and record_type not in ["A", "CNAME"]:
            raise ValueError(
                f"Invalid record type '{record_type}'. Must be 'A', 'CNAME', or None."
            )

        config = self.get_config()

        # Filter records by type if specified
        if record_type is None:
            return config.records
        return [
            record for record in config.records if record.record_type == record_type
        ]

    def add_a_record(self, domain: str, ip: str) -> bool:
        """Add a custom A record for local domain resolution.

        Creates a custom A record that maps a domain name to an IPv4 address.
        This allows Pi-hole to resolve the domain locally instead of forwarding
        the query to upstream DNS servers.

        Args:
            domain: Domain name to create A record for (e.g., "server.local").
            ip: IPv4 address to map the domain to (e.g., "192.168.1.100").

        Returns:
            True if the A record was added successfully.

        Raises:
            PiHoleConnectionError: If connection to Pi-hole fails.
            PiHoleAuthenticationError: If authentication fails.
            PiHoleAPIError: If the API request fails.

        Examples:
            ```python
            # Add A record for local server
            success = dns.add_a_record("server.local", "192.168.1.100")
            if success:
                print("A record added successfully")

            # Add A record for NAS
            success = dns.add_a_record("nas.local", "192.168.1.50")
            ```
        """
        # Format as "ip domain" for the API
        record_value = f"{ip} {domain}"
        encoded_record = quote(record_value, safe="")

        response = make_pihole_request(
            self._client,
            "PUT",
            f"{self.CONFIG_URL}/hosts/{encoded_record}",
        )
        # PUT returns 201 Created on success
        return response.status_code == 201

    def remove_a_record(self, domain: str, ip: str) -> bool:
        """Remove a custom A record.

        Removes an existing A record from Pi-hole's custom DNS configuration.
        Both the domain name and IP address must match exactly for removal.

        Args:
            domain: Domain name of the A record to remove.
            ip: IPv4 address of the A record to remove.

        Returns:
            True if the A record was removed successfully.

        Raises:
            PiHoleConnectionError: If connection to Pi-hole fails.
            PiHoleAuthenticationError: If authentication fails.
            PiHoleAPIError: If the API request fails.

        Examples:
            ```python
            # Remove A record
            success = dns.remove_a_record("server.local", "192.168.1.100")
            if success:
                print("A record removed successfully")
            ```
        """
        # Format as "ip domain" for the API
        record_value = f"{ip} {domain}"
        encoded_record = quote(record_value, safe="")

        response = make_pihole_request(
            self._client,
            "DELETE",
            f"{self.CONFIG_URL}/hosts/{encoded_record}",
        )
        # DELETE returns 204 No Content on success
        return response.status_code == 204

    def add_cname_record(self, domain: str, target: str) -> bool:
        """Add a custom CNAME record for domain aliasing.

        Creates a CNAME (Canonical Name) record that makes one domain name
        an alias for another. When the source domain is queried, Pi-hole
        will return the IP address of the target domain.

        Args:
            domain: Source domain name (the alias).
            target: Target domain name (what the alias points to).

        Returns:
            True if the CNAME record was added successfully.

        Raises:
            PiHoleConnectionError: If connection to Pi-hole fails.
            PiHoleAuthenticationError: If authentication fails.
            PiHoleAPIError: If the API request fails.

        Examples:
            ```python
            # Create alias for existing server
            success = dns.add_cname_record("www.local", "server.local")
            if success:
                print("CNAME record added successfully")

            # Create alias for NAS
            success = dns.add_cname_record("files.local", "nas.local")
            ```
        """
        # Format as "domain,target" for the API
        record_value = f"{domain},{target}"
        encoded_record = quote(record_value, safe="")

        response = make_pihole_request(
            self._client,
            "PUT",
            f"{self.CONFIG_URL}/cnameRecords/{encoded_record}",
        )
        # PUT returns 201 Created on success
        return response.status_code == 201

    def remove_cname_record(self, domain: str, target: str) -> bool:
        """Remove a custom CNAME record.

        Removes an existing CNAME record from Pi-hole's custom DNS configuration.
        Both the source domain and target domain must match exactly for removal.

        Args:
            domain: Source domain name of the CNAME record to remove.
            target: Target domain name of the CNAME record to remove.

        Returns:
            True if the CNAME record was removed successfully.

        Raises:
            PiHoleConnectionError: If connection to Pi-hole fails.
            PiHoleAuthenticationError: If authentication fails.
            PiHoleAPIError: If the API request fails.

        Examples:
            ```python
            # Remove CNAME record
            success = dns.remove_cname_record("www.local", "server.local")
            if success:
                print("CNAME record removed successfully")
            ```
        """
        # Format as "domain,target" for the API
        record_value = f"{domain},{target}"
        encoded_record = quote(record_value, safe="")

        response = make_pihole_request(
            self._client,
            "DELETE",
            f"{self.CONFIG_URL}/cnameRecords/{encoded_record}",
        )
        # DELETE returns 204 No Content on success
        return response.status_code == 204

    def get_blocking_status(self) -> DNSBlockingStatus:
        """Get DNS blocking status.

        Returns:
            DNSBlockingStatus: Current blocking status including whether blocking
            is enabled and any temporary disable timer.

        Raises:
            PiHoleConnectionError: If connection to Pi-hole fails.
            PiHoleAuthenticationError: If authentication fails.
            PiHoleAPIError: If the API request fails.

        Examples:
            ```python
            # Check blocking status
            status = dns.get_blocking_status()
            print(f"Blocking: {status.blocking}")
            if status.timer:
                print(f"Temporarily disabled for {status.timer} seconds")
            ```
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

        Change the current blocking mode by setting blocking to the desired value.
        The optional timer parameter can be used to set a timer. Once this timer
        elapses, the opposite blocking mode is automatically set.

        Args:
            blocking: Whether to enable (True) or disable (False) blocking.
                     Defaults to True (enabled).
            timer: Optional timer in seconds. If provided, the blocking status
                  will automatically revert after this many seconds. Set to None
                  to make the change permanent. Defaults to None.

        Returns:
            DNSBlockingStatus: Updated blocking status including any active timer.

        Raises:
            PiHoleConnectionError: If connection to Pi-hole fails.
            PiHoleAuthenticationError: If authentication fails.
            PiHoleAPIError: If the API request fails.

        Examples:
            ```python
            # Enable blocking permanently
            status = dns.set_blocking_status(blocking=True)
            print(f"Blocking enabled: {status.blocking}")

            # Disable blocking for 5 minutes
            status = dns.set_blocking_status(blocking=False, timer=300)
            print(f"Blocking disabled for {status.timer} seconds")

            # Enable blocking permanently (cancel any timer)
            status = dns.set_blocking_status(blocking=True, timer=None)
            print(f"Blocking enabled permanently")
            ```
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

        Convenience method to enable Pi-hole's DNS blocking functionality.

        Args:
            timer: Optional timer in seconds. If provided, blocking will be
                  automatically disabled after this many seconds. Set to None
                  to enable permanently. Defaults to None.

        Returns:
            DNSBlockingStatus: Updated blocking status.

        Raises:
            PiHoleConnectionError: If connection to Pi-hole fails.
            PiHoleAuthenticationError: If authentication fails.
            PiHoleAPIError: If the API request fails.

        Examples:
            ```python
            # Enable blocking permanently
            status = dns.enable_blocking()

            # Enable blocking for 1 hour, then auto-disable
            status = dns.enable_blocking(timer=3600)
            ```
        """
        return self.set_blocking_status(blocking=True, timer=timer)

    def disable_blocking(self, timer: int | None = None) -> DNSBlockingStatus:
        """Disable DNS blocking.

        Convenience method to disable Pi-hole's DNS blocking functionality.

        Args:
            timer: Optional timer in seconds. If provided, blocking will be
                  automatically re-enabled after this many seconds. Set to None
                  to disable permanently. Defaults to None.

        Returns:
            DNSBlockingStatus: Updated blocking status.

        Raises:
            PiHoleConnectionError: If connection to Pi-hole fails.
            PiHoleAuthenticationError: If authentication fails.
            PiHoleAPIError: If the API request fails.

        Examples:
            ```python
            # Disable blocking permanently
            status = dns.disable_blocking()

            # Disable blocking for 10 minutes, then auto-enable
            status = dns.disable_blocking(timer=600)
            ```
        """
        return self.set_blocking_status(blocking=False, timer=timer)
