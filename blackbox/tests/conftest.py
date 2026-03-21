"""
Fixtures and configuration for QuickCart API black-box testing.
"""
import pytest
import requests
from typing import Dict, Any


# API Configuration
BASE_URL = "http://localhost:8080/api/v1"
VALID_ROLL_NUMBER = "12345"
VALID_USER_ID = 1
INVALID_ROLL_NUMBER = "abc123"


@pytest.fixture
def valid_headers() -> Dict[str, str]:
    """Return valid authentication headers."""
    return {
        "X-Roll-Number": VALID_ROLL_NUMBER,
        "X-User-ID": str(VALID_USER_ID),
        "Content-Type": "application/json"
    }


@pytest.fixture
def admin_headers() -> Dict[str, str]:
    """Return admin-only headers (X-Roll-Number only)."""
    return {
        "X-Roll-Number": VALID_ROLL_NUMBER,
        "Content-Type": "application/json"
    }


@pytest.fixture
def no_roll_number_headers() -> Dict[str, str]:
    """Return headers missing X-Roll-Number."""
    return {
        "X-User-ID": str(VALID_USER_ID),
        "Content-Type": "application/json"
    }


@pytest.fixture
def invalid_roll_number_headers() -> Dict[str, str]:
    """Return headers with invalid X-Roll-Number."""
    return {
        "X-Roll-Number": INVALID_ROLL_NUMBER,
        "X-User-ID": str(VALID_USER_ID),
        "Content-Type": "application/json"
    }


@pytest.fixture
def no_user_id_headers() -> Dict[str, str]:
    """Return headers missing X-User-ID."""
    return {
        "X-Roll-Number": VALID_ROLL_NUMBER,
        "Content-Type": "application/json"
    }


@pytest.fixture
def invalid_user_id_headers() -> Dict[str, str]:
    """Return headers with non-existent user ID."""
    return {
        "X-Roll-Number": VALID_ROLL_NUMBER,
        "X-User-ID": "999999",
        "Content-Type": "application/json"
    }


@pytest.fixture
def api_session():
    """Create a requests session for API calls."""
    session = requests.Session()
    yield session
    session.close()


@pytest.fixture
def clear_cart(valid_headers, api_session):
    """Clear the user's cart before test."""
    api_session.delete(f"{BASE_URL}/cart/clear", headers=valid_headers)
    yield
    # Cleanup after test
    api_session.delete(f"{BASE_URL}/cart/clear", headers=valid_headers)


@pytest.fixture
def test_data():
    """Test data reference from exploration.txt"""
    return {
        "valid_products": {
            "apple_red": {"id": 1, "name": "Apple - Red", "price": 120, "stock": 195},
            "apple_green": {"id": 2, "name": "Apple - Green", "price": 130, "stock": 114},
            "banana": {"id": 3, "name": "Banana - Robusta", "price": 40, "stock": 282},
            "tomato": {"id": 16, "name": "Tomato - Hybrid", "price": 35, "stock": 190},
            "milk": {"id": 36, "name": "Milk - 1L", "price": 62, "stock": 260},
        },
        "inactive_products": [90, 91, 92],
        "out_of_stock_products": [70, 71, 72],
        "non_existent_product": 99999,
        "valid_coupons": {
            "WELCOME50": {"type": "FIXED", "value": 50, "min_cart": 100},
            "PERCENT10": {"type": "PERCENT", "value": 10, "min_cart": 300},
        },
        "expired_coupons": ["EXPIRED100", "EXPIRED50"],
        "valid_addresses": [
            {
                "label": "HOME",
                "street": "123 Main Street",
                "city": "Bangalore",
                "pincode": "560001"
            },
            {
                "label": "OFFICE",
                "street": "456 Corporate Avenue",
                "city": "Delhi",
                "pincode": "110001"
            }
        ],
        "valid_phone": "9876543210",
        "valid_name": "John Doe"
    }


def assert_valid_json_structure(response_data: Any, expected_keys: list = None):
    """Helper to assert response has valid structure."""
    assert isinstance(response_data, (dict, list)), "Response should be JSON serializable"
    if expected_keys and isinstance(response_data, dict):
        for key in expected_keys:
            assert key in response_data, f"Missing expected key: {key}"
