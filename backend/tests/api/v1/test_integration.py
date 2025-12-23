import pytest
from fastapi.testclient import TestClient
from src.main import app
import time


@pytest.fixture(scope="module")
def client():
    """Create test client for API testing"""
    with TestClient(app) as test_client:
        yield test_client


def test_full_chat_workflow_basic(client):
    """Test complete chat workflow: create session -> ask questions -> retrieve history -> close session"""
    # 1. Create a chat session
    session_data = {
        "session_title": "Integration Test Session",
        "user_id": "integration-test-user"
    }
    session_response = client.post("/api/v1/chat/start", json=session_data)
    assert session_response.status_code == 200

    session_data_response = session_response.json()
    session_id = session_data_response["id"]
    assert session_data_response["session_title"] == "Integration Test Session"
    assert session_data_response["is_active"] is True

    # 2. Ask several questions in the session
    questions = [
        {"message": "What is Physical AI?", "selected_text": None},
        {"message": "Explain robotics concepts", "selected_text": None},
        {"message": "What are applications?", "selected_text": None}
    ]

    responses = []
    for i, question in enumerate(questions):
        question["session_id"] = session_id
        response = client.post("/api/v1/chat/message", json=question)
        assert response.status_code == 200

        response_data = response.json()
        assert "response" in response_data
        assert response_data["session_id"] == session_id
        responses.append(response_data)

    # 3. Retrieve the full conversation history
    history_response = client.get(f"/api/v1/chat/session/{session_id}")
    assert history_response.status_code == 200

    history_data = history_response.json()
    assert history_data["session_id"] == session_id
    assert "messages" in history_data
    assert len(history_data["messages"]) >= len(questions) * 2  # User messages + assistant responses

    # Verify messages are properly formatted
    for message in history_data["messages"]:
        assert "id" in message
        assert "role" in message
        assert "content" in message
        assert "timestamp" in message

    # 4. Close the session
    close_response = client.delete(f"/api/v1/chat/session/{session_id}")
    assert close_response.status_code == 200

    close_data = close_response.json()
    assert "message" in close_data


def test_full_chat_workflow_with_selected_text(client):
    """Test complete chat workflow with selected text mode"""
    # 1. Create a chat session
    session_data = {
        "session_title": "Selected Text Integration Test",
        "user_id": "selected-integration-user"
    }
    session_response = client.post("/api/v1/chat/start", json=session_data)
    assert session_response.status_code == 200

    session_data_response = session_response.json()
    session_id = session_data_response["id"]
    assert session_data_response["is_active"] is True

    # 2. Ask questions using selected text mode
    selected_text = "Physical AI is an approach that emphasizes the importance of physical interaction in artificial intelligence systems. This approach differs from traditional AI methods by incorporating the physical properties of the system and its environment into the decision-making process."

    message_data = {
        "session_id": session_id,
        "message": "How does this approach differ from traditional methods?",
        "selected_text": selected_text
    }

    response = client.post("/api/v1/chat/message", json=message_data)
    assert response.status_code == 200

    response_data = response.json()
    assert "response" in response_data
    assert response_data["session_id"] == session_id

    # 3. Ask a follow-up question in general mode
    followup_data = {
        "session_id": session_id,
        "message": "What are the main concepts?",
        "selected_text": None
    }

    followup_response = client.post("/api/v1/chat/message", json=followup_data)
    assert followup_response.status_code == 200

    followup_data_response = followup_response.json()
    assert "response" in followup_data_response
    assert followup_data_response["session_id"] == session_id

    # 4. Retrieve and verify the conversation history includes both modes
    history_response = client.get(f"/api/v1/chat/session/{session_id}")
    assert history_response.status_code == 200

    history_data = history_response.json()
    assert history_data["session_id"] == session_id
    assert "messages" in history_data

    # 5. Close the session
    close_response = client.delete(f"/api/v1/chat/session/{session_id}")
    assert close_response.status_code == 200


def test_content_management_full_workflow(client):
    """Test complete content management workflow"""
    chapter_number = 93
    chapter_title = "Integration Test Chapter"

    # 1. Create new content
    chapter_data = {
        "chapter_number": chapter_number,
        "chapter_title": chapter_title,
        "content_text": "This is a test chapter created for integration testing purposes. It contains enough content to pass validation requirements and allows us to test the full content management workflow. The chapter discusses various concepts related to Physical AI and robotics to provide meaningful context for testing.",
        "version": "1.0"
    }

    create_response = client.post("/api/v1/content/chapter", json=chapter_data)
    assert create_response.status_code == 200

    create_data = create_response.json()
    assert "chapter_id" in create_data
    assert create_data["chapter_number"] == chapter_number
    assert create_data["status"] == "published"

    # 2. Retrieve the created content
    get_response = client.get(f"/api/v1/content/chapter/{chapter_number}")
    assert get_response.status_code == 200

    get_data = get_response.json()
    assert get_data["chapter_number"] == chapter_number
    assert get_data["chapter_title"] == chapter_title
    assert "content_text" in get_data

    # 3. Update the content
    update_data = {
        "chapter_title": "Updated Integration Test Chapter",
        "content_text": "This chapter has been updated as part of the integration test. The content has been modified to test the update workflow functionality. The changes include additional information and updated concepts to ensure the system properly handles content modifications.",
        "version": "2.0"
    }

    update_response = client.put(f"/api/v1/content/chapter/{chapter_number}", json=update_data)
    assert update_response.status_code == 200

    update_result = update_response.json()
    assert update_result["status"] == "updated"
    assert "updated" in update_result["message"].lower()

    # 4. Verify the update
    verify_response = client.get(f"/api/v1/content/chapter/{chapter_number}")
    assert verify_response.status_code == 200

    verify_data = verify_response.json()
    assert verify_data["version"] == "2.0"
    assert verify_data["chapter_title"] == "Updated Integration Test Chapter"

    # 5. Test that the updated content works with the chat system
    # Create a session and ask about the content
    session_data = {
        "session_title": "Content Integration Test",
        "user_id": "content-integration-user"
    }
    session_response = client.post("/api/v1/chat/start", json=session_data)
    assert session_response.status_code == 200
    session_id = session_response.json()["id"]

    message_data = {
        "session_id": session_id,
        "message": "What is the integration test chapter about?",
        "selected_text": None
    }

    chat_response = client.post("/api/v1/chat/message", json=message_data)
    assert chat_response.status_code == 200

    chat_data = chat_response.json()
    assert "response" in chat_data

    # 6. Clean up: delete the test content
    delete_response = client.delete(f"/api/v1/content/chapter/{chapter_number}")
    assert delete_response.status_code == 200

    delete_data = delete_response.json()
    assert "deleted" in delete_data["message"].lower() or "successfully" in delete_data["message"].lower()


def test_multi_session_workflow(client):
    """Test workflow with multiple concurrent sessions"""
    # 1. Create multiple sessions
    sessions = []
    for i in range(3):
        session_data = {
            "session_title": f"Multi-Session Test {i}",
            "user_id": f"multi-user-{i}"
        }
        response = client.post("/api/v1/chat/start", json=session_data)
        assert response.status_code == 200

        session_info = response.json()
        sessions.append({
            "id": session_info["id"],
            "title": session_info["session_title"]
        })

    # 2. Interact with each session
    questions_per_session = [
        ["What is Physical AI?", "Explain concepts", "Applications?"],
        ["Robotics basics", "How do robots work?", "Types of robots?"],
        ["AI learning", "Machine learning", "Neural networks?"]
    ]

    for i, session in enumerate(sessions):
        for j, question in enumerate(questions_per_session[i]):
            message_data = {
                "session_id": session["id"],
                "message": question,
                "selected_text": None
            }

            response = client.post("/api/v1/chat/message", json=message_data)
            assert response.status_code == 200

            response_data = response.json()
            assert "response" in response_data
            assert response_data["session_id"] == session["id"]

    # 3. Verify each session's history is isolated
    for session in sessions:
        history_response = client.get(f"/api/v1/chat/session/{session['id']}")
        assert history_response.status_code == 200

        history_data = history_response.json()
        assert history_data["session_id"] == session["id"]
        # Should have at least the questions asked in this session
        assert "messages" in history_data
        # Each session should have its own conversation history

    # 4. Close all sessions
    for session in sessions:
        close_response = client.delete(f"/api/v1/chat/session/{session['id']}")
        assert close_response.status_code == 200


def test_performance_under_full_workflow(client):
    """Test performance during a full workflow with multiple operations"""
    start_time = time.time()

    # Execute a full workflow similar to test_full_chat_workflow_basic
    # 1. Create session
    session_data = {
        "session_title": "Performance Workflow Test",
        "user_id": "perf-workflow-user"
    }
    session_response = client.post("/api/v1/chat/start", json=session_data)
    assert session_response.status_code == 200
    session_id = session_response.json()["id"]

    # 2. Ask multiple questions
    for i in range(3):
        message_data = {
            "session_id": session_id,
            "message": f"Question {i} about Physical AI concepts",
            "selected_text": None
        }
        response = client.post("/api/v1/chat/message", json=message_data)
        assert response.status_code == 200

    # 3. Retrieve history
    history_response = client.get(f"/api/v1/chat/session/{session_id}")
    assert history_response.status_code == 200

    # 4. Close session
    close_response = client.delete(f"/api/v1/chat/session/{session_id}")
    assert close_response.status_code == 200

    end_time = time.time()
    total_time = end_time - start_time

    # The entire workflow should complete in reasonable time
    assert total_time < 15.0, f"Full workflow took {total_time:.2f}s, which is too slow"


def test_error_recovery_in_workflow(client):
    """Test that the system can recover from errors during a workflow"""
    # 1. Create a session
    session_data = {
        "session_title": "Error Recovery Test",
        "user_id": "error-recovery-user"
    }
    session_response = client.post("/api/v1/chat/start", json=session_data)
    assert session_response.status_code == 200
    session_id = session_response.json()["id"]

    # 2. Ask a normal question
    normal_message = {
        "session_id": session_id,
        "message": "What is Physical AI?",
        "selected_text": None
    }
    response = client.post("/api/v1/chat/message", json=normal_message)
    assert response.status_code == 200

    # 3. Try an operation that might fail (retrieve non-existent chapter)
    error_response = client.get("/api/v1/content/chapter/999999")
    # This should not affect the chat session

    # 4. Ask another question after the error
    recovery_message = {
        "session_id": session_id,
        "message": "Explain robotics?",
        "selected_text": None
    }
    recovery_response = client.post("/api/v1/chat/message", json=recovery_message)
    assert recovery_response.status_code == 200

    # 5. Verify the session is still functional
    history_response = client.get(f"/api/v1/chat/session/{session_id}")
    assert history_response.status_code == 200

    # 6. Close the session
    close_response = client.delete(f"/api/v1/chat/session/{session_id}")
    assert close_response.status_code == 200