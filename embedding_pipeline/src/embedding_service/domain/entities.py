"""Domain entities - Business objects with no external dependencies."""

from dataclasses import dataclass
from typing import Optional


@dataclass
class DocumentChunk:
    """Represents a chunk of a document."""
    id: str                    # UUID
    content: str
    source: str                # S3 key
    chunk_index: int
    metadata: dict


@dataclass
class EmbeddingVector:
    """Represents an embedding vector with metadata."""
    id: str
    vector: list[float]
    metadata: dict
