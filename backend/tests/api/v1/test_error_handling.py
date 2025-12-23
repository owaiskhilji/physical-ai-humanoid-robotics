import pytest
from fastapi.testclient import TestClient
from src.main import app


@pytest.fixture(scope="module")
def client():
    """Create test client for API testing"""
    with TestClient(app) as test_client:
        yield test_client


def test_no_content_found_response(client):
    """Test response when no relevant content is found for a query (FR-010)"""
    # First create a session
    session_data = {
        "session_title": "No Content Found Test",
        "user_id": "no-content-user"
    }
    session_response = client.post("/api/v1/chat/start", json=session_data)
    assert session_response.status_code == 200
    session_id = session_response.json()["id"]

    # Ask a question that likely won't have relevant content in the textbook
    message_data = {
        "session_id": session_id,
        "message": "What is the current weather in Tokyo?",
        "selected_text": None
    }

    response = client.post("/api/v1/chat/message", json=message_data)
    assert response.status_code == 200

    data = response.json()
    response_text = data["response"]

    # The response should acknowledge that the information is not available in the textbook
    assert response_text is not None

    has_appropriate_response = (
        "not found" in response_text.lower() or
        "no relevant" in response_text.lower() or
        "cannot find" in response_text.lower() or
        "not available" in response_text.lower() or
        "not mentioned" in response_text.lower() or
        "only answer" in response_text.lower() or
        "based on the provided" in response_text.lower() or
        "textbook" in response_text.lower()
    )

    assert has_appropriate_response, f"Response should indicate lack of relevant content: {response_text}"


def test_invalid_session_id(client):
    """Test error handling when using an invalid session ID"""
    invalid_session_id = "invalid-session-id-12345"

    message_data = {
        "session_id": invalid_session_id,
        "message": "What is Physical AI?",
        "selected_text": None
    }

    response = client.post("/api/v1/chat/message", json=message_data)
    # This might return 404 or 422 depending on validation, both are acceptable
    assert response.status_code in [404, 422, 500]

    if response.status_code == 200:
        # If it somehow succeeds, check that it handles the invalid session appropriately
        data = response.json()
        assert "response" in data
        # The system might create a new session or return an error message


def test_retrieve_nonexistent_session(client):
    """Test retrieving a session that doesn't exist"""
    nonexistent_session_id = "nonexistent-session-id-67890"

    response = client.get(f"/api/v1/chat/session/{nonexistent_session_id}")
    assert response.status_code == 404

    data = response.json()
    assert "detail" in data


def test_close_nonexistent_session(client):
    """Test closing a session that doesn't exist"""
    nonexistent_session_id = "nonexistent-session-id-11111"

    response = client.delete(f"/api/v1/chat/session/{nonexistent_session_id}")
    assert response.status_code == 404

    data = response.json()
    assert "detail" in data


def test_invalid_chapter_number(client):
    """Test retrieving a chapter that doesn't exist"""
    invalid_chapter_number = 999  # Very high number that shouldn't exist

    response = client.get(f"/api/v1/content/chapter/{invalid_chapter_number}")
    # Should return 404 for not found
    assert response.status_code == 404

    data = response.json()
    assert "detail" in data
    assert "not found" in data["detail"].lower()


def test_duplicate_chapter_creation(client):
    """Test error handling when trying to create a duplicate chapter"""
    # First create a chapter
    chapter_data = {
        "chapter_number": 95,
        "chapter_title": "Duplicate Test Chapter",
        "content_text": "This chapter is created to test duplicate handling. It contains enough text to pass validation requirements.",
        "version": "1.0"
    }

    # Create the chapter (first time should succeed or conflict)
    first_response = client.post("/api/v1/content/chapter", json=chapter_data)
    assert first_response.status_code in [200, 409]  # 409 if already exists

    # Try to create the same chapter again (should fail with conflict)
    second_response = client.post("/api/v1/content/chapter", json=chapter_data)
    assert second_response.status_code == 409  # Conflict

    second_data = second_response.json()
    assert "detail" in second_data
    assert "already exists" in second_data["detail"]

    # Clean up
    client.delete("/api/v1/content/chapter/95")


def test_invalid_content_data(client):
    """Test error handling with invalid content data"""
    # Try to create content that doesn't meet validation requirements
    invalid_chapter_data = {
        "chapter_number": 94,
        "chapter_title": "Too Short Content Test",
        "content_text": "Too short",  # This is under the 100 character minimum
        "version": "1.0"
    }

    response = client.post("/api/v1/content/chapter", json=invalid_chapter_data)
    # Should return 400 for validation error
    assert response.status_code == 400

    data = response.json()
    assert "detail" in data


def test_empty_message_handling(client):
    """Test handling of empty or invalid messages"""
    # First create a session
    session_data = {
        "session_title": "Empty Message Test",
        "user_id": "empty-message-user"
    }
    session_response = client.post("/api/v1/chat/start", json=session_data)
    assert session_response.status_code == 200
    session_id = session_response.json()["id"]

    # Try sending an empty message
    message_data = {
        "session_id": session_id,
        "message": "",
        "selected_text": None
    }

    response = client.post("/api/v1/chat/message", json=message_data)
    # This might return 200 with an appropriate response or 422 for validation error
    assert response.status_code in [200, 422]

    if response.status_code == 200:
        data = response.json()
        assert "response" in data
        # The system should handle empty messages gracefully


def test_malformed_json_handling(client):
    """Test error handling for malformed JSON requests"""
    # Send malformed JSON to chat endpoint
    response = client.post(
        "/api/v1/chat/message",
        content="{invalid json",
        headers={"Content-Type": "application/json"}
    )
    # Should return 422 for validation error or 400 for malformed JSON
    assert response.status_code in [400, 422]


def test_rate_limiting_graceful_handling(client):
    """Test that the system handles high request volume gracefully"""
    # First create a session
    session_data = {
        "session_title": "Rate Limit Test",
        "user_id": "rate-limit-user"
    }
    session_response = client.post("/api/v1/chat/start", json=session_data)
    assert session_response.status_code == 200
    session_id = session_response.json()["id"]

    # Send multiple requests rapidly (simulating high load)
    for i in range(5):
        message_data = {
            "session_id": session_id,
            "message": f"Test message {i} for rate limiting",
            "selected_text": None
        }

        response = client.post("/api/v1/chat/message", json=message_data)
        # Each request should be handled appropriately
        assert response.status_code in [200, 429]  # 429 for rate limit exceeded

        if response.status_code == 200:
            data = response.json()
            assert "response" in data


def test_graceful_degradation(client):
    """Test that the system degrades gracefully under error conditions"""
    # Test various error conditions and ensure the system remains stable

    # Try to retrieve a very large number that shouldn't exist
    response = client.get("/api/v1/content/chapter/999999")
    assert response.status_code in [404, 400, 500]  # Should handle gracefully

    # Try to create content with invalid data
    invalid_data = {
        "chapter_number": -1,  # Invalid chapter number
        "chapter_title": "",
        "content_text": "",
        "version": ""
    }
    response = client.post("/api/v1/content/chapter", json=invalid_data)
    assert response.status_code in [400, 422]  # Should handle validation gracefully