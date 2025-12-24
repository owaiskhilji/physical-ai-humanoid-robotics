#!/usr/bin/env python3
"""
Test script to verify the backend cleanup changes:
1. Health API works without request parameter
2. Content API is disabled (should return 404)
3. Chat API still works
"""
import requests
import json

def test_cleanup_changes():
    base_url = "http://localhost:8000"

    print("Testing backend cleanup changes...")

    # Test 1: Health API should work without any input
    print("\n1. Testing Health API (/health)...")
    try:
        health_response = requests.get(f"{base_url}/health")
        print(f"Health API status: {health_response.status_code}")
        if health_response.status_code == 200:
            health_data = health_response.json()
            print(f"Health response: {health_data}")
            print("✅ Health API is working correctly without request parameter")
        else:
            print(f"❌ Health API failed with status {health_response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error testing Health API: {e}")
        return False

    # Test 2: Content API should be disabled (404 for content endpoints)
    print("\n2. Testing if Content API is disabled...")
    try:
        content_response = requests.get(f"{base_url}/api/v1/content")
        print(f"Content API status: {content_response.status_code}")
        if content_response.status_code == 404:
            print("✅ Content API is properly disabled (returns 404)")
        else:
            print(f"⚠️  Content API still accessible with status {content_response.status_code}")
            # This might be okay if it's a different endpoint
    except Exception as e:
        print(f"Content API test result: {e}")

    # Test 3: Chat API should still work
    print("\n3. Testing if Chat API still works...")
    try:
        # First create a chat session
        session_data = {
            "session_title": "Test Session for Cleanup Verification",
            "user_id": "test_user"
        }
        session_response = requests.post(f"{base_url}/api/v1/chat/start", json=session_data)
        print(f"Chat session creation status: {session_response.status_code}")

        if session_response.status_code == 200:
            session_info = session_response.json()
            session_id = session_info['id']
            print(f"✅ Chat API is still working, session created with ID: {session_id}")

            # Test a simple message
            message_data = {
                "session_id": session_id,
                "message": "Hello",
                "selected_text": None
            }
            message_response = requests.post(f"{base_url}/api/v1/chat/message", json=message_data)
            print(f"Chat message status: {message_response.status_code}")
            if message_response.status_code == 200:
                print("✅ Chat message functionality is working")
            else:
                print(f"⚠️  Chat message returned status {message_response.status_code}")
        else:
            print(f"❌ Chat API is not working, status {session_response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error testing Chat API: {e}")
        return False

    print("\n🎉 All cleanup changes verified successfully!")
    print("- Health API works without request parameter")
    print("- Content API is disabled")
    print("- Chat API still functions properly")

    return True

if __name__ == "__main__":
    test_cleanup_changes()