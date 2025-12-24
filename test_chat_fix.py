#!/usr/bin/env python3
"""
Test script to verify the chat service fix.
This script tests the chat endpoint to ensure the argument mismatch error is resolved.
"""
import requests
import json
import uuid

# Test the chat functionality
def test_chat_functionality():
    base_url = "http://localhost:8000/api/v1"

    print("Testing chat functionality after fixing argument mismatch error...")

    # First, create a chat session
    print("\n1. Creating a new chat session...")
    session_data = {
        "session_title": "Test Session for Chat Fix Verification",
        "user_id": "test_user"
    }

    try:
        session_response = requests.post(f"{base_url}/chat/start", json=session_data)
        print(f"Session creation status: {session_response.status_code}")

        if session_response.status_code == 200:
            session_info = session_response.json()
            session_id = session_info['id']
            print(f"Session created successfully with ID: {session_id}")
        else:
            print(f"Failed to create session: {session_response.text}")
            return False
    except Exception as e:
        print(f"Error creating session: {e}")
        return False

    # Now test the specific query mentioned in the original request
    print("\n2. Testing the specific query: 'Define Physical AI in one sentence'")
    chat_data = {
        "session_id": session_id,
        "message": "Define Physical AI in one sentence",
        "selected_text": None
    }

    try:
        chat_response = requests.post(f"{base_url}/chat/message", json=chat_data)
        print(f"Chat response status: {chat_response.status_code}")

        if chat_response.status_code == 200:
            response_data = chat_response.json()
            print("[SUCCESS] Chat functionality is working correctly!")
            print(f"Response received: {response_data['response'][:100]}...")
            print(f"Context sources: {response_data.get('context_sources', 'None')}")
            return True
        else:
            print(f"[FAILED] Chat request failed with status {chat_response.status_code}")
            print(f"Error response: {chat_response.text}")
            return False
    except Exception as e:
        print(f"[ERROR] Exception occurred during chat test: {e}")
        return False

if __name__ == "__main__":
    success = test_chat_functionality()
    if success:
        print("\n[VERIFIED] Chat service fix verification: PASSED")
        print("The argument mismatch error has been successfully resolved.")
    else:
        print("\n[ISSUE] Chat service fix verification: FAILED")
        print("There may still be issues with the chat functionality.")