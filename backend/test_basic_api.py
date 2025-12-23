"""
Basic API tests to verify the RAG Chatbot API is working correctly.
"""
import pytest
from fastapi.testclient import TestClient
from src.main import app


def test_root_endpoint():
    """Test the root endpoint"""
    with TestClient(app) as client:
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "RAG Chatbot API"
        assert "version" in data


def test_health_endpoint():
    """Test the health endpoint"""
    with TestClient(app) as client:
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "rag-chatbot-api"


def test_api_docs():
    """Test that API documentation is available"""
    with TestClient(app) as client:
        response = client.get("/docs")
        assert response.status_code == 200
        # Check that it contains Swagger UI
        assert "swagger" in response.text.lower()


def test_redoc():
    """Test that ReDoc documentation is available"""
    with TestClient(app) as client:
        response = client.get("/redoc")
        assert response.status_code == 200
        # Check that it contains ReDoc
        assert "redoc" in response.text.lower()


if __name__ == "__main__":
    pytest.main([__file__])