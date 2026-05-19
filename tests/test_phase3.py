"""Validation script for Phase 3: Metric Parsing."""

import sys
from pathlib import Path

# Ensure the project root is on PYTHONPATH so backend imports resolve.
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from backend.extraction.parser import parse_campaign_metrics
from backend.extraction.models import CampaignMetrics


def test_parse_campaign_metrics() -> None:
    """Run assertions against a sample metric string."""
    sample_text = (
        "Spend: $12,450.00, ROAS: 3.2x, CTR: 1.05%, Impressions: 1,245,000"
    )

    metrics = parse_campaign_metrics(sample_text)

    print("Parsed CampaignMetrics:")
    print(f"  spend       = {metrics.spend!r}")
    print(f"  roas        = {metrics.roas!r}")
    print(f"  ctr         = {metrics.ctr!r}")
    print(f"  impressions = {metrics.impressions!r}")
    print()

    # Type checks
    assert isinstance(metrics, CampaignMetrics), "Result must be a CampaignMetrics instance"
    assert isinstance(metrics.spend, float), f"spend should be float, got {type(metrics.spend)}"
    assert isinstance(metrics.roas, float), f"roas should be float, got {type(metrics.roas)}"
    assert isinstance(metrics.ctr, float), f"ctr should be float, got {type(metrics.ctr)}"
    assert isinstance(metrics.impressions, int), f"impressions should be int, got {type(metrics.impressions)}"

    # Value checks
    assert metrics.spend == 12450.00, f"Expected spend=12450.00, got {metrics.spend}"
    assert metrics.roas == 3.2, f"Expected roas=3.2, got {metrics.roas}"
    assert metrics.ctr == 1.05, f"Expected ctr=1.05, got {metrics.ctr}"
    assert metrics.impressions == 1245000, f"Expected impressions=1245000, got {metrics.impressions}"

    print("All assertions passed.")


def test_missing_metrics() -> None:
    """Ensure missing metrics are returned as None."""
    partial_text = "Spend: $500"
    metrics = parse_campaign_metrics(partial_text)

    assert metrics.spend == 500.0
    assert metrics.roas is None
    assert metrics.ctr is None
    assert metrics.impressions is None

    print("Missing-metrics test passed.")


if __name__ == "__main__":
    test_parse_campaign_metrics()
    test_missing_metrics()
    print("\nPhase 3 validation complete.")
