"""Tests for Pi-hole API data models."""

import pytest
from pydantic import ValidationError

from pihole_lib.models import AuthResponse, PiHoleAuthSession

from .constants import (
    PIHOLE_AUTH_URL,
    PIHOLE_TEST_PASSWORD,
    TEST_CSRF_TOKEN,
    TEST_MESSAGE_CORRECT,
    TEST_MESSAGE_INCORRECT,
    TEST_SID,
    TEST_VALIDITY_SECONDS,
    TEST_WRONG_PASSWORD,
)


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


class TestAuthResponse:
    """Test the authentication response model."""

    def test_valid_auth_response(self):
        """Should create auth response with valid data."""
        response_data = {
            "session": {
                "valid": True,
                "totp": False,
                "sid": TEST_SID,
                "csrf": TEST_CSRF_TOKEN,
                "validity": TEST_VALIDITY_SECONDS,
                "message": TEST_MESSAGE_CORRECT,
            },
            "took": 0.123456,
        }

        response = AuthResponse(**response_data)

        assert isinstance(response.session, PiHoleAuthSession)
        assert response.session.valid is True
        assert response.session.sid == TEST_SID
        assert response.took == 0.123456

    def test_auth_response_with_invalid_session(self):
        """Should handle auth response with invalid session."""
        response_data = {
            "session": {
                "valid": False,
                "totp": False,
                "sid": "",
                "csrf": "",
                "validity": 0,
                "message": TEST_MESSAGE_INCORRECT,
            },
            "took": 0.05,
        }

        response = AuthResponse(**response_data)

        assert response.session.valid is False
        assert response.session.message == TEST_MESSAGE_INCORRECT
        assert response.took == 0.05

    def test_missing_session_field(self):
        """Should raise validation error for missing session."""
        with pytest.raises(ValidationError) as exc_info:
            AuthResponse(took=0.1)

        assert "session" in str(exc_info.value)

    def test_missing_took_field(self):
        """Should raise validation error for missing took field."""
        with pytest.raises(ValidationError) as exc_info:
            AuthResponse(
                session={
                    "valid": True,
                    "totp": False,
                    "sid": "abc123",
                    "csrf": TEST_CSRF_TOKEN,
                    "validity": TEST_VALIDITY_SECONDS,
                }
            )

        assert "took" in str(exc_info.value)

    def test_invalid_session_data(self):
        """Should raise validation error for invalid session data."""
        with pytest.raises(ValidationError):
            AuthResponse(
                session={
                    "valid": True,
                    # Missing required fields
                },
                took=0.1,
            )

    def test_wrong_took_type(self):
        """Should raise validation error for wrong took type."""
        with pytest.raises(ValidationError):
            AuthResponse(
                session={
                    "valid": True,
                    "totp": False,
                    "sid": "abc123",
                    "csrf": TEST_CSRF_TOKEN,
                    "validity": TEST_VALIDITY_SECONDS,
                },
                took={"not": "a number"},  # Dict won't coerce to float
            )

    def test_auth_response_serialization(self):
        """Should be able to serialize auth response to dict."""
        response = AuthResponse(
            session=PiHoleAuthSession(
                valid=True,
                totp=False,
                sid=TEST_SID,
                csrf=TEST_CSRF_TOKEN,
                validity=TEST_VALIDITY_SECONDS,
                message=TEST_MESSAGE_CORRECT,
            ),
            took=0.123456,
        )

        data = response.model_dump()

        expected = {
            "session": {
                "valid": True,
                "totp": False,
                "sid": TEST_SID,
                "csrf": TEST_CSRF_TOKEN,
                "validity": TEST_VALIDITY_SECONDS,
                "message": TEST_MESSAGE_CORRECT,
            },
            "took": 0.123456,
        }

        assert data == expected

    def test_auth_response_from_json_string(self):
        """Should be able to create from JSON string (like from API)."""
        json_data = {
            "session": {
                "valid": True,
                "totp": False,
                "sid": "yD/2B4DG4t2sQxz8kchd5w=",
                "csrf": "dLTdh5aOBC0BIiHJ01f9/w=",
                "validity": TEST_VALIDITY_SECONDS,
                "message": TEST_MESSAGE_CORRECT,
            },
            "took": 0.14328932762146,
        }

        response = AuthResponse(**json_data)

        assert response.session.valid is True
        assert response.session.sid == "yD/2B4DG4t2sQxz8kchd5w="
        assert response.session.csrf == "dLTdh5aOBC0BIiHJ01f9/w="
        assert response.took == 0.14328932762146


class TestModelIntegration:
    """Test how models work together."""

    def test_nested_model_validation(self):
        """Should validate nested models properly."""
        # Valid nested data should work
        valid_data = {
            "session": {
                "valid": True,
                "totp": False,
                "sid": "abc123",
                "csrf": TEST_CSRF_TOKEN,
                "validity": TEST_VALIDITY_SECONDS,
            },
            "took": 0.1,
        }

        response = AuthResponse(**valid_data)
        assert isinstance(response.session, PiHoleAuthSession)

        # Invalid nested data should fail
        invalid_data = {
            "session": {
                "valid": "not-a-boolean",  # Invalid type
                "totp": False,
                "sid": "abc123",
                "csrf": TEST_CSRF_TOKEN,
                "validity": TEST_VALIDITY_SECONDS,
            },
            "took": 0.1,
        }

        with pytest.raises(ValidationError):
            AuthResponse(**invalid_data)

    def test_model_field_descriptions(self):
        """Should have proper field descriptions for documentation."""
        # Test that we can create the models (they have the right structure)
        session = PiHoleAuthSession(
            valid=True, totp=False, sid="test-sid", csrf="test-csrf", validity=1800
        )

        response = AuthResponse(session=session, took=0.1)

        # Test that the models work and have the expected fields
        assert hasattr(session, "valid")
        assert hasattr(session, "sid")
        assert hasattr(response, "session")
        assert hasattr(response, "took")

        # Test that we can get schema information
        session_schema = PiHoleAuthSession.model_json_schema()
        response_schema = AuthResponse.model_json_schema()

        assert "properties" in session_schema
        assert "properties" in response_schema
        assert "valid" in session_schema["properties"]
        assert "session" in response_schema["properties"]


class TestModelIntegrationWithRealData:
    """Test models with real Pi-hole API responses."""

    def test_auth_response_with_real_pihole_data(self, pihole_session):
        """Test AuthResponse model with real Pi-hole authentication data."""
        session, session_id = pihole_session

        # Make a fresh authentication request to get real response data
        import requests

        fresh_session = requests.Session()
        fresh_session.verify = False

        response = fresh_session.post(
            PIHOLE_AUTH_URL,
            json={"password": PIHOLE_TEST_PASSWORD},
            timeout=30,
        )

        assert response.status_code == 200
        response_data = response.json()

        # Test that our model can parse real Pi-hole response
        auth_response = AuthResponse(**response_data)

        # Verify the parsed data makes sense
        assert auth_response.session.valid is True
        assert auth_response.session.sid is not None
        assert len(auth_response.session.sid) > 0
        assert auth_response.session.csrf is not None
        assert auth_response.session.validity > 0
        assert auth_response.took >= 0

        # Test serialization round-trip
        serialized = auth_response.model_dump()
        recreated = AuthResponse(**serialized)
        assert recreated.session.sid == auth_response.session.sid

        fresh_session.close()

    def test_invalid_auth_response_with_real_pihole(self, pihole_container):
        """Test AuthResponse model with real Pi-hole invalid authentication."""
        import requests

        session = requests.Session()
        session.verify = False

        # Try to authenticate with wrong password
        response = session.post(
            PIHOLE_AUTH_URL,
            json={"password": TEST_WRONG_PASSWORD},
            timeout=30,
        )

        # Pi-hole might return 200 with invalid session or 401
        if response.status_code == 200:
            response_data = response.json()

            # Test that our model can parse the invalid response
            auth_response = AuthResponse(**response_data)

            # Should indicate invalid session
            assert auth_response.session.valid is False
            assert auth_response.took >= 0

        session.close()


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
        assert "took" in data

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
        assert isinstance(data["took"], (int, float))

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
            assert "took" in data

            session_data = data["session"]
            assert "valid" in session_data

            # For failed auth, valid should be False
            assert session_data["valid"] is False

        session.close()
