#!/usr/bin/env python3
"""
Simple test to verify content in Qdrant collection
"""
import sys
from pathlib import Path
import asyncio

# Add the backend src directory to the Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.core.config import settings
from qdrant_client import QdrantClient

async def test_qdrant_content():
    print("Connecting to Qdrant...")

    client = QdrantClient(
        url=settings.QDRANT_URL,
        api_key=settings.QDRANT_API_KEY,
        prefer_grpc=True
    )

    collection_name = "physical-ai"

    # Get collection info
    collection_info = client.get_collection(collection_name)
    print(f"Collection '{collection_name}' contains {collection_info.points_count} vectors")

    # Get sample points to see what content exists
    sample_points = client.scroll(
        collection_name=collection_name,
        limit=10  # Get first 10 points
    )

    print(f"\nSample points retrieved: {len(sample_points[0])}")
    print("\nSample entries:")
    for i, point in enumerate(sample_points[0]):
        payload = point.payload
        print(f"  {i+1}. File: {payload.get('source_file', 'N/A')}")
        print(f"     Chapter: {payload.get('chapter_number', 'N/A')}")
        print(f"     Title: {payload.get('chapter_title', 'N/A')}")
        print(f"     Text snippet: {payload.get('text', '')[:80]}...")
        print()

if __name__ == "__main__":
    import asyncio
    asyncio.run(test_qdrant_content())