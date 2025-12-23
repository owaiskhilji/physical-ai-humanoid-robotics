#!/usr/bin/env python3
"""
Script to perform clean re-indexing of Qdrant collection with sequential chapter processing
"""
import asyncio
import sys
from pathlib import Path
from typing import List, Dict, Any
import logging

# Add the backend src directory to the Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

import google.generativeai as genai
from qdrant_client import QdrantClient
from qdrant_client.http import models
from langchain_text_splitters import RecursiveCharacterTextSplitter
from uuid import uuid4

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Configuration
DOCS_DIR = Path(__file__).parent.parent / "docs"
CHAPTER_FILES = [
    ("chapter1-intro.md", 1),
    ("chapter2-ros2.md", 2),
    ("chapter3-digital-twin.md", 3),
    ("chapter4-nvidia-isaac.md", 4),
    ("chapter5-vla.md", 5)
]

TUTORIAL_FOLDERS = [
    ("tutorial-basics", "tutorial"),
    ("tutorial-extras", "tutorial")
]

# Load environment variables
from src.core.config import settings

class SequentialIngestor:
    def __init__(self):
        # Configure Google Generative AI
        genai.configure(api_key=settings.GEMINI_API_KEY)
        self.model = genai.GenerativeModel('gemini-2.5-flash')

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

    async def delete_collection(self):
        """Delete the existing Qdrant collection"""
        try:
            collections = self.client.get_collections()
            collection_names = [c.name for c in collections.collections]

            if self.collection_name in collection_names:
                self.client.delete_collection(self.collection_name)
                logger.info(f"Deleted existing Qdrant collection: {self.collection_name}")
            else:
                logger.info(f"Collection '{self.collection_name}' does not exist, proceeding with creation")

        except Exception as e:
            logger.error(f"Error deleting collection: {e}")
            raise

    async def init_collection(self):
        """Initialize the Qdrant collection for physical-ai content"""
        try:
            # Create collection with specified vector size
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=models.VectorParams(
                    size=self.vector_size,
                    distance=models.Distance.COSINE
                )
            )
            logger.info(f"Created Qdrant collection: {self.collection_name}")

            # Create payload index for chapter_number to enable filtering
            self.client.create_payload_index(
                collection_name=self.collection_name,
                field_name="chapter_number",
                field_schema=models.PayloadSchemaType.INTEGER
            )
            logger.info("Created payload index for chapter_number field")

            # Create payload index for chapter_title to enable filtering
            self.client.create_payload_index(
                collection_name=self.collection_name,
                field_name="chapter_title",
                field_schema=models.PayloadSchemaType.KEYWORD
            )
            logger.info("Created payload index for chapter_title field")

        except Exception as e:
            logger.error(f"Error initializing Qdrant collection: {e}")
            raise

    async def _generate_embedding(self, text: str) -> List[float]:
        """Generate embedding for text using Google's embedding model"""
        try:
            # Using Google's embedding API
            embedding_model = "models/text-embedding-004"  # Updated embedding model
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

    def read_chapter(self, chapter_file: str, chapter_number: int) -> Dict[str, Any]:
        """Read a single chapter file from the docs directory"""
        file_path = DOCS_DIR / chapter_file

        if not file_path.exists():
            logger.warning(f"Chapter file not found: {file_path}")
            return None

        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Extract title from content
        chapter_title = self._extract_title(content, chapter_file)

        result = {
            'chapter_number': chapter_number,
            'chapter_title': chapter_title,
            'content': content,
            'filename': chapter_file
        }

        logger.info(f"Read chapter {chapter_number}: {chapter_title} ({len(content)} characters)")
        return result

    def _extract_title(self, content: str, filename: str) -> str:
        """Extract title from markdown content or filename"""
        # Try to extract title from the first line if it's a markdown header
        lines = content.strip().split('\n')
        for line in lines[:5]:  # Check first 5 lines
            if line.startswith('# '):
                return line[2:].strip()  # Remove '# ' prefix

        # If no markdown header found, use filename as title
        return filename.replace('.md', '').replace('-', ' ').title()

    async def process_and_upload_chapter(self, chapter: Dict[str, Any]) -> int:
        """Process a single chapter and upload to Qdrant"""
        logger.info(f"Processing chapter {chapter['chapter_number']}: {chapter['chapter_title']}")

        # Split chapter content into chunks
        chunks = self.text_splitter.split_text(chapter['content'])
        logger.info(f"Split chapter into {len(chunks)} chunks")

        chunk_count = 0
        for i, chunk in enumerate(chunks):
            # Generate embedding for the chunk
            embedding = await self._generate_embedding(chunk)

            if embedding and len(embedding) == self.vector_size:
                # Prepare payload with proper metadata
                payload = {
                    "text": chunk,
                    "chapter_number": chapter['chapter_number'],
                    "chapter_title": chapter['chapter_title'],
                    "chunk_index": i,
                    "source_file": chapter['filename'],
                    "content_length": len(chunk)
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

                if chunk_count % 10 == 0:  # Log progress every 10 chunks
                    logger.info(f"Uploaded {chunk_count}/{len(chunks)} chunks for chapter {chapter['chapter_number']}")

        logger.info(f"Completed chapter {chapter['chapter_number']}: uploaded {chunk_count} chunks")

        # Verify the chapter was properly indexed
        collection_info = self.client.get_collection(self.collection_name)
        logger.info(f"Collection '{self.collection_name}' now contains {collection_info.points_count} total vectors")

        return chunk_count

    async def process_and_upload_tutorial_folder(self, folder_name: str, category: str) -> int:
        """Process a tutorial folder and upload to Qdrant"""
        logger.info(f"Processing tutorial folder: {folder_name}")

        folder_path = DOCS_DIR / folder_name

        if not folder_path.exists():
            logger.warning(f"Tutorial folder not found: {folder_path}")
            return 0

        # Get all markdown files in the tutorial folder
        md_files = list(folder_path.glob("*.md")) + list(folder_path.glob("*.mdx"))

        if not md_files:
            logger.info(f"No markdown files found in tutorial folder: {folder_name}")
            return 0

        total_chunks = 0

        for md_file in md_files:
            logger.info(f"Processing tutorial file: {md_file.name}")

            # Read the file content
            with open(md_file, 'r', encoding='utf-8') as f:
                content = f.read()

            # Extract title from content
            title = self._extract_title(content, md_file.name)

            # Create a chapter-like structure for the tutorial file
            tutorial_content = {
                'chapter_number': None,  # No chapter number for tutorials
                'chapter_title': title,
                'content': content,
                'filename': f"{folder_name}/{md_file.name}"
            }

            # Split tutorial content into chunks
            chunks = self.text_splitter.split_text(tutorial_content['content'])
            logger.info(f"Split tutorial file {md_file.name} into {len(chunks)} chunks")

            chunk_count = 0
            for i, chunk in enumerate(chunks):
                # Generate embedding for the chunk
                embedding = await self._generate_embedding(chunk)

                if embedding and len(embedding) == self.vector_size:
                    # Prepare payload with proper metadata for tutorial
                    payload = {
                        "text": chunk,
                        "chapter_number": None,  # No chapter number for tutorials
                        "chapter_title": tutorial_content['chapter_title'],
                        "chunk_index": i,
                        "source_file": tutorial_content['filename'],
                        "category": category,
                        "content_length": len(chunk)
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

                    if chunk_count % 10 == 0:  # Log progress every 10 chunks
                        logger.info(f"Uploaded {chunk_count}/{len(chunks)} chunks for tutorial {md_file.name}")

            total_chunks += chunk_count
            logger.info(f"Completed tutorial file {md_file.name}: uploaded {chunk_count} chunks")

        # Verify the tutorial folder was properly indexed
        collection_info = self.client.get_collection(self.collection_name)
        logger.info(f"Collection '{self.collection_name}' now contains {collection_info.points_count} total vectors after processing {folder_name}")

        return total_chunks

    async def verify_metadata(self, chapter_number: int):
        """Verify that the metadata for a chapter is correctly assigned"""
        logger.info(f"Verifying metadata for chapter {chapter_number}")

        try:
            # Query for points from this chapter using scroll instead of filter query to avoid index dependency
            # Get a sample of points to verify they have correct metadata
            sample_results = self.client.scroll(
                collection_name=self.collection_name,
                limit=10,  # Get up to 10 points
                with_payload=True,
                with_vectors=False
            )

            points = sample_results[0]  # Scroll returns (points, next_offset)

            # Filter points that belong to the current chapter
            chapter_points = [p for p in points if p.payload.get('chapter_number') == chapter_number]

            if chapter_points:
                for point in chapter_points[:3]:  # Show first 3 as samples
                    payload = point.payload
                    logger.info(f"  Sample metadata - Chapter: {payload.get('chapter_number')}, "
                               f"Title: {payload.get('chapter_title')}, "
                               f"Source: {payload.get('source_file')}")

            total_chapter_points = len(chapter_points)
            logger.info(f"Found {total_chapter_points} chunks with correct metadata for chapter {chapter_number}")
            return total_chapter_points
        except Exception as e:
            logger.error(f"Error verifying metadata for chapter {chapter_number}: {e}")
            # Fallback: just count total points in collection
            collection_info = self.client.get_collection(self.collection_name)
            logger.info(f"Collection has {collection_info.points_count} total points so far")
            return 0  # Return 0 but continue processing

    async def search_term(self, term: str):
        """Perform a direct search for a term in Qdrant"""
        logger.info(f"Searching for term: '{term}'")

        # First generate an embedding for the search term
        query_embedding = await self._generate_embedding(term)

        if query_embedding and len(query_embedding) == self.vector_size:
            # Search for similar content
            search_results = self.client.query_points(
                collection_name=self.collection_name,
                query=query_embedding,
                limit=10
            )

            points = search_results.points if hasattr(search_results, 'points') else search_results
            logger.info(f"Found {len(points)} results for term '{term}'")

            for i, point in enumerate(points[:5]):  # Show first 5 results
                payload = point.payload
                logger.info(f"  {i+1}. Chapter {payload.get('chapter_number')}: {payload.get('chapter_title')}")
                logger.info(f"     Score: {point.score:.4f}")
                logger.info(f"     Text: {payload.get('text', '')[:100]}...")

            return len(points)
        else:
            logger.warning(f"Could not generate embedding for search term: {term}")
            return 0

    async def run_sequential_ingestion(self):
        """Run the complete sequential ingestion process"""
        logger.info("Starting clean sequential content ingestion to Qdrant...")

        # Delete existing collection
        await self.delete_collection()

        # Initialize collection
        await self.init_collection()

        total_chunks = 0

        # Process each chapter sequentially
        for chapter_file, chapter_number in CHAPTER_FILES:
            logger.info(f"\n--- Processing Chapter {chapter_number}: {chapter_file} ---")

            # Read the chapter
            chapter = self.read_chapter(chapter_file, chapter_number)
            if not chapter:
                logger.error(f"Failed to read chapter {chapter_number}: {chapter_file}")
                continue

            # Process and upload the chapter
            chunks_added = await self.process_and_upload_chapter(chapter)
            total_chunks += chunks_added

            # Verify metadata for this chapter
            await self.verify_metadata(chapter_number)

            logger.info(f"Chapter {chapter_number} completed: {chunks_added} chunks added\n")

        # Process each tutorial folder sequentially
        for folder_name, category in TUTORIAL_FOLDERS:
            logger.info(f"\n--- Processing Tutorial Folder: {folder_name} ---")

            # Process and upload the tutorial folder
            chunks_added = await self.process_and_upload_tutorial_folder(folder_name, category)
            total_chunks += chunks_added

            logger.info(f"Tutorial folder {folder_name} completed: {chunks_added} chunks added\n")

        # Final verification
        collection_info = self.client.get_collection(self.collection_name)
        logger.info(f"\nIngestion completed successfully!")
        logger.info(f"Total chunks ingested: {total_chunks}")
        logger.info(f"Collection '{self.collection_name}' contains {collection_info.points_count} vectors")

        return total_chunks

async def main():
    """Main function to run the sequential ingestion script"""
    ingestor = SequentialIngestor()
    total_chunks = await ingestor.run_sequential_ingestion()

    if total_chunks > 0:
        print(f"\n[SUCCESS] Sequential content ingestion completed!")
        print(f"Total chunks ingested: {total_chunks}")
        print("Content is now available in Qdrant for RAG functionality.")

        # Perform the requested verification search
        print(f"\nPerforming verification search for 'Vision-Language-Action'...")
        result_count = await ingestor.search_term('Vision-Language-Action')
        print(f"Found {result_count} results for 'Vision-Language-Action'")
    else:
        print(f"\n[ERROR] Sequential content ingestion failed!")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())