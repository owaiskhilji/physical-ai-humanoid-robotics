#!/usr/bin/env python3
"""
Test script to verify the RAG functionality with the fixed Qdrant method.
"""
import requests
import json
import time

def test_rag_functionality():
    base_url = "http://localhost:8000/api/v1"

    print("Testing RAG functionality with 'What is Physical AI?' query...")

    # First, create a chat session
    print("\n1. Creating a new chat session...")
    session_data = {
        "session_title": "Test Session for Qdrant Fix Verification",
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

    # Test the specific query
    print("\n2. Testing the query: 'What is Physical AI?'")
    chat_data = {
        "session_id": session_id,
        "message": "What is Physical AI?",
        "selected_text": None
    }

    try:
        chat_response = requests.post(f"{base_url}/chat/message", json=chat_data)
        print(f"Chat response status: {chat_response.status_code}")

        if chat_response.status_code == 200:
            response_data = chat_response.json()
            print("[SUCCESS] RAG functionality is working!")
            print(f"Response received: {response_data['response'][:300]}...")
            print(f"Context sources: {len(response_data.get('context_sources', []))} sources found")
            return True
        else:
            print(f"[FAILED] Chat request failed with status {chat_response.status_code}")
            print(f"Error response: {chat_response.text}")
            return False
    except Exception as e:
        print(f"[ERROR] Exception occurred during test: {e}")
        return False

if __name__ == "__main__":
    success = test_rag_functionality()
    if success:
        print("\n[VERIFIED] RAG functionality with Qdrant fix is working correctly!")
    else:
        print("\n[ISSUE] There may be issues with the RAG functionality.")