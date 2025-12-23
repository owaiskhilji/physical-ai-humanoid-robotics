import pytest
import time
import threading
import concurrent.futures
from fastapi.testclient import TestClient
from src.main import app
import uuid


@pytest.fixture(scope="module")
def client():
    """Create test client for API testing"""
    with TestClient(app) as test_client:
        yield test_client


def create_session_and_ask_question(client, user_id, question, selected_text=None):
    """Helper function to create a session and ask a question"""
    # Create a session
    session_data = {
        "session_title": f"Concurrent Test Session {user_id}",
        "user_id": user_id
    }
    session_response = client.post("/api/v1/chat/start", json=session_data)
    assert session_response.status_code == 200
    session_id = session_response.json()["id"]

    # Ask a question
    message_data = {
        "session_id": session_id,
        "message": question,
        "selected_text": selected_text
    }

    start_time = time.time()
    response = client.post("/api/v1/chat/message", json=message_data)
    end_time = time.time()

    return {
        "response": response,
        "response_time": end_time - start_time,
        "session_id": session_id,
        "user_id": user_id
    }


def test_multiple_concurrent_sessions(client):
    """Test handling multiple concurrent sessions (FR-009)"""
    num_concurrent_users = 5
    user_ids = [f"user_{i}_{uuid.uuid4()}" for i in range(num_concurrent_users)]
    questions = [
        "What is Physical AI?",
        "Explain robotics concepts",
        "What are applications of AI?",
        "How does AI learn?",
        "What is machine learning?"
    ]

    # Execute requests concurrently
    with concurrent.futures.ThreadPoolExecutor(max_workers=num_concurrent_users) as executor:
        futures = [
            executor.submit(create_session_and_ask_question, client, user_ids[i], questions[i])
            for i in range(num_concurrent_users)
        ]

        results = [future.result() for future in concurrent.futures.as_completed(futures)]

    # Verify all requests were successful
    assert len(results) == num_concurrent_users

    for result in results:
        assert result["response"].status_code == 200
        response_data = result["response"].json()
        assert "response" in response_data
        assert len(response_data["response"]) > 0
        # Response time should be reasonable even under concurrent load
        assert result["response_time"] < 10.0, f"Response time {result['response_time']:.2f}s too high under concurrent load"


def test_shared_content_access(client):
    """Test that multiple users can access the same content simultaneously"""
    # First create a session to ensure content exists
    session_data = {
        "session_title": "Shared Content Test",
        "user_id": "shared-content-user-1"
    }
    session_response = client.post("/api/v1/chat/start", json=session_data)
    assert session_response.status_code == 200
    session_id_1 = session_response.json()["id"]

    # Create another session for a different user
    session_data_2 = {
        "session_title": "Shared Content Test 2",
        "user_id": "shared-content-user-2"
    }
    session_response_2 = client.post("/api/v1/chat/start", json=session_data_2)
    assert session_response_2.status_code == 200
    session_id_2 = session_response_2.json()["id"]

    # Both users ask about the same topic simultaneously
    question = "What are the main concepts of Physical AI?"

    def ask_question(session_id, user_id):
        message_data = {
            "session_id": session_id,
            "message": question,
            "selected_text": None
        }
        start_time = time.time()
        response = client.post("/api/v1/chat/message", json=message_data)
        end_time = time.time()
        return {
            "response": response,
            "response_time": end_time - start_time,
            "session_id": session_id
        }

    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
        future1 = executor.submit(ask_question, session_id_1, "user-1")
        future2 = executor.submit(ask_question, session_id_2, "user-2")

        result1 = future1.result()
        result2 = future2.result()

    # Both responses should be successful
    assert result1["response"].status_code == 200
    assert result2["response"].status_code == 200

    # Both should receive valid responses
    data1 = result1["response"].json()
    data2 = result2["response"].json()
    assert "response" in data1
    assert "response" in data2
    assert len(data1["response"]) > 0
    assert len(data2["response"]) > 0

    # Response times should be reasonable
    assert result1["response_time"] < 5.0
    assert result2["response_time"] < 5.0


def test_content_management_under_load(client):
    """Test content management endpoints under concurrent load"""
    # Test concurrent access to content listing
    def list_chapters():
        start_time = time.time()
        response = client.get("/api/v1/content/chapters")
        end_time = time.time()
        return {
            "response": response,
            "response_time": end_time - start_time
        }

    num_requests = 3

    with concurrent.futures.ThreadPoolExecutor(max_workers=num_requests) as executor:
        futures = [executor.submit(list_chapters) for _ in range(num_requests)]
        results = [future.result() for future in concurrent.futures.as_completed(futures)]

    # All requests should succeed
    for result in results:
        assert result["response"].status_code == 200
        data = result["response"].json()
        assert "chapters" in data
        assert isinstance(data["chapters"], list)
        assert result["response_time"] < 3.0  # Should be fast even under load


def test_session_isolation(client):
    """Test that concurrent sessions remain isolated from each other"""
    # Create multiple sessions concurrently
    sessions_info = []

    def create_session_and_store_info(user_id):
        session_data = {
            "session_title": f"Isolation Test Session {user_id}",
            "user_id": user_id
        }
        response = client.post("/api/v1/chat/start", json=session_data)
        return {
            "response": response,
            "user_id": user_id
        }

    num_sessions = 3
    user_ids = [f"iso_user_{i}" for i in range(num_sessions)]

    with concurrent.futures.ThreadPoolExecutor(max_workers=num_sessions) as executor:
        futures = [executor.submit(create_session_and_store_info, uid) for uid in user_ids]
        session_results = [future.result() for future in concurrent.futures.as_completed(futures)]

    # Verify all sessions were created successfully
    created_sessions = []
    for result in session_results:
        assert result["response"].status_code == 200
        session_data = result["response"].json()
        created_sessions.append({
            "session_id": session_data["id"],
            "user_id": result["user_id"]
        })

    # Now have each session ask different questions to test isolation
    questions = [
        "What is Physical AI?",
        "Explain robotics",
        "Applications of AI?"
    ]

    def ask_in_session(session_info, question):
        message_data = {
            "session_id": session_info["session_id"],
            "message": question,
            "selected_text": None
        }
        response = client.post("/api/v1/chat/message", json=message_data)
        return {
            "response": response,
            "session_info": session_info,
            "question": question
        }

    with concurrent.futures.ThreadPoolExecutor(max_workers=num_sessions) as executor:
        futures = [
            executor.submit(ask_in_session, created_sessions[i], questions[i])
            for i in range(num_sessions)
        ]
        message_results = [future.result() for future in concurrent.futures.as_completed(futures)]

    # Verify all responses are successful and isolated
    for result in message_results:
        assert result["response"].status_code == 200
        response_data = result["response"].json()
        assert "response" in response_data
        assert len(response_data["response"]) > 0
        # Each session should have its own unique conversation
        assert response_data["session_id"] == result["session_info"]["session_id"]


def test_selected_text_mode_concurrency(client):
    """Test selected text mode under concurrent usage"""
    selected_text = "Physical AI represents a paradigm shift in artificial intelligence development, emphasizing the integration of physical interaction capabilities with cognitive processing."

    def test_selected_text_in_session(user_id):
        # Create session
        session_data = {
            "session_title": f"Selected Text Concurrency Test {user_id}",
            "user_id": user_id
        }
        session_response = client.post("/api/v1/chat/start", json=session_data)
        assert session_response.status_code == 200
        session_id = session_response.json()["id"]

        # Ask question with selected text
        message_data = {
            "session_id": session_id,
            "message": "What does this text explain?",
            "selected_text": selected_text
        }

        start_time = time.time()
        response = client.post("/api/v1/chat/message", json=message_data)
        end_time = time.time()

        return {
            "response": response,
            "response_time": end_time - start_time,
            "session_id": session_id
        }

    num_users = 3

    with concurrent.futures.ThreadPoolExecutor(max_workers=num_users) as executor:
        futures = [executor.submit(test_selected_text_in_session, f"st_user_{i}") for i in range(num_users)]
        results = [future.result() for future in concurrent.futures.as_completed(futures)]

    # Verify all concurrent selected text requests work properly
    for result in results:
        assert result["response"].status_code == 200
        response_data = result["response"].json()
        assert "response" in response_data
        assert len(response_data["response"]) > 0
        assert result["response_time"] < 5.0