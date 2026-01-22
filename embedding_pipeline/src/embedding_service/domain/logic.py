"""Domain logic - Pure business rules with no external dependencies."""

import uuid


def generate_chunk_id(source: str, chunk_index: int) -> str:
    """
    Generate a unique ID for a document chunk.
    
    Args:
        source: Source identifier (e.g., S3 key)
        chunk_index: Index of the chunk within the document
        
    Returns:
        Unique UUID string
    """
    return str(uuid.uuid4())


def validate_chunk(chunk: 'DocumentChunk') -> bool:
    """
    Validate a document chunk.
    
    Args:
        chunk: DocumentChunk to validate
        
    Returns:
        True if valid, False otherwise
    """
    if not chunk.id:
        return False
    if not chunk.content or len(chunk.content.strip()) == 0:
        return False
    if not chunk.source:
        return False
    if chunk.chunk_index < 0:
        return False
    return True
