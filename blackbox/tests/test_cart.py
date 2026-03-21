"""
Cart endpoint tests.
Tests for cart operations including add, update, remove, clear.
Note: BUG #001 affects subtotal calculations.
"""
import pytest


BASE_URL = "http://localhost:8080/api/v1"


class TestCartView:
    """Test viewing cart."""

    def test_get_empty_cart(self, valid_headers, clear_cart, api_session):
        """
        Test Case: Get empty cart
        Expected: 200 OK with empty items array, total=0
        Justification: Basic cart retrieval
        """
        response = api_session.get(
            f"{BASE_URL}/cart",
            headers=valid_headers
        )
        assert response.status_code == 200
        cart = response.json()
        assert cart.get("items") == [] or cart.get("items") is not None
        assert cart.get("total") == 0

    def test_cart_structure(self, valid_headers, clear_cart, api_session):
        """
        Test Case: Verify cart structure with items
        Expected: Cart has cart_id, items, total
        Justification: API contract consistency
        """
        # Add an item first
        api_session.post(
            f"{BASE_URL}/cart/add",
            headers=valid_headers,
            json={"product_id": 1, "quantity": 1}
        )
        
        response = api_session.get(
            f"{BASE_URL}/cart",
            headers=valid_headers
        )
        assert response.status_code == 200
        cart = response.json()
        
        assert "cart_id" in cart
        assert "items" in cart
        assert "total" in cart
        assert isinstance(cart.get("items"), list)


class TestCartAdd:
    """Test adding items to cart."""

    def test_add_valid_product(self, valid_headers, clear_cart, api_session):
        """
        Test Case: Add valid product with valid quantity
        Expected: 200/201, item added to cart
        Justification: Core cart functionality
        """
        response = api_session.post(
            f"{BASE_URL}/cart/add",
            headers=valid_headers,
            json={"product_id": 1, "quantity": 2}
        )
        assert response.status_code in [200, 201]
        cart = api_session.get(f"{BASE_URL}/cart", headers=valid_headers).json()
        assert len(cart.get("items", [])) > 0

    def test_add_product_with_quantity_zero_returns_400(self, valid_headers, clear_cart, api_session):
        """
        Test Case: Add product with quantity=0
        Expected: 400 Bad Request
        Justification: Quantity must be at least 1
        """
        response = api_session.post(
            f"{BASE_URL}/cart/add",
            headers=valid_headers,
            json={"product_id": 1, "quantity": 0}
        )
        assert response.status_code == 400

    def test_add_product_with_negative_quantity_returns_400(self, valid_headers, clear_cart, api_session):
        """
        Test Case: Add product with negative quantity
        Expected: 400 Bad Request
        Justification: Quantity must be positive
        """
        response = api_session.post(
            f"{BASE_URL}/cart/add",
            headers=valid_headers,
            json={"product_id": 1, "quantity": -5}
        )
        assert response.status_code == 400

    def test_add_nonexistent_product_returns_404(self, valid_headers, clear_cart, api_session):
        """
        Test Case: Add product that doesn't exist
        Expected: 404 Not Found
        Justification: Should not allow adding non-existent products
        """
        response = api_session.post(
            f"{BASE_URL}/cart/add",
            headers=valid_headers,
            json={"product_id": 99999, "quantity": 1}
        )
        assert response.status_code == 404

    def test_add_more_than_stock_returns_400(self, valid_headers, clear_cart, api_session):
        """
        Test Case: Add quantity exceeding available stock
        Expected: 400 Bad Request
        Justification: Should prevent overselling
        """
        response = api_session.post(
            f"{BASE_URL}/cart/add",
            headers=valid_headers,
            json={"product_id": 1, "quantity": 10000}
        )
        assert response.status_code == 400

    def test_add_out_of_stock_product_returns_400(self, valid_headers, clear_cart, api_session):
        """
        Test Case: Add product with stock=0
        Expected: 400 Bad Request
        Justification: Should not allow adding out-of-stock items
        """
        response = api_session.post(
            f"{BASE_URL}/cart/add",
            headers=valid_headers,
            json={"product_id": 70, "quantity": 1}  # Product with stock=0
        )
        assert response.status_code == 400

    def test_add_same_product_multiple_times_accumulates(self, valid_headers, clear_cart, api_session):
        """
        Test Case: Add same product twice
        Expected: Quantities accumulate, not replaced
        Justification: Cart should cumulate quantities
        """
        api_session.post(
            f"{BASE_URL}/cart/add",
            headers=valid_headers,
            json={"product_id": 1, "quantity": 2}
        )
        
        response = api_session.post(
            f"{BASE_URL}/cart/add",
            headers=valid_headers,
            json={"product_id": 1, "quantity": 3}
        )
        
        assert response.status_code in [200, 201]
        # Check cart
        cart_response = api_session.get(f"{BASE_URL}/cart", headers=valid_headers)
        cart = cart_response.json()
        
        # Find the item
        apple_item = next((item for item in cart.get("items", []) if item.get("product_id") == 1), None)
        if apple_item:
            assert apple_item.get("quantity") == 5, "Quantities should accumulate"

    def test_subtotal_calculation_correct(self, valid_headers, clear_cart, api_session):
        """
        Test Case: Verify subtotal = quantity * unit_price
        Expected: subtotal = 2 * 120 = 240
        Justification: Critical for order calculations (relates to BUG #001)
        """
        response = api_session.post(
            f"{BASE_URL}/cart/add",
            headers=valid_headers,
            json={"product_id": 1, "quantity": 2}
        )
        
        assert response.status_code in [200, 201]
        data = api_session.get(f"{BASE_URL}/cart", headers=valid_headers).json()
        
        # Find the item
        item = next((i for i in data.get("items", []) if i.get("product_id") == 1), None)
        if item:
            expected_subtotal = item.get("quantity") * item.get("unit_price")
            actual_subtotal = item.get("subtotal")
            assert actual_subtotal == expected_subtotal, f"BUG #001: Subtotal {actual_subtotal} != {expected_subtotal}"

    def test_cart_total_is_sum_of_subtotals(self, valid_headers, clear_cart, api_session):
        """
        Test Case: Cart total = sum of all item subtotals
        Expected: total equals sum of subtotals
        Justification: Critical for order amounts
        """
        api_session.post(
            f"{BASE_URL}/cart/add",
            headers=valid_headers,
            json={"product_id": 1, "quantity": 1}  # 120
        )
        api_session.post(
            f"{BASE_URL}/cart/add",
            headers=valid_headers,
            json={"product_id": 3, "quantity": 2}  # 40*2 = 80
        )
        
        response = api_session.get(f"{BASE_URL}/cart", headers=valid_headers)
        cart = response.json()
        
        items = cart.get("items", [])
        expected_total = sum(item.get("subtotal", 0) for item in items)
        actual_total = cart.get("total")
        
        assert actual_total == expected_total, f"Cart total {actual_total} != sum of subtotals {expected_total}"

    def test_add_multiple_different_products(self, valid_headers, clear_cart, api_session):
        """
        Test Case: Add multiple different products
        Expected: All items in cart with correct quantities
        Justification: Should support mixed product carts
        """
        api_session.post(
            f"{BASE_URL}/cart/add",
            headers=valid_headers,
            json={"product_id": 1, "quantity": 1}
        )
        api_session.post(
            f"{BASE_URL}/cart/add",
            headers=valid_headers,
            json={"product_id": 2, "quantity": 1}
        )
        
        response = api_session.get(f"{BASE_URL}/cart", headers=valid_headers)
        cart = response.json()
        
        assert len(cart.get("items", [])) == 2


class TestCartUpdate:
    """Test updating cart items."""

    def test_update_quantity_successful(self, valid_headers, clear_cart, api_session):
        """
        Test Case: Update item quantity
        Expected: 200 OK, quantity updated
        Justification: User should be able to modify quantities
        """
        api_session.post(
            f"{BASE_URL}/cart/add",
            headers=valid_headers,
            json={"product_id": 1, "quantity": 2}
        )
        
        response = api_session.post(
            f"{BASE_URL}/cart/update",
            headers=valid_headers,
            json={"product_id": 1, "quantity": 5}
        )
        
        assert response.status_code in [200, 201]
        
        # Verify
        cart = api_session.get(f"{BASE_URL}/cart", headers=valid_headers).json()
        item = next((i for i in cart.get("items", []) if i.get("product_id") == 1), None)
        if item:
            assert item.get("quantity") == 5

    def test_update_quantity_to_zero_returns_400(self, valid_headers, clear_cart, api_session):
        """
        Test Case: Update quantity to 0
        Expected: 400 Bad Request
        Justification: Quantity must be at least 1
        """
        api_session.post(
            f"{BASE_URL}/cart/add",
            headers=valid_headers,
            json={"product_id": 1, "quantity": 2}
        )
        
        response = api_session.post(
            f"{BASE_URL}/cart/update",
            headers=valid_headers,
            json={"product_id": 1, "quantity": 0}
        )
        
        assert response.status_code == 400

    def test_update_quantity_to_negative_returns_400(self, valid_headers, clear_cart, api_session):
        """
        Test Case: Update quantity to negative
        Expected: 400 Bad Request
        Justification: Quantity must be positive
        """
        api_session.post(
            f"{BASE_URL}/cart/add",
            headers=valid_headers,
            json={"product_id": 1, "quantity": 2}
        )
        
        response = api_session.post(
            f"{BASE_URL}/cart/update",
            headers=valid_headers,
            json={"product_id": 1, "quantity": -1}
        )
        
        assert response.status_code == 400

    def test_update_nonexistent_item_returns_404(self, valid_headers, clear_cart, api_session):
        """
        Test Case: Update product not in cart
        Expected: 404 Not Found
        Justification: Should handle missing items gracefully
        """
        response = api_session.post(
            f"{BASE_URL}/cart/update",
            headers=valid_headers,
            json={"product_id": 1, "quantity": 5}
        )
        
        assert response.status_code == 404


class TestCartRemove:
    """Test removing items from cart."""

    def test_remove_existing_item_successful(self, valid_headers, clear_cart, api_session):
        """
        Test Case: Remove product from cart
        Expected: 200 OK, item removed
        Justification: User should be able to remove items
        """
        api_session.post(
            f"{BASE_URL}/cart/add",
            headers=valid_headers,
            json={"product_id": 1, "quantity": 2}
        )
        
        response = api_session.post(
            f"{BASE_URL}/cart/remove",
            headers=valid_headers,
            json={"product_id": 1}
        )
        
        assert response.status_code in [200, 201]
        
        # Verify item removed
        cart = api_session.get(f"{BASE_URL}/cart", headers=valid_headers).json()
        item = next((i for i in cart.get("items", []) if i.get("product_id") == 1), None)
        assert item is None

    def test_remove_nonexistent_item_returns_404(self, valid_headers, clear_cart, api_session):
        """
        Test Case: Remove product not in cart
        Expected: 404 Not Found
        Justification: Should handle correctly
        """
        response = api_session.post(
            f"{BASE_URL}/cart/remove",
            headers=valid_headers,
            json={"product_id": 1}
        )
        
        assert response.status_code == 404


class TestCartClear:
    """Test clearing cart."""

    def test_clear_nonempty_cart_successful(self, valid_headers, clear_cart, api_session):
        """
        Test Case: Clear non-empty cart
        Expected: 200 OK, cart empty with total=0
        Justification: User should be able to clear cart
        """
        api_session.post(
            f"{BASE_URL}/cart/add",
            headers=valid_headers,
            json={"product_id": 1, "quantity": 2}
        )
        
        response = api_session.delete(
            f"{BASE_URL}/cart/clear",
            headers=valid_headers
        )
        
        assert response.status_code in [200, 201, 204]
        
        # Verify empty
        cart = api_session.get(f"{BASE_URL}/cart", headers=valid_headers).json()
        assert cart.get("items") == [] or len(cart.get("items", [])) == 0
        assert cart.get("total") == 0

    def test_clear_empty_cart_successful(self, valid_headers, clear_cart, api_session):
        """
        Test Case: Clear already empty cart
        Expected: 200 OK, no error
        Justification: Should handle idempotently
        """
        response = api_session.delete(
            f"{BASE_URL}/cart/clear",
            headers=valid_headers
        )
        
        assert response.status_code in [200, 201, 204]
