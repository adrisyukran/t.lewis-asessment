"""Validation tests for Phase 5: LLM Analysis (Agentic Reasoning)."""

import json
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

# Ensure project root is on PYTHONPATH.
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from backend.analysis.llm_client import NanoGPTClient
from backend.analysis.models import AnalysisResult
from backend.extraction.models import CampaignMetrics


def test_analyze_campaign() -> None:
    """Validate that NanoGPTClient.analyze_campaign returns a valid AnalysisResult."""
    # Mock CampaignMetrics object.
    metrics = CampaignMetrics(
        spend=1250.00,
        roas=3.8,
        ctr=1.05,
        impressions=45000,
    )

    # Sample RAG context string.
    rag_context = (
        "Brand Goal: ROAS must be above 4.0. CTR should be at least 1.5%. "
        "Spend should not exceed $1,000 per week. Impressions target is 50,000."
    )

    # Expected JSON response from the LLM.
    expected_json = {
        "comparison": (
            "ROAS: Below target (3.8 vs 4.0 goal). "
            "CTR: Below target (1.05% vs 1.5% goal). "
            "Spend: Above target ($1,250 vs $1,000 goal). "
            "Impressions: Below target (45,000 vs 50,000 goal)."
        ),
        "red_flag": "ROAS is below the 4.0 target at 3.8.",
        "opportunity": "Increase CTR by refining ad creative to reach the 1.5% benchmark.",
        "summary": (
            "Campaign spend is slightly over budget, and ROAS is under the 4.0 goal. "
            "CTR is also below the 1.5% threshold, indicating room for creative optimization. "
            "Focusing on ad creative improvements can unlock better engagement and return."
        ),
    }

    # Instantiate the client with a dummy key.
    client = NanoGPTClient(api_key="dummy-key-for-testing")

    # Patch the underlying OpenAI chat completion to avoid real API calls.
    mock_choice = MagicMock()
    mock_choice.message.content = json.dumps(expected_json)
    mock_response = MagicMock()
    mock_response.choices = [mock_choice]

    with patch.object(
        client.client.chat.completions,
        "create",
        return_value=mock_response,
    ):
        result = client.analyze_campaign(metrics, rag_context)

    print("=" * 60)
    print("AnalysisResult Output")
    print("=" * 60)
    print(f"comparison : {result.comparison}")
    print(f"red_flag   : {result.red_flag}")
    print(f"opportunity: {result.opportunity}")
    print(f"summary    : {result.summary}")
    print("=" * 60)

    # Validate type and fields.
    assert isinstance(result, AnalysisResult), "Result must be an AnalysisResult instance"
    assert hasattr(result, "comparison") and isinstance(result.comparison, str)
    assert hasattr(result, "red_flag") and isinstance(result.red_flag, str)
    assert hasattr(result, "opportunity") and isinstance(result.opportunity, str)
    assert hasattr(result, "summary") and isinstance(result.summary, str)

    # Validate content matches the mocked LLM output.
    assert result.comparison == expected_json["comparison"]
    assert result.red_flag == expected_json["red_flag"]
    assert result.opportunity == expected_json["opportunity"]
    assert result.summary == expected_json["summary"]

    print("\nAll assertions passed. Phase 5 LLM Analysis is working correctly.")


if __name__ == "__main__":
    test_analyze_campaign()
