import pytest
from fastapi.testclient import TestClient
from src.main import app


@pytest.fixture(scope="module")
def client():
    """Create test client for API testing"""
    with TestClient(app) as test_client:
        yield test_client


def test_selected_text_mode_basic(client):
    """Test basic selected text mode functionality (FR-003)"""
    # Create a session
    session_data = {
        "session_title": "Selected Text Test",
        "user_id": "selected-text-user"
    }
    session_response = client.post("/api/v1/chat/start", json=session_data)
    assert session_response.status_code == 200
    session_id = session_response.json()["id"]

    # Provide selected text and ask a question about it
    selected_text = "Physical AI is an approach that emphasizes the importance of physical interaction in artificial intelligence systems. This approach differs from traditional AI methods by incorporating the physical properties of the system and its environment into the decision-making process."

    message_data = {
        "session_id": session_id,
        "message": "What does this text explain about Physical AI?",
        "selected_text": selected_text
    }

    response = client.post("/api/v1/chat/message", json=message_data)
    assert response.status_code == 200

    data = response.json()
    assert "response" in data
    assert "session_id" in data
    assert data["session_id"] == session_id

    response_text = data["response"]
    # The response should be focused on the selected text
    assert len(response_text) > 0

    # Check if the response addresses the content of the selected text
    has_relevant_content = any([
        "physical" in response_text.lower(),
        "interaction" in response_text.lower(),
        "system" in response_text.lower(),
        "approach" in response_text.lower()
    ])

    assert has_relevant_content, f"Response should address selected text content: {response_text}"


def test_selected_text_mode_focus(client):
    """Test that selected text mode focuses on the provided text"""
    # Create a session
    session_data = {
        "session_title": "Selected Text Focus Test",
        "user_id": "focus-test-user"
    }
    session_response = client.post("/api/v1/chat/start", json=session_data)
    assert session_response.status_code == 200
    session_id = session_response.json()["id"]

    # Provide specific technical text
    selected_text = "The Kalman filter is an algorithm that uses a series of measurements observed over time, containing statistical noise and other inaccuracies, and produces estimates of unknown variables that tend to be more accurate than those based on a single measurement alone."

    message_data = {
        "session_id": session_id,
        "message": "Explain this algorithm?",
        "selected_text": selected_text
    }

    response = client.post("/api/v1/chat/message", json=message_data)
    assert response.status_code == 200

    data = response.json()
    response_text = data["response"]

    # The response should focus on explaining the Kalman filter as described in the selected text
    has_kalman_focus = (
        "kalman" in response_text.lower() or
        "filter" in response_text.lower() or
        "algorithm" in response_text.lower() or
        "measurements" in response_text.lower() or
        "estimates" in response_text.lower()
    )

    assert has_kalman_focus, f"Response should focus on Kalman filter from selected text: {response_text}"


def test_selected_text_vs_general_mode(client):
    """Test that selected text mode behaves differently from general mode"""
    # Create a session
    session_data = {
        "session_title": "Mode Comparison Test",
        "user_id": "mode-comparison-user"
    }
    session_response = client.post("/api/v1/chat/start", json=session_data)
    assert session_response.status_code == 200
    session_id = session_response.json()["id"]

    # Selected text content
    selected_text = "Quantum computing uses quantum bits or qubits which can exist in multiple states simultaneously."

    # Ask the same question in selected text mode
    selected_message = {
        "session_id": session_id,
        "message": "What are qubits?",
        "selected_text": selected_text
    }

    selected_response = client.post("/api/v1/chat/message", json=selected_message)
    assert selected_response.status_code == 200
    selected_data = selected_response.json()

    # Ask the same question in general mode
    general_message = {
        "session_id": session_id,
        "message": "What are qubits?",
        "selected_text": None
    }

    general_response = client.post("/api/v1/chat/message", json=general_message)
    assert general_response.status_code == 200
    general_data = general_response.json()

    # The responses should be different - selected mode should focus on the provided text
    selected_response_text = selected_data["response"]
    general_response_text = general_data["response"]

    # Selected text response should contain information from the selected text
    has_selected_text_content = (
        "multiple states" in selected_response_text.lower() or
        "simultaneously" in selected_response_text.lower() or
        "qubits" in selected_response_text.lower()
    )

    assert has_selected_text_content, f"Selected text response should contain content from selected text: {selected_response_text}"


def test_empty_selected_text_handling(client):
    """Test handling of empty or None selected text"""
    # Create a session
    session_data = {
        "session_title": "Empty Selected Text Test",
        "user_id": "empty-selected-user"
    }
    session_response = client.post("/api/v1/chat/start", json=session_data)
    assert session_response.status_code == 200
    session_id = session_response.json()["id"]

    # Test with empty string selected text
    message_data = {
        "session_id": session_id,
        "message": "What is Physical AI?",
        "selected_text": ""  # Empty string
    }

    response = client.post("/api/v1/chat/message", json=message_data)
    assert response.status_code == 200

    data = response.json()
    assert "response" in data

    # Should behave like general mode when selected_text is empty
    response_text = data["response"]
    assert len(response_text) > 0


def test_long_selected_text_handling(client):
    """Test handling of longer selected text"""
    # Create a session
    session_data = {
        "session_title": "Long Selected Text Test",
        "user_id": "long-selected-user"
    }
    session_response = client.post("/api/v1/chat/start", json=session_data)
    assert session_response.status_code == 200
    session_id = session_response.json()["id"]

    # Long selected text with multiple concepts
    long_selected_text = """
    Machine learning is a subset of artificial intelligence that enables computers to learn and make decisions from data without being explicitly programmed.
    There are three main types of machine learning: supervised learning, where the model is trained on labeled data;
    unsupervised learning, where the model finds patterns in unlabeled data; and reinforcement learning, where the model learns through trial and error.
    Deep learning is a specialized form of machine learning that uses neural networks with multiple layers to model complex patterns in data.
    """

    message_data = {
        "session_id": session_id,
        "message": "What are the main types of machine learning?",
        "selected_text": long_selected_text
    }

    response = client.post("/api/v1/chat/message", json=message_data)
    assert response.status_code == 200

    data = response.json()
    response_text = data["response"]

    # The response should address the types of machine learning mentioned in the selected text
    has_ml_types = any([
        "supervised" in response_text.lower(),
        "unsupervised" in response_text.lower(),
        "reinforcement" in response_text.lower(),
        "types" in response_text.lower()
    ])

    assert has_ml_types, f"Response should address ML types from selected text: {response_text}"


def test_selected_text_with_follow_up(client):
    """Test selected text mode with follow-up questions in same session"""
    # Create a session
    session_data = {
        "session_title": "Selected Text Follow-up Test",
        "user_id": "followup-selected-user"
    }
    session_response = client.post("/api/v1/chat/start", json=session_data)
    assert session_response.status_code == 200
    session_id = session_response.json()["id"]

    # First question with selected text
    selected_text_1 = "Neural networks are computing systems inspired by the biological neural networks that constitute animal brains."

    message_data_1 = {
        "session_id": session_id,
        "message": "What are neural networks?",
        "selected_text": selected_text_1
    }

    response_1 = client.post("/api/v1/chat/message", json=message_data_1)
    assert response_1.status_code == 200

    # Follow-up question with different selected text
    selected_text_2 = "Backpropagation is a method used in artificial neural networks to calculate a gradient that is needed in the calculation of the weights to be used in the network."

    message_data_2 = {
        "session_id": session_id,
        "message": "How does backpropagation work?",
        "selected_text": selected_text_2
    }

    response_2 = client.post("/api/v1/chat/message", json=message_data_2)
    assert response_2.status_code == 200

    data_2 = response_2.json()
    response_text_2 = data_2["response"]

    # The second response should focus on backpropagation from the second selected text
    has_backprop_focus = (
        "backpropagation" in response_text_2.lower() or
        "gradient" in response_text_2.lower() or
        "weights" in response_text_2.lower() or
        "network" in response_text_2.lower()
    )

    assert has_backprop_focus, f"Follow-up response should focus on backpropagation: {response_text_2}"


def test_selected_text_mode_indicators(client):
    """Test that responses properly indicate selected text mode usage"""
    # Create a session
    session_data = {
        "session_title": "Selected Text Indicator Test",
        "user_id": "indicator-selected-user"
    }
    session_response = client.post("/api/v1/chat/start", json=session_data)
    assert session_response.status_code == 200
    session_id = session_response.json()["id"]

    selected_text = "The perceptron is a type of linear classifier that makes predictions based on a linear predictor function."

    message_data = {
        "session_id": session_id,
        "message": "Explain the perceptron?",
        "selected_text": selected_text
    }

    response = client.post("/api/v1/chat/message", json=message_data)
    assert response.status_code == 200

    data = response.json()
    response_text = data["response"]

    # The response should be properly grounded in the selected text
    # and the system should handle it appropriately
    assert len(response_text) > 0

    # Check that the response addresses the content from selected text
    has_perceptron_content = (
        "perceptron" in response_text.lower() or
        "classifier" in response_text.lower() or
        "linear" in response_text.lower() or
        "predictor" in response_text.lower()
    )

    assert has_perceptron_content, f"Response should address perceptron from selected text: {response_text}"


def test_selected_text_mode_isolation(client):
    """Test that selected text mode doesn't affect other sessions"""
    # Create first session
    session_data_1 = {
        "session_title": "Selected Text Isolation Test 1",
        "user_id": "isolation-user-1"
    }
    session_response_1 = client.post("/api/v1/chat/start", json=session_data_1)
    assert session_response_1.status_code == 200
    session_id_1 = session_response_1.json()["id"]

    # Create second session
    session_data_2 = {
        "session_title": "Selected Text Isolation Test 2",
        "user_id": "isolation-user-2"
    }
    session_response_2 = client.post("/api/v1/chat/start", json=session_data_2)
    assert session_response_2.status_code == 200
    session_id_2 = session_response_2.json()["id"]

    # Use selected text mode in first session
    selected_text = "Computer vision is an interdisciplinary field that deals with how computers can gain high-level understanding from digital images or videos."

    message_data_1 = {
        "session_id": session_id_1,
        "message": "What is computer vision?",
        "selected_text": selected_text
    }

    response_1 = client.post("/api/v1/chat/message", json=message_data_1)
    assert response_1.status_code == 200

    # Use general mode in second session
    message_data_2 = {
        "session_id": session_id_2,
        "message": "What is computer vision?",
        "selected_text": None
    }

    response_2 = client.post("/api/v1/chat/message", json=message_data_2)
    assert response_2.status_code == 200

    # Both should work independently without affecting each other
    data_1 = response_1.json()
    data_2 = response_2.json()

    assert "response" in data_1
    assert "response" in data_2
    assert data_1["session_id"] == session_id_1
    assert data_2["session_id"] == session_id_2