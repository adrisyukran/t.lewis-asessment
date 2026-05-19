"""Pipeline orchestrator that wires together all backend phases."""

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

        return {
            "metrics": {
                "spend": metrics.spend,
                "roas": metrics.roas,
                "ctr": metrics.ctr,
                "impressions": metrics.impressions,
            },
            "context": context_chunks,
            "analysis": {
                "red_flag": analysis_result.red_flag,
                "opportunity": analysis_result.opportunity,
                "summary": analysis_result.summary,
            },
        }
