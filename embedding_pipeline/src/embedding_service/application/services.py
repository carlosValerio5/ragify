"""Application services - Orchestration of domain logic and ports."""

import logging
from typing import List
from ..domain.entities import DocumentChunk, EmbeddingVector
from ..domain.ports import (
    DocumentLoaderPort,
    TextSplitterPort,
    EmbeddingModelPort,
    VectorDatabasePort
)
from ..domain.logic import generate_chunk_id, validate_chunk

logger = logging.getLogger(__name__)


class EmbeddingPipelineService:
    """Orchestrates the embedding pipeline workflow."""
    
    def __init__(
        self,
        document_loader: DocumentLoaderPort,
        text_splitter: TextSplitterPort,
        embedding_model: EmbeddingModelPort,
        vector_database: VectorDatabasePort
    ):
        """
        Initialize the embedding pipeline service.
        
        Args:
            document_loader: Port for loading documents
            text_splitter: Port for splitting text
            embedding_model: Port for generating embeddings
            vector_database: Port for storing vectors
        """
        self.document_loader = document_loader
        self.text_splitter = text_splitter
        self.embedding_model = embedding_model
        self.vector_database = vector_database
    
    def process_file(self, bucket: str, s3_key: str) -> int:
        """
        Process a single file through the embedding pipeline.
        
        Steps:
        1. Load document from S3
        2. Split into chunks
        3. Generate embeddings
        4. Upsert to vector database
        
        Args:
            bucket: S3 bucket name
            s3_key: S3 object key
            
        Returns:
            Number of vectors successfully processed
            
        Raises:
            Exception: If any step fails
        """
        logger.info(f"Processing file: s3://{bucket}/{s3_key}")
        
        # Step 1: Load document from S3
        logger.debug(f"Loading document from s3://{bucket}/{s3_key}")
        document_chunks = self.document_loader.load_document(bucket, s3_key)
        logger.info(f"Loaded {len(document_chunks)} chunks from document")
        
        if not document_chunks:
            logger.warning(f"No chunks extracted from s3://{bucket}/{s3_key}")
            return 0
        
        # Step 2: Validate and prepare chunks
        # S3FileLoader returns DocumentChunk objects, validate them
        all_chunks: List[DocumentChunk] = []
        for chunk in document_chunks:
            if validate_chunk(chunk):
                all_chunks.append(chunk)
            else:
                # If chunk is invalid, log warning and skip
                logger.warning(f"Invalid chunk skipped: {chunk.id}")
        
        if not all_chunks:
            logger.warning(f"No valid chunks after processing s3://{bucket}/{s3_key}")
            return 0
        
        # Step 3: Generate embeddings
        logger.debug(f"Generating embeddings for {len(all_chunks)} chunks")
        texts = [chunk.content for chunk in all_chunks]
        embeddings = self.embedding_model.generate_embeddings(texts)
        
        if len(embeddings) != len(all_chunks):
            raise ValueError(
                f"Embedding count mismatch: {len(embeddings)} embeddings for {len(all_chunks)} chunks"
            )
        
        # Step 4: Create embedding vectors and upsert
        logger.debug(f"Creating {len(embeddings)} embedding vectors")
        embedding_vectors = []
        for chunk, embedding in zip(all_chunks, embeddings):
            vector = EmbeddingVector(
                id=chunk.id,
                vector=embedding,
                metadata={
                    **chunk.metadata,
                    'source': chunk.source,
                    'chunk_index': chunk.chunk_index
                }
            )
            embedding_vectors.append(vector)
        
        logger.debug(f"Upserting {len(embedding_vectors)} vectors to database")
        count = self.vector_database.upsert(embedding_vectors)
        logger.info(f"Successfully processed {count} vectors from s3://{bucket}/{s3_key}")
        
        return count
