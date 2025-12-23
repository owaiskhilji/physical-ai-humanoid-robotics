from typing import List, Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
import logging
import asyncio
import datetime
import google.generativeai as genai
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings

from src.core.config import settings
from src.core.vector_db import vector_db
from src.models.content import BookContentDB
from src.services.content_service import ContentService
from src.services.chat_service import ChatService


class RAGService:
    """
    Service for Retrieval-Augmented Generation functionality
    """

    def __init__(self):
        # Configure Google Generative AI
        genai.configure(api_key=settings.GEMINI_API_KEY)
        self.model = genai.GenerativeModel('gemini-2.5-flash')
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
        )

    async def get_relevant_content(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Get relevant content for a query using vector search
        """
        try:
            print(f"DEBUG: Starting vector search for query: {query}")
            # For now, we'll simulate embedding generation
            # In a real implementation, we'd use proper embedding models
            embedding = await self._generate_embedding(query)

            if embedding is None:
                print("DEBUG: Embedding generation failed, returning empty results")
                # Fallback to simple content search if embedding fails
                return []

            print(f"DEBUG: Embedding generated successfully, vector size: {len(embedding) if embedding else 0}")
            # Search for similar content in vector database
            results = await vector_db.search_similar(embedding, limit=limit)
            print(f"DEBUG: Vector search completed, found {len(results)} results")
            return results
        except Exception as e:
            print(f"DEBUG: Error in get_relevant_content: {e}")
            logging.error(f"Error in get_relevant_content: {e}")
            return []

    async def generate_response(
        self,
        query: str,
        session_id: str,
        selected_text: Optional[str] = None,
        db: AsyncSession = None,
        use_selected_text_mode: bool = False
    ) -> Dict[str, Any]:
        """
        Generate a response to a query using RAG
        """
        try:
            # Get relevant content based on mode
            if selected_text and use_selected_text_mode:
                # Selected text mode - use only the selected text
                context_sources = [
                    {
                        "text": selected_text,
                        "chapter_number": "Selected Text",
                        "chapter_title": "User Selected Text",
                        "score": 1.0
                    }
                ]
                context_text = selected_text
            else:
                # General mode - search for relevant content
                context_sources = await self.get_relevant_content(query)
                context_text = " ".join([source["text"] for source in context_sources])

            # Prepare the prompt for the LLM
            if context_text:
                if selected_text and use_selected_text_mode:
                    prompt = f"""
                    You are an AI assistant for a Physical AI & Humanoid Robotics textbook.
                    You are currently in SELECTED TEXT MODE.
                    Answer the user's question based ONLY on the provided selected text from the textbook.
                    Do not use any other textbook content or external knowledge.
                    If the selected text doesn't contain information to answer the question, say so explicitly.
                    At the end of your response, add a note: '[Response based on selected text only]'

                    Selected Text: {context_text}

                    User's question: {query}

                    Answer:
                    """
                else:
                    prompt = f"""
                    You are an AI assistant for a Physical AI & Humanoid Robotics textbook.
                    You are currently in GENERAL BOOK MODE.
                    Answer the user's question based ONLY on the provided context from the textbook.
                    If the context doesn't contain information to answer the question, say so explicitly.
                    At the end of your response, add a note: '[Response based on textbook content]'

                    Context: {context_text}

                    User's question: {query}

                    Answer:
                    """
            else:
                prompt = f"""
                You are an AI assistant for a Physical AI & Humanoid Robotics textbook.
                The system couldn't find relevant content in the textbook to answer the user's question.
                Inform the user that you can only answer questions based on the textbook content.

                User's question: {query}

                Answer:
                """

            # Print the final prompt being sent to the LLM
            print(f"DEBUG: Final prompt being sent to LLM: {prompt[:200]}...")  # Only first 200 chars to avoid spam

            # Generate response using Gemini with try-except to catch specific errors
            try:
                response = await self.model.generate_content_async(prompt)
                print("DEBUG: Gemini API call completed successfully")
            except Exception as llm_error:
                print(f"DEBUG: Error during Gemini API call: {llm_error}")
                print(f"DEBUG: Error type: {type(llm_error).__name__}")
                # Re-raise the exception to be caught by the outer exception handler
                raise llm_error

            # Extract text from response
            answer = response.text if response.text else "I couldn't find relevant information in the textbook to answer your question."

            # Validate grounding to ensure response is based on provided context
            is_properly_grounded = await self.validate_grounding(answer, context_sources, use_selected_text_mode)

            # If not properly grounded, modify the response to indicate the issue
            if not is_properly_grounded and use_selected_text_mode and context_sources:
                answer = f"Warning: The response may not be fully based on the selected text. {answer}"

            return {
                "session_id": session_id,
                "response": answer,
                "context_sources": context_sources,
                "timestamp": datetime.datetime.utcnow(),
                "use_selected_text_mode": use_selected_text_mode
            }

        except Exception as e:
            logging.error(f"Error generating response: {e}")
            return {
                "session_id": session_id,
                "response": "Sorry, I encountered an error while processing your request. Please try again.",
                "context_sources": [],
                "timestamp": datetime.datetime.utcnow(),
                "use_selected_text_mode": use_selected_text_mode
            }

    async def _generate_embedding(self, text: str) -> Optional[List[float]]:
        """
        Generate embedding for text using Google's embedding model
        """
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
            logging.error(f"Error generating embedding: {e}")
            return None

    async def index_content(self, content: BookContentDB) -> bool:
        """
        Index book content for RAG retrieval
        """
        try:
            # Split content into chunks
            chunks = self.text_splitter.split_text(content.content_text)

            success_count = 0
            for i, chunk in enumerate(chunks):
                # Generate embedding for the chunk
                embedding = await self._generate_embedding(chunk)
                if embedding:
                    # Add to vector database
                    payload = {
                        "text": chunk,
                        "chapter_number": content.chapter_number,
                        "chapter_title": content.chapter_title,
                        "chunk_index": i
                    }
                    await vector_db.add_embedding(content.id, embedding, payload)
                    success_count += 1

            logging.info(f"Indexed {success_count}/{len(chunks)} chunks for chapter {content.chapter_number}")
            return True
        except Exception as e:
            logging.error(f"Error indexing content: {e}")
            return False

    async def validate_grounding(self, response: str, context_sources: List[Dict[str, Any]], use_selected_text_mode: bool = False) -> bool:
        """
        Validate that the response is properly grounded in the provided context
        """
        # This is a basic validation - in a real implementation,
        # we'd use more sophisticated grounding validation
        if not context_sources:
            # If there's no context, the response should acknowledge this
            if "couldn't find relevant information" in response.lower() or \
               "based on the provided context" in response.lower():
                return True
            return False

        # For selected text mode, ensure the response is grounded in the selected text
        if use_selected_text_mode and context_sources:
            # In selected text mode, check that the response is grounded in the selected text
            selected_text = context_sources[0].get("text", "")
            if selected_text:
                # Check if the response content is related to the selected text
                # This is a basic check - in a real implementation, we'd use more sophisticated validation
                response_lower = response.lower()
                selected_text_lower = selected_text.lower()

                # Check if response contains key phrases from selected text
                words_from_selected = selected_text_lower.split()[:20]  # Take first 20 words as reference
                found_reference = any(word in response_lower for word in words_from_selected if len(word) > 3)

                return found_reference

        # For general mode, check if response references the context in some way
        response_lower = response.lower()
        for source in context_sources:
            if source.get("text", "").lower() in response_lower[:500]:  # Check first 500 chars
                return True

        return True  # Being permissive for now