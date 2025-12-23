from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from src.models.content import BookContentDB, BookContentCreate, BookContentUpdate
from src.core.vector_db import vector_db
from src.core.logging import logger


class ContentService:
    """
    Service for managing book content and its integration with vector database
    """

    @staticmethod
    async def create_content(
        db: AsyncSession,
        content_create: BookContentCreate
    ) -> BookContentDB:
        """
        Create new book content and initialize vector embeddings
        """
        # Validate content quality before creating
        is_valid, validation_message = await ContentService.validate_content_quality(
            content_create.content_text,
            content_create.chapter_title
        )
        if not is_valid:
            raise ValueError(f"Content validation failed: {validation_message}")

        # Create the database record
        db_content = BookContentDB(
            chapter_number=content_create.chapter_number,
            chapter_title=content_create.chapter_title,
            content_text=content_create.content_text,
            version=content_create.version
        )

        db.add(db_content)
        await db.commit()
        await db.refresh(db_content)

        # Process content for RAG (chunking and embedding)
        await ContentService._process_content_for_rag(db_content)

        logger.info(f"Created content for chapter {content_create.chapter_number}: {content_create.chapter_title}")
        return db_content

    @staticmethod
    async def get_content_by_id(db: AsyncSession, content_id: str) -> Optional[BookContentDB]:
        """
        Get content by ID
        """
        result = await db.execute(
            select(BookContentDB).where(BookContentDB.id == content_id)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_content_by_chapter_number(db: AsyncSession, chapter_number: int) -> Optional[BookContentDB]:
        """
        Get content by chapter number
        """
        result = await db.execute(
            select(BookContentDB).where(BookContentDB.chapter_number == chapter_number)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_all_content(db: AsyncSession) -> List[BookContentDB]:
        """
        Get all book content
        """
        result = await db.execute(select(BookContentDB))
        return result.scalars().all()

    @staticmethod
    async def update_content(
        db: AsyncSession,
        content_id: str,
        content_update: BookContentUpdate
    ) -> Optional[BookContentDB]:
        """
        Update existing content and refresh vector embeddings
        """
        result = await db.execute(
            select(BookContentDB).where(BookContentDB.id == content_id)
        )
        db_content = result.scalar_one_or_none()

        if not db_content:
            return None

        # Prepare updated values
        updated_title = content_update.chapter_title if content_update.chapter_title is not None else db_content.chapter_title
        updated_content = content_update.content_text if content_update.content_text is not None else db_content.content_text

        # Validate content quality before updating
        if content_update.content_text is not None or content_update.chapter_title is not None:
            is_valid, validation_message = await ContentService.validate_content_quality(
                updated_content,
                updated_title
            )
            if not is_valid:
                raise ValueError(f"Content validation failed: {validation_message}")

        # Store original values for logging
        original_title = db_content.chapter_title
        original_content = db_content.content_text
        original_version = db_content.version

        # Update fields
        if content_update.chapter_title is not None:
            db_content.chapter_title = content_update.chapter_title
        if content_update.content_text is not None:
            db_content.content_text = content_update.content_text
        if content_update.version is not None:
            db_content.version = content_update.version

        await db.commit()
        await db.refresh(db_content)

        # Re-process content for RAG (chunking and embedding)
        success = await ContentService.update_existing_content(db_content)
        if not success:
            logger.error(f"Failed to update content in RAG system for chapter {db_content.chapter_number}")
            # Rollback the changes if RAG update fails
            db_content.chapter_title = original_title
            db_content.content_text = original_content
            db_content.version = original_version
            await db.commit()
            return None

        logger.info(f"Updated content for chapter {db_content.chapter_number}")
        return db_content

    @staticmethod
    async def incremental_update_content(
        db: AsyncSession,
        chapter_number: int,
        content_update: BookContentUpdate
    ) -> Optional[BookContentDB]:
        """
        Incrementally update content for a specific chapter without requiring a full rebuild
        """
        # Find the existing content by chapter number
        result = await db.execute(
            select(BookContentDB).where(BookContentDB.chapter_number == chapter_number)
        )
        db_content = result.scalar_one_or_none()

        if not db_content:
            return None

        # Prepare updated values
        updated_title = content_update.chapter_title if content_update.chapter_title is not None else db_content.chapter_title
        updated_content = content_update.content_text if content_update.content_text is not None else db_content.content_text

        # Validate content quality before updating
        if content_update.content_text is not None or content_update.chapter_title is not None:
            is_valid, validation_message = await ContentService.validate_content_quality(
                updated_content,
                updated_title
            )
            if not is_valid:
                raise ValueError(f"Content validation failed: {validation_message}")

        # Store original values for logging
        original_title = db_content.chapter_title
        original_content = db_content.content_text
        original_version = db_content.version

        # Update fields
        if content_update.chapter_title is not None:
            db_content.chapter_title = content_update.chapter_title
        if content_update.content_text is not None:
            db_content.content_text = content_update.content_text
        if content_update.version is not None:
            db_content.version = content_update.version

        await db.commit()
        await db.refresh(db_content)

        # Process only the changed content for RAG
        success = await ContentService.update_existing_content(db_content)
        if not success:
            logger.error(f"Failed to incrementally update content in RAG system for chapter {db_content.chapter_number}")
            # Rollback the changes if RAG update fails
            db_content.chapter_title = original_title
            db_content.content_text = original_content
            db_content.version = original_version
            await db.commit()
            return None

        logger.info(f"Successfully performed incremental update for chapter {db_content.chapter_number}")
        return db_content

    @staticmethod
    async def delete_content(db: AsyncSession, content_id: str) -> bool:
        """
        Delete content and associated vector embeddings
        """
        result = await db.execute(
            select(BookContentDB).where(BookContentDB.id == content_id)
        )
        db_content = result.scalar_one_or_none()

        if not db_content:
            return False

        # Remove from vector database
        await vector_db.delete_by_content_id(content_id)

        # Remove from database
        await db.delete(db_content)
        await db.commit()

        logger.info(f"Deleted content for chapter {db_content.chapter_number}")
        return True

    @staticmethod
    async def validate_content_quality(content_text: str, chapter_title: str) -> tuple[bool, str]:
        """
        Validate the quality of content before adding to the system
        Returns (is_valid, message)
        """
        # Check minimum content length
        if len(content_text.strip()) < 100:
            return False, "Content is too short (minimum 100 characters required)"

        # Check for basic structure (should have multiple paragraphs)
        paragraphs = [p.strip() for p in content_text.split('\n\n') if p.strip()]
        if len(paragraphs) < 2:
            return False, "Content should have at least 2 paragraphs for proper textbook structure"

        # Check for title relevance (basic check)
        title_words = set(chapter_title.lower().split())
        content_words = set(content_text.lower().split()[:50])  # Check first 50 words
        if len(title_words.intersection(content_words)) < 1:
            logger.warning(f"Content may not be well-matched to title: {chapter_title}")

        # Check for non-text elements that might affect quality
        excessive_caps = len([w for w in content_text.split() if w.isupper() and len(w) > 3])
        if excessive_caps > 10:  # More than 10 all-caps words
            logger.warning("Content contains many all-caps words which may affect readability")

        return True, "Content validation passed"

    @staticmethod
    async def _process_content_for_rag(content: BookContentDB):
        """
        Process content for RAG by chunking and creating vector embeddings
        """
        try:
            # Remove existing embeddings for this content
            await vector_db.delete_by_content_id(content.id)

            # Simple chunking strategy - split by paragraphs
            paragraphs = content.content_text.split('\n\n')
            chunks = []

            for i, paragraph in enumerate(paragraphs):
                if len(paragraph.strip()) > 50:  # Only include substantial paragraphs
                    chunks.append({
                        'text': paragraph.strip(),
                        'chunk_index': i,
                        'chapter_number': content.chapter_number,
                        'chapter_title': content.chapter_title
                    })

            # For now, we'll store the chunks in the content record
            # In a real implementation, we'd generate embeddings and store in vector DB
            content.content_chunks = [chunk['text'] for chunk in chunks]

            logger.info(f"Processed {len(chunks)} chunks for chapter {content.chapter_number}")

        except Exception as e:
            logger.error(f"Error processing content for RAG: {e}")
            raise

    @staticmethod
    async def process_new_content(content: BookContentDB) -> bool:
        """
        Process new content for RAG ingestion pipeline
        """
        try:
            # Process the content for RAG (chunking and embedding)
            await ContentService._process_content_for_rag(content)

            # Index the content in the vector database
            from src.services.rag_service import RAGService
            rag_service = RAGService()
            await rag_service.index_content(content)

            logger.info(f"Successfully processed and indexed content for chapter {content.chapter_number}")
            return True

        except Exception as e:
            logger.error(f"Error in content ingestion pipeline: {e}")
            return False

    @staticmethod
    async def update_existing_content(content: BookContentDB) -> bool:
        """
        Update existing content in the RAG system
        """
        try:
            # Process the updated content for RAG
            await ContentService._process_content_for_rag(content)

            # Re-index the content in the vector database
            from src.services.rag_service import RAGService
            rag_service = RAGService()
            await rag_service.index_content(content)

            logger.info(f"Successfully updated and re-indexed content for chapter {content.chapter_number}")
            return True

        except Exception as e:
            logger.error(f"Error updating content in RAG system: {e}")
            return False

    @staticmethod
    async def search_content(db: AsyncSession, query: str, limit: int = 5) -> List[BookContentDB]:
        """
        Search for content based on query (for basic search, not RAG)
        """
        # This is a simple text search implementation
        # In a real implementation, this would use the vector database
        result = await db.execute(
            select(BookContentDB)
            .where(BookContentDB.content_text.contains(query))
            .limit(limit)
        )
        return result.scalars().all()