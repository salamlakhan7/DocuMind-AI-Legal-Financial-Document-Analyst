# System Architecture

## End-to-End Flow

```text
User
  |
  v
Authentication
  |
  v
Dashboard
  |
  v
Document Upload
  |
  v
PDF Processing
  |
  v
Chunk Generation
  |
  v
Embedding Generation
  |
  v
ChromaDB
  |
  v
Semantic Retrieval
  |
  v
Prompt Builder
  |
  v
Groq LLM
  |
  v
Grounded Answer
  |
  v
Persistent Chat
```

## Layer Responsibilities

### User

The user interacts through Django templates. All document and chat operations require authentication.

### Authentication

Django's built-in authentication controls login and logout. Views that access dashboard, documents, retrieval, and chat use login enforcement.

### Dashboard

The dashboard aggregates document, processing, chunk, embedding, and vector statistics. It does not perform processing logic.

### Document Upload

The document upload view accepts a title and PDF file. Validation rejects non-PDF, unreadable, empty, or oversized files.

### PDF Processing

The PDF processor orchestrates:

- validation
- text extraction
- chunking
- embedding generation
- vector storage
- status updates

The processor updates `Document` and `DocumentProcessing` records.

### Chunk Generation

The chunking service splits extracted text into retrieval-sized chunks. It prefers paragraph and sentence boundaries and uses overlap.

### Embedding Generation

Sentence Transformers generate normalized vectors for chunks. PostgreSQL stores only embedding metadata, not vector values.

### ChromaDB

ChromaDB stores vectors persistently in the local `vector_store/` directory. Each vector includes metadata for document, chunk, page, user, and title.

### Semantic Retrieval

The retriever embeds a question, queries the vector store, filters by selected `document_id`, then loads chunk content from PostgreSQL.

### Prompt Builder

The prompt builder creates a strict grounded prompt using only retrieved chunks. It instructs the model to avoid unsupported claims.

### Groq LLM

The Groq client sends the grounded prompt to the configured Groq model and returns answer text only.

### Grounded Answer

The answer service returns the question, answer, model name, retrieved count, and source previews.

### Persistent Chat

The chat app stores user questions and assistant answers in `ChatMessage` records under a `ChatSession`.

## Runtime Architecture

```text
Django Templates
      |
      v
Class-Based Views
      |
      v
Domain Services
      |
      +--> PostgreSQL / SQLite
      +--> Local Media Storage
      +--> ChromaDB
      +--> Groq API
```

## Storage Architecture

```text
PostgreSQL / SQLite
  - users
  - document metadata
  - processing metadata
  - chunks
  - embedding metadata
  - chat sessions
  - chat messages

Media Storage
  - uploaded PDFs

ChromaDB
  - vector embeddings
  - vector metadata
```
