#!/usr/bin/env python3
"""
Test script to trigger the debug RAG functionality and see the output.
"""
import requests
import json
import time

def test_debug_rag():
    base_url = "http://localhost:8000/api/v1"

    print("Testing debug RAG functionality...")

    # First, create a chat session
    print("\n1. Creating a new chat session...")
    session_data = {
        "session_title": "Debug Test Session",
        "user_id": "debug_test_user"
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

    # Test a query that should trigger RAG
    print("\n2. Testing a query: 'What is Physical AI?'")
    chat_data = {
        "session_id": session_id,
        "message": "What is Physical AI?",
        "selected_text": None
    }

    try:
        print("Sending request to chat endpoint...")
        chat_response = requests.post(f"{base_url}/chat/message", json=chat_data)
        print(f"Chat response status: {chat_response.status_code}")

        if chat_response.status_code == 200:
            response_data = chat_response.json()
            print("[SUCCESS] Request completed!")
            print(f"Response received: {response_data['response'][:200]}...")
            print(f"Context sources: {response_data.get('context_sources', 'None')}")
            return True
        else:
            print(f"[FAILED] Chat request failed with status {chat_response.status_code}")
            print(f"Error response: {chat_response.text}")
            return False
    except Exception as e:
        print(f"[ERROR] Exception occurred during test: {e}")
        return False

if __name__ == "__main__":
    test_debug_rag()
    print("\nNote: Check the Docker container logs for debug output using:")
    print("docker compose logs rag-chatbot-api")