"""LLM-based cleanup for OCR-extracted text."""

from backend.analysis.llm_client import NanoGPTClient

_SYSTEM_PROMPT = """You are an OCR text cleanup assistant. Clean up the following text that was extracted from an image using OCR:
1. Fix obvious OCR errors (e.g., 'rn' misread as 'm', '0' as 'O', 'l' as '1')
2. Fix punctuation and spacing issues
3. Correct obvious spelling mistakes caused by OCR
4. Maintain paragraph breaks and structure
5. Preserve the original meaning - do NOT add or remove content
6. Do NOT summarise or paraphrase
Return ONLY the cleaned text with no explanations or commentary."""


def cleanup_ocr_text(raw_text: str, llm_client: NanoGPTClient) -> str:
    """Clean up raw OCR text using an LLM.

    Args:
        raw_text: The text extracted by OCR.
        llm_client: An instance of NanoGPTClient.

    Returns:
        Cleaned text.
    """
    if not raw_text.strip():
        return ""

    prompt = f"Clean up this OCR text:\n\n{raw_text}"
    return llm_client.complete(prompt, system_prompt=_SYSTEM_PROMPT)
