import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.future import select
from src.main import app
from src.core.database import Base
from src.models.chat import ChatSessionDB, ChatMessageDB
from src.models.content import BookContentDB
from src.services.content_service import ContentService
from src.services.chat_service import ChatService
import uuid
import asyncio
from datetime import datetime, timedelta


@pytest.fixture(scope="module")
def client():
    """Create test client for API testing"""
    with TestClient(app) as test_client:
        yield test_client


@pytest.mark.asyncio
async def test_create_chat_session(client):
    """Test creating a new chat session"""
    session_data = {
        "session_title": "Test Session",
        "user_id": str(uuid.uuid4())
    }

    response = client.post("/api/v1/chat/start", json=session_data)
    assert response.status_code == 200

    data = response.json()
    assert "id" in data
    assert data["session_title"] == "Test Session"
    assert data["is_active"] is True


@pytest.mark.asyncio
async def test_send_message_general_mode(client):
    """Test sending a message in general mode"""
    # First create a session
    session_data = {
        "session_title": "Test Session for Message",
        "user_id": str(uuid.uuid4())
    }
    session_response = client.post("/api/v1/chat/start", json=session_data)
    assert session_response.status_code == 200
    session_id = session_response.json()["id"]

    # Send a message
    message_data = {
        "session_id": session_id,
        "message": "What is Physical AI?",
        "selected_text": None
    }

    response = client.post("/api/v1/chat/message", json=message_data)
    assert response.status_code == 200

    data = response.json()
    assert "response" in data
    assert "session_id" in data
    assert data["session_id"] == session_id


@pytest.mark.asyncio
async def test_send_message_selected_text_mode(client):
    """Test sending a message in selected text mode"""
    # First create a session
    session_data = {
        "session_title": "Test Session for Selected Text",
        "user_id": str(uuid.uuid4())
    }
    session_response = client.post("/api/v1/chat/start", json=session_data)
    assert session_response.status_code == 200
    session_id = session_response.json()["id"]

    # Send a message with selected text
    selected_text = "Physical AI is an approach that emphasizes the importance of physical interaction in artificial intelligence systems."
    message_data = {
        "session_id": session_id,
        "message": "Explain this concept?",
        "selected_text": selected_text
    }

    response = client.post("/api/v1/chat/message", json=message_data)
    assert response.status_code == 200

    data = response.json()
    assert "response" in data
    assert "session_id" in data
    assert data["session_id"] == session_id


@pytest.mark.asyncio
async def test_get_chat_session(client):
    """Test retrieving a chat session with history"""
    # First create a session
    session_data = {
        "session_title": "Test Session for Retrieval",
        "user_id": str(uuid.uuid4())
    }
    session_response = client.post("/api/v1/chat/start", json=session_data)
    assert session_response.status_code == 200
    session_id = session_response.json()["id"]

    # Add a message to the session
    message_data = {
        "session_id": session_id,
        "message": "What is Physical AI?",
        "selected_text": None
    }
    client.post("/api/v1/chat/message", json=message_data)

    # Retrieve the session
    response = client.get(f"/api/v1/chat/session/{session_id}")
    assert response.status_code == 200

    data = response.json()
    assert data["session_id"] == session_id
    assert "messages" in data
    assert len(data["messages"]) >= 1


@pytest.mark.asyncio
async def test_close_chat_session(client):
    """Test closing a chat session"""
    # First create a session
    session_data = {
        "session_title": "Test Session for Closing",
        "user_id": str(uuid.uuid4())
    }
    session_response = client.post("/api/v1/chat/start", json=session_data)
    assert session_response.status_code == 200
    session_id = session_response.json()["id"]

    # Close the session
    response = client.delete(f"/api/v1/chat/session/{session_id}")
    assert response.status_code == 200

    data = response.json()
    assert "message" in data
    assert "closed" in data["message"].lower()


@pytest.mark.asyncio
async def test_content_endpoints(client):
    """Test content management endpoints"""
    # Test listing chapters
    response = client.get("/api/v1/content/chapters")
    assert response.status_code == 200

    data = response.json()
    assert "chapters" in data
    assert isinstance(data["chapters"], list)

    # Test creating a chapter (if needed for testing)
    chapter_data = {
        "chapter_number": 99,  # Use a high number to avoid conflicts
        "chapter_title": "Test Chapter for API Validation",
        "content_text": "This is a test chapter content for API validation purposes. It contains some text that can be used for testing the RAG functionality.",
        "version": "1.0"
    }

    # Try to create the chapter
    create_response = client.post("/api/v1/content/chapter", json=chapter_data)
    # This might fail if the chapter already exists, so we'll handle that
    assert create_response.status_code in [200, 409]  # 409 if already exists

    if create_response.status_code == 200:
        create_data = create_response.json()
        assert "chapter_id" in create_data
        assert create_data["chapter_number"] == 99

        # Test getting the specific chapter
        get_response = client.get("/api/v1/content/chapter/99")
        assert get_response.status_code == 200

        get_data = get_response.json()
        assert get_data["chapter_number"] == 99
        assert get_data["chapter_title"] == "Test Chapter for API Validation"

    # Clean up: delete the test chapter
    delete_response = client.delete("/api/v1/content/chapter/99")
    # This might fail if the chapter doesn't exist, which is fine
    assert delete_response.status_code in [200, 404]