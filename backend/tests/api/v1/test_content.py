import pytest
from fastapi.testclient import TestClient
from src.main import app
from src.models.content import BookContentCreate
import uuid


@pytest.fixture(scope="module")
def client():
    """Create test client for API testing"""
    with TestClient(app) as test_client:
        yield test_client


@pytest.mark.asyncio
async def test_list_chapters(client):
    """Test listing all available chapters"""
    response = client.get("/api/v1/content/chapters")
    assert response.status_code == 200

    data = response.json()
    assert "chapters" in data
    assert isinstance(data["chapters"], list)


@pytest.mark.asyncio
async def test_get_specific_chapter(client):
    """Test retrieving a specific chapter by number"""
    # Try to get chapter 1 (assuming it exists)
    response = client.get("/api/v1/content/chapter/1")

    # The response could be 200 (found) or 404 (not found), both are valid states
    assert response.status_code in [200, 404]

    if response.status_code == 200:
        data = response.json()
        assert "chapter_number" in data
        assert data["chapter_number"] == 1
        assert "content_text" in data


@pytest.mark.asyncio
async def test_create_and_manage_content(client):
    """Test creating, updating, and deleting content"""
    # Create test content
    chapter_data = {
        "chapter_number": 98,  # Use a high number to avoid conflicts
        "chapter_title": "Integration Test Chapter",
        "content_text": "This is a test chapter created for integration testing purposes. It contains enough text to meet the minimum length requirement of 100 characters needed for the content validation system. The content includes various concepts related to Physical AI and robotics to provide meaningful context for testing the RAG system.",
        "version": "1.0"
    }

    # Test creating content
    create_response = client.post("/api/v1/content/chapter", json=chapter_data)
    assert create_response.status_code in [200, 409]  # 409 if already exists

    if create_response.status_code == 200:
        create_data = create_response.json()
        assert "chapter_id" in create_data
        assert create_data["chapter_number"] == 98
        assert create_data["status"] == "published"

        # Test retrieving the created chapter
        get_response = client.get("/api/v1/content/chapter/98")
        assert get_response.status_code == 200

        get_data = get_response.json()
        assert get_data["chapter_number"] == 98
        assert get_data["chapter_title"] == "Integration Test Chapter"

        # Test updating the chapter
        update_data = {
            "chapter_title": "Updated Integration Test Chapter",
            "content_text": "This is an updated test chapter created for integration testing purposes. It contains enough text to meet the minimum length requirement of 100 characters needed for the content validation system. The content includes various concepts related to Physical AI and robotics to provide meaningful context for testing the RAG system.",
            "version": "2.0"
        }

        update_response = client.put("/api/v1/content/chapter/98", json=update_data)
        assert update_response.status_code == 200

        update_result = update_response.json()
        assert update_result["status"] == "updated"
        assert "updated" in update_result["message"].lower()

        # Verify the update
        verify_response = client.get("/api/v1/content/chapter/98")
        assert verify_response.status_code == 200
        verify_data = verify_response.json()
        assert verify_data["chapter_title"] == "Updated Integration Test Chapter"
        assert verify_data["version"] == "2.0"

    # Clean up: delete the test chapter
    delete_response = client.delete("/api/v1/content/chapter/98")
    # This might fail if the chapter doesn't exist, which is fine
    assert delete_response.status_code in [200, 404]


@pytest.mark.asyncio
async def test_content_validation(client):
    """Test content validation functionality"""
    # Test creating content that's too short (should fail validation)
    short_chapter_data = {
        "chapter_number": 97,
        "chapter_title": "Short Content Test",
        "content_text": "Too short",
        "version": "1.0"
    }

    response = client.post("/api/v1/content/chapter", json=short_chapter_data)
    # This should fail validation (400) or conflict if already exists (409)
    assert response.status_code in [400, 409]

    if response.status_code == 400:
        # Verify it's a validation error
        data = response.json()
        assert "detail" in data
        assert "short" in data["detail"].lower() or "100" in data["detail"]

    # Clean up: try to delete if it was created despite validation
    client.delete("/api/v1/content/chapter/97")


@pytest.mark.asyncio
async def test_incremental_update_endpoint(client):
    """Test the incremental update functionality"""
    # First create a chapter if it doesn't exist
    chapter_data = {
        "chapter_number": 96,
        "chapter_title": "Incremental Update Test",
        "content_text": "This chapter is used to test the incremental update functionality. It contains enough content to pass validation and allows us to test the update mechanism without requiring a full system rebuild.",
        "version": "1.0"
    }

    # Create the chapter (ignore if already exists)
    client.post("/api/v1/content/chapter", json=chapter_data)

    # Test updating the chapter incrementally
    update_data = {
        "chapter_title": "Incrementally Updated Chapter",
        "content_text": "This chapter has been updated incrementally. The content has been modified to test the incremental update functionality that allows changes without requiring a full system rebuild.",
        "version": "1.1"
    }

    update_response = client.put("/api/v1/content/chapter/96", json=update_data)
    assert update_response.status_code == 200

    update_result = update_response.json()
    assert update_result["status"] == "updated"
    assert "incrementally" in update_result["message"].lower()

    # Clean up
    client.delete("/api/v1/content/chapter/96")