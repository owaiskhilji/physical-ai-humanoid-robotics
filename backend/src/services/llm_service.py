from typing import Dict, Any, List, Optional
import logging
import asyncio
import google.generativeai as genai
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage

from src.core.config import settings


class LLMService:
    """
    Service for interacting with Large Language Models
    Supports both direct Gemini API and LangChain structure for OpenAI compatibility
    """

    def __init__(self):
        # Configure Google Generative AI
        genai.configure(api_key=settings.GEMINI_API_KEY)

        # Initialize Gemini model
        self.gemini_model = genai.GenerativeModel('gemini-pro')

        # Initialize LangChain-compatible model for potential OpenAI compatibility
        self.chat_model = ChatGoogleGenerativeAI(
            model="gemini-pro",
            google_api_key=settings.GEMINI_API_KEY,
            temperature=0.1  # Lower temperature for more consistent textbook responses
        )

    async def generate_response(
        self,
        prompt: str,
        context: Optional[Dict[str, Any]] = None,
        max_tokens: int = 1000
    ) -> str:
        """
        Generate response using the configured LLM
        """
        try:
            # Create a structured prompt with context if provided
            full_prompt = self._build_prompt(prompt, context)

            # Use the Gemini model to generate content
            response = await self.gemini_model.generate_content_async(
                full_prompt,
                generation_config=genai.types.GenerationConfig(
                    max_output_tokens=max_tokens,
                    temperature=0.1
                )
            )

            # Return the text response
            return response.text if response.text else "I couldn't generate a response to your query."

        except Exception as e:
            logging.error(f"Error generating response: {e}")
            return "Sorry, I encountered an error while processing your request. Please try again."

    async def generate_response_with_context(
        self,
        user_query: str,
        context_texts: List[str],
        grounding_only: bool = True
    ) -> str:
        """
        Generate response with specific context, enforcing grounding
        """
        try:
            # Build context-aware prompt
            if context_texts:
                context_str = "\n\n".join(context_texts)

                if grounding_only:
                    prompt = f"""
                    You are an AI assistant for a Physical AI & Humanoid Robotics textbook.
                    Answer the user's question based ONLY on the provided context from the textbook.
                    Do not use any external knowledge or make up information.
                    If the context doesn't contain information to answer the question, say so explicitly.

                    Context from textbook:
                    {context_str}

                    User's question: {user_query}

                    Provide a helpful answer based only on the textbook content:
                    """
                else:
                    prompt = f"""
                    You are an AI assistant for a Physical AI & Humanoid Robotics textbook.
                    Use the provided context from the textbook to help answer the user's question.
                    You may supplement with general knowledge if the context is insufficient,
                    but prioritize information from the textbook.

                    Context from textbook:
                    {context_str}

                    User's question: {user_query}

                    Provide an answer that incorporates the textbook content where relevant:
                    """
            else:
                if grounding_only:
                    prompt = f"""
                    You are an AI assistant for a Physical AI & Humanoid Robotics textbook.
                    I cannot find relevant content in the textbook to answer your question.
                    Inform the user that I can only answer questions based on the textbook content.

                    User's question: {user_query}

                    Response:
                    """
                else:
                    # For non-grounded mode, allow general response
                    prompt = f"""
                    You are an AI assistant for a Physical AI & Humanoid Robotics textbook.
                    I don't have specific context for this question, but I'll do my best to help.

                    User's question: {user_query}

                    Response:
                    """

            # Generate response
            response = await self.gemini_model.generate_content_async(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    max_output_tokens=1000,
                    temperature=0.1
                )
            )

            return response.text if response.text else "I couldn't generate a response to your query."

        except Exception as e:
            logging.error(f"Error generating response with context: {e}")
            return "Sorry, I encountered an error while processing your request. Please try again."

    async def generate_response_with_selected_text(
        self,
        user_query: str,
        selected_text: str
    ) -> str:
        """
        Generate response specifically focused on selected text context
        """
        try:
            # Create a prompt that strictly focuses on the selected text
            prompt = f"""
            You are an AI assistant for a Physical AI & Humanoid Robotics textbook.
            Answer the user's question based ONLY on the provided selected text from the textbook.
            Do not use any other textbook content or external knowledge.
            If the selected text doesn't contain information to answer the question, say so explicitly.

            Selected Text:
            {selected_text}

            User's question: {user_query}

            Provide a helpful answer based only on the selected text:
            """

            # Generate response
            response = await self.gemini_model.generate_content_async(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    max_output_tokens=1000,
                    temperature=0.1  # Low temperature for consistency
                )
            )

            return response.text if response.text else "I couldn't generate a response based on the selected text."

        except Exception as e:
            logging.error(f"Error generating response with selected text: {e}")
            return "Sorry, I encountered an error while processing your request. Please try again."

    async def validate_response_grounding(
        self,
        response: str,
        context_texts: List[str],
        threshold: float = 0.3
    ) -> Dict[str, Any]:
        """
        Validate if the response is properly grounded in the provided context
        """
        try:
            # This is a simplified grounding validation
            # In a real implementation, we'd use more sophisticated methods
            response_lower = response.lower()
            context_parts = [ctx.lower() for ctx in context_texts]

            # Check if response contains key phrases from context
            grounding_score = 0.0
            if context_parts:
                for context in context_parts:
                    if len(context) > 10:  # Only check substantial context
                        # Simple overlap check
                        words_in_context = set(context.split()[:50])  # First 50 words
                        words_in_response = set(response_lower.split())

                        overlap = len(words_in_context.intersection(words_in_response))
                        max_possible = len(words_in_context)

                        if max_possible > 0:
                            word_overlap_score = overlap / max_possible
                            grounding_score = max(grounding_score, word_overlap_score)

            is_adequately_anchored = grounding_score >= threshold

            return {
                "is_anchored": is_adequately_anchored,
                "grounding_score": grounding_score,
                "threshold": threshold,
                "message": f"Response {'is' if is_adequately_anchored else 'is not'} adequately grounded in context"
            }

        except Exception as e:
            logging.error(f"Error validating response grounding: {e}")
            return {
                "is_anchored": False,
                "grounding_score": 0.0,
                "threshold": threshold,
                "message": "Error occurred during grounding validation"
            }

    def _build_prompt(self, base_prompt: str, context: Optional[Dict[str, Any]]) -> str:
        """
        Build a complete prompt with context
        """
        if context:
            # Add context to the prompt
            context_str = ""
            if "source" in context:
                context_str += f"Source: {context['source']}\n"
            if "content" in context:
                context_str += f"Content: {context['content']}\n"

            if context_str:
                return f"{context_str}\n{base_prompt}"

        return base_prompt

    async def health_check(self) -> bool:
        """
        Check if the LLM service is accessible
        """
        try:
            # Simple test query
            test_response = await self.gemini_model.generate_content_async(
                "Hello, this is a test. Respond with 'Healthy' only.",
                generation_config=genai.types.GenerationConfig(
                    max_output_tokens=10,
                    temperature=0
                )
            )

            return bool(test_response.text and "healthy" in test_response.text.lower())
        except Exception as e:
            logging.error(f"LLM health check failed: {e}")
            return False