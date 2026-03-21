"""
Address management tests.
Tests for creating, updating, deleting addresses.
Known bug: BUG #008 (pincode validation), BUG #009 (address ID sequencing)
"""
import pytest


BASE_URL = "http://localhost:8080/api/v1"


class TestAddressCreation:
    """Test creating addresses."""

    def test_create_valid_address_home(self, valid_headers, api_session):
        """
        Test Case: Create valid HOME address
        Expected: 201 Created with address object
        Justification: Basic address creation
        """
        response = api_session.post(
            f"{BASE_URL}/addresses",
            headers=valid_headers,
            json={
                "label": "HOME",
                "street": "123 Main Street",
                "city": "Bangalore",
                "pincode": "560001"
            }
        )
        
        assert response.status_code in [200, 201]
        data = response.json()
        assert data.get("address_id") is not None
        assert data.get("label") == "HOME"
        assert data.get("street") == "123 Main Street"

    def test_create_address_invalid_label_returns_400(self, valid_headers, api_session):
        """
        Test Case: Create address with invalid label
        Expected: 400 Bad Request
        Justification: Only HOME, OFFICE, OTHER allowed
        """
        response = api_session.post(
            f"{BASE_URL}/addresses",
            headers=valid_headers,
            json={
                "label": "WORK",
                "street": "123 Main Street",
                "city": "Bangalore",
                "pincode": "560001"
            }
        )
        
        assert response.status_code == 400

    def test_create_address_street_too_short_returns_400(self, valid_headers, api_session):
        """
        Test Case: Street too short (< 5 chars)
        Expected: 400 Bad Request
        Justification: Street must be 5-100 chars
        """
        response = api_session.post(
            f"{BASE_URL}/addresses",
            headers=valid_headers,
            json={
                "label": "HOME",
                "street": "123",
                "city": "Bangalore",
                "pincode": "560001"
            }
        )
        
        assert response.status_code == 400

    def test_create_address_street_too_long_returns_400(self, valid_headers, api_session):
        """
        Test Case: Street too long (> 100 chars)
        Expected: 400 Bad Request
        Justification: Street must be 5-100 chars
        """
        response = api_session.post(
            f"{BASE_URL}/addresses",
            headers=valid_headers,
            json={
                "label": "HOME",
                "street": "A" * 101,
                "city": "Bangalore",
                "pincode": "560001"
            }
        )
        
        assert response.status_code == 400

    def test_create_address_city_too_short_returns_400(self, valid_headers, api_session):
        """
        Test Case: City too short (< 2 chars)
        Expected: 400 Bad Request
        Justification: City must be 2-50 chars
        """
        response = api_session.post(
            f"{BASE_URL}/addresses",
            headers=valid_headers,
            json={
                "label": "HOME",
                "street": "123 Main Street",
                "city": "B",
                "pincode": "560001"
            }
        )
        
        assert response.status_code == 400

    def test_create_address_city_too_long_returns_400(self, valid_headers, api_session):
        """
        Test Case: City too long (> 50 chars)
        Expected: 400 Bad Request
        Justification: City must be 2-50 chars
        """
        response = api_session.post(
            f"{BASE_URL}/addresses",
            headers=valid_headers,
            json={
                "label": "HOME",
                "street": "123 Main Street",
                "city": "A" * 51,
                "pincode": "560001"
            }
        )
        
        assert response.status_code == 400

    def test_create_address_pincode_invalid_returns_400(self, valid_headers, api_session):
        """
        Test Case: Pincode not exactly 6 digits
        Expected: 400 Bad Request
        Justification: Pincode must be exactly 6 digits (BUG #008)
        """
        response = api_session.post(
            f"{BASE_URL}/addresses",
            headers=valid_headers,
            json={
                "label": "HOME",
                "street": "123 Main Street",
                "city": "Bangalore",
                "pincode": "56000"  # Only 5 digits
            }
        )
        
        assert response.status_code == 400

    def test_create_address_pincode_with_letters_returns_400(self, valid_headers, api_session):
        """
        Test Case: Pincode with letters
        Expected: 400 Bad Request
        Justification: Pincode digits only
        """
        response = api_session.post(
            f"{BASE_URL}/addresses",
            headers=valid_headers,
            json={
                "label": "HOME",
                "street": "123 Main Street",
                "city": "Bangalore",
                "pincode": "56000A"
            }
        )
        
        assert response.status_code == 400

    def test_create_default_address_success(self, valid_headers, api_session):
        """
        Test Case: Create address as default
        Expected: 201 Created with is_default=true
        Justification: Should support setting default
        """
        response = api_session.post(
            f"{BASE_URL}/addresses",
            headers=valid_headers,
            json={
                "label": "HOME",
                "street": "123 Main Street",
                "city": "Bangalore",
                "pincode": "56000",
                "is_default": True
            }
        )
        
        assert response.status_code in [200, 201]
        data = response.json()
        assert data.get("is_default") is True

    def test_create_default_removes_old_default(self, valid_headers, api_session):
        """
        Test Case: Create new default when one exists
        Expected: Old default becomes is_default=false
        Justification: Only one default allowed
        """
        # Create first address as default
        first = api_session.post(
            f"{BASE_URL}/addresses",
            headers=valid_headers,
            json={
                "label": "HOME",
                "street": "123 Main Street",
                "city": "Bangalore",
                "pincode": "56000",
                "is_default": True
            }
        )
        
        # Create second address as default
        api_session.post(
            f"{BASE_URL}/addresses",
            headers=valid_headers,
            json={
                "label": "OFFICE",
                "street": "456 Office Ave",
                "city": "Delhi",
                "pincode": "11000",
                "is_default": True
            }
        )
        
        # Verify first is no longer default
        addresses = api_session.get(f"{BASE_URL}/addresses", headers=valid_headers).json()
        first_addr = next((a for a in addresses if a.get("address_id") == first.json().get("address_id")), None)
        if first_addr:
            assert first_addr.get("is_default") is False


class TestAddressUpdate:
    """Test updating addresses."""

    def test_update_street_successful(self, valid_headers, api_session):
        """
        Test Case: Update address street
        Expected: 200 OK with updated data
        Justification: Street should be updatable
        """
        # Create address
        created = api_session.post(
            f"{BASE_URL}/addresses",
            headers=valid_headers,
            json={
                "label": "HOME",
                "street": "123 Main Street",
                "city": "Bangalore",
                "pincode": "56000"
            }
        )
        assert created.status_code in [200, 201]
        
        address_id = created.json().get("address_id")
        
        response = api_session.put(
            f"{BASE_URL}/addresses/{address_id}",
            headers=valid_headers,
            json={"street": "456 New Street"}
        )
        
        assert response.status_code in [200, 201]
        data = response.json()
        assert data.get("street") == "456 New Street"

    def test_update_to_default_successful(self, valid_headers, api_session):
        """
        Test Case: Update address to default
        Expected: 200 OK, this address becomes default
        Justification: Should allow setting as default
        """
        created = api_session.post(
            f"{BASE_URL}/addresses",
            headers=valid_headers,
            json={
                "label": "HOME",
                "street": "123 Main Street",
                "city": "Bangalore",
                "pincode": "56000"
            }
        )
        assert created.status_code in [200, 201]
        
        address_id = created.json().get("address_id")
        
        response = api_session.put(
            f"{BASE_URL}/addresses/{address_id}",
            headers=valid_headers,
            json={"is_default": True}
        )
        
        assert response.status_code in [200, 201]
        data = response.json()
        assert data.get("is_default") is True

    def test_update_label_returns_400(self, valid_headers, api_session):
        """
        Test Case: Try to update label
        Expected: 400 Bad Request
        Justification: Label cannot be changed
        """
        created = api_session.post(
            f"{BASE_URL}/addresses",
            headers=valid_headers,
            json={
                "label": "HOME",
                "street": "123 Main Street",
                "city": "Bangalore",
                "pincode": "56000"
            }
        )
        assert created.status_code in [200, 201]
        
        address_id = created.json().get("address_id")
        
        response = api_session.put(
            f"{BASE_URL}/addresses/{address_id}",
            headers=valid_headers,
            json={"label": "OFFICE"}
        )
        
        assert response.status_code == 400

    def test_update_city_returns_400(self, valid_headers, api_session):
        """
        Test Case: Try to update city
        Expected: 400 Bad Request
        Justification: City cannot be changed
        """
        created = api_session.post(
            f"{BASE_URL}/addresses",
            headers=valid_headers,
            json={
                "label": "HOME",
                "street": "123 Main Street",
                "city": "Bangalore",
                "pincode": "56000"
            }
        )
        assert created.status_code in [200, 201]
        
        address_id = created.json().get("address_id")
        
        response = api_session.put(
            f"{BASE_URL}/addresses/{address_id}",
            headers=valid_headers,
            json={"city": "Delhi"}
        )
        
        assert response.status_code == 400

    def test_update_nonexistent_address_returns_404(self, valid_headers, api_session):
        """
        Test Case: Update non-existent address
        Expected: 404 Not Found
        Justification: Should handle missing resources
        """
        response = api_session.put(
            f"{BASE_URL}/addresses/99999",
            headers=valid_headers,
            json={"street": "New Street"}
        )
        
        assert response.status_code == 404


class TestAddressDelete:
    """Test deleting addresses."""

    def test_delete_address_successful(self, valid_headers, api_session):
        """
        Test Case: Delete existing address
        Expected: 200 OK, address removed
        Justification: Should support address deletion
        """
        created = api_session.post(
            f"{BASE_URL}/addresses",
            headers=valid_headers,
            json={
                "label": "HOME",
                "street": "123 Main Street",
                "city": "Bangalore",
                "pincode": "56000"
            }
        )
        assert created.status_code in [200, 201]
        
        address_id = created.json().get("address_id")
        
        response = api_session.delete(
            f"{BASE_URL}/addresses/{address_id}",
            headers=valid_headers
        )
        
        assert response.status_code in [200, 204]

    def test_delete_nonexistent_address_returns_404(self, valid_headers, api_session):
        """
        Test Case: Delete non-existent address
        Expected: 404 Not Found
        Justification: Should handle missing resources
        """
        response = api_session.delete(
            f"{BASE_URL}/addresses/99999",
            headers=valid_headers
        )
        
        assert response.status_code == 404


class TestAddressRetrieval:
    """Test retrieving addresses."""

    def test_get_all_addresses(self, valid_headers, api_session):
        """
        Test Case: Get user's addresses
        Expected: 200 OK with array of addresses
        Justification: Should list all user addresses
        """
        response = api_session.get(
            f"{BASE_URL}/addresses",
            headers=valid_headers
        )
        
        assert response.status_code == 200
        addresses = response.json()
        assert isinstance(addresses, list)

    def test_address_structure(self, valid_headers, api_session):
        """
        Test Case: Verify address object structure
        Expected: Has address_id, label, street, city, pincode, is_default
        Justification: API contract consistency
        """
        response = api_session.get(
            f"{BASE_URL}/addresses",
            headers=valid_headers
        )
        
        addresses = response.json()
        if len(addresses) > 0:
            address = addresses[0]
            required_fields = ["address_id", "label", "street", "city", "pincode", "is_default"]
            for field in required_fields:
                assert field in address, f"Missing field: {field}"
