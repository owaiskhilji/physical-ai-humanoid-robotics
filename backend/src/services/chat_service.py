from typing import List, Optional
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from uuid import uuid4

from src.models.chat import ChatSessionDB, ChatMessageDB, ChatSessionCreate, ChatMessageCreate
from src.core.logging import logger


class ChatService:
    """
    Service for managing chat sessions and messages
    """

    @staticmethod
    async def create_session(
        db: AsyncSession,
        session_create: ChatSessionCreate
    ) -> ChatSessionDB:
        """
        Create a new chat session
        """
        session_id = str(uuid4())
        session_title = session_create.session_title or f"Chat Session {session_id[:8]}"

        db_session = ChatSessionDB(
            id=session_id,
            user_id=session_create.user_id,
            session_title=session_title,
            is_active=True,
            expires_at=datetime.utcnow() + timedelta(hours=24)  # 24-hour session TTL
        )

        db.add(db_session)
        await db.commit()
        await db.refresh(db_session)

        logger.info(f"Created chat session: {session_id}")
        return db_session

    @staticmethod
    async def get_session_by_id(db: AsyncSession, session_id: str) -> Optional[ChatSessionDB]:
        """
        Get chat session by ID
        """
        result = await db.execute(
            select(ChatSessionDB).where(ChatSessionDB.id == session_id)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_session_with_messages(db: AsyncSession, session_id: str) -> Optional[ChatSessionDB]:
        """
        Get chat session with all its messages
        """
        result = await db.execute(
            select(ChatSessionDB)
            .where(ChatSessionDB.id == session_id)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def add_message(
        db: AsyncSession,
        message_create: ChatMessageCreate
    ) -> ChatMessageDB:
        """
        Add a message to a chat session
        """
        # Verify session exists and is active
        session = await ChatService.get_session_by_id(db, message_create.session_id)
        if not session or not session.is_active:
            raise ValueError("Session not found or inactive")

        db_message = ChatMessageDB(
            session_id=message_create.session_id,
            role="user",
            content=message_create.message,
            selected_text=message_create.selected_text,
            is_selected_text_mode=message_create.use_selected_text_mode
        )

        db.add(db_message)
        await db.commit()
        await db.refresh(db_message)

        # Update session timestamp
        session.updated_at = datetime.utcnow()
        await db.commit()

        logger.info(f"Added message to session {message_create.session_id}")
        return db_message

    @staticmethod
    async def add_assistant_message(
        db: AsyncSession,
        session_id: str,
        content: str,
        context_chunks: Optional[str] = None,
        is_selected_text_mode: bool = False
    ) -> ChatMessageDB:
        """
        Add an assistant message to a chat session
        """
        # Verify session exists and is active
        session = await ChatService.get_session_by_id(db, session_id)
        if not session or not session.is_active:
            raise ValueError("Session not found or inactive")

        db_message = ChatMessageDB(
            session_id=session_id,
            role="assistant",
            content=content,
            context_chunks=context_chunks,
            is_selected_text_mode=is_selected_text_mode
        )

        db.add(db_message)
        await db.commit()
        await db.refresh(db_message)

        # Update session timestamp
        session.updated_at = datetime.utcnow()
        await db.commit()

        logger.info(f"Added assistant message to session {session_id}")
        return db_message

    @staticmethod
    async def get_messages_by_session(db: AsyncSession, session_id: str) -> List[ChatMessageDB]:
        """
        Get all messages for a chat session
        """
        result = await db.execute(
            select(ChatMessageDB)
            .where(ChatMessageDB.session_id == session_id)
            .order_by(ChatMessageDB.created_at.asc())
        )
        return result.scalars().all()

    @staticmethod
    async def close_session(db: AsyncSession, session_id: str) -> bool:
        """
        Close and archive a chat session
        """
        result = await db.execute(
            select(ChatSessionDB).where(ChatSessionDB.id == session_id)
        )
        db_session = result.scalar_one_or_none()

        if not db_session:
            return False

        db_session.is_active = False
        await db.commit()

        logger.info(f"Closed chat session: {session_id}")
        return True

    @staticmethod
    async def cleanup_expired_sessions(db: AsyncSession) -> int:
        """
        Clean up expired chat sessions
        """
        result = await db.execute(
            select(ChatSessionDB)
            .where(ChatSessionDB.expires_at < datetime.utcnow())
            .where(ChatSessionDB.is_active == True)
        )
        expired_sessions = result.scalars().all()

        for session in expired_sessions:
            session.is_active = False

        await db.commit()
        logger.info(f"Cleaned up {len(expired_sessions)} expired sessions")
        return len(expired_sessions)