"""Pinecone Adapter - Implements VectorDatabasePort using Pinecone."""

import logging
from typing import List
from pinecone import Pinecone, ServerlessSpec
from ...domain.entities import EmbeddingVector
from ...domain.ports import VectorDatabasePort

logger = logging.getLogger(__name__)


class PineconeAdapter(VectorDatabasePort):
    """Adapter for vector database operations using Pinecone."""
    
    def __init__(
        self,
        api_key: str,
        index_name: str,
        dimension: int = 256,  # potion-base-4M produces 256-dimensional vectors
        cloud: str = "aws",
        region: str = "us-east-1"
    ):
        """
        Initialize the Pinecone adapter.
        
        Args:
            api_key: Pinecone API key
            index_name: Name of the Pinecone index
            dimension: Vector dimension (default: 256 for potion-base-4M)
            cloud: Cloud provider (default: aws)
            region: AWS region (default: us-east-1)
        """
        self.api_key = api_key
        self.index_name = index_name
        self.dimension = dimension
        self.cloud = cloud
        self.region = region
        
        logger.info(f"Initializing Pinecone adapter for index: {index_name}")
        self.pc = Pinecone(api_key=api_key)
        self._index = None
    
    @property
    def index(self):
        """Lazy load the index."""
        if self._index is None:
            # Get index info to get the host
            index_info = self.pc.describe_index(name=self.index_name)
            self._index = self.pc.Index(host=index_info.host)
            logger.info(f"Connected to Pinecone index: {self.index_name}")
        return self._index
    
    def upsert(self, vectors: List[EmbeddingVector]) -> int:
        """
        Upsert vectors into Pinecone.
        
        Args:
            vectors: List of EmbeddingVector objects to upsert
            
        Returns:
            Number of vectors successfully upserted
            
        Raises:
            Exception: If upsert fails
        """
        if not vectors:
            logger.warning("Empty vector list provided for upsert")
            return 0
        
        logger.info(f"Upserting {len(vectors)} vectors to Pinecone index: {self.index_name}")
        
        try:
            # Prepare vectors for Pinecone upsert
            # Format: [{"id": str, "values": list[float], "metadata": dict}, ...]
            pinecone_vectors = []
            for vec in vectors:
                pinecone_vector = {
                    "id": vec.id,
                    "values": vec.vector,
                    "metadata": vec.metadata
                }
                pinecone_vectors.append(pinecone_vector)
            
            # Upsert to Pinecone
            self.index.upsert(vectors=pinecone_vectors)
            
            logger.info(f"Successfully upserted {len(vectors)} vectors")
            return len(vectors)
            
        except Exception as e:
            logger.error(f"Failed to upsert vectors to Pinecone: {e}")
            raise
    
    def health_check(self) -> bool:
        """
        Check if Pinecone is healthy.
        
        Returns:
            True if healthy, False otherwise
        """
        try:
            # Try to describe the index
            self.pc.describe_index(name=self.index_name)
            return True
        except Exception as e:
            logger.error(f"Pinecone health check failed: {e}")
            return False
