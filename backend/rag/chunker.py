"""Text chunking utilities for the RAG pipeline."""


def chunk_guidelines(text: str) -> list[str]:
    """Split guideline text into chunks by paragraphs.

    Paragraphs are delimited by blank lines (double newlines).
    Empty chunks are removed and whitespace is stripped from each chunk.

    Args:
        text: Raw guideline text.

    Returns:
        List of non-empty, stripped paragraph chunks.
    """
    paragraphs = text.split("\n\n")
    chunks = [chunk.strip() for chunk in paragraphs if chunk.strip()]
    return chunks
