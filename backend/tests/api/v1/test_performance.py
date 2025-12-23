import pytest
import time
from fastapi.testclient import TestClient
from src.main import app
import asyncio


@pytest.fixture(scope="module")
def client():
    """Create test client for API testing"""
    with TestClient(app) as test_client:
        yield test_client


def test_response_time_basic_query(client):
    """Test response time for basic queries (should be <5 seconds per SC-001)"""
    # First create a session
    session_data = {
        "session_title": "Performance Test Session",
        "user_id": "perf-test-user"
    }
    session_response = client.post("/api/v1/chat/start", json=session_data)
    assert session_response.status_code == 200
    session_id = session_response.json()["id"]

    # Measure response time for a query
    start_time = time.time()

    message_data = {
        "session_id": session_id,
        "message": "What is Physical AI?",
        "selected_text": None
    }

    response = client.post("/api/v1/chat/message", json=message_data)

    end_time = time.time()
    response_time = end_time - start_time

    # Response time should be less than 5 seconds as per success criteria SC-001
    assert response_time < 5.0, f"Response time {response_time:.2f}s exceeds 5 second limit"

    assert response.status_code == 200
    data = response.json()
    assert "response" in data


def test_response_time_selected_text_mode(client):
    """Test response time for selected text mode queries"""
    # First create a session
    session_data = {
        "session_title": "Performance Test Session Selected Text",
        "user_id": "perf-test-user-2"
    }
    session_response = client.post("/api/v1/chat/start", json=session_data)
    assert session_response.status_code == 200
    session_id = session_response.json()["id"]

    # Measure response time for selected text query
    start_time = time.time()

    selected_text = "Physical AI is an approach that emphasizes the importance of physical interaction in artificial intelligence systems. This approach differs from traditional AI methods by incorporating the physical properties of the system and its environment into the decision-making process."
    message_data = {
        "session_id": session_id,
        "message": "Explain this concept?",
        "selected_text": selected_text
    }

    response = client.post("/api/v1/chat/message", json=message_data)

    end_time = time.time()
    response_time = end_time - start_time

    # Response time should be less than 5 seconds as per success criteria SC-001
    assert response_time < 5.0, f"Response time {response_time:.2f}s exceeds 5 second limit"

    assert response.status_code == 200
    data = response.json()
    assert "response" in data


def test_concurrent_user_response_time(client):
    """Test response time under simulated concurrent usage"""
    import concurrent.futures
    import threading

    # Create a session for testing
    session_data = {
        "session_title": "Concurrent Performance Test",
        "user_id": "concurrent-test-user"
    }
    session_response = client.post("/api/v1/chat/start", json=session_data)
    assert session_response.status_code == 200
    session_id = session_response.json()["id"]

    def make_request():
        start_time = time.time()

        message_data = {
            "session_id": session_id,
            "message": "What are the key concepts?",
            "selected_text": None
        }

        response = client.post("/api/v1/chat/message", json=message_data)
        end_time = time.time()

        return end_time - start_time, response.status_code

    # Simulate 3 concurrent requests
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
        futures = [executor.submit(make_request) for _ in range(3)]
        results = [future.result() for future in concurrent.futures.as_completed(futures)]

    # Check that all responses were successful and within time limits
    for response_time, status_code in results:
        assert status_code == 200, f"Request failed with status {status_code}"
        assert response_time < 5.0, f"Response time {response_time:.2f}s exceeds 5 second limit"


def test_content_retrieval_performance(client):
    """Test performance of content retrieval endpoints"""
    # Measure time for listing chapters
    start_time = time.time()
    response = client.get("/api/v1/content/chapters")
    end_time = time.time()

    response_time = end_time - start_time
    assert response.status_code == 200
    assert response_time < 2.0, f"Content listing took {response_time:.2f}s, should be <2s"


def test_multiple_queries_performance(client):
    """Test performance when making multiple sequential queries"""
    # First create a session
    session_data = {
        "session_title": "Multiple Queries Test",
        "user_id": "multi-query-test-user"
    }
    session_response = client.post("/api/v1/chat/start", json=session_data)
    assert session_response.status_code == 200
    session_id = session_response.json()["id"]

    queries = [
        "What is Physical AI?",
        "Explain robotics concepts",
        "What are the applications?",
        "How does it differ from traditional AI?"
    ]

    total_start_time = time.time()

    for query in queries:
        query_start_time = time.time()

        message_data = {
            "session_id": session_id,
            "message": query,
            "selected_text": None
        }

        response = client.post("/api/v1/chat/message", json=message_data)

        query_end_time = time.time()
        query_response_time = query_end_time - query_start_time

        assert response.status_code == 200, f"Query '{query}' failed"
        assert query_response_time < 5.0, f"Query '{query}' took {query_response_time:.2f}s, exceeds 5s limit"

    total_end_time = time.time()
    total_response_time = total_end_time - total_start_time

    # All queries combined should still perform reasonably
    assert total_response_time < 20.0, f"Total time for {len(queries)} queries was {total_response_time:.2f}s"