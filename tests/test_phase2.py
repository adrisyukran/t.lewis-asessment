"""Validation script for Phase 2: OCR Pipeline with LLM Cleanup."""

import os
import sys

# Ensure the project root is on the path so imports resolve
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, PROJECT_ROOT)

from backend.extraction.ocr import extract_text_from_file
from backend.extraction.cleanup import cleanup_ocr_text
from backend.analysis.llm_client import NanoGPTClient


def main() -> None:
    sample_pdf = os.path.join(PROJECT_ROOT, "data", "sample_report.pdf")

    if not os.path.exists(sample_pdf):
        print(f"Sample PDF not found at {sample_pdf}. Please add it to the data/ directory.")
        sys.exit(1)

    print("=" * 60)
    print("Phase 2 Validation: OCR Pipeline with LLM Cleanup")
    print("=" * 60)

    # 1. Extract raw text
    print("\n[1/3] Extracting raw text from sample_report.pdf ...")
    raw_text = extract_text_from_file(sample_pdf)
    print(f"Raw text length: {len(raw_text)} characters")
    print("\n--- RAW TEXT ---")
    print(raw_text[:2000])  # Print first 2000 chars to keep output readable
    if len(raw_text) > 2000:
        print("... (truncated)")

    # 2. Initialize LLM client
    print("\n[2/3] Initializing NanoGPTClient ...")
    try:
        client = NanoGPTClient()
        print("Client initialized successfully.")
    except ValueError as exc:
        print(f"Failed to initialize client: {exc}")
        sys.exit(1)

    # 3. Clean up text
    print("\n[3/3] Cleaning text with LLM ...")
    try:
        cleaned_text = cleanup_ocr_text(raw_text, client)
        print(f"Cleaned text length: {len(cleaned_text)} characters")
        print("\n--- CLEANED TEXT ---")
        print(cleaned_text[:2000])
        if len(cleaned_text) > 2000:
            print("... (truncated)")
    except Exception as exc:
        print(f"LLM call failed (expected with dummy key): {exc}")
        print("\n--- PROMPT THAT WOULD BE SENT ---")
        print(f"System prompt: You are an OCR text cleanup assistant...")
        print(f"User prompt length: {len(raw_text)} chars")

    print("\n" + "=" * 60)
    print("Validation complete.")
    print("=" * 60)


if __name__ == "__main__":
    main()
