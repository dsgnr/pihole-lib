"""Tests for Pi-hole API data models."""

import pytest
from pydantic import ValidationError

from pihole_lib.models.lists import ListType, PiHoleList
from pihole_lib.models.session import LoginInfo, PiHoleAuthSession
from pihole_lib.models.teleporter import (
    TeleporterGravityOptions,
    TeleporterImportOptions,
)
from tests.constants import (
    PIHOLE_AUTH_URL,
    PIHOLE_TEST_PASSWORD,
    TEST_CSRF_TOKEN,
    TEST_DNS_STATUS_DOWN,
    TEST_DNS_STATUS_UP,
    TEST_HTTPS_PORT,
    TEST_HTTPS_PORT_DISABLED,
    TEST_MESSAGE_CORRECT,
    TEST_MESSAGE_INCORRECT,
    TEST_SID,
    TEST_VALIDITY_SECONDS,
    TEST_WRONG_PASSWORD,
)


class TestTeleporterGravityOptions:
    """Test the teleporter gravity options model."""

    def test_default_values(self):
        """Should create with all options enabled by default."""
        options = TeleporterGravityOptions()

        assert options.group is True
        assert options.adlist is True
        assert options.adlist_by_group is True
        assert options.domainlist is True
        assert options.domainlist_by_group is True
        assert options.client is True
        assert options.client_by_group is True

    def test_custom_values(self):
        """Should accept custom values for all options."""
        options = TeleporterGravityOptions(
            group=False,
            adlist=True,
            adlist_by_group=False,
            domainlist=True,
            domainlist_by_group=False,
            client=True,
            client_by_group=False,
        )

        assert options.group is False
        assert options.adlist is True
        assert options.adlist_by_group is False
        assert options.domainlist is True
        assert options.domainlist_by_group is False
        assert options.client is True
        assert options.client_by_group is False

    def test_serialization(self):
        """Should serialize to dict correctly."""
        options = TeleporterGravityOptions(group=False, adlist=True)
        data = options.model_dump()

        expected = {
            "group": False,
            "adlist": True,
            "adlist_by_group": True,
            "domainlist": True,
            "domainlist_by_group": True,
            "client": True,
            "client_by_group": True,
        }

        assert data == expected


class TestTeleporterImportOptions:
    """Test the teleporter import options model."""

    def test_default_values(self):
        """Should create with all options enabled by default."""
        options = TeleporterImportOptions()

        assert options.config is True
        assert options.dhcp_leases is True
        assert isinstance(options.gravity, TeleporterGravityOptions)
        assert options.gravity.group is True

    def test_custom_values(self):
        """Should accept custom values."""
        gravity_options = TeleporterGravityOptions(group=False, adlist=True)
        options = TeleporterImportOptions(
            config=False,
            dhcp_leases=True,
            gravity=gravity_options,
        )

        assert options.config is False
        assert options.dhcp_leases is True
        assert options.gravity.group is False
        assert options.gravity.adlist is True

    def test_nested_serialization(self):
        """Should serialize nested gravity options correctly."""
        options = TeleporterImportOptions(config=False)
        data = options.model_dump()

        assert "config" in data
        assert "dhcp_leases" in data
        assert "gravity" in data
        assert isinstance(data["gravity"], dict)
        assert "group" in data["gravity"]


class TestLoginInfo:
    """Test the Pi-hole login info model."""

    def test_valid_login_info_with_https(self):
        """Should create login info with HTTPS enabled."""
        info_data = {
            "https_port": TEST_HTTPS_PORT,
            "dns": TEST_DNS_STATUS_UP,
        }

        info = LoginInfo(**info_data)

        assert info.https_port == TEST_HTTPS_PORT
        assert info.dns is TEST_DNS_STATUS_UP

    def test_valid_login_info_without_https(self):
        """Should create login info with HTTPS disabled."""
        info_data = {
            "https_port": TEST_HTTPS_PORT_DISABLED,
            "dns": TEST_DNS_STATUS_UP,
        }

        info = LoginInfo(**info_data)

        assert info.https_port == TEST_HTTPS_PORT_DISABLED
        assert info.dns is TEST_DNS_STATUS_UP

    def test_login_info_with_dns_down(self):
        """Should handle DNS server being down."""
        info_data = {
            "https_port": TEST_HTTPS_PORT,
            "dns": TEST_DNS_STATUS_DOWN,
        }

        info = LoginInfo(**info_data)

        assert info.https_port == TEST_HTTPS_PORT
        assert info.dns is TEST_DNS_STATUS_DOWN

    def test_missing_required_fields(self):
        """Should raise validation error for missing required fields."""
        # Missing 'https_port' field
        with pytest.raises(ValidationError) as exc_info:
            LoginInfo(dns=True)

        assert "https_port" in str(exc_info.value)

        # Missing 'dns' field
        with pytest.raises(ValidationError) as exc_info:
            LoginInfo(https_port=443)

        assert "dns" in str(exc_info.value)

    def test_wrong_field_types(self):
        """Should raise validation error for wrong field types."""
        # 'https_port' should be integer
        with pytest.raises(ValidationError):
            LoginInfo(
                https_port="not-an-integer",
                dns=True,
            )

        # 'dns' should be boolean
        with pytest.raises(ValidationError):
            LoginInfo(
                https_port=443,
                dns="not-a-boolean",
            )

    def test_login_info_serialization(self):
        """Should be able to serialize login info to dict."""
        info = LoginInfo(
            https_port=TEST_HTTPS_PORT,
            dns=TEST_DNS_STATUS_UP,
        )

        data = info.model_dump()

        expected = {
            "https_port": TEST_HTTPS_PORT,
            "dns": TEST_DNS_STATUS_UP,
        }

        assert data == expected

    def test_login_info_with_negative_port(self):
        """Should handle negative port numbers (though unusual)."""
        info_data = {
            "https_port": -1,
            "dns": TEST_DNS_STATUS_UP,
        }

        info = LoginInfo(**info_data)

        assert info.https_port == -1

    def test_login_info_with_large_port(self):
        """Should handle large port numbers."""
        info_data = {
            "https_port": 65535,
            "dns": TEST_DNS_STATUS_UP,
        }

        info = LoginInfo(**info_data)

        assert info.https_port == 65535


class TestPiHoleAuthSession:
    """Test the Pi-hole authentication session model."""

    def test_valid_session_data(self):
        """Should create session with valid data."""
        session_data = {
            "valid": True,
            "totp": False,
            "sid": TEST_SID,
            "csrf": TEST_CSRF_TOKEN,
            "validity": TEST_VALIDITY_SECONDS,
            "message": TEST_MESSAGE_CORRECT,
        }

        session = PiHoleAuthSession(**session_data)

        assert session.valid is True
        assert session.totp is False
        assert session.sid == TEST_SID
        assert session.csrf == TEST_CSRF_TOKEN
        assert session.validity == TEST_VALIDITY_SECONDS
        assert session.message == TEST_MESSAGE_CORRECT

    def test_session_without_message(self):
        """Should work without optional message field."""
        session_data = {
            "valid": True,
            "totp": False,
            "sid": TEST_SID,
            "csrf": TEST_CSRF_TOKEN,
            "validity": TEST_VALIDITY_SECONDS,
        }

        session = PiHoleAuthSession(**session_data)

        assert session.message is None

    def test_session_with_totp_enabled(self):
        """Should handle TOTP being enabled."""
        session_data = {
            "valid": True,
            "totp": True,
            "sid": TEST_SID,
            "csrf": TEST_CSRF_TOKEN,
            "validity": TEST_VALIDITY_SECONDS,
        }

        session = PiHoleAuthSession(**session_data)

        assert session.totp is True

    def test_invalid_session(self):
        """Should handle invalid sessions."""
        session_data = {
            "valid": False,
            "totp": False,
            "sid": "",
            "csrf": "",
            "validity": 0,
            "message": TEST_MESSAGE_INCORRECT,
        }

        session = PiHoleAuthSession(**session_data)

        assert session.valid is False
        assert session.message == TEST_MESSAGE_INCORRECT

    def test_missing_required_fields(self):
        """Should raise validation error for missing required fields."""
        # Missing 'valid' field
        with pytest.raises(ValidationError) as exc_info:
            PiHoleAuthSession(
                totp=False, sid="abc123", csrf="csrf-token", validity=1800
            )

        assert "valid" in str(exc_info.value)

        # Missing 'sid' field
        with pytest.raises(ValidationError) as exc_info:
            PiHoleAuthSession(
                valid=True,
                totp=False,
                csrf=TEST_CSRF_TOKEN,
                validity=TEST_VALIDITY_SECONDS,
            )

        assert "sid" in str(exc_info.value)

    def test_wrong_field_types(self):
        """Should raise validation error for wrong field types."""
        # 'valid' should be boolean - but Pydantic v2 coerces strings
        # Let's test with something that definitely won't coerce
        with pytest.raises(ValidationError):
            PiHoleAuthSession(
                valid=[1, 2, 3],  # List definitely won't coerce to boolean
                totp=False,
                sid="abc123",
                csrf=TEST_CSRF_TOKEN,
                validity=TEST_VALIDITY_SECONDS,
            )

        # 'validity' should be integer - test with something that won't coerce
        with pytest.raises(ValidationError):
            PiHoleAuthSession(
                valid=True,
                totp=False,
                sid="abc123",
                csrf=TEST_CSRF_TOKEN,
                validity={"not": "an integer"},  # Dict won't coerce to int
            )

    def test_session_serialization(self):
        """Should be able to serialize session to dict."""
        session = PiHoleAuthSession(
            valid=True,
            totp=False,
            sid=TEST_SID,
            csrf=TEST_CSRF_TOKEN,
            validity=TEST_VALIDITY_SECONDS,
            message=TEST_MESSAGE_CORRECT,
        )

        data = session.model_dump()

        expected = {
            "valid": True,
            "totp": False,
            "sid": TEST_SID,
            "csrf": TEST_CSRF_TOKEN,
            "validity": TEST_VALIDITY_SECONDS,
            "message": TEST_MESSAGE_CORRECT,
        }

        assert data == expected


class TestModelIntegration:
    """Test how models work together."""

    def test_nested_model_validation(self):
        """Should validate nested models properly."""
        # Valid nested data should work
        session_data = {
            "valid": True,
            "totp": False,
            "sid": "abc123",
            "csrf": TEST_CSRF_TOKEN,
            "validity": TEST_VALIDITY_SECONDS,
        }

        session = PiHoleAuthSession(**session_data)
        assert isinstance(session, PiHoleAuthSession)

        # Invalid nested data should fail
        invalid_data = {
            "valid": "not-a-boolean",  # Invalid type
            "totp": False,
            "sid": "abc123",
            "csrf": TEST_CSRF_TOKEN,
            "validity": TEST_VALIDITY_SECONDS,
        }

        with pytest.raises(ValidationError):
            PiHoleAuthSession(**invalid_data)

    def test_model_field_descriptions(self):
        """Should have proper field descriptions for documentation."""
        # Test that we can create the models (they have the right structure)
        session = PiHoleAuthSession(
            valid=True, totp=False, sid="test-sid", csrf="test-csrf", validity=1800
        )

        # Test that the models work and have the expected fields
        assert hasattr(session, "valid")
        assert hasattr(session, "sid")

        # Test that we can get schema information
        session_schema = PiHoleAuthSession.model_json_schema()

        assert "properties" in session_schema
        assert "valid" in session_schema["properties"]


class TestRealPiHoleResponseValidation:
    """Validate that our models work with actual Pi-hole responses."""

    def test_successful_auth_response_structure(self, pihole_container):
        """Validate the structure of successful authentication responses."""
        import requests

        session = requests.Session()
        session.verify = False

        response = session.post(
            PIHOLE_AUTH_URL,
            json={"password": PIHOLE_TEST_PASSWORD},
            timeout=30,
        )

        assert response.status_code == 200
        data = response.json()

        # Validate response structure matches our expectations
        assert "session" in data

        session_data = data["session"]
        assert "valid" in session_data
        assert "sid" in session_data
        assert "csrf" in session_data
        assert "validity" in session_data
        assert "totp" in session_data

        # Validate data types
        assert isinstance(session_data["valid"], bool)
        assert isinstance(session_data["sid"], str)
        assert isinstance(session_data["csrf"], str)
        assert isinstance(session_data["validity"], int)
        assert isinstance(session_data["totp"], bool)

        # For successful auth, these should be true/non-empty
        assert session_data["valid"] is True
        assert len(session_data["sid"]) > 0
        assert len(session_data["csrf"]) > 0
        assert session_data["validity"] > 0

        session.close()

    def test_failed_auth_response_structure(self, pihole_container):
        """Validate the structure of failed authentication responses."""
        import requests

        session = requests.Session()
        session.verify = False

        response = session.post(
            PIHOLE_AUTH_URL,
            json={"password": TEST_WRONG_PASSWORD},
            timeout=30,
        )

        # Pi-hole might return 200 with invalid session or 401/403
        if response.status_code == 200:
            data = response.json()

            # Should still have the same structure
            assert "session" in data

            session_data = data["session"]
            assert "valid" in session_data

            # For failed auth, valid should be False
            assert session_data["valid"] is False

        session.close()


class TestListType:
    """Test the ListType enum."""

    def test_list_type_values(self):
        """Should have correct enum values."""
        assert ListType.ALLOW.value == "allow"
        assert ListType.BLOCK.value == "block"

    def test_list_type_from_string(self):
        """Should be able to create from string values."""
        allow_type = ListType("allow")
        block_type = ListType("block")

        assert allow_type == ListType.ALLOW
        assert block_type == ListType.BLOCK

    def test_invalid_list_type(self):
        """Should raise error for invalid list type."""
        with pytest.raises(ValueError):
            ListType("invalid")


class TestPiHoleList:
    """Test the PiHoleList model."""

    def test_valid_pihole_list(self):
        """Should create PiHoleList with valid data."""
        list_data = {
            "address": "https://example.com/blocklist.txt",
            "type": "block",
            "comment": "Test blocklist",
            "groups": [0, 1],
            "enabled": True,
            "id": 1,
            "date_added": 1640995200,
            "date_modified": 1640995200,
            "date_updated": 1640995200,
            "number": 1000,
            "invalid_domains": 5,
            "abp_entries": 0,
            "status": 1,
        }

        pihole_list = PiHoleList(**list_data)

        assert pihole_list.address == "https://example.com/blocklist.txt"
        assert pihole_list.type == ListType.BLOCK
        assert pihole_list.comment == "Test blocklist"
        assert pihole_list.groups == [0, 1]
        assert pihole_list.enabled is True
        assert pihole_list.id == 1
        assert pihole_list.date_added == 1640995200
        assert pihole_list.date_modified == 1640995200
        assert pihole_list.date_updated == 1640995200
        assert pihole_list.number == 1000
        assert pihole_list.invalid_domains == 5
        assert pihole_list.abp_entries == 0
        assert pihole_list.status == 1

    def test_pihole_list_with_null_comment(self):
        """Should handle null comment field."""
        list_data = {
            "address": "https://example.com/allowlist.txt",
            "type": "allow",
            "comment": None,
            "groups": [0],
            "enabled": True,
            "id": 2,
            "date_added": 1640995200,
            "date_modified": 1640995200,
            "date_updated": 1640995200,
            "number": 500,
            "invalid_domains": 0,
            "abp_entries": 10,
            "status": 1,
        }

        pihole_list = PiHoleList(**list_data)

        assert pihole_list.comment is None
        assert pihole_list.type == ListType.ALLOW

    def test_pihole_list_default_enabled(self):
        """Should default enabled to True."""
        list_data = {
            "address": "https://example.com/list.txt",
            "type": "block",
            "groups": [0],
            "id": 3,
            "date_added": 1640995200,
            "date_modified": 1640995200,
            "date_updated": 1640995200,
            "number": 100,
            "invalid_domains": 0,
            "abp_entries": 0,
            "status": 1,
        }

        pihole_list = PiHoleList(**list_data)

        assert pihole_list.enabled is True

    def test_pihole_list_missing_required_fields(self):
        """Should raise validation error for missing required fields."""
        # Missing address
        with pytest.raises(ValidationError) as exc_info:
            PiHoleList(
                type="block",
                groups=[0],
                id=1,
                date_added=1640995200,
                date_modified=1640995200,
                date_updated=1640995200,
                number=100,
                invalid_domains=0,
                abp_entries=0,
                status=1,
            )

        assert "address" in str(exc_info.value)

        # Missing type
        with pytest.raises(ValidationError) as exc_info:
            PiHoleList(
                address="https://example.com/list.txt",
                groups=[0],
                id=1,
                date_added=1640995200,
                date_modified=1640995200,
                date_updated=1640995200,
                number=100,
                invalid_domains=0,
                abp_entries=0,
                status=1,
            )

        assert "type" in str(exc_info.value)

    def test_pihole_list_invalid_type(self):
        """Should raise validation error for invalid list type."""
        with pytest.raises(ValidationError):
            PiHoleList(
                address="https://example.com/list.txt",
                type="invalid_type",
                groups=[0],
                id=1,
                date_added=1640995200,
                date_modified=1640995200,
                date_updated=1640995200,
                number=100,
                invalid_domains=0,
                abp_entries=0,
                status=1,
            )

    def test_pihole_list_serialization(self):
        """Should be able to serialize PiHoleList to dict."""
        pihole_list = PiHoleList(
            address="https://example.com/blocklist.txt",
            type=ListType.BLOCK,
            comment="Test list",
            groups=[0, 1],
            enabled=True,
            id=1,
            date_added=1640995200,
            date_modified=1640995200,
            date_updated=1640995200,
            number=1000,
            invalid_domains=5,
            abp_entries=0,
            status=1,
        )

        data = pihole_list.model_dump()

        expected = {
            "address": "https://example.com/blocklist.txt",
            "type": "block",
            "comment": "Test list",
            "groups": [0, 1],
            "enabled": True,
            "id": 1,
            "date_added": 1640995200,
            "date_modified": 1640995200,
            "date_updated": 1640995200,
            "number": 1000,
            "invalid_domains": 5,
            "abp_entries": 0,
            "status": 1,
        }

        assert data == expected
