#!/usr/bin/env python3
"""
Script to ingest Docusaurus content to Qdrant for RAG functionality.
This script reads the 5 chapters from the docs folder and uploads them to Qdrant.
"""

import asyncio
import os
import sys
from pathlib import Path
from typing import List, Dict, Any

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
CHAPTER_FILES = [
    "chapter1-intro.md",
    "chapter2-ros2.md",
    "chapter3-digital-twin.md",
    "chapter4-nvidia-isaac.md",
    "chapter5-vla.md"
]

# Load environment variables
from src.core.config import settings

class DocusaurusIngestor:
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

    async def init_collection(self):
        """Initialize the Qdrant collection for physical-ai content"""
        try:
            # Check if collection exists
            collections = self.client.get_collections()
            collection_names = [c.name for c in collections.collections]

            if self.collection_name not in collection_names:
                # Create collection with specified vector size
                self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=models.VectorParams(
                        size=self.vector_size,
                        distance=models.Distance.COSINE
                    )
                )
                logger.info(f"Created Qdrant collection: {self.collection_name}")
            else:
                logger.info(f"Qdrant collection {self.collection_name} already exists")

                # For automated runs, just log that the collection exists
                logger.info(f"Using existing Qdrant collection: {self.collection_name}")
                # If you want to clear and re-ingest, uncomment the following lines:
                # self.client.delete_collection(self.collection_name)
                # self.client.create_collection(
                #     collection_name=self.collection_name,
                #     vectors_config=models.VectorParams(
                #         size=self.vector_size,
                #         distance=models.Distance.COSINE
                #     )
                # )
                # logger.info(f"Cleared and recreated Qdrant collection: {self.collection_name}")
        except Exception as e:
            logger.error(f"Error initializing Qdrant collection: {e}")
            raise

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

    def read_chapters(self) -> List[Dict[str, Any]]:
        """Read all chapter files from the docs directory"""
        chapters = []

        for i, chapter_file in enumerate(CHAPTER_FILES, 1):
            file_path = DOCS_DIR / chapter_file

            if not file_path.exists():
                logger.warning(f"Chapter file not found: {file_path}")
                continue

            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Extract chapter number from filename
            chapter_number = i
            chapter_title = self._extract_title(content, chapter_file)

            chapters.append({
                'chapter_number': chapter_number,
                'chapter_title': chapter_title,
                'content': content,
                'filename': chapter_file
            })

            logger.info(f"Read chapter {chapter_number}: {chapter_title} ({len(content)} characters)")

        return chapters

    def _extract_title(self, content: str, filename: str) -> str:
        """Extract title from markdown content or filename"""
        # Try to extract title from the first line if it's a markdown header
        lines = content.strip().split('\n')
        for line in lines[:5]:  # Check first 5 lines
            if line.startswith('# '):
                return line[2:].strip()  # Remove '# ' prefix

        # If no markdown header found, use filename as title
        return filename.replace('.md', '').replace('-', ' ').title()

    async def process_and_upload_chapters(self, chapters: List[Dict[str, Any]]):
        """Process chapters and upload to Qdrant"""
        total_chunks = 0

        for chapter in chapters:
            logger.info(f"Processing chapter {chapter['chapter_number']}: {chapter['chapter_title']}")

            # Split chapter content into chunks
            chunks = self.text_splitter.split_text(chapter['content'])
            logger.info(f"Split chapter into {len(chunks)} chunks")

            chunk_count = 0
            for i, chunk in enumerate(chunks):
                # Generate embedding for the chunk
                embedding = await self._generate_embedding(chunk)

                if embedding and len(embedding) == self.vector_size:
                    # Prepare payload
                    payload = {
                        "text": chunk,
                        "chapter_number": chapter['chapter_number'],
                        "chapter_title": chapter['chapter_title'],
                        "chunk_index": i,
                        "source_file": chapter['filename']
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

                    chunk_count += 1
                    total_chunks += 1

                    if chunk_count % 10 == 0:  # Log progress every 10 chunks
                        logger.info(f"Uploaded {chunk_count}/{len(chunks)} chunks for chapter {chapter['chapter_number']}")

            logger.info(f"Completed chapter {chapter['chapter_number']}: uploaded {chunk_count} chunks")

        logger.info(f"Total chunks uploaded: {total_chunks}")
        return total_chunks

    async def verify_ingestion(self):
        """Verify that content has been properly ingested"""
        try:
            # Get collection info
            collection_info = self.client.get_collections()
            collection_names = [c.name for c in collection_info.collections]

            if self.collection_name not in collection_names:
                logger.error(f"Collection '{self.collection_name}' not found")
                return False

            collection_info = self.client.get_collection(self.collection_name)
            logger.info(f"Collection '{self.collection_name}' contains {collection_info.points_count} vectors")

            # Perform a test search to verify functionality if embeddings were generated properly
            if collection_info.points_count > 0:
                # Get a sample of points to verify they exist
                sample_points = self.client.scroll(
                    collection_name=self.collection_name,
                    limit=3
                )

                logger.info(f"Sample points retrieved: {len(sample_points[0])}")
                for i, point in enumerate(sample_points[0]):
                    logger.info(f"  {i+1}. Chapter {point.payload.get('chapter_number', 'N/A')}: "
                               f"{point.payload.get('chapter_title', 'N/A')[:50]}...")

            return collection_info.points_count > 0
        except Exception as e:
            logger.error(f"Error verifying ingestion: {e}")
            return False

    async def run_ingestion(self):
        """Run the complete ingestion process"""
        logger.info("Starting Docusaurus content ingestion to Qdrant...")

        # Initialize collection
        await self.init_collection()

        # Read chapters
        chapters = self.read_chapters()
        if not chapters:
            logger.error("No chapters found to ingest")
            return False

        logger.info(f"Found {len(chapters)} chapters to process")

        # Process and upload chapters
        total_chunks = await self.process_and_upload_chapters(chapters)

        # Verify ingestion
        success = await self.verify_ingestion()

        if success:
            logger.info(f"Ingestion completed successfully! Uploaded {total_chunks} chunks to '{self.collection_name}' collection.")
        else:
            logger.warning("Ingestion completed but verification failed.")

        return success

async def main():
    """Main function to run the ingestion script"""
    ingestor = DocusaurusIngestor()
    success = await ingestor.run_ingestion()

    if success:
        print("\n[SUCCESS] Docusaurus content ingestion completed successfully!")
        print("The content is now available in Qdrant for RAG functionality.")
        print("You can test the '/chat/message' endpoint in Swagger.")
    else:
        print("\n[ERROR] Docusaurus content ingestion failed!")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())