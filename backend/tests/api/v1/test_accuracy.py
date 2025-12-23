import pytest
from fastapi.testclient import TestClient
from src.main import app
import re


@pytest.fixture(scope="module")
def client():
    """Create test client for API testing"""
    with TestClient(app) as test_client:
        yield test_client


def test_response_grounding_validation(client):
    """Test that responses are properly grounded in book content (FR-001)"""
    # First create a session
    session_data = {
        "session_title": "Accuracy Test Session",
        "user_id": "accuracy-test-user"
    }
    session_response = client.post("/api/v1/chat/start", json=session_data)
    assert session_response.status_code == 200
    session_id = session_response.json()["id"]

    # Ask a question that should be answerable from textbook content
    message_data = {
        "session_id": session_id,
        "message": "What is the main concept of Physical AI?",
        "selected_text": None
    }

    response = client.post("/api/v1/chat/message", json=message_data)
    assert response.status_code == 200

    data = response.json()
    response_text = data["response"]

    # Check that the response acknowledges the source of information
    # The response should indicate it's based on the textbook content
    assert response_text is not None
    assert len(response_text) > 0

    # Check if the response contains appropriate textbook-related language
    # rather than claiming to have general knowledge
    has_textbook_reference = any([
        "textbook" in response_text.lower(),
        "book" in response_text.lower(),
        "chapter" in response_text.lower(),
        "content" in response_text.lower()
    ])

    # Response should be grounded and not make up information
    is_properly_grounded = (
        "according to" in response_text.lower() or
        "based on" in response_text.lower() or
        "the text" in response_text.lower() or
        "the content" in response_text.lower() or
        has_textbook_reference
    )

    assert is_properly_grounded, f"Response may not be properly grounded: {response_text}"


def test_selected_text_mode_accuracy(client):
    """Test accuracy of selected text mode responses (FR-003)"""
    # First create a session
    session_data = {
        "session_title": "Selected Text Accuracy Test",
        "user_id": "selected-accuracy-test-user"
    }
    session_response = client.post("/api/v1/chat/start", json=session_data)
    assert session_response.status_code == 200
    session_id = session_response.json()["id"]

    # Provide specific text and ask a related question
    selected_text = "Physical AI is an approach that emphasizes the importance of physical interaction in artificial intelligence systems. This approach differs from traditional AI methods by incorporating the physical properties of the system and its environment into the decision-making process."

    message_data = {
        "session_id": session_id,
        "message": "How does Physical AI differ from traditional AI?",
        "selected_text": selected_text
    }

    response = client.post("/api/v1/chat/message", json=message_data)
    assert response.status_code == 200

    data = response.json()
    response_text = data["response"]

    # The response should be based on the selected text and mention the difference
    assert response_text is not None
    assert len(response_text) > 0

    # Check if the response addresses the question about differences
    mentions_difference = (
        "differ" in response_text.lower() or
        "difference" in response_text.lower() or
        "traditional" in response_text.lower() or
        "incorporat" in response_text.lower()
    )

    assert mentions_difference, f"Response doesn't adequately address the difference: {response_text}"


def test_no_content_found_response(client):
    """Test response when no relevant content is found"""
    # First create a session
    session_data = {
        "session_title": "No Content Found Test",
        "user_id": "no-content-test-user"
    }
    session_response = client.post("/api/v1/chat/start", json=session_data)
    assert session_response.status_code == 200
    session_id = session_response.json()["id"]

    # Ask about something that might not be in the textbook
    message_data = {
        "session_id": session_id,
        "message": "What is the weather today?",
        "selected_text": None
    }

    response = client.post("/api/v1/chat/message", json=message_data)
    assert response.status_code == 200

    data = response.json()
    response_text = data["response"]

    # The response should acknowledge that the information is not in the textbook
    assert response_text is not None

    has_appropriate_response = any([
        "not found" in response_text.lower(),
        "no relevant" in response_text.lower(),
        "cannot find" in response_text.lower(),
        "not available" in response_text.lower(),
        "not mentioned" in response_text.lower(),
        "only answer" in response_text.lower(),
        "textbook" in response_text.lower()
    ])

    assert has_appropriate_response, f"Response should indicate lack of relevant content: {response_text}"


def test_response_relevance(client):
    """Test that responses are relevant to the questions asked"""
    # First create a session
    session_data = {
        "session_title": "Relevance Test Session",
        "user_id": "relevance-test-user"
    }
    session_response = client.post("/api/v1/chat/start", json=session_data)
    assert session_response.status_code == 200
    session_id = session_response.json()["id"]

    test_cases = [
        {
            "question": "What are robotics applications?",
            "keywords": ["robot", "application", "use", "robotic"]
        },
        {
            "question": "Explain AI concepts",
            "keywords": ["ai", "artificial", "intelligence", "concept"]
        }
    ]

    for case in test_cases:
        message_data = {
            "session_id": session_id,
            "message": case["question"],
            "selected_text": None
        }

        response = client.post("/api/v1/chat/message", json=message_data)
        assert response.status_code == 200

        data = response.json()
        response_text = data["response"]

        # Check if response contains relevant keywords
        response_lower = response_text.lower()
        has_relevant_content = any(keyword in response_lower for keyword in case["keywords"])

        assert has_relevant_content, f"Response to '{case['question']}' doesn't contain relevant keywords: {response_text}"


def test_external_knowledge_rejection(client):
    """Test that the system doesn't provide external knowledge (FR-001)"""
    # First create a session
    session_data = {
        "session_title": "External Knowledge Rejection Test",
        "user_id": "external-knowledge-test-user"
    }
    session_response = client.post("/api/v1/chat/start", json=session_data)
    assert session_response.status_code == 200
    session_id = session_response.json()["id"]

    # Ask for information that should not be in the textbook
    external_questions = [
        "What is the current stock price of Google?",
        "Who won the World Cup in 2026?",
        "What is the latest news?"
    ]

    for question in external_questions:
        message_data = {
            "session_id": session_id,
            "message": question,
            "selected_text": None
        }

        response = client.post("/api/v1/chat/message", json=message_data)
        assert response.status_code == 200

        data = response.json()
        response_text = data["response"]

        # The system should not provide external information
        should_not_contain_external_info = (
            "not in textbook" in response_text.lower() or
            "not available" in response_text.lower() or
            "cannot provide" in response_text.lower() or
            "only answer" in response_text.lower() or
            "based on provided" in response_text.lower()
        )

        assert should_not_contain_external_info, f"Response should not provide external info for '{question}': {response_text}"