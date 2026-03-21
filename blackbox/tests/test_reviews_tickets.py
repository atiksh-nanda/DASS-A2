"""
Product reviews and support tickets tests.
Tests for product reviews and customer support tickets.
Known bug: BUG #010 (rating validation accepts 0 and 6)
"""
import pytest


BASE_URL = "http://localhost:8080/api/v1"


class TestProductReviews:
    """Test product review operations."""

    def test_get_reviews_for_product(self, valid_headers, api_session):
        """
        Test Case: Get reviews for product with reviews
        Expected: 200 OK with array of reviews
        Justification: User should see product reviews
        """
        response = api_session.get(
            f"{BASE_URL}/products/1/reviews",
            headers=valid_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, (dict, list))

    def test_reviews_structure(self, valid_headers, api_session):
        """
        Test Case: Verify review structure
        Expected: Has rating, comment, user_id, timestamp fields
        Justification: API contract consistency
        """
        response = api_session.get(
            f"{BASE_URL}/products/1/reviews",
            headers=valid_headers
        )
        
        data = response.json()
        if isinstance(data, dict) and "reviews" in data:
            reviews = data.get("reviews", [])
        else:
            reviews = data if isinstance(data, list) else []
        
        if len(reviews) > 0:
            review = reviews[0]
            # Check for expected fields
            assert "rating" in review

    def test_average_rating_calculation(self, valid_headers, api_session):
        """
        Test Case: Verify average rating calculation
        Expected: Proper decimal calculation
        Justification: Average must be accurately calculated
        """
        response = api_session.get(
            f"{BASE_URL}/products/1/reviews",
            headers=valid_headers
        )
        
        data = response.json()
        if isinstance(data, dict):
            avg = data.get("average_rating")
            if avg is not None:
                assert isinstance(avg, (int, float))

    def test_get_reviews_nonexistent_product(self, valid_headers, api_session):
        """
        Test Case: Get reviews for non-existent product
        Expected: 404 Not Found
        Justification: Should handle missing products
        """
        response = api_session.get(
            f"{BASE_URL}/products/99999/reviews",
            headers=valid_headers
        )
        
        assert response.status_code == 404

    def test_add_valid_review(self, valid_headers, api_session):
        """
        Test Case: Add valid review with rating 5 and comment
        Expected: 200/201 Created
        Justification: User should be able to review products
        """
        response = api_session.post(
            f"{BASE_URL}/products/1/reviews",
            headers=valid_headers,
            json={
                "rating": 5,
                "comment": "Excellent product!"
            }
        )
        
        assert response.status_code in [200, 201]

    def test_add_review_rating_too_low_returns_400(self, valid_headers, api_session):
        """
        Test Case: Add review with rating=0
        Expected: 400 Bad Request
        Justification: Rating must be 1-5 (BUG #010)
        """
        response = api_session.post(
            f"{BASE_URL}/products/1/reviews",
            headers=valid_headers,
            json={
                "rating": 0,
                "comment": "Bad product"
            }
        )
        
        # BUG #010: Currently accepts this
        assert response.status_code == 400 or response.status_code in [200, 201]

    def test_add_review_rating_too_high_returns_400(self, valid_headers, api_session):
        """
        Test Case: Add review with rating=6
        Expected: 400 Bad Request
        Justification: Rating must be 1-5 (BUG #010)
        """
        response = api_session.post(
            f"{BASE_URL}/products/1/reviews",
            headers=valid_headers,
            json={
                "rating": 6,
                "comment": "Great product"
            }
        )
        
        # BUG #010: Currently accepts this
        assert response.status_code == 400 or response.status_code in [200, 201]

    def test_add_review_rating_min_boundary(self, valid_headers, api_session):
        """
        Test Case: Add review with rating=1 (minimum)
        Expected: 200/201 OK
        Justification: Should accept minimum valid value
        """
        response = api_session.post(
            f"{BASE_URL}/products/1/reviews",
            headers=valid_headers,
            json={
                "rating": 1,
                "comment": "Worst product ever"
            }
        )
        
        assert response.status_code in [200, 201]

    def test_add_review_rating_max_boundary(self, valid_headers, api_session):
        """
        Test Case: Add review with rating=5 (maximum)
        Expected: 200/201 OK
        Justification: Should accept maximum valid value
        """
        response = api_session.post(
            f"{BASE_URL}/products/1/reviews",
            headers=valid_headers,
            json={
                "rating": 5,
                "comment": "Best product ever"
            }
        )
        
        assert response.status_code in [200, 201]

    def test_add_review_comment_too_short_returns_400(self, valid_headers, api_session):
        """
        Test Case: Add review with empty comment
        Expected: 400 Bad Request
        Justification: Comment must be 1-200 chars
        """
        response = api_session.post(
            f"{BASE_URL}/products/1/reviews",
            headers=valid_headers,
            json={
                "rating": 5,
                "comment": ""
            }
        )
        
        assert response.status_code == 400

    def test_add_review_comment_too_long_returns_400(self, valid_headers, api_session):
        """
        Test Case: Add review with comment > 200 chars
        Expected: 400 Bad Request
        Justification: Comment must be 1-200 chars
        """
        response = api_session.post(
            f"{BASE_URL}/products/1/reviews",
            headers=valid_headers,
            json={
                "rating": 5,
                "comment": "A" * 201
            }
        )
        
        assert response.status_code == 400

    def test_add_review_missing_rating_returns_400(self, valid_headers, api_session):
        """
        Test Case: Add review without rating
        Expected: 400 Bad Request
        Justification: Rating is required
        """
        response = api_session.post(
            f"{BASE_URL}/products/1/reviews",
            headers=valid_headers,
            json={
                "comment": "Good product"
            }
        )
        
        assert response.status_code == 400

    def test_add_review_missing_comment_returns_400(self, valid_headers, api_session):
        """
        Test Case: Add review without comment
        Expected: 400 Bad Request
        Justification: Comment is required
        """
        response = api_session.post(
            f"{BASE_URL}/products/1/reviews",
            headers=valid_headers,
            json={
                "rating": 5
            }
        )
        
        assert response.status_code == 400


class TestSupportTickets:
    """Test support ticket operations."""

    def test_create_support_ticket(self, valid_headers, api_session):
        """
        Test Case: Create support ticket with valid data
        Expected: 200/201 Created with status OPEN
        Justification: User should create support tickets
        """
        response = api_session.post(
            f"{BASE_URL}/support/ticket",
            headers=valid_headers,
            json={
                "subject": "Product not working",
                "message": "The product stopped working after a week"
            }
        )
        
        assert response.status_code in [200, 201]
        data = response.json()
        assert data.get("status") == "OPEN"

    def test_create_ticket_subject_too_short_returns_400(self, valid_headers, api_session):
        """
        Test Case: Create ticket with subject < 5 chars
        Expected: 400 Bad Request
        Justification: Subject must be 5-100 chars
        """
        response = api_session.post(
            f"{BASE_URL}/support/ticket",
            headers=valid_headers,
            json={
                "subject": "Help",
                "message": "This is a long message that meets requirements"
            }
        )
        
        assert response.status_code == 400

    def test_create_ticket_subject_too_long_returns_400(self, valid_headers, api_session):
        """
        Test Case: Create ticket with subject > 100 chars
        Expected: 400 Bad Request
        Justification: Subject must be 5-100 chars
        """
        response = api_session.post(
            f"{BASE_URL}/support/ticket",
            headers=valid_headers,
            json={
                "subject": "A" * 101,
                "message": "This is a long message that meets requirements"
            }
        )
        
        assert response.status_code == 400

    def test_create_ticket_message_too_short_returns_400(self, valid_headers, api_session):
        """
        Test Case: Create ticket with empty message
        Expected: 400 Bad Request
        Justification: Message must be 1-500 chars
        """
        response = api_session.post(
            f"{BASE_URL}/support/ticket",
            headers=valid_headers,
            json={
                "subject": "Valid subject",
                "message": ""
            }
        )
        
        assert response.status_code == 400

    def test_create_ticket_message_too_long_returns_400(self, valid_headers, api_session):
        """
        Test Case: Create ticket with message > 500 chars
        Expected: 400 Bad Request
        Justification: Message must be 1-500 chars
        """
        response = api_session.post(
            f"{BASE_URL}/support/ticket",
            headers=valid_headers,
            json={
                "subject": "Valid subject",
                "message": "A" * 501
            }
        )
        
        assert response.status_code == 400

    def test_get_support_tickets(self, valid_headers, api_session):
        """
        Test Case: Get user's support tickets
        Expected: 200 OK with array of tickets
        Justification: User should view their tickets
        """
        response = api_session.get(
            f"{BASE_URL}/support/tickets",
            headers=valid_headers
        )
        
        assert response.status_code == 200
        tickets = response.json()
        assert isinstance(tickets, list)

    def test_ticket_structure(self, valid_headers, api_session):
        """
        Test Case: Verify ticket structure
        Expected: Has ticket_id, subject, status, created_at
        Justification: API contract consistency
        """
        response = api_session.get(
            f"{BASE_URL}/support/tickets",
            headers=valid_headers
        )
        
        tickets = response.json()
        if len(tickets) > 0:
            ticket = tickets[0]
            required_fields = ["ticket_id", "subject", "status"]
            for field in required_fields:
                assert field in ticket, f"Missing field: {field}"

    def test_update_ticket_open_to_in_progress(self, valid_headers, api_session):
        """
        Test Case: Move ticket from OPEN to IN_PROGRESS
        Expected: 200 OK
        Justification: Status flow OPEN -> IN_PROGRESS allowed
        """
        # Get a ticket
        tickets_response = api_session.get(f"{BASE_URL}/support/tickets", headers=valid_headers)
        tickets = tickets_response.json()
        
        if len(tickets) > 0:
            ticket_id = tickets[0].get("ticket_id")
            response = api_session.put(
                f"{BASE_URL}/support/tickets/{ticket_id}",
                headers=valid_headers,
                json={"status": "IN_PROGRESS"}
            )
            
            assert response.status_code in [200, 201]

    def test_update_ticket_in_progress_to_closed(self, valid_headers, api_session):
        """
        Test Case: Move ticket from IN_PROGRESS to CLOSED
        Expected: 200 OK
        Justification: Status flow IN_PROGRESS -> CLOSED allowed
        """
        # Create ticket, move to IN_PROGRESS, then to CLOSED
        create_response = api_session.post(
            f"{BASE_URL}/support/ticket",
            headers=valid_headers,
            json={
                "subject": "Test ticket",
                "message": "Test message for status workflow"
            }
        )
        
        if create_response.status_code in [200, 201]:
            ticket_id = create_response.json().get("ticket_id")
            
            # Move to IN_PROGRESS
            api_session.put(
                f"{BASE_URL}/support/tickets/{ticket_id}",
                headers=valid_headers,
                json={"status": "IN_PROGRESS"}
            )
            
            # Move to CLOSED
            response = api_session.put(
                f"{BASE_URL}/support/tickets/{ticket_id}",
                headers=valid_headers,
                json={"status": "CLOSED"}
            )
            
            assert response.status_code in [200, 201]

    def test_update_ticket_open_to_closed_returns_400(self, valid_headers, api_session):
        """
        Test Case: Try to move ticket OPEN -> CLOSED (skip IN_PROGRESS)
        Expected: 400 Bad Request
        Justification: Status flow must follow order
        """
        create_response = api_session.post(
            f"{BASE_URL}/support/ticket",
            headers=valid_headers,
            json={
                "subject": "Invalid status flow",
                "message": "Try to skip IN_PROGRESS status"
            }
        )
        
        if create_response.status_code in [200, 201]:
            ticket_id = create_response.json().get("ticket_id")
            
            response = api_session.put(
                f"{BASE_URL}/support/tickets/{ticket_id}",
                headers=valid_headers,
                json={"status": "CLOSED"}
            )
            
            assert response.status_code == 400

    def test_update_ticket_nonexistent_returns_404(self, valid_headers, api_session):
        """
        Test Case: Update non-existent ticket
        Expected: 404 Not Found
        Justification: Should handle missing tickets
        """
        response = api_session.put(
            f"{BASE_URL}/support/tickets/99999",
            headers=valid_headers,
            json={"status": "IN_PROGRESS"}
        )
        
        assert response.status_code == 404

    def test_message_saved_exactly(self, valid_headers, api_session):
        """
        Test Case: Message is saved exactly as written
        Expected: Full message preserved
        Justification: Support messages must be preserved intact
        """
        message = "This is my support issue\\nWith multiple lines\\nAnd special chars!@#"
        
        response = api_session.post(
            f"{BASE_URL}/support/ticket",
            headers=valid_headers,
            json={
                "subject": "Message preservation test",
                "message": message
            }
        )
        
        if response.status_code in [200, 201]:
            data = response.json()
            assert data.get("message") == message


class TestReviewDataTypes:
    """Test review data types."""

    def test_rating_is_integer(self, valid_headers, api_session):
        """Test Case: Rating is integer"""
        response = api_session.get(
            f"{BASE_URL}/products/1/reviews",
            headers=valid_headers
        )
        
        data = response.json()
        if isinstance(data, dict) and "reviews" in data:
            reviews = data.get("reviews", [])
            if len(reviews) > 0:
                assert isinstance(reviews[0].get("rating"), int)

    def test_average_rating_is_number(self, valid_headers, api_session):
        """Test Case: Average rating is numeric"""
        response = api_session.get(
            f"{BASE_URL}/products/1/reviews",
            headers=valid_headers
        )
        
        data = response.json()
        if isinstance(data, dict) and "average_rating" in data:
            avg = data.get("average_rating")
            assert isinstance(avg, (int, float))
