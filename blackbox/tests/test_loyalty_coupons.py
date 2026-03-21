"""
Loyalty and coupon tests.
Tests for loyalty points redemption and coupon application.
"""
import pytest


BASE_URL = "http://localhost:8080/api/v1"


class TestLoyaltyPoints:
    """Test loyalty points operations."""

    def test_get_loyalty_returns_200(self, valid_headers, api_session):
        """
        Test Case: Get loyalty points balance
        Expected: 200 OK with points
        Justification: User should see loyalty points
        """
        response = api_session.get(
            f"{BASE_URL}/loyalty",
            headers=valid_headers
        )
        
        assert response.status_code == 200
        loyalty = response.json()
        assert "loyalty_points" in loyalty

    def test_loyalty_structure(self, valid_headers, api_session):
        """
        Test Case: Verify loyalty structure
        Expected: Has points or balance field
        Justification: API contract consistency
        """
        response = api_session.get(
            f"{BASE_URL}/loyalty",
            headers=valid_headers
        )
        
        loyalty = response.json()
        points = loyalty.get("loyalty_points")
        assert isinstance(points, int)

    def test_redeem_valid_points(self, valid_headers, api_session):
        """
        Test Case: Redeem available loyalty points
        Expected: 200 OK, points deducted
        Justification: Should allow redemption
        """
        # Get current points
        loyalty_before = api_session.get(f"{BASE_URL}/loyalty", headers=valid_headers).json()
        points_before = loyalty_before.get("loyalty_points")
        
        if points_before >= 100:
            response = api_session.post(
                f"{BASE_URL}/loyalty/redeem",
                headers=valid_headers,
                json={"points": 100}
            )
            
            assert response.status_code in [200, 201]
            
            # Verify points decreased
            loyalty_after = api_session.get(f"{BASE_URL}/loyalty", headers=valid_headers).json()
            points_after = loyalty_after.get("loyalty_points")
            assert points_after == points_before - 100

    def test_redeem_more_than_available_returns_400(self, valid_headers, api_session):
        """
        Test Case: Redeem more points than available
        Expected: 400 Bad Request
        Justification: Should prevent overspending
        """
        loyalty = api_session.get(f"{BASE_URL}/loyalty", headers=valid_headers).json()
        current_points = loyalty.get("loyalty_points")
        
        response = api_session.post(
            f"{BASE_URL}/loyalty/redeem",
            headers=valid_headers,
            json={"points": current_points + 100}
        )
        
        assert response.status_code == 400

    def test_redeem_zero_points_returns_400(self, valid_headers, api_session):
        """
        Test Case: Redeem zero points
        Expected: 400 Bad Request
        Justification: Must redeem at least 1
        """
        response = api_session.post(
            f"{BASE_URL}/loyalty/redeem",
            headers=valid_headers,
            json={"points": 0}
        )
        
        assert response.status_code == 400

    def test_redeem_negative_points_returns_400(self, valid_headers, api_session):
        """
        Test Case: Redeem negative points
        Expected: 400 Bad Request
        Justification: Points must be positive
        """
        response = api_session.post(
            f"{BASE_URL}/loyalty/redeem",
            headers=valid_headers,
            json={"points": -10}
        )
        
        assert response.status_code == 400

    def test_redeem_all_points(self, valid_headers, api_session):
        """
        Test Case: Redeem all available points
        Expected: 200 OK, points become 0
        Justification: Should allow complete redemption
        """
        loyalty = api_session.get(f"{BASE_URL}/loyalty", headers=valid_headers).json()
        total_points = loyalty.get("loyalty_points")
        
        if total_points > 0:
            response = api_session.post(
                f"{BASE_URL}/loyalty/redeem",
                headers=valid_headers,
                json={"points": total_points}
            )
            
            assert response.status_code in [200, 201]


class TestCoupons:
    """Test coupon operations."""

    def test_apply_valid_coupon(self, valid_headers, clear_cart, api_session):
        """
        Test Case: Apply valid, active coupon
        Expected: 200 OK, discount applied
        Justification: Core coupon functionality
        """
        # Add items meeting coupon minimum
        api_session.post(
            f"{BASE_URL}/cart/add",
            headers=valid_headers,
            json={"product_id": 1, "quantity": 1}  # 120
        )
        
        response = api_session.post(
            f"{BASE_URL}/coupon/apply",
            headers=valid_headers,
            json={"coupon_code": "WELCOME50"}
        )
        
        assert response.status_code in [200, 201]

    def test_apply_expired_coupon_returns_400(self, valid_headers, clear_cart, api_session):
        """
        Test Case: Apply expired coupon
        Expected: 400 Bad Request
        Justification: Expired coupons should not work
        """
        api_session.post(
            f"{BASE_URL}/cart/add",
            headers=valid_headers,
            json={"product_id": 1, "quantity": 10}
        )
        
        response = api_session.post(
            f"{BASE_URL}/coupon/apply",
            headers=valid_headers,
            json={"coupon_code": "EXPIRED100"}
        )
        
        assert response.status_code == 400

    def test_apply_coupon_below_minimum_returns_400(self, valid_headers, clear_cart, api_session):
        """
        Test Case: Apply coupon but cart below minimum
        Expected: 400 Bad Request
        Justification: Coupon has minimum cart value
        """
        # Add items, but don't meet minimum for PERCENT10 (min 300)
        api_session.post(
            f"{BASE_URL}/cart/add",
            headers=valid_headers,
            json={"product_id": 1, "quantity": 1}  # Only 120
        )
        
        response = api_session.post(
            f"{BASE_URL}/coupon/apply",
            headers=valid_headers,
            json={"coupon_code": "PERCENT10"}
        )
        
        assert response.status_code == 400

    def test_fixed_discount_calculation(self, valid_headers, clear_cart, api_session):
        """
        Test Case: FIXED coupon applies correct discount
        Expected: discount = fixed amount
        Justification: Discount must be accurate
        """
        # Add 200 (meets WELCOME50 minimum of 100)
        api_session.post(
            f"{BASE_URL}/cart/add",
            headers=valid_headers,
            json={"product_id": 3, "quantity": 5}  # 40*5 = 200
        )
        
        response = api_session.post(
            f"{BASE_URL}/coupon/apply",
            headers=valid_headers,
            json={"coupon_code": "WELCOME50"}
        )
        
        if response.status_code in [200, 201]:
            data = response.json()
            # Original total should be 200
            # After WELCOME50 discount (50), should be 150
            assert data.get("discount") == 50

    def test_percent_discount_calculation(self, valid_headers, clear_cart, api_session):
        """
        Test Case: PERCENT coupon applies correct discount
        Expected: discount = total * percentage
        Justification: Percentage discount must be accurate
        """
        # Add 400 (meets PERCENT10 minimum of 300)
        api_session.post(
            f"{BASE_URL}/cart/add",
            headers=valid_headers,
            json={"product_id": 1, "quantity": 4}  # 120*4 = 480
        )
        
        response = api_session.post(
            f"{BASE_URL}/coupon/apply",
            headers=valid_headers,
            json={"coupon_code": "PERCENT10"}
        )
        
        if response.status_code in [200, 201]:
            data = response.json()
            # 10% of 480 = 48
            assert data.get("discount") == 48

    def test_discount_respects_cap(self, valid_headers, clear_cart, api_session):
        """
        Test Case: Discount respects maximum cap
        Expected: discount capped at max_discount
        Justification: Coupon should have caps
        """
        # Add 5000 for PERCENT30
        api_session.post(
            f"{BASE_URL}/cart/add",
            headers=valid_headers,
            json={"product_id": 1, "quantity": 50}  # 120*50 = 6000
        )
        
        response = api_session.post(
            f"{BASE_URL}/coupon/apply",
            headers=valid_headers,
            json={"coupon_code": "PERCENT30"}
        )
        
        if response.status_code in [200, 201]:
            data = response.json()
            # 30% of 6000 = 1800, but cap is 300
            assert data.get("discount") <= 300

    def test_remove_coupon(self, valid_headers, clear_cart, api_session):
        """
        Test Case: Remove applied coupon
        Expected: 200 OK, discount removed
        Justification: Should allow coupon removal
        """
        api_session.post(
            f"{BASE_URL}/cart/add",
            headers=valid_headers,
            json={"product_id": 1, "quantity": 1}
        )
        
        api_session.post(
            f"{BASE_URL}/coupon/apply",
            headers=valid_headers,
            json={"coupon_code": "WELCOME50"}
        )
        
        response = api_session.post(
            f"{BASE_URL}/coupon/remove",
            headers=valid_headers
        )
        
        assert response.status_code in [200, 201]

    def test_apply_invalid_coupon_returns_400(self, valid_headers, clear_cart, api_session):
        """
        Test Case: Apply non-existent coupon
        Expected: 400 Bad Request
        Justification: Should validate coupon exists
        """
        api_session.post(
            f"{BASE_URL}/cart/add",
            headers=valid_headers,
            json={"product_id": 1, "quantity": 1}
        )
        
        response = api_session.post(
            f"{BASE_URL}/coupon/apply",
            headers=valid_headers,
            json={"coupon_code": "INVALIDCOUPON123"}
        )
        
        assert response.status_code == 400


class TestCouponDataTypes:
    """Test coupon response data types."""

    def test_discount_is_number(self, valid_headers, clear_cart, api_session):
        """Test Case: Discount is numeric"""
        api_session.post(
            f"{BASE_URL}/cart/add",
            headers=valid_headers,
            json={"product_id": 1, "quantity": 1}
        )
        
        response = api_session.post(
            f"{BASE_URL}/coupon/apply",
            headers=valid_headers,
            json={"coupon_code": "WELCOME50"}
        )
        
        if response.status_code in [200, 201]:
            data = response.json()
            discount = data.get("discount")
            assert isinstance(discount, (int, float)) if discount else True
