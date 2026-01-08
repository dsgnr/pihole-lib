"""Pi-hole domain management operations."""

from urllib.parse import quote

from .base import BasePiHoleAPIClient
from .exceptions import PiHoleAPIError
from .models import (
    Domain,
    DomainBatchDeleteItem,
    DomainKind,
    DomainMutationResponse,
    DomainRequest,
    DomainsResponse,
    DomainType,
)
from .utils import make_pihole_request


class PiHoleDomains(BasePiHoleAPIClient):
    """Pi-hole domain management operations.

    This class provides methods to manage domains on your Pi-hole instance,
    including adding, updating, deleting, and retrieving domains with various
    filtering options.

    Examples::

        from pihole_lib import PiHoleClient, DomainType, DomainKind

        with PiHoleClient("http://192.168.1.100", password="secret") as client:
            domains = client.domains

            # Get all domains
            all_domains = domains.get_domains()

            # Get only allowed domains
            allowed_domains = domains.get_domains(domain_type=DomainType.ALLOW)

            # Get specific domain
            domain = domains.get_domain("example.com", DomainType.ALLOW, DomainKind.EXACT)

            # Add a new domain
            result = domains.add_domain(
                domain="badsite.com",
                domain_type=DomainType.DENY,
                domain_kind=DomainKind.EXACT,
                comment="Blocked site",
                groups=[0],
                enabled=True
            )

            # Update a domain
            updated = domains.update_domain(
                domain="example.com",
                domain_type=DomainType.ALLOW,
                domain_kind=DomainKind.EXACT,
                comment="Updated comment",
                enabled=False
            )

            # Delete a domain
            domains.delete_domain("badsite.com", DomainType.DENY, DomainKind.EXACT)

            # Batch delete domains
            domains.batch_delete_domains([
                DomainBatchDeleteItem(
                    item="site1.com",
                    type=DomainType.DENY,
                    kind=DomainKind.EXACT
                ),
                DomainBatchDeleteItem(
                    item="site2.com",
                    type=DomainType.DENY,
                    kind=DomainKind.EXACT
                )
            ])

    """

    BASE_URL = "/api/domains"

    def get_domains(
        self,
        domain_type: DomainType | None = None,
        domain_kind: DomainKind | None = None,
        domain: str | None = None,
    ) -> list[Domain]:
        """Get domains with optional filtering.

        Args:
            domain_type: Filter by domain type (allow/deny).
            domain_kind: Filter by domain kind (exact/regex).
            domain: Filter by specific domain name.

        Returns:
            List of Domain objects matching the filters.

        Raises:
            PiHoleAPIError: API request failed.
            PiHoleConnectionError: Connection failed.
            PiHoleServerError: Server error.

        Examples::

            # Get all domains
            all_domains = domains.get_domains()

            # Get only allowed domains
            allowed = domains.get_domains(domain_type=DomainType.ALLOW)

            # Get only exact domains
            exact = domains.get_domains(domain_kind=DomainKind.EXACT)

            # Get specific domain across all types/kinds
            specific = domains.get_domains(domain="example.com")

            # Get allowed exact domains
            allowed_exact = domains.get_domains(
                domain_type=DomainType.ALLOW,
                domain_kind=DomainKind.EXACT
            )

        """
        # Build the URL path based on filters
        path_parts = [self.BASE_URL]

        if domain_type:
            path_parts.append(domain_type.value)

        if domain_kind:
            path_parts.append(domain_kind.value)

        if domain:
            # URL encode the domain for safe transmission
            encoded_domain = quote(domain, safe="")
            path_parts.append(encoded_domain)

        url_path = "/".join(path_parts)

        response = make_pihole_request(self._client, "GET", url_path)
        data = response.json()
        domains_response = DomainsResponse(**data)
        return domains_response.domains

    def get_domain(
        self, domain: str, domain_type: DomainType, domain_kind: DomainKind
    ) -> Domain | None:
        """Get a specific domain by exact match.

        Args:
            domain: The domain name to retrieve.
            domain_type: Type of domain (allow/deny).
            domain_kind: Kind of domain (exact/regex).

        Returns:
            Domain object if found, None otherwise.

        Raises:
            PiHoleAPIError: API request failed.
            PiHoleConnectionError: Connection failed.
            PiHoleServerError: Server error.

        Examples::

            # Get specific allowed exact domain
            domain = domains.get_domain(
                "example.com",
                DomainType.ALLOW,
                DomainKind.EXACT
            )

            if domain:
                print(f"Found domain: {domain.domain}")
            else:
                print("Domain not found")

        """
        domains_list = self.get_domains(domain_type, domain_kind, domain)
        # Return the first match (should be unique)
        return domains_list[0] if domains_list else None

    def add_domain(
        self,
        domain: str,
        domain_type: DomainType,
        domain_kind: DomainKind,
        comment: str | None = None,
        groups: list[int] | None = None,
        enabled: bool = True,
    ) -> DomainMutationResponse:
        r"""Add a new domain.

        Args:
            domain: The domain name or regex pattern to add.
            domain_type: Type of domain (allow/deny).
            domain_kind: Kind of domain (exact/regex).
            comment: Optional comment for the domain.
            groups: List of group IDs. Defaults to [0] if not provided.
            enabled: Whether the domain is enabled. Defaults to True.

        Returns:
            DomainMutationResponse with the operation results.

        Raises:
            PiHoleAPIError: API request failed or domain already exists.
            PiHoleConnectionError: Connection failed.
            PiHoleServerError: Server error.

        Examples::

            # Add an exact blocked domain
            result = domains.add_domain(
                domain="badsite.com",
                domain_type=DomainType.DENY,
                domain_kind=DomainKind.EXACT,
                comment="Malicious site",
                groups=[0, 1],
                enabled=True
            )

            # Add a regex pattern
            result = domains.add_domain(
                domain=r".*\.ads\..*",
                domain_type=DomainType.DENY,
                domain_kind=DomainKind.REGEX,
                comment="Block ads subdomains"
            )

        """
        if groups is None:
            groups = [0]

        url_path = f"{self.BASE_URL}/{domain_type.value}/{domain_kind.value}"

        request_data = DomainRequest(
            domain=domain,
            type=None,
            kind=None,
            comment=comment,
            groups=groups,
            enabled=enabled,
        )

        # Convert to dict and remove None values
        payload = {k: v for k, v in request_data.model_dump().items() if v is not None}

        response = make_pihole_request(self._client, "POST", url_path, json=payload)
        data = response.json()
        return DomainMutationResponse(**data)

    def update_domain(
        self,
        domain: str,
        domain_type: DomainType,
        domain_kind: DomainKind,
        new_type: DomainType | None = None,
        new_kind: DomainKind | None = None,
        comment: str | None = None,
        groups: list[int] | None = None,
        enabled: bool | None = None,
    ) -> DomainMutationResponse:
        """Update an existing domain.

        Args:
            domain: The domain name to update.
            domain_type: Current type of domain (allow/deny).
            domain_kind: Current kind of domain (exact/regex).
            new_type: New type to move domain to (optional).
            new_kind: New kind to move domain to (optional).
            comment: New comment for the domain.
            groups: New list of group IDs.
            enabled: New enabled status.

        Returns:
            DomainMutationResponse with the operation results.

        Raises:
            PiHoleAPIError: API request failed or domain not found.
            PiHoleConnectionError: Connection failed.
            PiHoleServerError: Server error.

        Examples::

            # Update domain comment and disable it
            result = domains.update_domain(
                domain="example.com",
                domain_type=DomainType.ALLOW,
                domain_kind=DomainKind.EXACT,
                comment="Updated comment",
                enabled=False
            )

            # Move domain from allow to deny
            result = domains.update_domain(
                domain="example.com",
                domain_type=DomainType.ALLOW,
                domain_kind=DomainKind.EXACT,
                new_type=DomainType.DENY,
                new_kind=DomainKind.EXACT
            )

        """
        # URL encode the domain for safe transmission
        encoded_domain = quote(domain, safe="")
        url_path = (
            f"{self.BASE_URL}/{domain_type.value}/{domain_kind.value}/{encoded_domain}"
        )

        request_data = DomainRequest(
            domain=None,
            type=new_type,
            kind=new_kind,
            comment=comment,
            groups=groups,
            enabled=enabled,
        )

        # Convert to dict and remove None values
        payload = {k: v for k, v in request_data.model_dump().items() if v is not None}

        response = make_pihole_request(self._client, "PUT", url_path, json=payload)
        data = response.json()
        return DomainMutationResponse(**data)

    def delete_domain(
        self, domain: str, domain_type: DomainType, domain_kind: DomainKind
    ) -> None:
        r"""Delete a domain.

        Args:
            domain: The domain name to delete.
            domain_type: Type of domain (allow/deny).
            domain_kind: Kind of domain (exact/regex).

        Raises:
            PiHoleAPIError: API request failed or domain not found.
            PiHoleConnectionError: Connection failed.
            PiHoleServerError: Server error.

        Examples::

            # Delete an exact blocked domain
            domains.delete_domain(
                "badsite.com",
                DomainType.DENY,
                DomainKind.EXACT
            )

            # Delete a regex pattern
            domains.delete_domain(
                r".*\.ads\..*",
                DomainType.DENY,
                DomainKind.REGEX
            )

        """
        # URL encode the domain for safe transmission
        encoded_domain = quote(domain, safe="")
        url_path = (
            f"/api/domains/{domain_type.value}/{domain_kind.value}/{encoded_domain}"
        )

        make_pihole_request(self._client, "DELETE", url_path)

    def batch_delete_domains(self, domains: list[DomainBatchDeleteItem]) -> bool:
        r"""Delete multiple domains in a single request.

        Args:
            domains: List of DomainBatchDeleteItem objects specifying domains to delete.

        Returns:
            True if successful.

        Raises:
            PiHoleAPIError: API request failed.
            PiHoleConnectionError: Connection failed.
            PiHoleServerError: Server error.

        Examples::

            # Delete multiple domains
            success = domains.batch_delete_domains([
                DomainBatchDeleteItem(
                    item="site1.com",
                    type=DomainType.DENY,
                    kind=DomainKind.EXACT
                ),
                DomainBatchDeleteItem(
                    item="site2.com",
                    type=DomainType.DENY,
                    kind=DomainKind.EXACT
                ),
                DomainBatchDeleteItem(
                    item=r".*\.ads\..*",
                    type=DomainType.DENY,
                    kind=DomainKind.REGEX
                )
            ])
            print(f"Batch delete successful: {success}")

        """
        url_path = f"{self.BASE_URL}:batchDelete"

        # Convert to list of dicts
        payload = [domain.model_dump() for domain in domains]

        response = make_pihole_request(self._client, "POST", url_path, json=payload)

        if response.status_code == 204:  # No Content - success
            return True

        raise PiHoleAPIError(
            f"{response.json().get("error", {}).get('message', 'Unknown error')}"
        )
