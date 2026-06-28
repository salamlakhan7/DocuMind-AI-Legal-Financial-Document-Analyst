class EmbeddingError(Exception):
    """Raised when chunk embedding generation fails."""


class EmbeddingModelError(EmbeddingError):
    """Raised when an embedding model cannot be loaded."""


class VectorStoreError(Exception):
    """Raised when vector store operations fail."""


class RetrievalError(Exception):
    """Raised when semantic retrieval cannot be completed."""
