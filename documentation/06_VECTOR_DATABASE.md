# Vector Database

## Why ChromaDB

ChromaDB is used because it provides a simple persistent vector database suitable for local development and early production validation. It supports:

- local persistence
- metadata filtering
- vector upsert
- similarity query
- collection management

## Collection Design

DocuMind uses one collection:

```text
documind
```

Vectors are stored per document chunk.

## Metadata

Each vector includes:

- `document_id`
- `chunk_id`
- `page_number`
- `chunk_index`
- `user_id`
- `title`

## Chunk IDs

Vector IDs use the format:

```text
chunk-<chunk_id>
```

This maps Chroma entries back to PostgreSQL `DocumentChunk` records.

## User Isolation

User isolation is primarily enforced in Django querysets. Vector metadata also stores `user_id` to support future user-level filters.

Version 1.0 retrieval filters by selected `document_id`, and document ownership is checked before retrieval.

## Document Filtering

Retrieval calls ChromaDB with:

```text
where = {"document_id": document.pk}
```

This restricts semantic search to one selected document.

## Retrieval Flow

```text
Question
  |
  v
Question Embedding
  |
  v
Chroma Query filtered by document_id
  |
  v
Chunk IDs and scores
  |
  v
PostgreSQL chunk content
```

## Future Migration Possibilities

The vector store is accessed through `BaseVectorStore`. Future implementations can support:

- pgvector
- Pinecone
- Weaviate
- Qdrant
- managed Chroma

Only `services/rag/vector_store/` should need major changes.
