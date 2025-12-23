from fastapi import APIRouter, Depends, HTTPException, status,Request
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
import datetime

from slowapi import Limiter
from slowapi.util import get_remote_address

from src.api.deps import get_db
from src.models.content import (
    BookContentCreate, BookContentUpdate, BookContentResponse
)
from src.services.content_service import ContentService
from src.services.rag_service import RAGService
from src.core.logging import logger


# Initialize rate limiter
limiter = Limiter(key_func=get_remote_address)
router = APIRouter()


@router.get("/content/chapters", response_model=dict)
@limiter.limit("50/minute") 
async def list_chapters(
    request: Request, # <--- **FIX 1**
    db: AsyncSession = Depends(get_db)
):
    
    """
    List available textbook chapters
    """
    try:
        contents = await ContentService.get_all_content(db)

        chapters = [
            {
                "chapter_number": content.chapter_number,
                "chapter_title": content.chapter_title,
                "version": content.version,
                "published_at": content.created_at,
                "content_length": len(content.content_text)
            }
            for content in contents
        ]

        # Sort by chapter number
        chapters.sort(key=lambda x: x["chapter_number"])

        return {"chapters": chapters}
    except Exception as e:
        logger.error(f"Error listing chapters: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list chapters"
        )


@router.get("/content/chapter/{chapter_number}", response_model=BookContentResponse)
@limiter.limit("100/minute") 
async def get_chapter(
    request: Request, # <--- **FIX 2**
    chapter_number: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Retrieve specific chapter content
    """
    try:
        content = await ContentService.get_content_by_chapter_number(db, chapter_number)
        if not content:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Chapter {chapter_number} not found"
            )

        return BookContentResponse(
            id=content.id,
            chapter_number=content.chapter_number,
            chapter_title=content.chapter_title,
            content_text=content.content_text,
            content_chunks=content.content_chunks,
            version=content.version,
            created_at=content.created_at,
            updated_at=content.updated_at
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving chapter {chapter_number}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve chapter"
        )


@router.post("/content/chapter", response_model=dict)
@limiter.limit("5/hour") 
async def create_chapter(
    request: Request, # <--- **FIX 3**
    content_create: BookContentCreate,
    db: AsyncSession = Depends(get_db)
):
    # ... baki code
    """
    Add or update textbook content (admin only)
    """
    try:
        # Check if chapter already exists
        existing_content = await ContentService.get_content_by_chapter_number(db, content_create.chapter_number)
        if existing_content:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Chapter {content_create.chapter_number} already exists"
            )

        # Create the content
        db_content = await ContentService.create_content(db, content_create)

        # Initialize RAG service and index the content
        rag_service = RAGService()
        await rag_service.index_content(db_content)

        return {
            "chapter_id": db_content.id,
            "chapter_number": db_content.chapter_number,
            "chapter_title": db_content.chapter_title,
            "version": db_content.version,
            "status": "published"
        }
    except ValueError as e:
        logger.error(f"Content validation error creating chapter: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating chapter: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create chapter"
        )


@router.put("/content/chapter/{chapter_number}", response_model=dict)
async def update_chapter(
    chapter_number: int,
    content_update: BookContentUpdate,
    db: AsyncSession = Depends(get_db)
):
    """
    Update existing chapter content with incremental update mechanism
    """
    try:
        # Use the incremental update method which handles RAG updates efficiently
        updated_content = await ContentService.incremental_update_content(db, chapter_number, content_update)
        if not updated_content:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Chapter {chapter_number} not found or update failed"
            )

        return {
            "chapter_id": updated_content.id,
            "chapter_number": updated_content.chapter_number,
            "chapter_title": updated_content.chapter_title,
            "version": updated_content.version,
            "status": "updated",
            "message": f"Chapter {chapter_number} updated incrementally without requiring full system rebuild"
        }
    except ValueError as e:
        logger.error(f"Content validation error updating chapter {chapter_number}: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating chapter {chapter_number}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update chapter"
        )


@router.delete("/content/chapter/{chapter_number}")
async def delete_chapter(
    chapter_number: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Delete chapter content
    """
    try:
        # Find the existing content by chapter number
        existing_content = await ContentService.get_content_by_chapter_number(db, chapter_number)
        if not existing_content:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Chapter {chapter_number} not found"
            )

        # Delete the content (this also removes from vector DB)
        success = await ContentService.delete_content(db, existing_content.id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete chapter"
            )

        return {"message": f"Chapter {chapter_number} deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting chapter {chapter_number}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete chapter"
        )