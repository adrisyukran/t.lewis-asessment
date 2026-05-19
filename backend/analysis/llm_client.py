"""Simple LLM client wrapper for NanoGPT."""

import json
import os

from dotenv import load_dotenv
from openai import OpenAI

from backend.analysis.models import AnalysisResult
from backend.analysis.prompt_templates import (
    ANALYSIS_SYSTEM_PROMPT,
    ANALYSIS_USER_TEMPLATE,
)

# Load environment variables from .env file
load_dotenv()


class NanoGPTClient:
    """Client for interacting with the NanoGPT API."""

    def __init__(self, api_key: str | None = None, base_url: str = "https://nano-gpt.com/api/v1") -> None:
        """Initialize the NanoGPT client.

        Args:
            api_key: API key for NanoGPT. If not provided, loads from NANOGPT_API_KEY env var.
            base_url: Base URL for the NanoGPT API.
        """
        key = api_key or os.getenv("NANOGPT_API_KEY")
        if not key:
            raise ValueError("NANOGPT_API_KEY is not set. Provide it via argument or .env file.")

        self.client = OpenAI(api_key=key, base_url=base_url)

    def complete(self, prompt: str, system_prompt: str = "") -> str:
        """Send a completion request to the NanoGPT API.

        Args:
            prompt: The user prompt.
            system_prompt: Optional system prompt to guide the model.

        Returns:
            The model's text response.
        """
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        response = self.client.chat.completions.create(
            model="minimax/minimax-m2.7",  # NanoGPT supports OpenAI-compatible models
            messages=messages,
            temperature=0.2,
            max_tokens=2048,
        )

        return response.choices[0].message.content.strip()

    def analyze_campaign(self, metrics, rag_context: str) -> AnalysisResult:
        """Analyze campaign metrics using the LLM and return a structured result.

        Args:
            metrics: A CampaignMetrics object (or any object with a readable representation).
            rag_context: The retrieved brand guideline context to ground the analysis.

        Returns:
            An AnalysisResult dataclass containing the comparison, red flag, opportunity, and summary.
        """
        campaign_metrics_str = str(metrics)
        user_prompt = ANALYSIS_USER_TEMPLATE.format(
            brand_context=rag_context,
            campaign_metrics=campaign_metrics_str,
        )

        raw_response = self.complete(
            prompt=user_prompt,
            system_prompt=ANALYSIS_SYSTEM_PROMPT,
        )

        # Strip potential markdown code fences.
        cleaned = raw_response.strip()
        if cleaned.startswith("```"):
            cleaned = cleaned.removeprefix("```").removeprefix("```json")
            cleaned = cleaned.removesuffix("```").strip()

        parsed = json.loads(cleaned)

        return AnalysisResult(
            comparison=parsed.get("comparison", "No comparison data available."),
            red_flag=parsed.get("red_flag", "No red flags identified."),
            opportunity=parsed.get("opportunity", "No opportunities identified."),
            summary=parsed.get("summary", "No summary available."),
        )
