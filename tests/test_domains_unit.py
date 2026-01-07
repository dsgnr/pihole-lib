"""Unit tests for PiHoleDomains (no network calls)."""

from unittest.mock import Mock, patch
from urllib.parse import quote

import pytest

from pihole_lib import PiHoleClient, PiHoleDomains
from pihole_lib.exceptions import (
    PiHoleAPIError,
    PiHoleConnectionError,
    PiHoleServerError,
)
from pihole_lib.models import (
    Domain,
    DomainBatchDeleteItem,
    DomainKind,
    DomainMutationResponse,
    DomainType,
)

from .constants import (
    CONNECTION_FAILED_MESSAGE,
    PIHOLE_BASE_URL,
    TEST_SECRET_PASSWORD,
    TEST_SESSION_ID,
)


class TestPiHoleDomainsGetDomains:
    """Test domain retrieval functionality (no network calls)."""

    @patch("pihole_lib.domains.make_pihole_request")
    def test_get_domains_all_success(self, mock_request):
        """Should successfully get all domains."""
        mock_response_data = {
            "domains": [
                {
                    "domain": "example.com",
                    "unicode": "example.com",
                    "type": "allow",
                    "kind": "exact",
                    "comment": "Test domain",
                    "groups": [0],
                    "enabled": True,
                    "id": 1,
                    "date_added": 1767816399,
                    "date_modified": 1767816399,
                },
                {
                    "domain": "badsite.com",
                    "unicode": "badsite.com",
                    "type": "deny",
                    "kind": "exact",
                    "comment": "Blocked site",
                    "groups": [0],
                    "enabled": True,
                    "id": 2,
                    "date_added": 1767816403,
                    "date_modified": 1767816403,
                },
            ],
            "took": 0.001,
        }

        mock_response = Mock()
        mock_response.json.return_value = mock_response_data
        mock_request.return_value = mock_response

        client = PiHoleClient(PIHOLE_BASE_URL, TEST_SECRET_PASSWORD)
        client._session_id = TEST_SESSION_ID
        domains_client = PiHoleDomains(client)

        result = domains_client.get_domains()

        assert isinstance(result, list)
        assert len(result) == 2
        assert all(isinstance(domain, Domain) for domain in result)
        assert result[0].domain == "example.com"
        assert result[0].type == DomainType.ALLOW
        assert result[1].domain == "badsite.com"
        assert result[1].type == DomainType.DENY

        mock_request.assert_called_once_with(
            domains_client._client, "GET", "/api/domains"
        )

    @patch("pihole_lib.domains.make_pihole_request")
    def test_get_domains_with_type_filter(self, mock_request):
        """Should filter domains by type."""
        mock_response_data = {
            "domains": [
                {
                    "domain": "example.com",
                    "unicode": "example.com",
                    "type": "allow",
                    "kind": "exact",
                    "comment": "Test domain",
                    "groups": [0],
                    "enabled": True,
                    "id": 1,
                    "date_added": 1767816399,
                    "date_modified": 1767816399,
                }
            ],
            "took": 0.001,
        }

        mock_response = Mock()
        mock_response.json.return_value = mock_response_data
        mock_request.return_value = mock_response

        client = PiHoleClient(PIHOLE_BASE_URL, TEST_SECRET_PASSWORD)
        client._session_id = TEST_SESSION_ID
        domains_client = PiHoleDomains(client)

        result = domains_client.get_domains(domain_type=DomainType.ALLOW)

        assert len(result) == 1
        assert result[0].type == DomainType.ALLOW

        mock_request.assert_called_once_with(
            domains_client._client, "GET", "/api/domains/allow"
        )

    @patch("pihole_lib.domains.make_pihole_request")
    def test_get_domains_connection_error(self, mock_request):
        """Should raise PiHoleConnectionError on connection failure."""
        mock_request.side_effect = PiHoleConnectionError(CONNECTION_FAILED_MESSAGE)

        client = PiHoleClient(PIHOLE_BASE_URL, TEST_SECRET_PASSWORD)
        client._session_id = TEST_SESSION_ID
        domains_client = PiHoleDomains(client)

        with pytest.raises(PiHoleConnectionError, match=CONNECTION_FAILED_MESSAGE):
            domains_client.get_domains()


class TestPiHoleDomainsGetDomain:
    """Test single domain retrieval functionality."""

    @patch("pihole_lib.domains.make_pihole_request")
    def test_get_domain_found(self, mock_request):
        """Should return domain when found."""
        mock_response_data = {
            "domains": [
                {
                    "domain": "example.com",
                    "unicode": "example.com",
                    "type": "allow",
                    "kind": "exact",
                    "comment": "Test domain",
                    "groups": [0],
                    "enabled": True,
                    "id": 1,
                    "date_added": 1767816399,
                    "date_modified": 1767816399,
                }
            ],
            "took": 0.001,
        }

        mock_response = Mock()
        mock_response.json.return_value = mock_response_data
        mock_request.return_value = mock_response

        client = PiHoleClient(PIHOLE_BASE_URL, TEST_SECRET_PASSWORD)
        client._session_id = TEST_SESSION_ID
        domains_client = PiHoleDomains(client)

        result = domains_client.get_domain(
            "example.com", DomainType.ALLOW, DomainKind.EXACT
        )

        assert result is not None
        assert isinstance(result, Domain)
        assert result.domain == "example.com"

    @patch("pihole_lib.domains.make_pihole_request")
    def test_get_domain_not_found(self, mock_request):
        """Should return None when domain not found."""
        mock_response_data = {"domains": [], "took": 0.001}

        mock_response = Mock()
        mock_response.json.return_value = mock_response_data
        mock_request.return_value = mock_response

        client = PiHoleClient(PIHOLE_BASE_URL, TEST_SECRET_PASSWORD)
        client._session_id = TEST_SESSION_ID
        domains_client = PiHoleDomains(client)

        result = domains_client.get_domain(
            "nonexistent.com", DomainType.ALLOW, DomainKind.EXACT
        )

        assert result is None


class TestPiHoleDomainsAddDomain:
    """Test domain addition functionality."""

    @patch("pihole_lib.domains.make_pihole_request")
    def test_add_domain_success(self, mock_request):
        """Should successfully add a domain."""
        mock_response_data = {
            "domains": [
                {
                    "domain": "newsite.com",
                    "unicode": "newsite.com",
                    "type": "deny",
                    "kind": "exact",
                    "comment": "New blocked site",
                    "groups": [0],
                    "enabled": True,
                    "id": 3,
                    "date_added": 1767816500,
                    "date_modified": 1767816500,
                }
            ],
            "processed": {"errors": [], "success": [{"item": "newsite.com"}]},
            "took": 0.005,
        }

        mock_response = Mock()
        mock_response.json.return_value = mock_response_data
        mock_request.return_value = mock_response

        client = PiHoleClient(PIHOLE_BASE_URL, TEST_SECRET_PASSWORD)
        client._session_id = TEST_SESSION_ID
        domains_client = PiHoleDomains(client)

        result = domains_client.add_domain(
            domain="newsite.com",
            domain_type=DomainType.DENY,
            domain_kind=DomainKind.EXACT,
            comment="New blocked site",
            groups=[0],
            enabled=True,
        )

        assert isinstance(result, DomainMutationResponse)
        assert len(result.domains) == 1
        assert result.domains[0].domain == "newsite.com"
        assert len(result.processed.success) == 1
        assert len(result.processed.errors) == 0

        expected_payload = {
            "domain": "newsite.com",
            "comment": "New blocked site",
            "groups": [0],
            "enabled": True,
        }
        mock_request.assert_called_once_with(
            domains_client._client,
            "POST",
            "/api/domains/deny/exact",
            json=expected_payload,
        )


class TestPiHoleDomainsUpdateDomain:
    """Test domain update functionality."""

    @patch("pihole_lib.domains.make_pihole_request")
    def test_update_domain_success(self, mock_request):
        """Should successfully update a domain."""
        mock_response_data = {
            "domains": [
                {
                    "domain": "example.com",
                    "unicode": "example.com",
                    "type": "allow",
                    "kind": "exact",
                    "comment": "Updated comment",
                    "groups": [0],
                    "enabled": False,
                    "id": 1,
                    "date_added": 1767816399,
                    "date_modified": 1767816600,
                }
            ],
            "processed": {"errors": [], "success": [{"item": "example.com"}]},
            "took": 0.004,
        }

        mock_response = Mock()
        mock_response.json.return_value = mock_response_data
        mock_request.return_value = mock_response

        client = PiHoleClient(PIHOLE_BASE_URL, TEST_SECRET_PASSWORD)
        client._session_id = TEST_SESSION_ID
        domains_client = PiHoleDomains(client)

        result = domains_client.update_domain(
            domain="example.com",
            domain_type=DomainType.ALLOW,
            domain_kind=DomainKind.EXACT,
            comment="Updated comment",
            enabled=False,
        )

        assert isinstance(result, DomainMutationResponse)
        assert result.domains[0].comment == "Updated comment"
        assert result.domains[0].enabled is False

        expected_encoded = quote("example.com", safe="")
        expected_payload = {
            "comment": "Updated comment",
            "enabled": False,
        }
        mock_request.assert_called_once_with(
            domains_client._client,
            "PUT",
            f"/api/domains/allow/exact/{expected_encoded}",
            json=expected_payload,
        )


class TestPiHoleDomainsDeleteDomain:
    """Test domain deletion functionality."""

    @patch("pihole_lib.domains.make_pihole_request")
    def test_delete_domain_success(self, mock_request):
        """Should successfully delete a domain."""
        mock_response = Mock()
        mock_request.return_value = mock_response

        client = PiHoleClient(PIHOLE_BASE_URL, TEST_SECRET_PASSWORD)
        client._session_id = TEST_SESSION_ID
        domains_client = PiHoleDomains(client)

        # Should not raise any exception
        domains_client.delete_domain("badsite.com", DomainType.DENY, DomainKind.EXACT)

        expected_encoded = quote("badsite.com", safe="")
        mock_request.assert_called_once_with(
            domains_client._client,
            "DELETE",
            f"/api/domains/deny/exact/{expected_encoded}",
        )


class TestPiHoleDomainsBatchDelete:
    """Test batch domain deletion functionality."""

    @patch("pihole_lib.domains.make_pihole_request")
    def test_batch_delete_domains_success(self, mock_request):
        """Should successfully batch delete domains."""
        mock_response = Mock()
        mock_response.status_code = 204  # No Content
        mock_request.return_value = mock_response

        client = PiHoleClient(PIHOLE_BASE_URL, TEST_SECRET_PASSWORD)
        client._session_id = TEST_SESSION_ID
        domains_client = PiHoleDomains(client)

        domains_to_delete = [
            DomainBatchDeleteItem(
                item="site1.com", type=DomainType.DENY, kind=DomainKind.EXACT
            ),
            DomainBatchDeleteItem(
                item="site2.com", type=DomainType.DENY, kind=DomainKind.EXACT
            ),
        ]

        result = domains_client.batch_delete_domains(domains_to_delete)

        assert result is True

        expected_payload = [
            {"item": "site1.com", "type": "deny", "kind": "exact"},
            {"item": "site2.com", "type": "deny", "kind": "exact"},
        ]
        mock_request.assert_called_once_with(
            domains_client._client,
            "POST",
            "/api/domains:batchDelete",
            json=expected_payload,
        )

    @patch("pihole_lib.domains.make_pihole_request")
    def test_batch_delete_empty_list(self, mock_request):
        """Should handle empty domain list."""
        mock_response = Mock()
        mock_response.status_code = 204  # No Content
        mock_request.return_value = mock_response

        client = PiHoleClient(PIHOLE_BASE_URL, TEST_SECRET_PASSWORD)
        client._session_id = TEST_SESSION_ID
        domains_client = PiHoleDomains(client)

        result = domains_client.batch_delete_domains([])

        assert result is True

        mock_request.assert_called_once_with(
            domains_client._client, "POST", "/api/domains:batchDelete", json=[]
        )


class TestPiHoleDomainsExceptionHandling:
    """Test exception handling in domains operations."""

    @patch("pihole_lib.domains.make_pihole_request")
    def test_api_error_handling(self, mock_request):
        """Should properly handle API errors."""
        mock_request.side_effect = PiHoleAPIError("API Error")

        client = PiHoleClient(PIHOLE_BASE_URL, TEST_SECRET_PASSWORD)
        client._session_id = TEST_SESSION_ID
        domains_client = PiHoleDomains(client)

        with pytest.raises(PiHoleAPIError, match="API Error"):
            domains_client.get_domains()

    @patch("pihole_lib.domains.make_pihole_request")
    def test_server_error_handling(self, mock_request):
        """Should properly handle server errors."""
        mock_request.side_effect = PiHoleServerError("Server Error")

        client = PiHoleClient(PIHOLE_BASE_URL, TEST_SECRET_PASSWORD)
        client._session_id = TEST_SESSION_ID
        domains_client = PiHoleDomains(client)

        with pytest.raises(PiHoleServerError, match="Server Error"):
            domains_client.add_domain("test.com", DomainType.ALLOW, DomainKind.EXACT)

    @patch("pihole_lib.domains.make_pihole_request")
    def test_connection_error_handling(self, mock_request):
        """Should properly handle connection errors."""
        mock_request.side_effect = PiHoleConnectionError("Connection Error")

        client = PiHoleClient(PIHOLE_BASE_URL, TEST_SECRET_PASSWORD)
        client._session_id = TEST_SESSION_ID
        domains_client = PiHoleDomains(client)

        with pytest.raises(PiHoleConnectionError, match="Connection Error"):
            domains_client.delete_domain("test.com", DomainType.DENY, DomainKind.EXACT)
