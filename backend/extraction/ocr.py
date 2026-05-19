"""OCR pipeline for extracting text from PDF and image files."""

import os
from pathlib import Path

import pytesseract
from PIL import Image
from PyPDF2 import PdfReader
from pdf2image import convert_from_path


def extract_text_from_file(path: str) -> str:
    """Extract text from a file (PDF or image).

    For PDFs, attempts direct text extraction first. If the result is empty or
    very short, falls back to OCR on the first page. For images, runs OCR
    directly.

    Args:
        path: Path to the file.

    Returns:
        Extracted text as a single string.
    """
    file_path = Path(path)
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {path}")

    suffix = file_path.suffix.lower()

    if suffix == ".pdf":
        return _extract_text_from_pdf(path)

    if suffix in (".png", ".jpg", ".jpeg"):
        return _extract_text_from_image(path)

    raise ValueError(f"Unsupported file type: {suffix}")


def _extract_text_from_pdf(path: str) -> str:
    """Extract text from a PDF, falling back to OCR if needed."""
    reader = PdfReader(path)
    text_parts = []
    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text_parts.append(page_text)

    extracted = "\n".join(text_parts).strip()

    # If direct extraction yielded little or no text, fall back to OCR on the first page.
    if len(extracted) < 50:
        images = convert_from_path(path, first_page=1, last_page=1)
        if images:
            extracted = pytesseract.image_to_string(images[0]).strip()

    return extracted


def _extract_text_from_image(path: str) -> str:
    """Extract text from an image using Tesseract OCR."""
    image = Image.open(path)
    return pytesseract.image_to_string(image).strip()
