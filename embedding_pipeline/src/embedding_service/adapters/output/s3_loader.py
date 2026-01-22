"""S3 File Loader Adapter - Implements DocumentLoaderPort using LangChain S3FileLoader."""

import logging
from typing import List
from langchain_community.document_loaders import S3FileLoader
from ...domain.entities import DocumentChunk
from ...domain.ports import DocumentLoaderPort
from ...domain.logic import generate_chunk_id

logger = logging.getLogger(__name__)


class S3FileLoaderAdapter(DocumentLoaderPort):
    """Adapter for loading documents from S3 using LangChain S3FileLoader."""
    
    def __init__(
        self,
        aws_access_key_id: str,
        aws_secret_access_key: str,
        region_name: str = "us-east-1"
    ):
        """
        Initialize the S3 file loader adapter.
        
        Args:
            aws_access_key_id: AWS access key ID
            aws_secret_access_key: AWS secret access key
            region_name: AWS region name
        """
        self.aws_access_key_id = aws_access_key_id
        self.aws_secret_access_key = aws_secret_access_key
        self.region_name = region_name
    
    def load_document(self, bucket: str, key: str) -> List[DocumentChunk]:
        """
        Load a document from S3 and return as chunks.
        
        Args:
            bucket: S3 bucket name
            key: S3 object key
            
        Returns:
            List of DocumentChunk objects
            
        Raises:
            Exception: If document cannot be loaded
        """
        logger.info(f"Loading document from s3://{bucket}/{key}")
        
        try:
            loader = S3FileLoader(
                bucket=bucket,
                key=key,
                aws_access_key_id=self.aws_access_key_id,
                aws_secret_access_key=self.aws_secret_access_key,
                region_name=self.region_name
            )
            
            # Load documents using LangChain loader
            documents = loader.load()
            
            if not documents:
                logger.warning(f"No content extracted from s3://{bucket}/{key}")
                return []
            
            # Convert LangChain documents to domain DocumentChunk entities
            chunks = []
            for idx, doc in enumerate(documents):
                chunk = DocumentChunk(
                    id=generate_chunk_id(key, idx),
                    content=doc.page_content,
                    source=key,
                    chunk_index=idx,
                    metadata={
                        **doc.metadata,
                        'bucket': bucket,
                        's3_key': key
                    }
                )
                chunks.append(chunk)
            
            logger.info(f"Successfully loaded {len(chunks)} chunks from s3://{bucket}/{key}")
            return chunks
            
        except Exception as e:
            logger.error(f"Failed to load document from s3://{bucket}/{key}: {e}")
            raise
