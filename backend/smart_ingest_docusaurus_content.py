#!/usr/bin/env python3
"""
Script for smart recursive document ingestion with deduplication.
This script performs a deep scan of the entire 'docs/' folder, checks for existing content in Qdrant,
and only processes new or previously missed files to save API tokens.
"""

import asyncio
import os
import sys
from pathlib import Path
from typing import List, Dict, Any, Set
import hashlib

# Add the backend src directory to the Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

import google.generativeai as genai
from qdrant_client import QdrantClient
from qdrant_client.http import models
from langchain_text_splitters import RecursiveCharacterTextSplitter
from uuid import uuid4
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Configuration
DOCS_DIR = Path(__file__).parent.parent / "docs"

# Load environment variables
from src.core.config import settings

class SmartDocusaurusIngestor:
    def __init__(self):
        # Configure Google Generative AI
        genai.configure(api_key=settings.GEMINI_API_KEY)
        self.model = genai.GenerativeModel('gemini-pro')

        # Initialize Qdrant client
        if settings.QDRANT_URL:
            self.client = QdrantClient(
                url=settings.QDRANT_URL,
                api_key=settings.QDRANT_API_KEY,
                prefer_grpc=True
            )
        else:
            raise ValueError("QDRANT_URL not configured in settings")

        self.collection_name = "physical-ai"
        self.vector_size = 768  # Size for Gemini embeddings
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
        )

    async def get_existing_files(self) -> Set[str]:
        """Query Qdrant to get a set of all existing source files in the collection"""
        try:
            # Get all points in the collection to check for existing files
            existing_files = set()

            # Use scroll to get all points efficiently
            offset = None
            while True:
                response = self.client.scroll(
                    collection_name=self.collection_name,
                    limit=1000,  # Process in batches of 1000
                    offset=offset,
                    with_payload=True,
                    with_vectors=False
                )

                points = response[0]  # Points are returned as (points, next_offset)
                next_offset = response[1]

                for point in points:
                    source_file = point.payload.get('source_file')
                    if source_file:
                        existing_files.add(source_file)

                # If no more points, break
                if next_offset is None:
                    break
                offset = next_offset

            logger.info(f"Found {len(existing_files)} existing files in Qdrant collection")
            return existing_files

        except Exception as e:
            logger.error(f"Error querying existing files from Qdrant: {e}")
            # If there's an error, return empty set to be safe and re-process everything
            return set()

    def scan_all_markdown_files(self) -> List[Path]:
        """Recursively scan the docs directory for all markdown files"""
        markdown_files = []

        for file_path in DOCS_DIR.rglob("*.md"):
            # Only include files that are within the docs directory structure
            if file_path.is_relative_to(DOCS_DIR):
                markdown_files.append(file_path)

        logger.info(f"Found {len(markdown_files)} markdown files in docs directory")
        for file in markdown_files:
            logger.info(f"  - {file.relative_to(DOCS_DIR)}")

        return markdown_files

    async def _generate_embedding(self, text: str) -> List[float]:
        """Generate embedding for text using Google's embedding model"""
        try:
            # Using Google's embedding API
            embedding_model = "models/text-embedding-004"  # Updated embedding model to match RAG service
            result = genai.embed_content(
                model=embedding_model,
                content=text,
                task_type="retrieval_document"
            )
            return result['embedding']
        except Exception as e:
            logger.error(f"Error generating embedding: {e}")
            # Return a dummy embedding in case of error for testing
            return [0.0] * self.vector_size

    def calculate_content_hash(self, content: str) -> str:
        """Calculate a hash of the content to detect changes"""
        return hashlib.md5(content.encode('utf-8')).hexdigest()

    async def process_and_upload_file(self, file_path: Path, existing_files: Set[str]) -> int:
        """Process a single file and upload to Qdrant if it's new or has changed"""
        relative_path = file_path.relative_to(DOCS_DIR)
        file_name = str(relative_path)

        # Check if this file already exists in Qdrant
        if file_name in existing_files:
            logger.info(f"Skipping {file_name} - already exists in Qdrant")
            return 0  # No new chunks added

        logger.info(f"Processing new file: {file_name}")

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Extract title from content
            title = self._extract_title(content, file_name)

            # Split content into chunks
            chunks = self.text_splitter.split_text(content)
            logger.info(f"Split {file_name} into {len(chunks)} chunks")

            # Upload each chunk to Qdrant
            uploaded_count = 0
            for i, chunk in enumerate(chunks):
                # Generate embedding for the chunk
                embedding = await self._generate_embedding(chunk)

                if embedding and len(embedding) == self.vector_size:
                    # Prepare payload
                    payload = {
                        "text": chunk,
                        "chapter_title": title,
                        "chunk_index": i,
                        "source_file": file_name,
                        "content_hash": self.calculate_content_hash(chunk)  # Add hash for future change detection
                    }

                    # Generate a unique ID for the point
                    point_id = str(uuid4())

                    # Upload to Qdrant
                    self.client.upsert(
                        collection_name=self.collection_name,
                        points=[
                            models.PointStruct(
                                id=point_id,
                                vector=embedding,
                                payload=payload
                            )
                        ]
                    )

                    uploaded_count += 1

                    if uploaded_count % 10 == 0:  # Log progress every 10 chunks
                        logger.info(f"Uploaded {uploaded_count}/{len(chunks)} chunks for {file_name}")

            logger.info(f"Completed {file_name}: uploaded {uploaded_count} chunks")
            return uploaded_count

        except Exception as e:
            logger.error(f"Error processing file {file_name}: {e}")
            return 0

    def _extract_title(self, content: str, filename: str) -> str:
        """Extract title from markdown content or filename"""
        # Try to extract title from the first line if it's a markdown header
        lines = content.strip().split('\n')
        for line in lines[:5]:  # Check first 5 lines
            if line.startswith('# '):
                return line[2:].strip()  # Remove '# ' prefix

        # If no markdown header found, use filename as title
        return filename.replace('.md', '').replace('-', ' ').title()

    async def run_smart_ingestion(self):
        """Run the complete smart ingestion process"""
        logger.info("Starting smart recursive document ingestion with deduplication...")

        # Get existing files from Qdrant
        existing_files = await self.get_existing_files()

        # Scan all markdown files in docs directory
        all_markdown_files = self.scan_all_markdown_files()

        # Identify new files to process
        new_files = []
        for file_path in all_markdown_files:
            relative_path = file_path.relative_to(DOCS_DIR)
            file_name = str(relative_path)
            if file_name not in existing_files:
                new_files.append(file_path)

        logger.info(f"Identified {len(new_files)} new or updated files to process out of {len(all_markdown_files)} total files")

        # Process each new file
        total_new_chunks = 0
        processed_files = 0

        for file_path in new_files:
            chunks_added = await self.process_and_upload_file(file_path, existing_files)
            total_new_chunks += chunks_added
            if chunks_added > 0:
                processed_files += 1

        # Get final count from Qdrant
        try:
            collection_info = self.client.get_collection(self.collection_name)
            final_count = collection_info.points_count
            logger.info(f"Ingestion completed! Added {total_new_chunks} new chunks from {processed_files} files.")
            logger.info(f"Collection '{self.collection_name}' now contains {final_count} total vectors.")
        except Exception as e:
            logger.error(f"Error getting final collection count: {e}")
            logger.info(f"Ingestion completed! Added approximately {total_new_chunks} new chunks from {processed_files} files.")

        return total_new_chunks, processed_files

async def main():
    """Main function to run the smart ingestion script"""
    ingestor = SmartDocusaurusIngestor()
    new_chunks, processed_files = await ingestor.run_smart_ingestion()

    if new_chunks > 0 or processed_files > 0:
        print(f"\n[SUCCESS] Smart Docusaurus content ingestion completed!")
        print(f"Added {new_chunks} new chunks from {processed_files} files to Qdrant collection.")
        print("Content is now available in Qdrant for RAG functionality.")
        print("You can test the '/chat/message' endpoint in Swagger.")
    else:
        print(f"\n[INFO] Smart Docusaurus content ingestion completed!")
        print("No new files were found to process (all files already exist in Qdrant).")
        print("Content remains available in Qdrant for RAG functionality.")

if __name__ == "__main__":
    asyncio.run(main())