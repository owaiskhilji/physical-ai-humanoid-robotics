#!/usr/bin/env python3
"""
Script to specifically index the 9 sections from Chapter 5 (VLA) in the Qdrant database.
This script checks if sections with the same section_title and source_file already exist,
and only indexes sections that are missing from the database.
"""

import asyncio
import os
import sys
from pathlib import Path
from typing import List, Dict, Any
import re
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
CHAPTER_FILE = "chapter5-vla.md"

# Load environment variables
from src.core.config import settings

class Chapter5SectionIndexer:
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

        # Create required indexes for filtering
        self.create_indexes()

    def create_indexes(self):
        """Create required indexes for filtering by section_title and source_file"""
        try:
            # Create index for section_title field
            self.client.create_payload_index(
                collection_name=self.collection_name,
                field_name="section_title",
                field_schema=models.PayloadSchemaType.KEYWORD
            )
            logger.info("Created index for section_title field")
        except Exception as e:
            # Index might already exist, which is fine
            logger.info(f"Index for section_title field already exists or error: {e}")

        try:
            # Create index for source_file field
            self.client.create_payload_index(
                collection_name=self.collection_name,
                field_name="source_file",
                field_schema=models.PayloadSchemaType.KEYWORD
            )
            logger.info("Created index for source_file field")
        except Exception as e:
            # Index might already exist, which is fine
            logger.info(f"Index for source_file field already exists or error: {e}")

    def extract_sections_from_content(self, content: str) -> Dict[str, str]:
        """
        Extract the 9 specific sections from Chapter 5 content based on H2 headers.
        Returns a dictionary mapping section titles to their content.
        """
        # Define the 9 specific sections we want to extract
        target_sections = [
            "VLA System Architecture",
            "Humanoid Kinematics & Dynamics",
            "ROS 2 Integration",
            "Simulation Environments",
            "Mathematical Foundations",
            "Natural Language Processing & Understanding",
            "Practical Considerations",
            "Case Studies",
            "Capstone Project"
        ]

        sections = {}

        # Split content by H2 headers (##)
        h2_pattern = r'^##\s+(.+)$'
        lines = content.split('\n')

        current_section = None
        current_content = []

        for line in lines:
            h2_match = re.match(h2_pattern, line.strip())
            if h2_match:
                # If we were collecting content for a previous section, save it
                if current_section and current_content:
                    sections[current_section] = '\n'.join(current_content).strip()

                # Check if this is one of our target sections
                section_title = h2_match.group(1).strip()
                if section_title in target_sections:
                    current_section = section_title
                    current_content = [line]  # Start with the header line
                else:
                    current_section = None
                    current_content = []
            else:
                # Add line to current section if we're tracking one
                if current_section is not None:
                    current_content.append(line)

        # Don't forget the last section
        if current_section and current_content:
            sections[current_section] = '\n'.join(current_content).strip()

        return sections

    async def check_section_exists(self, section_title: str, source_file: str) -> bool:
        """
        Check if a section with the same section_title and source_file already exists in Qdrant.
        """
        try:
            # Search for points that have matching section_title and source_file in payload
            search_result = self.client.scroll(
                collection_name=self.collection_name,
                scroll_filter=models.Filter(
                    must=[
                        models.FieldCondition(
                            key="section_title",
                            match=models.MatchValue(value=section_title)
                        ),
                        models.FieldCondition(
                            key="source_file",
                            match=models.MatchValue(value=source_file)
                        )
                    ]
                ),
                limit=1
            )

            points = search_result[0]
            return len(points) > 0
        except Exception as e:
            logger.error(f"Error checking if section exists: {e}")
            # If there's an error, assume it doesn't exist to be safe
            return False

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

    async def index_section(self, section_title: str, section_content: str, source_file: str) -> int:
        """
        Index a single section into Qdrant with proper metadata.
        Returns the number of chunks added.
        """
        logger.info(f"Indexing section: {section_title}")

        # Split section content into chunks
        chunks = self.text_splitter.split_text(section_content)
        logger.info(f"Split section '{section_title}' into {len(chunks)} chunks")

        # Upload each chunk to Qdrant
        uploaded_count = 0
        for i, chunk in enumerate(chunks):
            # Generate embedding for the chunk
            embedding = await self._generate_embedding(chunk)

            if embedding and len(embedding) == self.vector_size:
                # Prepare payload with specific section_title metadata
                payload = {
                    "text": chunk,
                    "section_title": section_title,  # Critical: tag with specific section title
                    "source_file": source_file,
                    "chunk_index": i,
                    "content_hash": self.calculate_content_hash(chunk),
                    "chapter_title": "Chapter 5: Vision-Language-Action in Physical AI"  # Additional context
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
                    logger.info(f"Uploaded {uploaded_count}/{len(chunks)} chunks for section '{section_title}'")

        logger.info(f"Completed section '{section_title}': uploaded {uploaded_count} chunks")
        return uploaded_count

    def calculate_content_hash(self, content: str) -> str:
        """Calculate a hash of the content to detect changes"""
        return hashlib.md5(content.encode('utf-8')).hexdigest()

    async def get_total_chunks_for_chapter5(self) -> int:
        """Get the total number of chunks for Chapter 5 after the update"""
        try:
            # Count all points that are from chapter5-vla.md
            search_result = self.client.scroll(
                collection_name=self.collection_name,
                scroll_filter=models.Filter(
                    must=[
                        models.FieldCondition(
                            key="source_file",
                            match=models.MatchValue(value="chapter5-vla.md")
                        )
                    ]
                ),
                limit=999999  # Large limit to get all matches
            )

            points = search_result[0]
            return len(points)
        except Exception as e:
            logger.error(f"Error getting total chunks for Chapter 5: {e}")
            return 0

    async def run_indexing(self):
        """Run the complete indexing process for Chapter 5 sections"""
        logger.info("Starting Chapter 5 section indexing...")

        # Read the chapter file
        file_path = DOCS_DIR / CHAPTER_FILE
        if not file_path.exists():
            logger.error(f"Chapter file not found: {file_path}")
            return [], [], 0

        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Extract the 9 specific sections
        sections = self.extract_sections_from_content(content)
        logger.info(f"Found {len(sections)} sections to process: {list(sections.keys())}")

        # Track results
        already_present = []
        newly_added = []
        total_new_chunks = 0

        # Process each section
        for section_title, section_content in sections.items():
            # Check if this section already exists in the database
            exists = await self.check_section_exists(section_title, CHAPTER_FILE)

            if exists:
                logger.info(f"Section '{section_title}' already exists in database - skipping")
                already_present.append(section_title)
            else:
                logger.info(f"Section '{section_title}' not found in database - indexing")
                chunks_added = await self.index_section(section_title, section_content, CHAPTER_FILE)
                total_new_chunks += chunks_added
                newly_added.append({
                    'section_title': section_title,
                    'chunks_added': chunks_added
                })

        # Get total chunk count for Chapter 5 after update
        final_chunk_count = await self.get_total_chunks_for_chapter5()

        # Report results
        logger.info(f"\n=== INDEXING RESULTS ===")
        logger.info(f"Sections already present (skipped): {len(already_present)}")
        for section in already_present:
            logger.info(f"  - {section}")

        logger.info(f"\nNew sections added: {len(newly_added)}")
        for item in newly_added:
            logger.info(f"  - {item['section_title']}: {item['chunks_added']} chunks")

        logger.info(f"\nTotal new chunks added: {total_new_chunks}")
        logger.info(f"Total Chapter 5 chunks after update: {final_chunk_count}")

        return already_present, newly_added, final_chunk_count

async def main():
    """Main function to run the Chapter 5 section indexing script"""
    indexer = Chapter5SectionIndexer()
    already_present, newly_added, final_chunk_count = await indexer.run_indexing()

    print(f"\n=== SUMMARY ===")
    print(f"Sections already present (skipped): {len(already_present)}")
    for section in already_present:
        print(f"  - {section}")

    print(f"\nNew sections added: {len(newly_added)}")
    for item in newly_added:
        print(f"  - {item['section_title']}: {item['chunks_added']} chunks")

    print(f"\nTotal Chapter 5 chunks after update: {final_chunk_count}")

    print(f"\n[SUCCESS] Chapter 5 section indexing completed!")

if __name__ == "__main__":
    asyncio.run(main())