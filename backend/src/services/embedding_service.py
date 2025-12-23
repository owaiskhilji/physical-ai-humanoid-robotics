from typing import List, Optional
import logging
import google.generativeai as genai

from src.core.config import settings


class EmbeddingService:
    """
    Service for generating and managing text embeddings
    """

    def __init__(self):
        # Configure Google Generative AI
        genai.configure(api_key=settings.GEMINI_API_KEY)
        self.embedding_model = "models/embedding-001"

    async def generate_embedding(self, text: str) -> Optional[List[float]]:
        """
        Generate embedding for a single text
        """
        try:
            result = genai.embed_content(
                model=self.embedding_model,
                content=[text],  # API expects a list
                task_type="retrieval_document"
            )
            if result and 'embedding' in result and len(result['embedding']) > 0:
                return result['embedding'][0]  # Return first embedding
            return None
        except Exception as e:
            logging.error(f"Error generating embedding for text: {e}")
            return None

    async def generate_embeddings_batch(self, texts: List[str]) -> List[Optional[List[float]]]:
        """
        Generate embeddings for a batch of texts
        """
        embeddings = []
        for text in texts:
            embedding = await self.generate_embedding(text)
            embeddings.append(embedding)
        return embeddings

    async def calculate_similarity(self, embedding1: List[float], embedding2: List[float]) -> float:
        """
        Calculate cosine similarity between two embeddings
        """
        try:
            # Using numpy for cosine similarity calculation
            import numpy as np
            v1 = np.array(embedding1)
            v2 = np.array(embedding2)

            # Cosine similarity: (A · B) / (||A|| * ||B||)
            dot_product = np.dot(v1, v2)
            norm_v1 = np.linalg.norm(v1)
            norm_v2 = np.linalg.norm(v2)

            if norm_v1 == 0 or norm_v2 == 0:
                return 0.0

            similarity = dot_product / (norm_v1 * norm_v2)
            return float(similarity)
        except Exception as e:
            logging.error(f"Error calculating similarity: {e}")
            return 0.0

    async def find_most_similar_texts(
        self,
        query_embedding: List[float],
        candidate_embeddings: List[List[float]],
        candidate_texts: List[str],
        top_k: int = 5
    ) -> List[dict]:
        """
        Find the most similar texts to the query embedding
        """
        similarities = []
        for i, candidate_embedding in enumerate(candidate_embeddings):
            similarity = await self.calculate_similarity(query_embedding, candidate_embedding)
            similarities.append({
                'text': candidate_texts[i],
                'similarity': similarity,
                'index': i
            })

        # Sort by similarity in descending order and return top_k
        similarities.sort(key=lambda x: x['similarity'], reverse=True)
        return similarities[:top_k]