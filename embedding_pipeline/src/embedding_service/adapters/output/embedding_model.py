"""Embedding Model Adapter - Implements EmbeddingModelPort using model2vec."""

import logging
from typing import List
from model2vec import StaticModel
from ...domain.ports import EmbeddingModelPort

logger = logging.getLogger(__name__)


class Model2VecAdapter(EmbeddingModelPort):
    """Adapter for generating embeddings using model2vec StaticModel."""
    
    def __init__(self, model_name: str = "minishlab/potion-base-4M"):
        """
        Initialize the embedding model adapter.
        
        Args:
            model_name: Name of the model to load (default: minishlab/potion-base-4M)
        """
        self.model_name = model_name
        self._model = None
        logger.info(f"Initializing embedding model: {model_name}")
    
    @property
    def model(self) -> StaticModel:
        """Lazy load the model."""
        if self._model is None:
            logger.info(f"Loading model: {self.model_name}")
            self._model = StaticModel.from_pretrained(self.model_name)
            logger.info(f"Model loaded successfully")
        return self._model
    
    def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for a list of texts.
        
        Args:
            texts: List of text strings to embed
            
        Returns:
            List of embedding vectors (each is a list of floats)
        """
        if not texts:
            logger.warning("Empty text list provided for embedding")
            return []
        
        logger.debug(f"Generating embeddings for {len(texts)} texts")
        
        try:
            # Use model2vec to encode texts
            embeddings = self.model.encode(texts)
            
            # Convert numpy array to list of lists
            if hasattr(embeddings, 'tolist'):
                embeddings_list = embeddings.tolist()
            else:
                embeddings_list = [list(emb) for emb in embeddings]
            
            logger.debug(f"Generated {len(embeddings_list)} embeddings with dimension {len(embeddings_list[0]) if embeddings_list else 0}")
            return embeddings_list
            
        except Exception as e:
            logger.error(f"Failed to generate embeddings: {e}")
            raise
