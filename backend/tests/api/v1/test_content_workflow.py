import pytest
from fastapi.testclient import TestClient
from src.main import app
import time


@pytest.fixture(scope="module")
def client():
    """Create test client for API testing"""
    with TestClient(app) as test_client:
        yield test_client


def test_content_creation_workflow(client):
    """Test the complete content creation workflow"""
    chapter_number = 91
    chapter_title = "Content Creation Test Chapter"

    # 1. Create new content
    chapter_data = {
        "chapter_number": chapter_number,
        "chapter_title": chapter_title,
        "content_text": "This chapter is created to test the content creation workflow. It contains sufficient content to pass validation requirements and allows us to verify that new content can be properly ingested into the RAG system.",
        "version": "1.0"
    }

    create_response = client.post("/api/v1/content/chapter", json=chapter_data)
    assert create_response.status_code == 200

    create_data = create_response.json()
    assert "chapter_id" in create_data
    assert create_data["chapter_number"] == chapter_number
    assert create_data["chapter_title"] == chapter_title
    assert create_data["status"] == "published"

    # 2. Verify the content exists
    get_response = client.get(f"/api/v1/content/chapter/{chapter_number}")
    assert get_response.status_code == 200

    get_data = get_response.json()
    assert get_data["chapter_number"] == chapter_number
    assert get_data["chapter_title"] == chapter_title
    assert get_data["version"] == "1.0"

    # 3. Test that the new content is available for chat
    session_data = {
        "session_title": "New Content Test",
        "user_id": "new-content-user"
    }
    session_response = client.post("/api/v1/chat/start", json=session_data)
    assert session_response.status_code == 200
    session_id = session_response.json()["id"]

    message_data = {
        "session_id": session_id,
        "message": "What is the content creation test chapter about?",
        "selected_text": None
    }

    chat_response = client.post("/api/v1/chat/message", json=message_data)
    assert chat_response.status_code == 200

    chat_data = chat_response.json()
    assert "response" in chat_data

    # 4. Clean up
    delete_response = client.delete(f"/api/v1/content/chapter/{chapter_number}")
    assert delete_response.status_code == 200


def test_incremental_content_update_workflow(client):
    """Test the incremental content update workflow (FR-006)"""
    chapter_number = 90
    original_title = "Original Test Chapter"
    updated_title = "Updated Test Chapter"

    # 1. Create initial content
    initial_data = {
        "chapter_number": chapter_number,
        "chapter_title": original_title,
        "content_text": "This is the original content of the test chapter. It contains basic information for testing the update workflow.",
        "version": "1.0"
    }

    create_response = client.post("/api/v1/content/chapter", json=initial_data)
    assert create_response.status_code == 200

    # 2. Update the content incrementally
    update_data = {
        "chapter_title": updated_title,
        "content_text": "This is the updated content of the test chapter. The content has been significantly modified to test the incremental update mechanism without requiring a full system rebuild.",
        "version": "2.0"
    }

    update_response = client.put(f"/api/v1/content/chapter/{chapter_number}", json=update_data)
    assert update_response.status_code == 200

    update_result = update_response.json()
    assert update_result["status"] == "updated"
    assert "incrementally" in update_result["message"].lower()

    # 3. Verify the update was successful
    verify_response = client.get(f"/api/v1/content/chapter/{chapter_number}")
    assert verify_response.status_code == 200

    verify_data = verify_response.json()
    assert verify_data["chapter_title"] == updated_title
    assert verify_data["version"] == "2.0"
    assert "updated content" in verify_data["content_text"].lower()

    # 4. Test that updated content is available for chat
    session_data = {
        "session_title": "Updated Content Test",
        "user_id": "updated-content-user"
    }
    session_response = client.post("/api/v1/chat/start", json=session_data)
    assert session_response.status_code == 200
    session_id = session_response.json()["id"]

    message_data = {
        "session_id": session_id,
        "message": "What is the updated test chapter about?",
        "selected_text": None
    }

    chat_response = client.post("/api/v1/chat/message", json=message_data)
    assert chat_response.status_code == 200

    chat_data = chat_response.json()
    assert "response" in chat_data

    # 5. Clean up
    delete_response = client.delete(f"/api/v1/content/chapter/{chapter_number}")
    assert delete_response.status_code == 200


def test_content_state_management(client):
    """Test content state management (DRAFT → PUBLISHED)"""
    chapter_number = 89
    chapter_title = "State Management Test Chapter"

    # Note: Our current implementation doesn't have explicit state management in the API
    # but we can test the basic content lifecycle
    chapter_data = {
        "chapter_number": chapter_number,
        "chapter_title": chapter_title,
        "content_text": "This chapter tests the content lifecycle and state management. It contains information about how content moves through different states in the system.",
        "version": "1.0"
    }

    create_response = client.post("/api/v1/content/chapter", json=chapter_data)
    assert create_response.status_code == 200

    # Verify the content is created and accessible
    get_response = client.get(f"/api/v1/content/chapter/{chapter_number}")
    assert get_response.status_code == 200

    get_data = get_response.json()
    assert get_data["chapter_number"] == chapter_number
    assert get_data["state"] in ["DRAFT", "PUBLISHED"]  # Should have a state value

    # Test that the content works with the chat system
    session_data = {
        "session_title": "State Management Test",
        "user_id": "state-test-user"
    }
    session_response = client.post("/api/v1/chat/start", json=session_data)
    assert session_response.status_code == 200
    session_id = session_response.json()["id"]

    message_data = {
        "session_id": session_id,
        "message": "What is the state management test chapter about?",
        "selected_text": None
    }

    chat_response = client.post("/api/v1/chat/message", json=message_data)
    assert chat_response.status_code == 200

    # Clean up
    delete_response = client.delete(f"/api/v1/content/chapter/{chapter_number}")
    assert delete_response.status_code == 200


def test_content_validation_in_workflow(client):
    """Test content validation during the workflow"""
    chapter_number = 88

    # 1. Try to create content that fails validation (too short)
    short_content_data = {
        "chapter_number": chapter_number,
        "chapter_title": "Short Content Test",
        "content_text": "Too short",
        "version": "1.0"
    }

    short_response = client.post("/api/v1/content/chapter", json=short_content_data)
    assert short_response.status_code == 400  # Should fail validation

    short_data = short_response.json()
    assert "detail" in short_data
    assert "short" in short_data["detail"].lower() or "100" in short_data["detail"]

    # 2. Try to create content that passes validation
    valid_content_data = {
        "chapter_number": chapter_number,
        "chapter_title": "Valid Content Test",
        "content_text": "This is valid content that meets the minimum length requirement of 100 characters needed for the content validation system. The content includes various concepts related to Physical AI and robotics to provide meaningful context for testing the RAG system. This ensures that the content is substantial enough for proper processing.",
        "version": "1.0"
    }

    valid_response = client.post("/api/v1/content/chapter", json=valid_content_data)
    assert valid_response.status_code == 200

    # 3. Verify the valid content exists
    get_response = client.get(f"/api/v1/content/chapter/{chapter_number}")
    assert get_response.status_code == 200

    get_data = get_response.json()
    assert get_data["chapter_number"] == chapter_number
    assert len(get_data["content_text"]) >= 100

    # 4. Clean up
    delete_response = client.delete(f"/api/v1/content/chapter/{chapter_number}")
    assert delete_response.status_code == 200


def test_multiple_content_updates(client):
    """Test multiple updates to the same content"""
    chapter_number = 87
    chapter_title = "Multiple Updates Test"

    # 1. Create initial content
    initial_data = {
        "chapter_number": chapter_number,
        "chapter_title": f"{chapter_title} v1",
        "content_text": "This is the initial version of the test chapter.",
        "version": "1.0"
    }

    create_response = client.post("/api/v1/content/chapter", json=initial_data)
    assert create_response.status_code == 200

    # 2. First update
    update_1_data = {
        "chapter_title": f"{chapter_title} v2",
        "content_text": "This is the first updated version of the test chapter. The content has been modified to test the update mechanism.",
        "version": "2.0"
    }

    update_1_response = client.put(f"/api/v1/content/chapter/{chapter_number}", json=update_1_data)
    assert update_1_response.status_code == 200

    # 3. Second update
    update_2_data = {
        "chapter_title": f"{chapter_title} v3",
        "content_text": "This is the second updated version of the test chapter. The content has been modified again to test multiple updates.",
        "version": "3.0"
    }

    update_2_response = client.put(f"/api/v1/content/chapter/{chapter_number}", json=update_2_data)
    assert update_2_response.status_code == 200

    # 4. Verify final state
    final_response = client.get(f"/api/v1/content/chapter/{chapter_number}")
    assert final_response.status_code == 200

    final_data = final_response.json()
    assert final_data["version"] == "3.0"
    assert f"{chapter_title} v3" in final_data["chapter_title"]

    # 5. Test that the final content works with chat
    session_data = {
        "session_title": "Multiple Updates Test",
        "user_id": "multi-update-user"
    }
    session_response = client.post("/api/v1/chat/start", json=session_data)
    assert session_response.status_code == 200
    session_id = session_response.json()["id"]

    message_data = {
        "session_id": session_id,
        "message": "What is the multiple updates test chapter about?",
        "selected_text": None
    }

    chat_response = client.post("/api/v1/chat/message", json=message_data)
    assert chat_response.status_code == 200

    # 6. Clean up
    delete_response = client.delete(f"/api/v1/content/chapter/{chapter_number}")
    assert delete_response.status_code == 200


def test_content_workflow_performance(client):
    """Test performance of content workflow operations"""
    chapter_number = 86

    # 1. Measure creation time
    start_time = time.time()
    chapter_data = {
        "chapter_number": chapter_number,
        "chapter_title": "Performance Test Chapter",
        "content_text": "This chapter is created to test the performance of content workflow operations. It contains sufficient content to pass validation requirements and allows us to measure how quickly content can be created, updated, and made available for the RAG system.",
        "version": "1.0"
    }

    create_response = client.post("/api/v1/content/chapter", json=chapter_data)
    assert create_response.status_code == 200
    create_time = time.time() - start_time

    # Creation should be reasonably fast
    assert create_time < 5.0, f"Content creation took {create_time:.2f}s, which is too slow"

    # 2. Measure update time
    start_time = time.time()
    update_data = {
        "content_text": "This chapter has been updated to test the performance of content update operations. The content has been modified to verify that updates are processed efficiently.",
        "version": "2.0"
    }

    update_response = client.put(f"/api/v1/content/chapter/{chapter_number}", json=update_data)
    assert update_response.status_code == 200
    update_time = time.time() - start_time

    # Update should be reasonably fast (incremental updates should be faster)
    assert update_time < 5.0, f"Content update took {update_time:.2f}s, which is too slow"

    # 3. Measure deletion time
    start_time = time.time()
    delete_response = client.delete(f"/api/v1/content/chapter/{chapter_number}")
    assert delete_response.status_code == 200
    delete_time = time.time() - start_time

    # Deletion should be reasonably fast
    assert delete_time < 3.0, f"Content deletion took {delete_time:.2f}s, which is too slow"


def test_content_workflow_with_chat_integration(client):
    """Test content workflow with full chat integration"""
    chapter_number = 85
    chapter_title = "Workflow Integration Test"

    # 1. Create content
    chapter_data = {
        "chapter_number": chapter_number,
        "chapter_title": chapter_title,
        "content_text": "This chapter is created to test the integration between content management and chat functionality. It discusses concepts related to Physical AI and robotics, providing meaningful content for the RAG system to work with.",
        "version": "1.0"
    }

    create_response = client.post("/api/v1/content/chapter", json=chapter_data)
    assert create_response.status_code == 200

    # 2. Create a chat session and test with the new content
    session_data = {
        "session_title": "Workflow Integration Chat Test",
        "user_id": "workflow-integration-user"
    }
    session_response = client.post("/api/v1/chat/start", json=session_data)
    assert session_response.status_code == 200
    session_id = session_response.json()["id"]

    # Ask about the newly created content
    message_data = {
        "session_id": session_id,
        "message": "What is the workflow integration test chapter about?",
        "selected_text": None
    }

    chat_response = client.post("/api/v1/chat/message", json=message_data)
    assert chat_response.status_code == 200

    chat_data = chat_response.json()
    assert "response" in chat_data

    # 3. Update the content
    update_data = {
        "chapter_title": "Updated Workflow Integration Test",
        "content_text": "This chapter has been updated to test the integration between content updates and chat functionality. The content now includes additional information about how updates are processed and made available to users.",
        "version": "2.0"
    }

    update_response = client.put(f"/api/v1/content/chapter/{chapter_number}", json=update_data)
    assert update_response.status_code == 200

    # 4. Ask about the updated content in the same session
    updated_message_data = {
        "session_id": session_id,
        "message": "What does the updated chapter say about content updates?",
        "selected_text": None
    }

    updated_chat_response = client.post("/api/v1/chat/message", json=updated_message_data)
    assert updated_chat_response.status_code == 200

    updated_chat_data = updated_chat_response.json()
    assert "response" in updated_chat_data

    # 5. Clean up
    delete_response = client.delete(f"/api/v1/content/chapter/{chapter_number}")
    assert delete_response.status_code == 200

    close_response = client.delete(f"/api/v1/chat/session/{session_id}")
    assert close_response.status_code == 200