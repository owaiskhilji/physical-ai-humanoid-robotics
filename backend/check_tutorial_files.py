#!/usr/bin/env python3
"""
Check if tutorial files are in Qdrant collection
"""
import sys
from pathlib import Path
import asyncio

# Add the backend src directory to the Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.core.config import settings
from qdrant_client import QdrantClient

async def check_tutorial_files():
    print("Connecting to Qdrant...")

    client = QdrantClient(
        url=settings.QDRANT_URL,
        api_key=settings.QDRANT_API_KEY,
        prefer_grpc=True
    )

    collection_name = "physical-ai"

    # Get all unique source files
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
    for point in all_points:
        source_file = point.payload.get('source_file', 'unknown')
        unique_files.add(source_file)

    print(f'\nUnique source files in collection: {len(unique_files)}')
    tutorial_files = [f for f in unique_files if 'tutorial' in f.lower()]
    chapter_files = [f for f in unique_files if 'chapter' in f.lower()]

    print('\nTutorial files found:')
    for file in sorted(tutorial_files):
        print(f'  - {file}')

    print('\nChapter files found:')
    for file in sorted(chapter_files):
        print(f'  - {file}')

    print('\nOther files found:')
    other_files = [f for f in unique_files if f not in tutorial_files and f not in chapter_files]
    for file in sorted(other_files):
        print(f'  - {file}')

if __name__ == "__main__":
    import asyncio
    asyncio.run(check_tutorial_files())