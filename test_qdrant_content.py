#!/usr/bin/env python3
"""
Test script to verify content in Qdrant collection
"""
import sys
from pathlib import Path
import asyncio

# Add the backend src directory to the Python path
backend_path = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_path / "src"))

from src.core.config import settings
from qdrant_client import QdrantClient
from qdrant_client.http import models

async def test_qdrant_content():
    """Test the Qdrant collection to see what content is available"""
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
        limit=20  # Get first 20 points
    )

    print(f"\nSample points retrieved: {len(sample_points[0])}")
    print("\nFirst 20 sample entries:")
    for i, point in enumerate(sample_points[0]):
        payload = point.payload
        print(f"  {i+1}. Chapter: {payload.get('chapter_number', 'N/A')}, "
              f"File: {payload.get('source_file', 'N/A')[:50]}...")
        print(f"     Title: {payload.get('chapter_title', 'N/A')[:60]}...")
        print(f"     Text snippet: {payload.get('text', '')[:100]}...")
        print()

    # Count unique source files
    all_points = []
    offset = None
    while True:
        response = client.scroll(
            collection_name=collection_name,
            limit=1000,
            offset=offset,
            with_payload=True,
            with_vectors=False
        )

        points = response[0]
        next_offset = response[1]

        all_points.extend(points)

        if next_offset is None:
            break
        offset = next_offset

    unique_files = set()
    chapter_counts = {}

    for point in all_points:
        source_file = point.payload.get('source_file', 'unknown')
        chapter_num = point.payload.get('chapter_number', 'unknown')

        unique_files.add(source_file)

        if chapter_num not in chapter_counts:
            chapter_counts[chapter_num] = 0
        chapter_counts[chapter_num] += 1

    print(f"\nUnique source files in collection: {len(unique_files)}")
    for file in sorted(unique_files):
        print(f"  - {file}")

    print(f"\nContent distribution by chapter:")
    for chapter, count in sorted(chapter_counts.items()):
        print(f"  Chapter {chapter}: {count} chunks")

if __name__ == "__main__":
    asyncio.run(test_qdrant_content())