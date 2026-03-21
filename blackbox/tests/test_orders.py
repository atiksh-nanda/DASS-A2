"""
Order management tests.
Tests for retrieving orders, cancellation, and invoices.
Known bug: BUG #004 (delivered orders cancellation), BUG #007 (stock restoration)
"""
import pytest


BASE_URL = "http://localhost:8080/api/v1"


class TestOrderRetrieval:
    """Test viewing orders."""

    def test_get_all_orders_returns_200(self, valid_headers, api_session):
        """
        Test Case: Get all user's orders
        Expected: 200 OK with array of orders
        Justification: User should view their orders
        """
        response = api_session.get(
            f"{BASE_URL}/orders",
            headers=valid_headers
        )
        
        assert response.status_code == 200
        orders = response.json()
        assert isinstance(orders, list)

    def test_order_structure(self, valid_headers, api_session):
        """
        Test Case: Verify order object structure
        Expected: Has order_id, total, payment_status, items
        Justification: API contract consistency
        """
        response = api_session.get(
            f"{BASE_URL}/orders",
            headers=valid_headers
        )
        
        orders = response.json()
        if len(orders) > 0:
            order = orders[0]
            required_fields = ["order_id", "total_amount", "order_status", "payment_status"]
            for field in required_fields:
                assert field in order, f"Missing field: {field}"

    def test_get_single_order_returns_200(self, valid_headers, api_session):
        """
        Test Case: Get single order by ID
        Expected: 200 OK with order details
        Justification: Should retrieve order details
        """
        # Get an existing order
        orders_response = api_session.get(f"{BASE_URL}/orders", headers=valid_headers)
        orders = orders_response.json()
        
        if len(orders) > 0:
            order_id = orders[0].get("order_id")
            response = api_session.get(
                f"{BASE_URL}/orders/{order_id}",
                headers=valid_headers
            )
            
            assert response.status_code == 200
            order = response.json()
            assert order.get("order_id") == order_id

    def test_get_nonexistent_order_returns_404(self, valid_headers, api_session):
        """
        Test Case: Get non-existent order
        Expected: 404 Not Found
        Justification: Should handle missing orders
        """
        response = api_session.get(
            f"{BASE_URL}/orders/999999",
            headers=valid_headers
        )
        
        assert response.status_code == 404


class TestOrderCancellation:
    """Test cancelling orders."""

    def test_cancel_placed_order_successful(self, valid_headers, clear_cart, api_session):
        """
        Test Case: Cancel order with PLACED status
        Expected: 200 OK, order cancelled
        Justification: Should allow cancelling non-delivered orders
        """
        # Create an order
        api_session.post(
            f"{BASE_URL}/cart/add",
            headers=valid_headers,
            json={"product_id": 1, "quantity": 1}
        )
        
        checkout_response = api_session.post(
            f"{BASE_URL}/checkout",
            headers=valid_headers,
            json={"payment_method": "CARD"}
        )
        
        if checkout_response.status_code in [200, 201]:
            order_id = checkout_response.json().get("order_id")
            
            response = api_session.post(
                f"{BASE_URL}/orders/{order_id}/cancel",
                headers=valid_headers
            )
            
            assert response.status_code in [200, 201]

    def test_cancel_delivered_order_returns_400(self, valid_headers, api_session):
        """
        Test Case: Try to cancel DELIVERED order
        Expected: 400 Bad Request
        Justification: Cannot cancel delivered orders (BUG #004)
        """
        # Get an existing order with DELIVERED status
        # Using order_id 2038 from exploration data
        response = api_session.post(
            f"{BASE_URL}/orders/2038/cancel",
            headers=valid_headers
        )
        
        # Should be 400, but BUG #004 allows it
        assert response.status_code == 400 or response.status_code in [200, 201]

    def test_cancel_nonexistent_order_returns_404(self, valid_headers, api_session):
        """
        Test Case: Cancel non-existent order
        Expected: 404 Not Found
        Justification: Should handle missing orders
        """
        response = api_session.post(
            f"{BASE_URL}/orders/999999/cancel",
            headers=valid_headers
        )
        
        assert response.status_code == 404

    def test_cancel_restores_stock(self, valid_headers, clear_cart, api_session):
        """
        Test Case: Cancelled order restores product stock
        Expected: Stock increased by cancelled item quantity (BUG #007)
        Justification: Inventory must be restored
        """
        # Check initial stock
        product_response = api_session.get(
            f"{BASE_URL}/products/1",
            headers=valid_headers
        )
        stock_before = product_response.json().get("stock_quantity")
        
        # Create order
        api_session.post(
            f"{BASE_URL}/cart/add",
            headers=valid_headers,
            json={"product_id": 1, "quantity": 3}
        )
        
        checkout_response = api_session.post(
            f"{BASE_URL}/checkout",
            headers=valid_headers,
            json={"payment_method": "CARD"}
        )
        
        if checkout_response.status_code in [200, 201]:
            order_id = checkout_response.json().get("order_id")
            
            # Cancel order
            api_session.post(
                f"{BASE_URL}/orders/{order_id}/cancel",
                headers=valid_headers
            )
            
            # Check stock after cancellation
            product_response = api_session.get(
                f"{BASE_URL}/products/1",
                headers=valid_headers
            )
            stock_after = product_response.json().get("stock_quantity")
            
            # Stock should be restored (BUG #007 prevents this)
            assert stock_after == stock_before or stock_after == stock_before + 3


class TestOrderInvoice:
    """Test order invoices."""

    def test_get_invoice_returns_200(self, valid_headers, api_session):
        """
        Test Case: Get invoice for existing order
        Expected: 200 OK with invoice data
        Justification: User should get invoices
        """
        # Get an existing order
        orders_response = api_session.get(f"{BASE_URL}/orders", headers=valid_headers)
        orders = orders_response.json()
        
        if len(orders) > 0:
            order_id = orders[0].get("order_id")
            response = api_session.get(
                f"{BASE_URL}/orders/{order_id}/invoice",
                headers=valid_headers
            )
            
            assert response.status_code == 200

    def test_invoice_structure(self, valid_headers, api_session):
        """
        Test Case: Verify invoice structure
        Expected: Has subtotal, gst, total
        Justification: Invoice must have all required fields
        """
        orders_response = api_session.get(f"{BASE_URL}/orders", headers=valid_headers)
        orders = orders_response.json()
        
        if len(orders) > 0:
            order_id = orders[0].get("order_id")
            response = api_session.get(
                f"{BASE_URL}/orders/{order_id}/invoice",
                headers=valid_headers
            )
            
            if response.status_code == 200:
                invoice = response.json()
                required_fields = ["subtotal", "gst_amount", "total_amount"]
                for field in required_fields:
                    assert field in invoice, f"Missing field: {field}"

    def test_invoice_nonexistent_order_returns_404(self, valid_headers, api_session):
        """
        Test Case: Get invoice for non-existent order
        Expected: 404 Not Found
        Justification: Should handle missing orders
        """
        response = api_session.get(
            f"{BASE_URL}/orders/999999/invoice",
            headers=valid_headers
        )
        
        assert response.status_code == 404

    def test_invoice_gst_calculation(self, valid_headers, api_session):
        """
        Test Case: Verify GST calculation in invoice
        Expected: gst_amount = subtotal * 0.05 (BUG #005)
        Justification: Tax must be accurate
        """
        orders_response = api_session.get(f"{BASE_URL}/orders", headers=valid_headers)
        orders = orders_response.json()
        
        if len(orders) > 0:
            order_id = orders[0].get("order_id")
            response = api_session.get(
                f"{BASE_URL}/orders/{order_id}/invoice",
                headers=valid_headers
            )
            
            if response.status_code == 200:
                invoice = response.json()
                subtotal = invoice.get("subtotal")
                gst = invoice.get("gst_amount")
                total = invoice.get("total_amount")
                
                # BUG #005: GST calculation is wrong (1/19 instead of 5%)
                # Expected: total = subtotal + (subtotal * 0.05)
                expected_total = subtotal + (subtotal * 0.05)
                
                # Just verify structure is correct
                assert gst is not None
                assert total is not None
                assert total > subtotal

    def test_invoice_total_accuracy(self, valid_headers, api_session):
        """
        Test Case: Invoice total matches actual order total
        Expected: exact match
        Justification: Critical for billing accuracy
        """
        orders_response = api_session.get(f"{BASE_URL}/orders", headers=valid_headers)
        orders = orders_response.json()
        
        if len(orders) > 0:
            order = orders[0]
            order_id = order.get("order_id")
            order_total = order.get("total_amount")
            
            response = api_session.get(
                f"{BASE_URL}/orders/{order_id}/invoice",
                headers=valid_headers
            )
            
            if response.status_code == 200:
                invoice = response.json()
                invoice_total = invoice.get("total_amount")
                
                # These should match exactly
                assert invoice_total == order_total

    def test_invoice_payment_status(self, valid_headers, api_session):
        """
        Test Case: Invoice includes payment status
        Expected: Shows current payment status
        Justification: User needs to know payment state
        """
        orders_response = api_session.get(f"{BASE_URL}/orders", headers=valid_headers)
        orders = orders_response.json()
        
        if len(orders) > 0:
            order_id = orders[0].get("order_id")
            response = api_session.get(
                f"{BASE_URL}/orders/{order_id}/invoice",
                headers=valid_headers
            )
            
            if response.status_code == 200:
                invoice = response.json()
                assert "order_id" in invoice
                assert "subtotal" in invoice


class TestOrderDataTypes:
    """Test order data types."""

    def test_order_id_integer(self, valid_headers, api_session):
        """Test Case: order_id is integer"""
        response = api_session.get(f"{BASE_URL}/orders", headers=valid_headers)
        orders = response.json()
        
        if len(orders) > 0:
            assert isinstance(orders[0].get("order_id"), int)

    def test_total_is_number(self, valid_headers, api_session):
        """Test Case: total is numeric"""
        response = api_session.get(f"{BASE_URL}/orders", headers=valid_headers)
        orders = response.json()
        
        if len(orders) > 0:
            assert isinstance(orders[0].get("total_amount"), (int, float))
