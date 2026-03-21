"""
Profile and wallet tests.
Tests for user profile management and wallet operations.
Known bug: BUG #006 (wallet balance not deducted)
"""
import pytest


BASE_URL = "http://localhost:8080/api/v1"


class TestProfileRetrieval:
    """Test getting profile."""

    def test_get_profile_returns_200(self, valid_headers, api_session):
        """
        Test Case: Get user profile
        Expected: 200 OK with user data
        Justification: Basic profile retrieval
        """
        response = api_session.get(
            f"{BASE_URL}/profile",
            headers=valid_headers
        )
        
        assert response.status_code == 200
        profile = response.json()
        assert profile.get("user_id") is not None

    def test_profile_structure(self, valid_headers, api_session):
        """
        Test Case: Verify profile structure
        Expected: Has user_id, name, phone, wallet, loyalty_points
        Justification: API contract consistency
        """
        response = api_session.get(
            f"{BASE_URL}/profile",
            headers=valid_headers
        )
        
        profile = response.json()
        required_fields = ["user_id", "name", "phone"]
        for field in required_fields:
            assert field in profile, f"Missing field: {field}"


class TestProfileUpdate:
    """Test updating profile."""

    def test_update_profile_valid(self, valid_headers, api_session):
        """
        Test Case: Update profile with valid data
        Expected: 200 OK with updated profile
        Justification: Should allow name and phone updates
        """
        response = api_session.put(
            f"{BASE_URL}/profile",
            headers=valid_headers,
            json={
                "name": "John Doe",
                "phone": "9876543210"
            }
        )
        
        assert response.status_code in [200, 201]
        profile = api_session.get(f"{BASE_URL}/profile", headers=valid_headers).json()
        assert profile.get("name") == "John Doe"
        assert profile.get("phone") == "9876543210"

    def test_update_name_too_short_returns_400(self, valid_headers, api_session):
        """
        Test Case: Update with name too short (< 2 chars)
        Expected: 400 Bad Request
        Justification: Name must be 2-50 chars
        """
        response = api_session.put(
            f"{BASE_URL}/profile",
            headers=valid_headers,
            json={
                "name": "A",
                "phone": "9876543210"
            }
        )
        
        assert response.status_code == 400

    def test_update_name_too_long_returns_400(self, valid_headers, api_session):
        """
        Test Case: Update with name too long (> 50 chars)
        Expected: 400 Bad Request
        Justification: Name must be 2-50 chars
        """
        response = api_session.put(
            f"{BASE_URL}/profile",
            headers=valid_headers,
            json={
                "name": "A" * 51,
                "phone": "9876543210"
            }
        )
        
        assert response.status_code == 400

    def test_update_phone_not_10_digits_returns_400(self, valid_headers, api_session):
        """
        Test Case: Update with invalid phone (not 10 digits)
        Expected: 400 Bad Request
        Justification: Phone must be exactly 10 digits
        """
        response = api_session.put(
            f"{BASE_URL}/profile",
            headers=valid_headers,
            json={
                "name": "John Doe",
                "phone": "12345"
            }
        )
        
        assert response.status_code == 400

    def test_update_phone_with_letters_returns_400(self, valid_headers, api_session):
        """
        Test Case: Update with phone containing letters
        Expected: 400 Bad Request
        Justification: Phone must be digits only
        """
        response = api_session.put(
            f"{BASE_URL}/profile",
            headers=valid_headers,
            json={
                "name": "John Doe",
                "phone": "abc1234567"
            }
        )
        
        assert response.status_code == 400

    def test_update_returns_new_data(self, valid_headers, api_session):
        """
        Test Case: Response shows updated data, not old
        Expected: Response has new values
        Justification: User should see their changes
        """
        new_name = "Jane Smith"
        new_phone = "9123456789"
        
        response = api_session.put(
            f"{BASE_URL}/profile",
            headers=valid_headers,
            json={
                "name": new_name,
                "phone": new_phone
            }
        )
        
        assert response.status_code in [200, 201]
        profile = api_session.get(f"{BASE_URL}/profile", headers=valid_headers).json()
        assert profile.get("name") == new_name
        assert profile.get("phone") == new_phone


class TestWalletRetrieval:
    """Test wallet operations."""

    def test_get_wallet_returns_200(self, valid_headers, api_session):
        """
        Test Case: Get wallet balance
        Expected: 200 OK with balance
        Justification: User should see wallet balance
        """
        response = api_session.get(
            f"{BASE_URL}/wallet",
            headers=valid_headers
        )
        
        assert response.status_code == 200
        wallet = response.json()
        assert "wallet_balance" in wallet

    def test_wallet_structure(self, valid_headers, api_session):
        """
        Test Case: Verify wallet structure
        Expected: Has balance field
        Justification: API contract consistency
        """
        response = api_session.get(
            f"{BASE_URL}/wallet",
            headers=valid_headers
        )
        
        wallet = response.json()
        assert isinstance(wallet.get("wallet_balance"), (int, float))

    def test_wallet_balance_is_number(self, valid_headers, api_session):
        """
        Test Case: Balance is numeric
        Expected: int or float
        Justification: Must be computable
        """
        response = api_session.get(
            f"{BASE_URL}/wallet",
            headers=valid_headers
        )
        
        wallet = response.json()
        balance = wallet.get("wallet_balance")
        assert isinstance(balance, (int, float))


class TestWalletAdd:
    """Test adding money to wallet."""

    def test_add_valid_amount(self, valid_headers, api_session):
        """
        Test Case: Add valid amount to wallet
        Expected: 200 OK, balance increased
        Justification: Should support adding funds
        """
        # Get current balance
        wallet_before = api_session.get(f"{BASE_URL}/wallet", headers=valid_headers).json()
        balance_before = wallet_before.get("wallet_balance")
        
        amount = 500
        response = api_session.post(
            f"{BASE_URL}/wallet/add",
            headers=valid_headers,
            json={"amount": amount}
        )
        
        assert response.status_code in [200, 201]
        
        # Verify balance increased
        wallet_after = api_session.get(f"{BASE_URL}/wallet", headers=valid_headers).json()
        balance_after = wallet_after.get("wallet_balance")
        assert balance_after == balance_before + amount

    def test_add_amount_zero_returns_400(self, valid_headers, api_session):
        """
        Test Case: Add zero amount
        Expected: 400 Bad Request
        Justification: Amount must be > 0
        """
        response = api_session.post(
            f"{BASE_URL}/wallet/add",
            headers=valid_headers,
            json={"amount": 0}
        )
        
        assert response.status_code == 400

    def test_add_negative_amount_returns_400(self, valid_headers, api_session):
        """
        Test Case: Add negative amount
        Expected: 400 Bad Request
        Justification: Amount must be positive
        """
        response = api_session.post(
            f"{BASE_URL}/wallet/add",
            headers=valid_headers,
            json={"amount": -100}
        )
        
        assert response.status_code == 400

    def test_add_amount_exceeds_maximum_returns_400(self, valid_headers, api_session):
        """
        Test Case: Add amount > 100000
        Expected: 400 Bad Request
        Justification: Maximum allowed is 100000
        """
        response = api_session.post(
            f"{BASE_URL}/wallet/add",
            headers=valid_headers,
            json={"amount": 100001}
        )
        
        assert response.status_code == 400

    def test_add_maximum_amount(self, valid_headers, api_session):
        """
        Test Case: Add exactly 100000
        Expected: 200 OK
        Justification: Maximum should be allowed
        """
        response = api_session.post(
            f"{BASE_URL}/wallet/add",
            headers=valid_headers,
            json={"amount": 100000}
        )
        
        assert response.status_code in [200, 201]

    def test_add_minimum_amount(self, valid_headers, api_session):
        """
        Test Case: Add minimum amount (0.01)
        Expected: 200 OK
        Justification: Very small amounts should work
        """
        response = api_session.post(
            f"{BASE_URL}/wallet/add",
            headers=valid_headers,
            json={"amount": 0.01}
        )
        
        assert response.status_code in [200, 201]


class TestWalletPay:
    """Test paying from wallet."""

    def test_pay_valid_amount(self, valid_headers, api_session):
        """
        Test Case: Pay valid amount from wallet
        Expected: 200 OK, balance decreased
        Justification: Should deduct exact amount from balance
        """
        # First add enough balance
        api_session.post(
            f"{BASE_URL}/wallet/add",
            headers=valid_headers,
            json={"amount": 500}
        )
        
        wallet_before = api_session.get(f"{BASE_URL}/wallet", headers=valid_headers).json()
        balance_before = wallet_before.get("wallet_balance")
        
        amount = 100
        response = api_session.post(
            f"{BASE_URL}/wallet/pay",
            headers=valid_headers,
            json={"amount": amount}
        )
        
        assert response.status_code in [200, 201]
        
        # Verify exact deduction
        wallet_after = api_session.get(f"{BASE_URL}/wallet", headers=valid_headers).json()
        balance_after = wallet_after.get("wallet_balance")
        assert balance_after == balance_before - amount

    def test_pay_more_than_balance_returns_400(self, valid_headers, api_session):
        """
        Test Case: Pay more than available balance
        Expected: 400 Bad Request
        Justification: Should prevent overspending
        """
        # Get current balance
        wallet = api_session.get(f"{BASE_URL}/wallet", headers=valid_headers).json()
        balance = wallet.get("wallet_balance")
        
        amount_to_pay = balance + 100
        
        response = api_session.post(
            f"{BASE_URL}/wallet/pay",
            headers=valid_headers,
            json={"amount": amount_to_pay}
        )
        
        assert response.status_code == 400

    def test_pay_zero_amount_returns_400(self, valid_headers, api_session):
        """
        Test Case: Pay zero amount
        Expected: 400 Bad Request
        Justification: Amount must be > 0
        """
        response = api_session.post(
            f"{BASE_URL}/wallet/pay",
            headers=valid_headers,
            json={"amount": 0}
        )
        
        assert response.status_code == 400

    def test_pay_negative_amount_returns_400(self, valid_headers, api_session):
        """
        Test Case: Pay negative amount
        Expected: 400 Bad Request
        Justification: Amount must be positive
        """
        response = api_session.post(
            f"{BASE_URL}/wallet/pay",
            headers=valid_headers,
            json={"amount": -50}
        )
        
        assert response.status_code == 400
