from qdrant_client import QdrantClient
from qdrant_client.http import models
from typing import List, Dict, Any, Optional
import logging
from uuid import uuid4

from src.core.config import settings


class VectorDB:
    """
    Vector database client for Qdrant
    """
    def __init__(self):
        if settings.QDRANT_URL:
            self.client = QdrantClient(
                url=settings.QDRANT_URL,
                api_key=settings.QDRANT_API_KEY,
                prefer_grpc=True
            )
        else:
            # For development, can use local instance
            self.client = QdrantClient(":memory:")  # In-memory for development

        self.collection_name = "physical-ai"
        self.vector_size = 768  # Default size for text-embedding-004 or similar

    async def init_collection(self):
        """
        Initialize the Qdrant collection for book content embeddings
        """
        try:
            # Check if collection exists
            collections = self.client.get_collections()
            collection_names = [c.name for c in collections.collections]

            if self.collection_name not in collection_names:
                # Create collection
                self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=models.VectorParams(
                        size=self.vector_size,
                        distance=models.Distance.COSINE
                    )
                )
                logging.info(f"Created Qdrant collection: {self.collection_name}")
            else:
                logging.info(f"Qdrant collection {self.collection_name} already exists")

        except Exception as e:
            logging.error(f"Error initializing Qdrant collection: {e}")
            raise

    async def add_embedding(self, content_id: str, vector: List[float], payload: Dict[str, Any]):
        """
        Add a vector embedding to the collection
        """
        try:
            point_id = str(uuid4())
            self.client.upsert(
                collection_name=self.collection_name,
                points=[
                    models.PointStruct(
                        id=point_id,
                        vector=vector,
                        payload={
                            "content_id": content_id,
                            **payload
                        }
                    )
                ]
            )
            return point_id
        except Exception as e:
            logging.error(f"Error adding embedding: {e}")
            raise

    async def search_similar(self, query_vector: List[float], limit: int = 5) -> List[Dict[str, Any]]:
        """
        Search for similar content based on vector similarity
        """
        try:
            print(f"DEBUG: Starting vector search in collection: {self.collection_name}")
            print(f"DEBUG: Query vector size: {len(query_vector) if query_vector else 0}, limit: {limit}")

            # Using the query_points method for vector similarity search (Qdrant API)
            search_results = self.client.query_points(
                collection_name=self.collection_name,
                query=query_vector,
                limit=limit
            )

            # Handle the QueryResponse object - access the points inside
            points = search_results.points if hasattr(search_results, 'points') else search_results
            print(f"DEBUG: Qdrant search completed, raw results count: {len(points)}")

            processed_results = [
                {
                    "content_id": point.payload.get("content_id") if point.payload else None,
                    "text": point.payload.get("text", "") if point.payload else "",
                    "chapter_number": point.payload.get("chapter_number") if point.payload else None,
                    "chapter_title": point.payload.get("chapter_title") if point.payload else None,
                    "score": point.score
                }

                for point in points
            ]

            print(f"DEBUG: Processed {len(processed_results)} results from vector search")
            return processed_results
        except AttributeError as e:
            # If search method doesn't exist, try the legacy method
            print(f"DEBUG: Search method not available, trying legacy approach: {e}")
            logging.error(f"Search method not available: {e}")
            # Fallback to returning empty results to avoid breaking the system
            return []
        except Exception as e:
            print(f"DEBUG: Error searching similar content: {e}")
            logging.error(f"Error searching similar content: {e}")
            raise

    async def delete_by_content_id(self, content_id: str):
        """
        Delete all embeddings associated with a content ID
        """
        try:
            # Find all points with this content_id using query_points method
            search_results = self.client.query_points(
                collection_name=self.collection_name,
                query_filter=models.Filter(
                    must=[
                        models.FieldCondition(
                            key="content_id",
                            match=models.MatchValue(value=content_id)
                        )
                    ]
                ),
                limit=10000  # Assuming we don't have more than 10k chunks per content
            )

            # Handle the QueryResponse object - access the points inside
            points = search_results.points if hasattr(search_results, 'points') else search_results
            point_ids = [point.id for point in points]

            if point_ids:
                self.client.delete(
                    collection_name=self.collection_name,
                    points_selector=models.PointIdsList(
                        points=point_ids
                    )
                )
        except AttributeError:
            # If query_points method doesn't exist, try the legacy query method
            try:
                search_results = self.client.query(
                    collection_name=self.collection_name,
                    query_filter=models.Filter(
                        must=[
                            models.FieldCondition(
                                key="content_id",
                                match=models.MatchValue(value=content_id)
                            )
                        ]
                    ),
                    limit=10000
                )

                # Handle the QueryResponse object - access the points inside
                points = search_results.points if hasattr(search_results, 'points') else search_results
                point_ids = [point.id for point in points]

                if point_ids:
                    self.client.delete(
                        collection_name=self.collection_name,
                        points_selector=models.PointIdsList(
                            points=point_ids
                        )
                    )
            except AttributeError:
                # If query method also doesn't exist, try the legacy search method
                try:
                    search_results = self.client.search(
                        collection_name=self.collection_name,
                        query_filter=models.Filter(
                            must=[
                                models.FieldCondition(
                                    key="content_id",
                                    match=models.MatchValue(value=content_id)
                                )
                            ]
                        ),
                        limit=10000
                    )

                    # Handle the QueryResponse object - access the points inside
                    points = search_results.points if hasattr(search_results, 'points') else search_results
                    point_ids = [point.id for point in points]

                    if point_ids:
                        self.client.delete(
                            collection_name=self.collection_name,
                            points_selector=models.PointIdsList(
                                points=point_ids
                            )
                        )
                except AttributeError:
                    # If search method also doesn't exist, skip deletion to avoid breaking the system
                    logging.warning("Query/query_points/search methods not available, skipping deletion by content ID")
                    return
        except Exception as e:
            logging.error(f"Error deleting embeddings by content_id: {e}")
            raise


# Global instance
vector_db = VectorDB()