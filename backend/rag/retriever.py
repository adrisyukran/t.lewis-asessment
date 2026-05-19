"""Retrieval utilities for the RAG pipeline."""

import numpy as np

from backend.rag.embedder import embed_chunks


def retrieve_top_k(
    query: str,
    chunks: list[str],
    embeddings: np.ndarray,
    k: int = 4,
) -> list[str]:
    """Retrieve the top-k most relevant chunks for a query using cosine similarity.

    Args:
        query: The user or synthetic query string.
        chunks: List of text chunks corresponding to the embeddings rows.
        embeddings: 2-D numpy array of shape (n_chunks, embedding_dim).
        k: Number of top chunks to return (default 4).

    Returns:
        List of the top-k most similar chunks, ordered by descending similarity.
    """
    if embeddings.size == 0 or not chunks:
        return []

    # Embed the query using the same model.
    query_embedding = embed_chunks([query])
    if query_embedding.size == 0:
        return []

    # Compute cosine similarity via dot product of L2-normalised vectors.
    # Normalise embeddings.
    embeddings_norm = embeddings / np.linalg.norm(embeddings, axis=1, keepdims=True)
    query_norm = query_embedding / np.linalg.norm(query_embedding, axis=1, keepdims=True)

    similarities = np.dot(embeddings_norm, query_norm.T).flatten()

    # Get indices of top-k similarities (descending).
    top_k_indices = np.argsort(similarities)[::-1][:k]

    return [chunks[i] for i in top_k_indices]
