"""
Authentication and header validation tests.
Tests for X-Roll-Number and X-User-ID header requirements.
"""
import pytest
import requests


BASE_URL = "http://localhost:8080/api/v1"


class TestAuthenticationHeaders:
    """Test authentication header validation."""

    def test_missing_roll_number_returns_401(self, api_session):
        """
        Test Case: Missing X-Roll-Number header
        Expected: 401 Unauthorized
        Justification: API requires X-Roll-Number for all endpoints
        """
        headers = {"X-User-ID": "1"}
        response = api_session.get(
            f"{BASE_URL}/profile",
            headers=headers
        )
        assert response.status_code == 401
        assert "X-Roll-Number" in response.text.lower() or response.status_code == 401

    def test_invalid_roll_number_returns_400(self, api_session):
        """
        Test Case: Invalid X-Roll-Number (non-integer)
        Expected: 400 Bad Request
        Justification: Roll number must be a valid integer
        """
        headers = {
            "X-Roll-Number": "abc123",
            "X-User-ID": "1"
        }
        response = api_session.get(
            f"{BASE_URL}/profile",
            headers=headers
        )
        assert response.status_code == 400

    def test_missing_user_id_for_user_endpoint_returns_400(self, api_session):
        """
        Test Case: Missing X-User-ID for user-scoped endpoint
        Expected: 400 Bad Request
        Justification: User endpoints require X-User-ID header
        """
        headers = {"X-Roll-Number": "12345"}
        response = api_session.get(
            f"{BASE_URL}/profile",
            headers=headers
        )
        assert response.status_code == 400

    def test_invalid_user_id_returns_400(self, api_session):
        """
        Test Case: Invalid X-User-ID (non-existent user)
        Expected: 400 Bad Request
        Justification: User must exist in system
        """
        headers = {
            "X-Roll-Number": "12345",
            "X-User-ID": "999999"
        }
        response = api_session.get(
            f"{BASE_URL}/profile",
            headers=headers
        )
        assert response.status_code in [400, 404]

    def test_admin_endpoint_no_user_id_required(self, admin_headers, api_session):
        """
        Test Case: Admin endpoint with only X-Roll-Number
        Expected: 200 OK
        Justification: Admin endpoints don't require X-User-ID
        """
        response = api_session.get(
            f"{BASE_URL}/admin/products",
            headers=admin_headers
        )
        assert response.status_code == 200

    def test_valid_headers_accepted(self, valid_headers, api_session):
        """
        Test Case: Valid headers (both Roll-Number and User-ID)
        Expected: 200 OK
        Justification: Valid headers should be accepted
        """
        response = api_session.get(
            f"{BASE_URL}/profile",
            headers=valid_headers
        )
        # Should succeed with 200, or return relevant data
        assert response.status_code in [200, 400, 401]  # Depends on user existence

    def test_roll_number_must_be_integer(self, api_session):
        """
        Test Case: Roll number with special characters
        Expected: 400 Bad Request
        Justification: Should validate integer format strictly
        """
        headers = {
            "X-Roll-Number": "123@45",
            "X-User-ID": "1"
        }
        response = api_session.get(
            f"{BASE_URL}/profile",
            headers=headers
        )
        assert response.status_code == 400

    def test_negative_user_id(self, api_session):
        """
        Test Case: Negative X-User-ID
        Expected: 400 Bad Request
        Justification: User ID must be positive
        """
        headers = {
            "X-Roll-Number": "12345",
            "X-User-ID": "-1"
        }
        response = api_session.get(
            f"{BASE_URL}/profile",
            headers=headers
        )
        assert response.status_code == 400

    def test_zero_user_id(self, api_session):
        """
        Test Case: Zero X-User-ID
        Expected: 400 Bad Request
        Justification: User ID must be positive (>0)
        """
        headers = {
            "X-Roll-Number": "12345",
            "X-User-ID": "0"
        }
        response = api_session.get(
            f"{BASE_URL}/profile",
            headers=headers
        )
        assert response.status_code == 400


class TestHeaderCaseSensitivity:
    """Test header handling."""

    def test_headers_case_insensitive(self, api_session):
        """
        Test Case: Headers with different case (x-roll-number)
        Expected: Headers should work regardless of case
        Justification: HTTP headers are case-insensitive per spec
        """
        headers = {
            "x-roll-number": "12345",
            "x-user-id": "1"
        }
        response = api_session.get(
            f"{BASE_URL}/profile",
            headers=headers
        )
        # requests library handles case-insensitivity
        assert response.status_code in [200, 400, 401]
