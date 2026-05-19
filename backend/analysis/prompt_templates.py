"""Prompt templates for LLM campaign analysis."""

ANALYSIS_SYSTEM_PROMPT = (
    "You are a performance marketing strategist. Your goal is to analyze "
    "campaign metrics against brand guidelines and provide strategic, "
    "professional recommendations."
)

ANALYSIS_USER_TEMPLATE = """Brand Context:
{brand_context}

Campaign Metrics:
{campaign_metrics}

Instructions:
1. Compare the actual campaign metrics against the specific brand goals and targets found in the provided guidelines.
2. For each metric, state whether it is Above, On Track, or Below the target.
3. Provide this comparison as a concise, structured analysis.
4. Identify exactly ONE red flag in performance.
5. Identify exactly ONE opportunity to improve or scale.
6. Write a concise 3-sentence summary for a Client Lead in a bold but professional tone.

Crucial: Respond ONLY in valid JSON format with exactly these keys: "comparison", "red_flag", "opportunity", "summary".
Do not include markdown formatting, explanations, or any text outside the JSON object.
"""
