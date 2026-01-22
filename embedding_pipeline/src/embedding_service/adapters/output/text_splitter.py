"""Text Splitter Adapter - Implements TextSplitterPort using LangChain RecursiveCharacterTextSplitter."""

import logging
from typing import List
from langchain_text_splitters import RecursiveCharacterTextSplitter
from ...domain.entities import DocumentChunk
from ...domain.ports import TextSplitterPort
from ...domain.logic import generate_chunk_id

logger = logging.getLogger(__name__)


class RecursiveTextSplitterAdapter(TextSplitterPort):
    """Adapter for splitting text using LangChain RecursiveCharacterTextSplitter."""
    
    def __init__(
        self,
        chunk_size: int = 1000,
        chunk_overlap: int = 200,
        separators: List[str] = None
    ):
        """
        Initialize the text splitter adapter.
        
        Args:
            chunk_size: Maximum size of chunks in characters
            chunk_overlap: Number of characters to overlap between chunks
            separators: List of separators to use for splitting (default: ["\n\n", "\n", " ", ""])
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        
        if separators is None:
            separators = ["\n\n", "\n", " ", ""]
        
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=separators,
            is_separator_regex=False
        )
    
    def split_text(self, text: str, metadata: dict) -> List[DocumentChunk]:
        """
        Split text into chunks.
        
        Args:
            text: Text to split
            metadata: Metadata to attach to each chunk
            
        Returns:
            List of DocumentChunk objects
        """
        logger.debug(f"Splitting text into chunks (size={self.chunk_size}, overlap={self.chunk_overlap})")
        
        # Use LangChain splitter to split text
        text_chunks = self.splitter.split_text(text)
        
        # Convert to domain DocumentChunk entities
        chunks = []
        for idx, chunk_text in enumerate(text_chunks):
            chunk = DocumentChunk(
                id=generate_chunk_id(metadata.get('source', 'unknown'), idx),
                content=chunk_text,
                source=metadata.get('source', 'unknown'),
                chunk_index=idx,
                metadata={
                    **metadata,
                    'chunk_size': len(chunk_text)
                }
            )
            chunks.append(chunk)
        
        logger.debug(f"Split text into {len(chunks)} chunks")
        return chunks
