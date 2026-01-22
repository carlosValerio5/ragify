"""Domain ports - Abstract Base Classes defining contracts for external dependencies."""

from abc import ABC, abstractmethod
from typing import Optional
from .entities import DocumentChunk, EmbeddingVector


class MessageQueuePort(ABC):
    """Port for message queue operations (SQS)."""
    
    @abstractmethod
    def receive_messages(self, max_messages: int = 10) -> list[dict]:
        """
        Receive messages from the queue.
        
        Args:
            max_messages: Maximum number of messages to receive
            
        Returns:
            List of message dictionaries containing at least:
            - 'Body': message body (str)
            - 'ReceiptHandle': receipt handle for deletion (str)
            - 'MessageAttributes': optional message attributes (dict)
        """
        pass
    
    @abstractmethod
    def delete_message(self, receipt_handle: str) -> None:
        """
        Delete a message from the queue.
        
        Args:
            receipt_handle: Receipt handle from the received message
        """
        pass
    
    @abstractmethod
    def send_to_dlq(self, message_body: str, original_message_attributes: dict) -> None:
        """
        Send a failed message to the dead letter queue.
        
        Args:
            message_body: Original message body
            original_message_attributes: Original message attributes including error metadata
        """
        pass


class DocumentLoaderPort(ABC):
    """Port for loading documents from storage (S3)."""
    
    @abstractmethod
    def load_document(self, bucket: str, key: str) -> list[DocumentChunk]:
        """
        Load a document from storage and return as chunks.
        
        Args:
            bucket: S3 bucket name
            key: S3 object key
            
        Returns:
            List of DocumentChunk objects
            
        Raises:
            Exception: If document cannot be loaded
        """
        pass


class TextSplitterPort(ABC):
    """Port for splitting text into chunks."""
    
    @abstractmethod
    def split_text(self, text: str, metadata: dict) -> list[DocumentChunk]:
        """
        Split text into chunks.
        
        Args:
            text: Text to split
            metadata: Metadata to attach to each chunk
            
        Returns:
            List of DocumentChunk objects
        """
        pass


class EmbeddingModelPort(ABC):
    """Port for generating embeddings."""
    
    @abstractmethod
    def generate_embeddings(self, texts: list[str]) -> list[list[float]]:
        """
        Generate embeddings for a list of texts.
        
        Args:
            texts: List of text strings to embed
            
        Returns:
            List of embedding vectors (each is a list of floats)
        """
        pass


class VectorDatabasePort(ABC):
    """Port for vector database operations (swappable implementation)."""
    
    @abstractmethod
    def upsert(self, vectors: list[EmbeddingVector]) -> int:
        """
        Upsert vectors into the database.
        
        Args:
            vectors: List of EmbeddingVector objects to upsert
            
        Returns:
            Number of vectors successfully upserted
            
        Raises:
            Exception: If upsert fails
        """
        pass
    
    @abstractmethod
    def health_check(self) -> bool:
        """
        Check if the vector database is healthy.
        
        Returns:
            True if healthy, False otherwise
        """
        pass


class SecretsManagerPort(ABC):
    """Port for secrets management operations (swappable implementation)."""
    
    @abstractmethod
    def get_embedding_pipeline_credentials(self) -> dict[str, str]:
        """
        Retrieve all credentials needed for embedding pipeline.
        
        Expected keys:
        - aws_access_key_id
        - aws_secret_access_key
        - aws_region (optional, defaults to us-east-1)
        - sqs_queue_url
        - sqs_dlq_url
        - s3_bucket_name (optional)
        - pinecone_api_key
        - pinecone_index_name
        
        Returns:
            dict: Contains all credential fields
            
        Raises:
            Exception: If credentials cannot be retrieved
        """
        pass
