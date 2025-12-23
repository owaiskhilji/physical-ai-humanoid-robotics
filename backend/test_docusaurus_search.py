#!/usr/bin/env python3
"""
Script to test search for 'Docusaurus basics' in the reindexed content
"""
import asyncio
import sys
from pathlib import Path

# Add the backend src directory to the Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from reindex_content import SequentialIngestor

async def test_docusaurus_search():
    ingestor = SequentialIngestor()
    print("Performing verification search for 'Docusaurus basics'...")
    result_count = await ingestor.search_term('Docusaurus basics')
    print(f'Found {result_count} results for \'Docusaurus basics\'')

if __name__ == "__main__":
    asyncio.run(test_docusaurus_search())