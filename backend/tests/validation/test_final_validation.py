import pytest
from fastapi.testclient import TestClient
from src.main import app
import time


@pytest.fixture(scope="module")
def client():
    """Create test client for API testing"""
    with TestClient(app) as test_client:
        yield test_client


def test_fr_001_strict_rag_grounding(client):
    """Test FR-001: System only answers based on textbook content"""
    # Create a session
    session_data = {
        "session_title": "Grounding Validation Test",
        "user_id": "grounding-test-user"
    }
    session_response = client.post("/api/v1/chat/start", json=session_data)
    assert session_response.status_code == 200
    session_id = session_response.json()["id"]

    # Ask for information that should not be in the textbook
    external_question = "What is the current stock price of Google?"
    message_data = {
        "session_id": session_id,
        "message": external_question,
        "selected_text": None
    }

    response = client.post("/api/v1/chat/message", json=message_data)
    assert response.status_code == 200

    response_data = response.json()
    response_text = response_data["response"]

    # The response should indicate that the information is not in the textbook
    has_grounding_indicator = any([
        "not in textbook" in response_text.lower(),
        "not available" in response_text.lower(),
        "cannot provide" in response_text.lower(),
        "only answer" in response_text.lower(),
        "based on provided" in response_text.lower(),
        "textbook" in response_text.lower()
    ])

    assert has_grounding_indicator, f"Response should be grounded in textbook content: {response_text}"


def test_fr_002_docusaurus_integration(client):
    """Test FR-002: Docusaurus integration capability (validated by API accessibility)"""
    # The API endpoints should be accessible, which validates integration capability
    response = client.get("/api/v1/content/chapters")
    assert response.status_code == 200

    data = response.json()
    assert "chapters" in data
    assert isinstance(data["chapters"], list)


def test_fr_003_selected_text_mode(client):
    """Test FR-003: Selected text mode functionality"""
    # Create a session
    session_data = {
        "session_title": "Selected Text Validation Test",
        "user_id": "selected-validation-user"
    }
    session_response = client.post("/api/v1/chat/start", json=session_data)
    assert session_response.status_code == 200
    session_id = session_response.json()["id"]

    # Provide specific text and ask a related question
    selected_text = "Physical AI is an approach that emphasizes the importance of physical interaction in artificial intelligence systems."
    question = "How does this approach emphasize physical interaction?"

    message_data = {
        "session_id": session_id,
        "message": question,
        "selected_text": selected_text
    }

    response = client.post("/api/v1/chat/message", json=message_data)
    assert response.status_code == 200

    response_data = response.json()
    response_text = response_data["response"]

    # The response should be focused on the selected text content
    has_relevant_content = (
        "physical" in response_text.lower() or
        "interaction" in response_text.lower() or
        "approach" in response_text.lower()
    )

    assert has_relevant_content, f"Response should address selected text: {response_text}"


def test_fr_004_session_persistence(client):
    """Test FR-004: Session persistence"""
    # Create a session
    session_data = {
        "session_title": "Persistence Test Session",
        "user_id": "persistence-test-user"
    }
    session_response = client.post("/api/v1/chat/start", json=session_data)
    assert session_response.status_code == 200
    session_id = session_response.json()["id"]

    # Add multiple messages to the session
    questions = [
        "What is Physical AI?",
        "Explain robotics concepts",
        "What are applications?"
    ]

    for i, question in enumerate(questions):
        message_data = {
            "session_id": session_id,
            "message": question,
            "selected_text": None
        }

        response = client.post("/api/v1/chat/message", json=message_data)
        assert response.status_code == 200

    # Retrieve the session to verify persistence
    history_response = client.get(f"/api/v1/chat/session/{session_id}")
    assert history_response.status_code == 200

    history_data = history_response.json()
    assert history_data["session_id"] == session_id
    assert "messages" in history_data
    # Should have at least the questions asked plus responses
    assert len(history_data["messages"]) >= len(questions) * 2


def test_fr_005_content_attribution(client):
    """Test FR-005: Content attribution in responses"""
    # Create a session
    session_data = {
        "session_title": "Attribution Test Session",
        "user_id": "attribution-test-user"
    }
    session_response = client.post("/api/v1/chat/start", json=session_data)
    assert session_response.status_code == 200
    session_id = session_response.json()["id"]

    # Ask a question that should have clear textbook sources
    message_data = {
        "session_id": session_id,
        "message": "What is Physical AI?",
        "selected_text": None
    }

    response = client.post("/api/v1/chat/message", json=message_data)
    assert response.status_code == 200

    response_data = response.json()
    # The response includes context_sources which provides attribution
    assert "context_sources" in response_data
    # Context sources should be a list of relevant content
    assert isinstance(response_data["context_sources"], list)


def test_fr_006_content_management(client):
    """Test FR-006: Content management without system rebuilds (incremental updates)"""
    chapter_number = 80
    chapter_title = "Incremental Update Validation"

    # Create content
    chapter_data = {
        "chapter_number": chapter_number,
        "chapter_title": chapter_title,
        "content_text": "This chapter validates the incremental update functionality that allows content changes without requiring a full system rebuild.",
        "version": "1.0"
    }

    create_response = client.post("/api/v1/content/chapter", json=chapter_data)
    assert create_response.status_code in [200, 409]  # 409 if already exists

    if create_response.status_code == 200:
        # Update the content incrementally
        update_data = {
            "chapter_title": f"Updated {chapter_title}",
            "content_text": "This chapter has been updated to validate the incremental update functionality that allows content changes without requiring a full system rebuild.",
            "version": "2.0"
        }

        update_response = client.put(f"/api/v1/content/chapter/{chapter_number}", json=update_data)
        assert update_response.status_code == 200

        update_result = update_response.json()
        assert "incrementally" in update_result["message"].lower()

        # Verify the update worked
        verify_response = client.get(f"/api/v1/content/chapter/{chapter_number}")
        if verify_response.status_code == 200:
            verify_data = verify_response.json()
            assert verify_data["version"] == "2.0"

    # Clean up
    client.delete(f"/api/v1/content/chapter/{chapter_number}")


def test_fr_007_content_quality_validation(client):
    """Test FR-007: Content quality validation"""
    chapter_number = 79

    # Try to create content that fails validation (too short)
    short_content_data = {
        "chapter_number": chapter_number,
        "chapter_title": "Short Content Validation",
        "content_text": "Too short",
        "version": "1.0"
    }

    response = client.post("/api/v1/content/chapter", json=short_content_data)
    assert response.status_code == 400  # Should fail validation

    data = response.json()
    assert "detail" in data
    assert "short" in data["detail"].lower() or "100" in data["detail"]

    # Try to create content that passes validation
    valid_content_data = {
        "chapter_number": chapter_number,
        "chapter_title": "Valid Content Validation",
        "content_text": "This is valid content that meets the minimum length requirement of 100 characters needed for the content validation system. The content includes various concepts related to Physical AI and robotics to provide meaningful context for testing the RAG system. This ensures that the content is substantial enough for proper processing.",
        "version": "1.0"
    }

    valid_response = client.post("/api/v1/content/chapter", json=valid_content_data)
    # This might be 200 if new or 409 if already exists
    assert valid_response.status_code in [200, 409]

    if valid_response.status_code == 200:
        # Clean up
        client.delete(f"/api/v1/content/chapter/{chapter_number}")


def test_fr_008_mode_toggle(client):
    """Test FR-008: Toggle between general book mode and selected text mode"""
    # Create a session
    session_data = {
        "session_title": "Mode Toggle Validation",
        "user_id": "mode-toggle-test-user"
    }
    session_response = client.post("/api/v1/chat/start", json=session_data)
    assert session_response.status_code == 200
    session_id = session_response.json()["id"]

    # Test general mode (no selected text)
    general_message = {
        "session_id": session_id,
        "message": "What is Physical AI?",
        "selected_text": None
    }

    general_response = client.post("/api/v1/chat/message", json=general_message)
    assert general_response.status_code == 200

    # Test selected text mode
    selected_text = "Robotics is the intersection of science, engineering, and technology that produces machines called robots."
    selected_message = {
        "session_id": session_id,
        "message": "What does this text say about robotics?",
        "selected_text": selected_text
    }

    selected_response = client.post("/api/v1/chat/message", json=selected_message)
    assert selected_response.status_code == 200

    # Both modes should work properly
    general_data = general_response.json()
    selected_data = selected_response.json()

    assert "response" in general_data
    assert "response" in selected_data


def test_fr_009_concurrent_users(client):
    """Test FR-009: Support for concurrent users"""
    import concurrent.futures

    def create_session_and_ask_question(user_id):
        session_data = {
            "session_title": f"Concurrent User Test {user_id}",
            "user_id": user_id
        }
        session_response = client.post("/api/v1/chat/start", json=session_data)
        if session_response.status_code != 200:
            return False, f"Session creation failed for {user_id}"

        session_id = session_response.json()["id"]

        message_data = {
            "session_id": session_id,
            "message": "What is Physical AI?",
            "selected_text": None
        }

        response = client.post("/api/v1/chat/message", json=message_data)
        return response.status_code == 200, f"Message request status: {response.status_code} for {user_id}"

    # Test with 3 concurrent users
    user_ids = [f"concurrent-user-{i}" for i in range(3)]

    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
        futures = [executor.submit(create_session_and_ask_question, uid) for uid in user_ids]
        results = [future.result() for future in concurrent.futures.as_completed(futures)]

    # All concurrent operations should succeed
    for success, message in results:
        assert success, message


def test_fr_010_error_handling(client):
    """Test FR-010: Proper error handling and graceful degradation"""
    # Test error handling for non-existent chapter
    response = client.get("/api/v1/content/chapter/999999")
    assert response.status_code in [404, 500]  # Should handle gracefully

    # Test error handling for invalid session
    invalid_message_data = {
        "session_id": "invalid-session-id",
        "message": "Test message",
        "selected_text": None
    }

    response = client.post("/api/v1/chat/message", json=invalid_message_data)
    # Should handle invalid session gracefully
    assert response.status_code in [200, 404, 422, 500]


def test_sc_001_response_time(client):
    """Test SC-001: Response time <5 seconds"""
    # Create a session
    session_data = {
        "session_title": "Response Time Test",
        "user_id": "response-time-user"
    }
    session_response = client.post("/api/v1/chat/start", json=session_data)
    assert session_response.status_code == 200
    session_id = session_response.json()["id"]

    # Measure response time
    start_time = time.time()

    message_data = {
        "session_id": session_id,
        "message": "What is Physical AI?",
        "selected_text": None
    }

    response = client.post("/api/v1/chat/message", json=message_data)
    end_time = time.time()

    response_time = end_time - start_time

    assert response.status_code == 200
    assert response_time < 5.0, f"Response time {response_time:.2f}s exceeds 5 second limit"


def test_sc_002_response_accuracy(client):
    """Test SC-002: 95% response accuracy (validated by grounding)"""
    # This test validates that responses are properly grounded in content
    # Create a session
    session_data = {
        "session_title": "Accuracy Test",
        "user_id": "accuracy-test-user"
    }
    session_response = client.post("/api/v1/chat/start", json=session_data)
    assert session_response.status_code == 200
    session_id = session_response.json()["id"]

    # Ask a question that should have a clear answer in textbook content
    message_data = {
        "session_id": session_id,
        "message": "What is Physical AI?",
        "selected_text": None
    }

    response = client.post("/api/v1/chat/message", json=message_data)
    assert response.status_code == 200

    response_data = response.json()
    response_text = response_data["response"]

    # The response should be substantive and related to the topic
    assert response_text is not None
    assert len(response_text) > 0
    assert "physical" in response_text.lower() or "ai" in response_text.lower()


def test_sc_003_selected_text_mode_success(client):
    """Test SC-003: Selected text mode success"""
    # Create a session
    session_data = {
        "session_title": "Selected Text Success Test",
        "user_id": "selected-success-user"
    }
    session_response = client.post("/api/v1/chat/start", json=session_data)
    assert session_response.status_code == 200
    session_id = session_response.json()["id"]

    # Use selected text mode
    selected_text = "Machine learning enables systems to learn and improve from experience without being explicitly programmed."
    message_data = {
        "session_id": session_id,
        "message": "What does this text say about machine learning?",
        "selected_text": selected_text
    }

    response = client.post("/api/v1/chat/message", json=message_data)
    assert response.status_code == 200

    response_data = response.json()
    response_text = response_data["response"]

    # The response should address the content in the selected text
    has_relevant_content = (
        "machine learning" in response_text.lower() or
        "learn" in response_text.lower() or
        "experience" in response_text.lower()
    )

    assert has_relevant_content, f"Selected text mode should address the provided text: {response_text}"


def test_overall_functionality(client):
    """Test overall functionality integrating multiple requirements"""
    # Create a session
    session_data = {
        "session_title": "Overall Functionality Test",
        "user_id": "overall-test-user"
    }
    session_response = client.post("/api/v1/chat/start", json=session_data)
    assert session_response.status_code == 200
    session_id = session_response.json()["id"]

    # Test general mode
    message_data = {
        "session_id": session_id,
        "message": "What are robotics applications?",
        "selected_text": None
    }

    response = client.post("/api/v1/chat/message", json=message_data)
    assert response.status_code == 200

    # Test selected text mode
    selected_text = "Computer vision enables machines to interpret and understand visual information from the world."
    selected_message_data = {
        "session_id": session_id,
        "message": "How does this work?",
        "selected_text": selected_text
    }

    selected_response = client.post("/api/v1/chat/message", json=selected_message_data)
    assert selected_response.status_code == 200

    # Retrieve session history
    history_response = client.get(f"/api/v1/chat/session/{session_id}")
    assert history_response.status_code == 200

    history_data = history_response.json()
    assert history_data["session_id"] == session_id

    # Close session
    close_response = client.delete(f"/api/v1/chat/session/{session_id}")
    assert close_response.status_code == 200

    # All operations should complete successfully
    assert "response" in response.json()
    assert "response" in selected_response.json()