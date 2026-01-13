"""DNS models."""

from typing import Any

from pydantic import Field

from pihole_lib.models.base import StrictModel, TimedResponse


class DNSRecord(StrictModel):
    """DNS record information."""

    domain: str = Field(..., description="Domain name")
    target: str = Field(
        ..., description="Target (IP address for A records, domain for CNAME records)"
    )
    record_type: str = Field(..., description="Record type ('A' or 'CNAME')")


class DNSConfig(StrictModel):
    """DNS configuration information."""

    upstreams: list[str] = Field(..., description="List of upstream DNS servers")
    records: list[DNSRecord] = Field(..., description="List of custom DNS records")
    port: int = Field(..., description="DNS port number")
    query_logging: bool = Field(
        alias="queryLogging", description="Whether DNS query logging is enabled"
    )
    dnssec: bool = Field(..., description="Whether DNSSEC validation is enabled")
    blocking: dict[str, Any] = Field(..., description="DNS blocking configuration")

    @property
    def blocking_active(self) -> bool:
        """Whether DNS blocking is active."""
        return bool(self.blocking.get("active", False))

    @property
    def hosts(self) -> list[DNSRecord]:
        """List of A records (host entries)."""
        return [r for r in self.records if r.record_type == "A"]

    @property
    def cname_records(self) -> list[DNSRecord]:
        """List of CNAME records."""
        return [r for r in self.records if r.record_type == "CNAME"]

    @classmethod
    def from_raw_config(cls, raw_config: dict[str, Any]) -> "DNSConfig":
        """Create DNSConfig from raw API response."""
        records = []
        for host_entry in raw_config.get("hosts", []):
            if " " in host_entry:
                ip, domain = host_entry.split(" ", 1)
                records.append(DNSRecord(domain=domain, target=ip, record_type="A"))
        for cname_entry in raw_config.get("cnameRecords", []):
            if "," in cname_entry:
                domain, target = cname_entry.split(",", 1)
                records.append(
                    DNSRecord(domain=domain, target=target, record_type="CNAME")
                )
        return cls(
            upstreams=raw_config.get("upstreams", []),
            records=records,
            port=raw_config.get("port", 53),
            queryLogging=raw_config.get("queryLogging", False),
            dnssec=raw_config.get("dnssec", False),
            blocking=raw_config.get("blocking", {}),
        )


class DNSConfigInfo(StrictModel):
    """DNS configuration response information."""

    config: dict = Field(..., description="DNS configuration data")


class DNSBlockingStatus(TimedResponse):
    """DNS blocking status information."""

    blocking: str = Field(..., description="Blocking status ('enabled' or 'disabled')")
    timer: int | None = Field(
        None, description="Timer for temporary disable (seconds remaining)"
    )
