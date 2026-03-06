# PDF-AutoMem — Document Processing & Retrieval-Augmented Generation

**PDF-AutoMem** is a Retrieval-Augmented Generation (RAG) microservice for processing, embedding, and querying documents. It integrates document parsing, semantic search, knowledge graph construction, and LLM-based generation to provide advanced document intelligence.

Built with scalability in mind, it uses **PostgreSQL** for session management, **Qdrant** for vector storage, **Dgraph** for graph-based indexing, and **Celery** for asynchronous task processing. LLM calls are routed through [**FastRouter**](https://fastrouter.ai), enabling flexible model selection (Claude, GPT, Gemini, etc.) via a single OpenAI-compatible endpoint.

## Architecture

```
┌─────────────┐     ┌──────────────┐     ┌────────────┐
│  Streamlit   │────▶│   FastAPI     │────▶│  FastRouter │
│  Frontend    │     │   Backend     │     │  LLM API   │
└─────────────┘     └──────┬───────┘     └────────────┘
                           │
              ┌────────────┼────────────┐
              ▼            ▼            ▼
        ┌──────────┐ ┌──────────┐ ┌──────────┐
        │ PostgreSQL│ │  Qdrant  │ │  Celery  │
        │ (sessions)│ │ (vectors)│ │ + Redis  │
        └──────────┘ └──────────┘ └──────────┘
```

## Features

- 🗃 **Multi-Format Support**: `.pdf`, `.txt`, `.doc(x)`, `.xls(x)`, `.csv`, `.jpg`, `.png`, `.heic`, `.webp`, `.md`, `.rtf`, `.odt`, `.ods`
- 🔄 **Smart Conversion**: Documents → markdown via specialized parsers
- ✂️ **Chunking & Embedding**: 500-token segments, embeddings via FastRouter (OpenAI, Mistral, etc.)
- 🔍 **Hybrid Search**: Combines semantic vector search + entity graph relationships
- 💬 **Chat**: `/chat` endpoint with cited sources, Master Chat (all docs) & Category Chat
- 🧠 **Knowledge Graph**: Entity/relationship extraction via spaCy NLP
- 🚀 **Async OCR**: Celery-powered background processing for file uploads
- 🗂 **Categories**: Organize documents with custom category prompts
- 🔒 **API Key Auth**: All endpoints secured via `X-API-Key` header

## Quick Start

1. **Clone & configure**:
   ```bash
   git clone https://github.com/KshitijDatir/PDF-AutoMem.git
   cd PDF-AutoMem
   cp env_example .env
   ```

2. **Edit `.env`** — set your FastRouter API key and app auth key:
   ```env
   OPENAI_API_KEY=sk-v1-your_fastrouter_key
   OPENAI_BASE_URL=https://go.fastrouter.ai/api/v1
   OPENAI_CHAT_MODEL=anthropic/claude-sonnet-4-20250514
   APP_API_KEY=your_secret_app_key
   ```

3. **Launch**:
   ```bash
   docker compose up -d --build
   ```

4. **Access**:
   - FastAPI backend: `http://localhost:8000/api/docs`
   - Streamlit UI: `http://localhost:8501`
   - pgAdmin: `http://localhost:9012`

## Model Configuration

FastRouter routes requests to any supported provider. Configure via `.env`:

| Setting | Default | Description |
|---------|---------|-------------|
| `OPENAI_CHAT_MODEL` | `anthropic/claude-sonnet-4-20250514` | Chat/generation model |
| `OPENAI_EMBEDDING_MODEL` | `openai/text-embedding-3-small` | Embedding model |
| `OPENAI_BASE_URL` | `https://go.fastrouter.ai/api/v1` | FastRouter endpoint |

### Supported Embedding Models

| Provider | Model | Dimensions | Max Tokens | Price ($/1M tokens) |
|----------|-------|-----------|------------|---------------------|
| **OpenAI** | text-embedding-3-small | 1,536 | ~8,191 | $0.020 |
| **OpenAI** | text-embedding-3-large | 3,072 | ~8,191 | $0.130 |
| **Google** | gemini-embedding-001 | 3,072 | 2,048 | *Not disclosed* |
| **Mistral** | mistral-embed | 1,024 | 32,768 | $0.010 |

## Example Use Cases

- Extract payroll details from scanned PDFs and summarize hours worked
- Organize business documents into categories (inventory, payroll, utility bills) with category-specific prompts
- Query across all documents or specific categories for coherent, cited responses

## Tech Stack

| Component | Technology |
|-----------|-----------|
| Backend | FastAPI + Uvicorn |
| Frontend | Streamlit |
| LLM Routing | FastRouter (OpenAI-compatible) |
| Vector DB | Qdrant |
| Relational DB | PostgreSQL |
| Task Queue | Celery + Redis |
| OCR | ocrmypdf + Tesseract |
| NLP | spaCy (en_core_web_sm) |
| Containerization | Docker Compose |

## API Documentation

See [`api_docs.md`](./api_docs.md) for detailed endpoint usage.

## Current Limitations

- Large PDFs (>40 pages) may face context window limitations
- Multi-file processing tested up to 5 concurrent files
- Master Chat orchestration chain is still under development

## License

MIT License