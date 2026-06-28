# AI Pipeline

## Pipeline Overview

```text
PDF
  |
  v
Extraction
  |
  v
Cleaning
  |
  v
Chunking
  |
  v
Embedding
  |
  v
Vector Storage
  |
  v
Retrieval
  |
  v
Prompt Building
  |
  v
Groq Generation
  |
  v
Response Formatting
  |
  v
Persistent Chat
```

## PDF

Users upload PDF files through the document upload form. Files are validated before processing.

## Extraction

`PDFTextExtractor` opens the uploaded file using `document.file.path` and uses `pypdf` to read pages. It extracts text page by page and returns a structured `PDFExtractionResult`.

## Cleaning

Extracted page text is normalized by stripping line whitespace and removing empty lines. Blank pages are represented as empty strings.

## Chunking

`TextChunker` splits text into chunks using:

1. paragraph boundaries
2. sentence boundaries
3. character boundaries

The default chunk size is 800 characters with 120 characters of overlap.

## Embedding

`EmbeddingService` uses Sentence Transformers with the default model `sentence-transformers/all-MiniLM-L6-v2`. It returns `EmbeddingResult` objects containing vectors and metadata.

## Vector Storage

`ChunkEmbeddingManager` stores metadata in PostgreSQL and sends vectors to the vector store abstraction. The Chroma implementation persists vectors locally.

## Retrieval

`DocumentRetriever` embeds the user's question, queries ChromaDB with a `document_id` filter, then loads matching chunk content from PostgreSQL.

## Prompt Building

`PromptBuilder` creates a strict grounded prompt. It includes:

- user question
- retrieved chunk context
- page and chunk references
- grounding rules
- legal and financial caution language

## Groq Generation

`GroqLLMClient` sends the prompt to Groq using `llama-3.3-70b-versatile` by default.

## Response Formatting

`DocumentAnswerService` returns:

- question
- answer
- sources
- model name
- retrieved chunk count

## Persistent Chat

The chat view stores:

- user message
- assistant answer
- source metadata
- model name

Messages are attached to a `ChatSession`.
