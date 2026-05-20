# Campaign Analyzer PoC

**Goal**: Automate the analysis of marketing campaign reports by extracting performance metrics from PDFs/images, retrieving relevant brand guidelines, and generating actionable insights using LLMs.

### The Problem It Solves

Marketing teams receive campaign reports in PDF or image formats that are time-consuming to manually review. Brand guidelines exist but are rarely consulted during quick assessments. This PoC demonstrates an automated pipeline that combines OCR, retrieval-augmented generation, and LLM reasoning to provide consistent, data-driven campaign analysis in seconds.

---

## The Pipeline

### Phase 1: OCR & Extraction

The extraction pipeline uses a **hybrid approach** to handle both digitally-created PDFs and scanned documents or images.

- **For PDFs**: The pipeline first attempts direct text extraction using [`PyPDF2`](backend/extraction/ocr.py:12). If the extracted text is empty or very short (< 50 characters), it falls back to **OCR on the first page** using [`pdf2image`](backend/extraction/ocr.py:12) + [`pytesseract`](backend/extraction/ocr.py:12) (Tesseract).
- **For Images**: PNG, JPG, and JPEG files are processed directly with [`pytesseract.image_to_string()`](backend/extraction/ocr.py:12).

This ensures that both selectable-text PDFs and image-based reports are handled without relying on cloud vision APIs.

**Extracted Metrics**: Spend, ROAS, CTR, Impressions.

---

### Phase 2: Contextual Logic (RAG)

The RAG pipeline grounds the LLM's analysis in the brand guidelines provided.

1. **Chunking**: Guidelines are split into semantic chunks by paragraph (double newlines) via [`backend/rag/chunker.py`](backend/rag/chunker.py:4). This preserves context within each section while keeping chunks small enough for embedding.
2. **Embedding**: All chunks are embedded using [`sentence-transformers/all-MiniLM-L6-v2`](backend/rag/embedder.py:20), a lightweight but high-quality model that produces 384-dimensional dense vectors. The model is loaded once and cached to avoid reloading on every call.
3. **Indexing & Retrieval**: Instead of a persistent vector database, the system uses an **in-memory FAISS index** built via LangChain's `FAISS` class. The index is ephemeral—created at runtime for each request and discarded after. A synthetic query is built from the extracted metrics, and the top-4 most similar chunks are retrieved using cosine similarity in [`backend/rag/retriever.py`](backend/rag/retriever.py:8).

---

### Phase 3: Agentic Reasoning

The analysis pipeline uses the [`NanoGPTClient`](backend/analysis/llm_client.py:19) class to call an OpenAI-compatible endpoint (NanoGPT).

The prompt injects:
1. The retrieved brand guideline context.
2. The parsed campaign metrics.

The LLM is instructed to respond **only in JSON** with exactly four keys:
- `comparison`: Metric-by-metric comparison against targets (Above / On Track / Below).
- `red_flag`: Exactly ONE identified issue with specific numbers and channels.
- `opportunity`: Exactly ONE improvement or scaling opportunity.
- `summary`: A bold, professional 3-sentence summary for a Client Lead.

This is intentionally **not** a multi-step agent loop. The design is one prompt → one response → structured result, making it fast, deterministic, and easy to debug.

---

## Design Philosophy

**Simple, not over-engineered.**

This project deliberately avoids complex patterns. Every architectural decision prioritizes simplicity:

- **No multi-step agent loops**: One prompt, one response; deterministic and fast.
- **No persistent vector databases**: Guidelines are chunked, embedded, and indexed at runtime using in-memory FAISS. This avoids infrastructure overhead, cost, and vendor lock-in for a PoC scope.
- **No cloud vision APIs**: The OCR stack (`PyPDF2`, `pdf2image`, `Tesseract`) is 100% local and open-source, eliminating per-page costs and network dependencies.
- **Minimal dependencies**: Core functionality relies on well-maintained open-source libraries.

The goal is a **proof-of-concept that demonstrates core competency**—the integration of OCR, RAG, and LLM reasoning—without over-engineering for production scale.

---

## Project Structure

```
.
├── backend/
│   ├── app.py                  # Flask API entry point
│   ├── pipeline.py             # Orchestrator
│   ├── analysis/
│   │   ├── llm_client.py       # NanoGPT API client
│   │   ├── models.py           # Pydantic data models
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
│   └── aurora_q1_report.pdf    # Sample campaign report
├── tests/
│   ├── test_phase2.py          # OCR / extraction tests
│   ├── test_phase3.py          # Chunking / embedding tests
│   ├── test_phase4.py          # Retrieval tests
│   ├── test_phase5.py          # LLM client tests
│   └── test_phase6.py          # End-to-end pipeline tests
├── requirements.txt            # Python dependencies
├── .env.example                # Example environment configuration
└── README.md                   # This file
```

---

## License

This project is a proof-of-concept for demonstration purposes.
