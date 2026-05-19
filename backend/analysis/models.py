"""Data models for LLM analysis results."""

from dataclasses import dataclass


@dataclass
class AnalysisResult:
    """Represents the structured output from the LLM campaign analysis.

    Attributes:
        comparison: Detailed comparison of actual metrics vs. brand goals.
        red_flag: Exactly one identified performance red flag.
        opportunity: Exactly one identified opportunity to improve or scale.
        summary: A concise 3-sentence client-facing summary.
    """

    comparison: str
    red_flag: str
    opportunity: str
    summary: str
