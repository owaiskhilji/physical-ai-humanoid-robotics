from sqlalchemy import Column, Integer, String, Text, DateTime, JSON, Enum as SQLEnum
from sqlalchemy.sql import func
from src.core.database import Base
from pydantic import BaseModel, Field
from typing import Optional, List
from uuid import UUID, uuid4
import datetime


class BookContentDB(Base):
    """
    Database model for textbook content
    """
    __tablename__ = "book_content"

    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    chapter_number = Column(Integer, nullable=False)
    chapter_title = Column(String, nullable=False)
    content_text = Column(Text, nullable=False)
    content_chunks = Column(JSON, nullable=True)  # Array of text chunks for RAG
    version = Column(String, nullable=False, default="1.0")
    state = Column(SQLEnum("DRAFT", "PUBLISHED", "ARCHIVED", name="content_state_enum"), default="PUBLISHED", nullable=False)  # Content state management
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class BookContentCreate(BaseModel):
    chapter_number: int = Field(..., ge=1, le=6)
    chapter_title: str = Field(..., min_length=1)
    content_text: str = Field(..., min_length=100)
    version: str = "1.0"


class BookContentUpdate(BaseModel):
    chapter_title: Optional[str] = Field(None, min_length=1)
    content_text: Optional[str] = Field(None, min_length=100)
    version: Optional[str] = None


class BookContentResponse(BaseModel):
    id: str
    chapter_number: int
    chapter_title: str
    content_text: str
    content_chunks: Optional[List[str]] = None
    version: str
    created_at: datetime.datetime
    updated_at: Optional[datetime.datetime] = None

    class Config:
        from_attributes = True