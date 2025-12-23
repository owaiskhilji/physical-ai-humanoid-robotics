#!/usr/bin/env python3
"""
Test retrieval functionality to see if there's bias toward Chapter 1
"""
import sys
from pathlib import Path
import asyncio
import google.generativeai as genai

# Add the backend src directory to the Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.core.config import settings
from src.core.vector_db import vector_db

# Configure Google Generative AI
genai.configure(api_key=settings.GEMINI_API_KEY)

async def test_retrieval():
    print("Testing retrieval functionality...")

    # Test with a query that should match Chapter 5 content
    chapter5_query = "What are Vision-Language-Action (VLA) models in robotics?"
    print(f"\nQuery: {chapter5_query}")

    # Generate embedding for the query
    embedding_model = "models/text-embedding-004"
    query_embedding = genai.embed_content(
        model=embedding_model,
        content=chapter5_query,
        task_type="retrieval_document"
    )['embedding']

    print(f"Generated embedding with size: {len(query_embedding)}")

    # Search for similar content
    results = await vector_db.search_similar(query_embedding, limit=5)

    print(f"\nTop 5 results for Chapter 5 query:")
    for i, result in enumerate(results, 1):
        print(f"  {i}. Chapter: {result['chapter_number']}, File: {result['chapter_title']}")
        print(f"     Score: {result['score']:.4f}")
        print(f"     Text snippet: {result['text'][:100]}...")
        print()

    # Test with a query that should match tutorial content
    tutorial_query = "How to create a blog post in Docusaurus?"
    print(f"\nQuery: {tutorial_query}")

    # Generate embedding for the query
    query_embedding2 = genai.embed_content(
        model=embedding_model,
        content=tutorial_query,
        task_type="retrieval_document"
    )['embedding']

    # Search for similar content
    results2 = await vector_db.search_similar(query_embedding2, limit=5)

    print(f"\nTop 5 results for tutorial query:")
    for i, result in enumerate(results2, 1):
        print(f"  {i}. Chapter: {result['chapter_number']}, File: {result['chapter_title']}")
        print(f"     Score: {result['score']:.4f}")
        print(f"     Text snippet: {result['text'][:100]}...")
        print()

if __name__ == "__main__":
    import asyncio
    asyncio.run(test_retrieval())