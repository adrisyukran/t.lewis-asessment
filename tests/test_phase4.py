"""Validation tests for Phase 4: RAG Pipeline."""

import sys
from pathlib import Path

# Ensure project root is on PYTHONPATH.
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from backend.extraction.models import CampaignMetrics
from backend.rag.context_builder import build_rag_context


def test_build_rag_context() -> None:
    """End-to-end smoke test for the RAG context builder."""
    guidelines_path = PROJECT_ROOT / "data" / "brand_guidelines.txt"
    assert guidelines_path.exists(), f"Guidelines file not found: {guidelines_path}"

    metrics = CampaignMetrics(
        spend=1250.00,
        roas=3.8,
        ctr=1.05,
        impressions=45000,
    )

    context = build_rag_context(str(guidelines_path), metrics)

    print("=" * 60)
    print("Generated RAG Context")
    print("=" * 60)
    print(context)
    print("=" * 60)

    # Basic sanity checks.
    assert isinstance(context, str)
    assert len(context) > 0, "Context should not be empty"

    # Verify that relevant guideline snippets are present.
    # The synthetic query targets Spend, ROAS, CTR, and Impressions,
    # so we expect chunks mentioning ROAS, CTR, or performance thresholds.
    lower_context = context.lower()
    assert "roas" in lower_context, "Expected 'ROAS' in retrieved context"
    assert "ctr" in lower_context, "Expected 'CTR' in retrieved context"
    assert "spend" in lower_context or "budget" in lower_context, "Expected spend/budget references"

    print("\nAll assertions passed. Phase 4 RAG pipeline is working correctly.")


if __name__ == "__main__":
    test_build_rag_context()
