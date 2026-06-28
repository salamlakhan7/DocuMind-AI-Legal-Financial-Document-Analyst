# Application Architecture

## Django Project Layout

```text
config/
  settings.py
  urls.py
  asgi.py
  wsgi.py

apps/
  accounts/
  core/
  documents/
  chat/

services/
  pdf/
  rag/
  llm/

templates/
static/
media/
vector_store/
```

## App Responsibilities

### accounts

Owns login and logout views. Uses Django's built-in `User` model.

### core

Owns home, dashboard, and settings shell. Dashboard aggregates statistics from document, processing, embedding, and vector layers.

### documents

Owns document upload, listing, detail, deletion, retrieval test page, and answer test page. It contains document-related models.

### chat

Owns persistent document chat sessions and chat messages. It provides `/chat/`, `/chat/document/<id>/`, and `/history/`.

## Services Layer

Business logic lives in `services/` rather than views.

### services/pdf

- PDF validation
- PDF extraction
- PDF metadata
- Processing orchestration
- PDF exceptions

### services/rag

- Chunking
- Embeddings
- Embedding metadata management
- Vector store interface and Chroma implementation
- Semantic retrieval
- Prompt building
- Answer orchestration

### services/llm

- Groq client
- LLM exceptions

## Utility Layer

The project currently keeps utility behavior close to service packages. Examples include:

- chunk constants in `services/rag/constants.py`
- vector store abstraction in `services/rag/vector_store/base.py`
- domain exceptions inside service packages

## Separation of Concerns

Views handle HTTP concerns:

- authentication
- request parsing
- form submission
- messages
- response rendering

Services handle business behavior:

- processing
- extraction
- chunking
- embeddings
- retrieval
- prompt building
- LLM calls

Models represent persisted data and relationships.

Templates render state but do not perform business logic.

## Why Services Were Introduced

The RAG pipeline has multiple steps that should remain testable and replaceable. Keeping these steps in services allows:

- reuse between test pages and final chat
- easier background job migration
- cleaner view code
- isolated error handling
- easier replacement of ChromaDB or Groq

## Why Business Logic Is Outside Views

Business logic in views becomes difficult to test and tends to duplicate across pages. DocuMind uses services so the same answer pipeline supports:

- temporary answer page
- persistent chat
- future APIs
- future background workers

This design keeps views thin and the application easier to evolve.
