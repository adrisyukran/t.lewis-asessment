"""Embedding generation for the RAG pipeline using sentence-transformers."""

import numpy as np
from sentence_transformers import SentenceTransformer

# Load the lightweight all-MiniLM-L6-v2 model once at module import time.
# This avoids reloading the model on every call and improves performance.
_MODEL_NAME = "all-MiniLM-L6-v2"
_model: SentenceTransformer | None = None


def _get_model() -> SentenceTransformer:
    """Lazy-load the SentenceTransformer model."""
    global _model
    if _model is None:
        _model = SentenceTransformer(_MODEL_NAME)
    return _model


def embed_chunks(chunks: list[str]) -> np.ndarray:
    """Generate dense embeddings for a list of text chunks.

    Args:
        chunks: List of text chunks.

    Returns:
        A 2-D numpy array of shape (len(chunks), embedding_dim).
    """
    if not chunks:
        return np.array([])

    model = _get_model()
    embeddings = model.encode(chunks, convert_to_numpy=True)
    return embeddings
