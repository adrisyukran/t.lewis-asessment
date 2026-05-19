# Campaign Analyzer PoC

A lightweight, end-to-end proof-of-concept application that analyzes campaign reports against brand guidelines using **OCR**, **RAG (Retrieval-Augmented Generation)**, and **LLM-powered agentic reasoning**.

## Project Overview

The Campaign Analyzer allows users to upload a campaign report (PDF or image) and a brand guidelines text file. The system then:

1. **Extracts** text from the report using OCR (Tesseract) and PDF parsing.
2. **Chunks & embeds** the brand guidelines using `sentence-transformers` for semantic retrieval.
3. **Retrieves** relevant guideline sections based on the report content.
4. **Analyzes** the campaign report using an LLM (NanoGPT API) with the retrieved guidelines as context.
5. **Presents** the analysis results in a clean, interactive web UI.

## Prerequisites

Before running the project, ensure you have the following installed:

- **Python 3.8+**
- **Tesseract OCR**
  - Download and install from: https://github.com/UB-Mannheim/tesseract/wiki
  - Make sure `tesseract` is added to your system PATH.
- **Poppler (for pdf2image)**
  - Download from: https://github.com/oschwartz10612/poppler-windows/releases
  - Extract and add the `bin/` folder to your system PATH.

## Setup Instructions

1. **Clone or extract the project** to your local machine.

2. **Configure environment variables:**
   - Copy `.env.example` to `.env`:
     ```bash
     copy .env.example .env
     ```
   - Open `.env` and set your NanoGPT API key:
     ```
     NANOGPT_API_KEY=your_actual_api_key_here
     ```

3. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

## How to Run

On **Windows**, simply double-click the provided batch script:

```bash
run.bat
```

This script will:
- Verify Python is available.
- Install any missing dependencies from `requirements.txt`.
- Start the Flask backend in a new console window.
- Open the frontend (`frontend/index.html`) in your default web browser.

### Manual Run (Alternative)

If you prefer to run manually:

```bash
# Terminal 1: Start the backend
python backend/app.py

# Terminal 2: Serve the frontend (or simply open frontend/index.html in a browser)
```

The backend API will be available at `http://127.0.0.1:5000`.

## Project Structure

```
.
├── backend/
│   ├── app.py                  # Flask API entry point
│   ├── pipeline.py             # Orchestrator that wires the pipeline together
│   ├── analysis/
│   │   ├── llm_client.py       # NanoGPT API client
│   │   ├── models.py           # Pydantic data models for analysis
│   │   └── prompt_templates.py # LLM prompt templates
│   ├── extraction/
│   │   ├── ocr.py              # OCR and PDF text extraction
│   │   ├── parser.py           # Text parsing utilities
│   │   ├── cleanup.py          # Text cleanup / normalization
│   │   └── models.py           # Extraction data models
│   └── rag/
│       ├── chunker.py          # Guideline text chunking
│       ├── embedder.py         # sentence-transformers embedding
│       ├── retriever.py        # Semantic retrieval logic
│       └── context_builder.py  # Context assembly for LLM
├── frontend/
│   ├── index.html              # Main UI
│   ├── style.css               # Stylesheet
│   └── script.js               # Frontend logic
├── data/
│   ├── brand_guidelines.txt    # Sample brand guidelines
│   └── sample_report.pdf       # Sample campaign report
├── tests/
│   ├── test_phase2.py          # OCR / extraction tests
│   ├── test_phase3.py          # Chunking / embedding tests
│   ├── test_phase4.py          # Retrieval tests
│   ├── test_phase5.py          # LLM client tests
│   └── test_phase6.py          # End-to-end pipeline tests
├── requirements.txt            # Python dependencies
├── .env.example                # Example environment configuration
├── run.bat                     # Windows startup script
└── README.md                   # This file
```

## Technical Details

- **OCR & Extraction**: Uses `pytesseract` + `pdf2image` / `PyPDF2` to extract text from images and PDFs.
- **RAG**: Uses `sentence-transformers` (`all-MiniLM-L6-v2`) to embed brand guideline chunks and perform cosine-similarity retrieval.
- **LLM**: Uses the **NanoGPT API** for agentic reasoning, generating campaign analysis based on the report and retrieved guideline context.
- **Backend**: Flask with CORS enabled, exposing `/api/health` and `/api/analyze` endpoints.
- **Frontend**: Vanilla HTML/CSS/JS with a responsive drag-and-drop file upload interface.

## License

This project is a proof-of-concept for demonstration purposes.
