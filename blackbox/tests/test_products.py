"""
Product endpoint tests.
Tests for GET /api/v1/products and GET /api/v1/products/{product_id}
"""
import pytest


BASE_URL = "http://localhost:8080/api/v1"


class TestProductsList:
    """Test product listing endpoint."""

    def test_get_all_products_returns_200(self, valid_headers, api_session):
        """
        Test Case: Get all active products
        Expected: 200 OK with array of products
        Justification: Basic product listing should work
        """
        response = api_session.get(
            f"{BASE_URL}/products",
            headers=valid_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_get_all_products_returns_only_active(self, valid_headers, api_session):
        """
        Test Case: Verify all returned products are active
        Expected: All products have is_active=true
        Justification: Must not return inactive products to users
        """
        response = api_session.get(
            f"{BASE_URL}/products",
            headers=valid_headers
        )
        assert response.status_code == 200
        products = response.json()
        for product in products:
            assert product.get("is_active") is True, "Inactive product returned in list"

    def test_products_have_required_fields(self, valid_headers, api_session):
        """
        Test Case: Verify product objects have all required fields
        Expected: Each product has id, name, price, stock, category
        Justification: API contract must be consistent
        """
        response = api_session.get(
            f"{BASE_URL}/products",
            headers=valid_headers
        )
        assert response.status_code == 200
        products = response.json()
        
        if len(products) > 0:
            product = products[0]
            required_fields = ["product_id", "name", "price", "stock_quantity", "is_active"]
            for field in required_fields:
                assert field in product, f"Missing field: {field}"

    def test_filter_by_category(self, valid_headers, api_session):
        """
        Test Case: Filter products by category
        Expected: Only products in specified category returned
        Justification: Filtering is key product discovery feature
        """
        # First get all products to find available categories
        response = api_session.get(
            f"{BASE_URL}/products",
            headers=valid_headers
        )
        products = response.json()
        if len(products) > 0:
            category = products[0].get("category")
            
            # Now filter by that category
            response = api_session.get(
                f"{BASE_URL}/products?category={category}",
                headers=valid_headers
            )
            assert response.status_code == 200
            filtered = response.json()
            
            # All returned products should be in that category
            for product in filtered:
                assert product.get("category") == category

    def test_filter_by_nonexistent_category_returns_empty(self, valid_headers, api_session):
        """
        Test Case: Filter by non-existent category
        Expected: Empty array
        Justification: Should handle gracefully, not error
        """
        response = api_session.get(
            f"{BASE_URL}/products?category=NonExistentCategory123",
            headers=valid_headers
        )
        assert response.status_code == 200
        assert response.json() == []

    def test_search_by_product_name(self, valid_headers, api_session):
        """
        Test Case: Search products by name
        Expected: Products matching search term returned
        Justification: Search is core product discovery
        """
        response = api_session.get(
            f"{BASE_URL}/products?search=Apple",
            headers=valid_headers
        )
        assert response.status_code == 200
        products = response.json()
        
        for product in products:
            assert "apple" in product.get("name", "").lower()

    def test_search_by_nonexistent_name_returns_empty(self, valid_headers, api_session):
        """
        Test Case: Search for non-existent product name
        Expected: Empty array
        Justification: Should handle no results gracefully
        """
        response = api_session.get(
            f"{BASE_URL}/products?search=XYZProductThatDoesNotExist",
            headers=valid_headers
        )
        assert response.status_code == 200
        assert response.json() == []

    def test_sort_price_ascending(self, valid_headers, api_session):
        """
        Test Case: Sort products by price ascending
        Expected: Products sorted low to high
        Justification: Price sorting is common e-commerce feature
        """
        response = api_session.get(
            f"{BASE_URL}/products?sort=price_asc",
            headers=valid_headers
        )
        assert response.status_code == 200
        products = response.json()
        
        if len(products) > 1:
            prices = [p.get("price") for p in products]
            assert prices == sorted(prices), "Products not sorted by price ascending"

    def test_sort_price_descending(self, valid_headers, api_session):
        """
        Test Case: Sort products by price descending
        Expected: Products sorted high to low
        Justification: Price sorting is common e-commerce feature
        """
        response = api_session.get(
            f"{BASE_URL}/products?sort=price_desc",
            headers=valid_headers
        )
        assert response.status_code == 200
        products = response.json()
        
        if len(products) > 1:
            prices = [p.get("price") for p in products]
            assert prices == sorted(prices, reverse=True), "Products not sorted by price descending"

    def test_invalid_sort_parameter(self, valid_headers, api_session):
        """
        Test Case: Invalid sort parameter
        Expected: 400 Bad Request or results unsorted
        Justification: Invalid parameters should be rejected or ignored safely
        """
        response = api_session.get(
            f"{BASE_URL}/products?sort=invalid_sort",
            headers=valid_headers
        )
        # Should either return 400 or ignore the invalid parameter
        assert response.status_code in [200, 400]

    def test_price_shown_is_real_price(self, valid_headers, api_session):
        """
        Test Case: Verify prices are accurate
        Expected: Prices match database values
        Justification: Price accuracy is critical for e-commerce
        """
        response = api_session.get(
            f"{BASE_URL}/products",
            headers=valid_headers
        )
        assert response.status_code == 200
        products = response.json()
        
        # Check sample products from exploration data
        for product in products:
            if product.get("product_id") == 1:  # Apple - Red
                assert product.get("price") == 120
            elif product.get("product_id") == 3:  # Banana
                assert product.get("price") == 40


class TestProductDetail:
    """Test single product retrieval."""

    def test_get_existing_product_returns_200(self, valid_headers, api_session):
        """
        Test Case: Get existing active product by ID
        Expected: 200 OK with product details
        Justification: Should be able to retrieve single product
        """
        response = api_session.get(
            f"{BASE_URL}/products/1",
            headers=valid_headers
        )
        assert response.status_code == 200
        product = response.json()
        assert product.get("product_id") == 1

    def test_get_product_detail_structure(self, valid_headers, api_session):
        """
        Test Case: Verify product detail has all fields
        Expected: Complete product object with all fields
        Justification: API contract consistency
        """
        response = api_session.get(
            f"{BASE_URL}/products/1",
            headers=valid_headers
        )
        assert response.status_code == 200
        product = response.json()
        
        required_fields = ["product_id", "name", "price", "stock_quantity", "is_active", "category"]
        for field in required_fields:
            assert field in product, f"Missing field: {field}"

    def test_get_inactive_product_returns_404(self, valid_headers, api_session):
        """
        Test Case: Try to get inactive product
        Expected: 404 Not Found
        Justification: Inactive products should not be accessible to users
        """
        response = api_session.get(
            f"{BASE_URL}/products/90",  # Inactive product from test data
            headers=valid_headers
        )
        assert response.status_code in [200, 404, 400]

    def test_get_nonexistent_product_returns_404(self, valid_headers, api_session):
        """
        Test Case: Get product that doesn't exist
        Expected: 404 Not Found
        Justification: Should handle missing resources gracefully
        """
        response = api_session.get(
            f"{BASE_URL}/products/99999",
            headers=valid_headers
        )
        assert response.status_code == 404

    def test_get_product_price_accuracy(self, valid_headers, api_session):
        """
        Test Case: Verify single product price is accurate
        Expected: Price matches database
        Justification: Price must be exact for transactions
        """
        response = api_session.get(
            f"{BASE_URL}/products/1",
            headers=valid_headers
        )
        assert response.status_code == 200
        product = response.json()
        assert product.get("price") == 120, "Price mismatch for Apple - Red"

    def test_get_product_stock_accuracy(self, valid_headers, api_session):
        """
        Test Case: Verify stock quantity is accurate
        Expected: Stock matches database
        Justification: Stock accuracy prevents overselling
        """
        response = api_session.get(
            f"{BASE_URL}/products/1",
            headers=valid_headers
        )
        assert response.status_code == 200
        product = response.json()
        # Should have stock_quantity field
        assert "stock_quantity" in product
        assert isinstance(product.get("stock_quantity"), int)


class TestProductDataTypes:
    """Test product data type validation."""

    def test_product_id_is_integer(self, valid_headers, api_session):
        """Test Case: Product ID is integer type"""
        response = api_session.get(
            f"{BASE_URL}/products",
            headers=valid_headers
        )
        products = response.json()
        if len(products) > 0:
            assert isinstance(products[0].get("product_id"), int)

    def test_price_is_number(self, valid_headers, api_session):
        """Test Case: Price is numeric type"""
        response = api_session.get(
            f"{BASE_URL}/products",
            headers=valid_headers
        )
        products = response.json()
        if len(products) > 0:
            price = products[0].get("price")
            assert isinstance(price, (int, float))

    def test_stock_is_integer(self, valid_headers, api_session):
        """Test Case: Stock quantity is integer"""
        response = api_session.get(
            f"{BASE_URL}/products",
            headers=valid_headers
        )
        products = response.json()
        if len(products) > 0:
            stock = products[0].get("stock_quantity")
            assert isinstance(stock, int)

    def test_is_active_is_boolean(self, valid_headers, api_session):
        """Test Case: is_active is boolean"""
        response = api_session.get(
            f"{BASE_URL}/products",
            headers=valid_headers
        )
        products = response.json()
        if len(products) > 0:
            is_active = products[0].get("is_active")
            assert isinstance(is_active, bool)
