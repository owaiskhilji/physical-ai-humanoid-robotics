from fastapi import APIRouter, Depends, HTTPException, status,Request
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
import datetime

from slowapi import Limiter
from slowapi.util import get_remote_address

from src.api.deps import get_db
from src.models.chat import (
    ChatSessionCreate, ChatSessionResponse, ChatMessageCreate,
    ChatMessageResponse, ChatRequest, ChatResponse
)
from src.services.chat_service import ChatService
from src.services.rag_service import RAGService
from src.services.llm_service import LLMService
from src.core.logging import logger


# Initialize rate limiter
limiter = Limiter(key_func=get_remote_address)
router = APIRouter()

@router.post("/chat/start", response_model=ChatSessionResponse)
@limiter.limit("10/minute") 
async def start_chat_session(
    request: Request, # <--- **ISE ADD KAREN**
    session_create: ChatSessionCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Initialize a new chat session
    """
    print(f"DEBUG: Request received for user_id: {session_create.user_id}")
    # ... baki code waisa hi rahega    
    try:
        print("DEBUG: Attempting to create session in DB...")
        db_session = await ChatService.create_session(db, session_create)
        print(f"DEBUG: Session created successfully with ID: {db_session.id}")
        return ChatSessionResponse(
            id=db_session.id,
            session_title=db_session.session_title,
            is_active=db_session.is_active,
            created_at=db_session.created_at,
            updated_at=db_session.updated_at,
            expires_at=db_session.expires_at
        )
    except Exception as e:
        print(f"CRITICAL ERROR: {str(e)}")
        logger.error(f"Error creating chat session: {e}")
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create chat session"
        )


@router.post("/chat/message", response_model=ChatResponse)
@limiter.limit("30/minute") # Limit to 30 messages per minute per IP
async def send_message(
    request: Request, # <--- **ISE ADD KAREN**
    chat_request: ChatRequest,
    db: AsyncSession = Depends(get_db)
):
    # ... function logic
    try:
        print(f"DEBUG: Received message for session_id: {chat_request.session_id}")
        print(f"DEBUG: Received message for session_id: {chat_request.message}")
        # Determine if selected text mode should be used
        use_selected_text_mode = bool(chat_request.selected_text)
        print(f"DEBUG: use_selected_text_mode set to {use_selected_text_mode}")

        # Add user message to session
        user_message = await ChatService.add_message(
            db,
            ChatMessageCreate(
                session_id=chat_request.session_id,
                message=chat_request.message,
                selected_text=chat_request.selected_text,
                use_selected_text_mode=use_selected_text_mode
            )
        )

        # Initialize services
        rag_service = RAGService()
        llm_service = LLMService()

        # Generate response using RAG
        response_data = await rag_service.generate_response(
            query=chat_request.message,
            session_id=chat_request.session_id,
            selected_text=chat_request.selected_text,
            db=db,
            use_selected_text_mode=use_selected_text_mode
        )

        # Add assistant message to session
        await ChatService.add_assistant_message(
            db,
            chat_request.session_id,
            response_data["response"],
            str(response_data["context_sources"]),
            is_selected_text_mode=response_data.get("use_selected_text_mode", False)
        )

        return ChatResponse(
            session_id=response_data["session_id"],
            response="Selected text mode: " + response_data["response"] if response_data.get("use_selected_text_mode", False) else response_data["response"],
            context_sources=response_data["context_sources"],
            timestamp=datetime.datetime.utcnow()
        )
    except Exception as e:
        print(f"CRITICAL ERROR: {str(e)}")
        logger.error(f"Error processing chat message: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process chat message"
        )


@router.get("/chat/session/{session_id}", response_model=dict)
@limiter.limit("20/minute") # Limit to 20 session retrievals per minute per IP
async def get_chat_session(
    request: Request, # <--- **ISE ADD KAREN**
    session_id: str,
    db: AsyncSession = Depends(get_db)
):
    # ... function logic
    try:
        # Get session
        db_session = await ChatService.get_session_by_id(db, session_id)
        if not db_session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Session not found"
            )

        # Get messages
        messages = await ChatService.get_messages_by_session(db, session_id)

        return {
            "session_id": db_session.id,
            "session_title": db_session.session_title,
            "messages": [
                {
                    "id": msg.id,
                    "role": msg.role,
                    "content": msg.content,
                    "selected_text": msg.selected_text,
                    "timestamp": msg.created_at
                }
                for msg in messages
            ],
            "created_at": db_session.created_at,
            "updated_at": db_session.updated_at
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving chat session: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve chat session"
        )


@router.delete("/chat/session/{session_id}")
@limiter.limit("15/minute") # Limit to 15 session closures per minute per IP
async def close_chat_session(
    request: Request, # <--- **ISE ADD KAREN**
    session_id: str,
    db: AsyncSession = Depends(get_db)
      ):
    # ... function logic
    try:
        success = await ChatService.close_session(db, session_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Session not found"
            )

        return {"message": "Session closed successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error closing chat session: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to close chat session"
        )