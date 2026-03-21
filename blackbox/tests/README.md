"""
QuickCart API - Comprehensive Black Box Test Suite

This test suite provides comprehensive black-box testing for the QuickCart REST API.
Tests are organized by functionality and endpoint, covering:

- Authentication and header validation
- Product listing and retrieval
- Shopping cart operations
- Checkout and payment processing
- Address management
- User profiles and wallet
- Order management
- Loyalty points and coupons
- Product reviews
- Support tickets

Known Bugs Documented:
1. BUG #001: Cart subtotal calculation produces negative/incorrect values
2. BUG #002: COD payment allowed for orders > 5000 (should be restricted)
3. BUG #003: Wallet payment allowed with insufficient balance
4. BUG #004: Delivered orders can be cancelled (should be prevented)
5. BUG #005: GST calculation is wrong (1/19 instead of 5%)
6. BUG #006: Wallet balance not deducted on wallet payment
7. BUG #007: Stock not properly restored on order cancellation
8. BUG #008: Pincode validation broken (accepts 5 digits, rejects 6)
9. BUG #009: Address IDs non-sequential (1001 after 2)
10. BUG #010: Rating validation accepts 0 and 6 (should be 1-5)

Test Organization:
- test_auth.py: Authentication and header validation
- test_products.py: Product endpoints
- test_cart.py: Cart operations
- test_checkout.py: Payment and checkout
- test_addresses.py: Address management
- test_wallet.py: Wallet and profile operations
- test_orders.py: Order management
- test_loyalty_coupons.py: Loyalty points and coupons
- test_reviews_tickets.py: Reviews and support tickets
- conftest.py: Shared fixtures and configuration

Running the Tests:
pytest -v                          # Run all tests with verbose output
pytest -v test_auth.py            # Run specific test file
pytest -v -k "test_cart"          # Run tests matching keyword
pytest -v --tb=short              # Short traceback format
pytest --co                        # List all tests without running

Test Coverage:
Each test case includes:
- Clear test case description
- Expected behavior based on API documentation
- Justification for the test
- Validation of HTTP status codes
- JSON response structure validation
- Data type validation
- Boundary value testing
- Invalid input handling

Notes:
- Tests assume API server running at http://localhost:8080
- Default test user ID: 1
- Default Roll Number: 12345
- Clear cart fixture automatically clears cart before/after tests
- Tests document known bugs without failing
"""
