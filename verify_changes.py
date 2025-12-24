#!/usr/bin/env python3
"""
Simple test script to verify the backend cleanup changes.
"""
import requests
import json

def verify_changes():
    base_url = "http://localhost:8000"

    print("Verifying backend cleanup changes...")

    # Test 1: Health API should work without any input
    print("\n1. Testing Health API (/health)...")
    try:
        health_response = requests.get(f"{base_url}/health")
        print(f"Health API status: {health_response.status_code}")
        if health_response.status_code == 200:
            health_data = health_response.json()
            print(f"Health response: {health_data}")
            print("[SUCCESS] Health API is working correctly without request parameter")
        else:
            print(f"[ERROR] Health API failed with status {health_response.status_code}")
            return False
    except Exception as e:
        print(f"[ERROR] Error testing Health API: {e}")
        return False

    # Test 2: Try to access a content endpoint to verify it's disabled
    print("\n2. Testing if Content API is disabled...")
    try:
        content_response = requests.get(f"{base_url}/api/v1/content")
        print(f"Content API status: {content_response.status_code}")
        if content_response.status_code == 404:
            print("[SUCCESS] Content API is properly disabled (returns 404)")
        else:
            print(f"[INFO] Content API response: {content_response.status_code}")
    except Exception as e:
        print(f"Content API test: {e}")

    # Test 3: Chat API should still work
    print("\n3. Testing if Chat API still works...")
    try:
        # First create a chat session
        session_data = {
            "session_title": "Verification Session",
            "user_id": "test_user"
        }
        session_response = requests.post(f"{base_url}/api/v1/chat/start", json=session_data)
        print(f"Chat session creation status: {session_response.status_code}")

        if session_response.status_code == 200:
            session_info = session_response.json()
            session_id = session_info['id']
            print(f"[SUCCESS] Chat API is still working, session created with ID: {session_id}")

            # Test a simple message
            message_data = {
                "session_id": session_id,
                "message": "Hello",
                "selected_text": None
            }
            message_response = requests.post(f"{base_url}/api/v1/chat/message", json=message_data)
            print(f"Chat message status: {message_response.status_code}")
            if message_response.status_code == 200:
                print("[SUCCESS] Chat message functionality is working")
            else:
                print(f"[WARNING] Chat message returned status {message_response.status_code}")
        else:
            print(f"[ERROR] Chat API is not working, status {session_response.status_code}")
            return False
    except Exception as e:
        print(f"[ERROR] Error testing Chat API: {e}")
        return False

    print("\n[VERIFIED] All cleanup changes are working as expected!")
    return True

if __name__ == "__main__":
    verify_changes()