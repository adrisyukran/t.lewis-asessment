"""Data models for extracted campaign metrics."""

from dataclasses import dataclass
from typing import Optional


@dataclass
class CampaignMetrics:
    """Represents key performance metrics for a marketing campaign.

    All fields are optional because extraction may not find every metric
    in a given input.
    """

    spend: Optional[float] = None
    roas: Optional[float] = None
    ctr: Optional[float] = None
    impressions: Optional[int] = None
