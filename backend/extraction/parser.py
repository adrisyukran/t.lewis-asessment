"""Parser for extracting campaign metrics from raw text."""

import re
from typing import Optional

from backend.extraction.models import CampaignMetrics


def _normalize_number(text: str) -> str:
    """Remove currency symbols, commas, and percentage signs from a numeric string."""
    # Strip common currency symbols, commas, spaces, and percent signs
    cleaned = re.sub(r"[$€£,\s%]", "", text)
    return cleaned


def _extract_float(pattern: str, text: str) -> Optional[float]:
    """Search *text* with *pattern* (case-insensitive) and return the first capture group as float."""
    match = re.search(pattern, text, re.IGNORECASE)
    if not match:
        return None
    raw = match.group(1)
    cleaned = _normalize_number(raw)
    try:
        return float(cleaned)
    except ValueError:
        return None


def _extract_int(pattern: str, text: str) -> Optional[int]:
    """Search *text* with *pattern* (case-insensitive) and return the first capture group as int."""
    match = re.search(pattern, text, re.IGNORECASE)
    if not match:
        return None
    raw = match.group(1)
    cleaned = _normalize_number(raw)
    try:
        return int(float(cleaned))
    except ValueError:
        return None


def parse_campaign_metrics(text: str) -> CampaignMetrics:
    """Extract campaign metrics from *text* using case-insensitive regex.

    Normalization logic:
      - Currency symbols and commas are stripped.
      - Percentages (e.g. ``1.05%``) are converted to floats (``1.05``).
      - Missing metrics are set to ``None``.
    """
    # Patterns intentionally capture the numeric portion in group 1.
    spend = _extract_float(r"spend[:\s]+([$€£]?[\d,]+(?:\.\d+)?)", text)
    roas = _extract_float(r"roas[:\s]+([\d,]+(?:\.\d+)?)\s*x?", text)
    ctr = _extract_float(r"ctr[:\s]+([\d,]+(?:\.\d+)?)\s*%?", text)
    impressions = _extract_int(r"impressions[:\s]+([\d,]+)", text)

    return CampaignMetrics(
        spend=spend,
        roas=roas,
        ctr=ctr,
        impressions=impressions,
    )
