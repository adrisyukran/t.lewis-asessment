"""Build RAG context for LLM prompts from brand guidelines."""

from backend.extraction.models import CampaignMetrics
from backend.rag.chunker import chunk_guidelines
from backend.rag.embedder import embed_chunks
from backend.rag.retriever import retrieve_top_k


def build_rag_context(guidelines_path: str, campaign_metrics: CampaignMetrics) -> list[str]:
    """Load guidelines, chunk & embed them, then retrieve relevant snippets.

    Args:
        guidelines_path: Path to the plain-text brand-guidelines file.
        campaign_metrics: A CampaignMetrics instance used to build the query.

    Returns:
        A list of the top-k relevant guideline chunks.
    """
    with open(guidelines_path, "r", encoding="utf-8") as f:
        text = f.read()

    chunks = chunk_guidelines(text)
    embeddings = embed_chunks(chunks)

    # Build a synthetic query from whichever metrics are present.
    query_parts = ["performance targets"]
    if campaign_metrics.spend is not None:
        query_parts.append("Spend")
    if campaign_metrics.roas is not None:
        query_parts.append("ROAS")
    if campaign_metrics.ctr is not None:
        query_parts.append("CTR")
    if campaign_metrics.impressions is not None:
        query_parts.append("Impressions")

    query = "performance targets for " + ", ".join(query_parts[1:]) if len(query_parts) > 1 else " ".join(query_parts)

    top_chunks = retrieve_top_k(query, chunks, embeddings, k=4)
    return top_chunks
