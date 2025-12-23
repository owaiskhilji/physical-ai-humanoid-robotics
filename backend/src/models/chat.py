from sqlalchemy import Column, String, Text, DateTime, Boolean, ForeignKey, Enum as SQLEnum
from sqlalchemy.sql import func
from src.core.database import Base
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from uuid import UUID, uuid4
import datetime


class ChatSessionDB(Base):
    """
    Database model for chat sessions
    """
    __tablename__ = "chat_sessions"

    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    user_id = Column(String, nullable=True)  # Optional for anonymous users
    session_title = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    expires_at = Column(DateTime(timezone=True))  # TTL for session cleanup


class ChatMessageDB(Base):
    """
    Database model for chat messages
    """
    __tablename__ = "chat_messages"

    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    session_id = Column(String, ForeignKey("chat_sessions.id"), nullable=False)
    role = Column(SQLEnum("user", "assistant", name="role_enum"), nullable=False)
    content = Column(Text, nullable=False)
    selected_text = Column(Text, nullable=True)  # For selected text mode
    context_chunks = Column(String, nullable=True)  # JSON string of context chunks used
    is_selected_text_mode = Column(Boolean, default=False)  # Flag to indicate if this was in selected text mode
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class ChatSessionCreate(BaseModel):
    user_id: Optional[str] = None
    session_title: Optional[str] = Field(None, max_length=100)


class ChatSessionResponse(BaseModel):
    id: str
    session_title: str
    is_active: bool
    created_at: datetime.datetime
    updated_at: Optional[datetime.datetime] = None
    expires_at: Optional[datetime.datetime]

    class Config:
        from_attributes = True


class ChatMessageCreate(BaseModel):
    session_id: str
    message: str = Field(..., min_length=1)
    selected_text: Optional[str] = None
    use_selected_text_mode: bool = False  # Whether to use selected text mode


class ChatMessageResponse(BaseModel):
    id: str
    session_id: str
    role: str
    content: str
    selected_text: Optional[str] = None
    is_selected_text_mode: bool = False
    created_at: datetime.datetime

    class Config:
        from_attributes = True


class ChatResponse(BaseModel):
    session_id: str
    response: str
    context_sources: List[Dict[str, Any]]
    timestamp: datetime.datetime


class ChatRequest(BaseModel):
    session_id: str
    message: str = Field(..., min_length=1)
    selected_text: Optional[str] = None