"""Pipeline orchestrator that wires together all backend phases."""

import re

from backend.analysis.llm_client import NanoGPTClient
from backend.extraction.cleanup import cleanup_ocr_text
from backend.extraction.ocr import extract_text_from_file
from backend.extraction.parser import parse_campaign_metrics
from backend.rag.context_builder import build_rag_context


class Orchestrator:
    """Orchestrates the end-to-end campaign analysis pipeline."""

    def __init__(self, llm_client: NanoGPTClient | None = None) -> None:
        """Initialize the orchestrator with an optional LLM client.

        Args:
            llm_client: An existing NanoGPTClient instance. If not provided,
                a new one is instantiated using environment variables.
        """
        self.llm_client = llm_client or NanoGPTClient()

    @staticmethod
    def extract_targets_from_guidelines(guidelines_text: str) -> dict:
        """Extract target metric values from brand guidelines text.

        Uses regex to find common target patterns such as
        "target ROAS is 4.0" or "CTR > 1.5%".

        Args:
            guidelines_text: The raw text of the brand guidelines.

        Returns:
            A dictionary mapping normalized metric names to their target
            values as floats (percentages are converted to decimals).
        """
        targets: dict[str, float] = {}

        # Pattern: "target <metric> is <value>" or "<metric> is <value>"
        # Also catches "target overall ROAS is 4.0"
        target_patterns = [
            (r"target\s+(?:overall\s+)?ROAS\s+is\s+(\d+\.?\d*)", "roas"),
            (r"minimum\s+acceptable\s+(?:Return\s+on\s+Ad\s+Spend\s+\(ROAS\)\s+)?(?:ROAS\s+)?is\s+(\d+\.?\d*)", "min_roas"),
            (r"ROAS\s+for\s+.*?(?:is|should\s+be)\s+(\d+\.?\d*)", "roas"),
            (r"achieve\s+(?:at\s+least\s+)?(\d+\.?\d*)[x×]", "roas"),
            (r"CTR\s+(?:is\s+)?[>\s]+(\d+\.?\d*)%?", "ctr"),
            (r"target\s+blended\s+CTR\s+is\s+(\d+\.?\d*)%?", "ctr"),
            (r"CTR\s+must\s+remain\s+above\s+(\d+\.?\d*)%?", "ctr"),
            (r"above\s+(\d+\.?\d*)%\s+for\s+display", "ctr"),
            (r"above\s+(\d+\.?\d*)%\s+for\s+search", "ctr"),
            (r"CPA\s+should\s+not\s+exceed\s+\$(\d+)", "cpa"),
        ]

        for pattern, key in target_patterns:
            for match in re.finditer(pattern, guidelines_text, re.IGNORECASE):
                value_str = match.group(1)
                try:
                    value = float(value_str)
                    # If the pattern explicitly includes a % sign or the key is CTR,
                    # store as decimal (e.g., 2.0% -> 0.02) only when the raw value
                    # looks like a percentage (> 1 usually implies percent points).
                    if key == "ctr" and value > 1:
                        value = value / 100.0
                    targets[key] = value
                except ValueError:
                    continue

        return targets

    def run_pipeline(self, report_path: str, guidelines_path: str) -> dict:
        """Execute the full analysis pipeline.

        Steps:
            1. Extract text from the report file (OCR).
            2. Clean up the extracted text using an LLM.
            3. Parse campaign metrics from the cleaned text.
            4. Build RAG context from the brand guidelines.
            5. Analyze the campaign using the LLM.

        Args:
            report_path: Path to the campaign report file (PDF or image).
            guidelines_path: Path to the brand guidelines text file.

        Returns:
            A dictionary containing:
                - "metrics": The parsed CampaignMetrics as a dict.
                - "targets": Extracted target values from the guidelines.
                - "context": The retrieved RAG context string.
                - "analysis": The final AnalysisResult as a dict.
        """
        # Phase 1: OCR extraction
        raw_text = extract_text_from_file(report_path)

        # Phase 2: LLM-based cleanup
        cleaned_text = cleanup_ocr_text(raw_text, self.llm_client)

        # Phase 3: Parse metrics
        metrics = parse_campaign_metrics(cleaned_text)

        # Phase 4: Build RAG context
        context_chunks = build_rag_context(guidelines_path, metrics)
        context_string = "\n\n".join(context_chunks)

        # Phase 5: LLM analysis
        analysis_result = self.llm_client.analyze_campaign(metrics, context_string)

        # Extract targets from the raw guidelines text
        with open(guidelines_path, "r", encoding="utf-8") as f:
            guidelines_text = f.read()
        targets = self.extract_targets_from_guidelines(guidelines_text)

        return {
            "metrics": {
                "spend": metrics.spend,
                "roas": metrics.roas,
                "ctr": metrics.ctr,
                "impressions": metrics.impressions,
            },
            "targets": targets,
            "context": context_chunks,
            "analysis": {
                "red_flag": analysis_result.red_flag,
                "opportunity": analysis_result.opportunity,
                "summary": analysis_result.summary,
            },
        }
