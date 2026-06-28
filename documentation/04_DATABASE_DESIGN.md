# Database Design

## Document

### Purpose

Stores uploaded PDF metadata and high-level processing state.

### Fields

- `user`: owner of the document.
- `title`: user-provided title.
- `file`: uploaded PDF path.
- `original_filename`: sanitized original filename.
- `file_size`: uploaded file size.
- `file_type`: MIME type.
- `status`: uploaded, processing, ready, failed.
- `page_count`: extracted page count.
- `chunk_count`: number of generated chunks.
- `error_message`: processing error text.
- `created_at`, `updated_at`: timestamps.

### Relationships

- Many documents belong to one user.
- One document has one `DocumentProcessing`.
- One document has many `DocumentChunk`.
- One document has many `ChatSession`.

### Ownership

All document querysets are scoped to `request.user`.

### Indexes

No custom indexes in Version 1.0. Default primary key indexes and foreign key indexes are used.

### Lifecycle

Uploaded -> processing -> ready or failed. Deleting the document cascades related processing, chunks, embeddings, and chat sessions.

## DocumentProcessing

### Purpose

Tracks processing workflow metadata independently from document metadata.

### Fields

- `document`: one-to-one document relationship.
- `status`: pending, processing, completed, failed.
- `started_at`: processing start timestamp.
- `completed_at`: processing completion timestamp.
- `processing_time_ms`: elapsed time.
- `processing_version`: version marker, default `v1`.
- `error_message`: failure reason.
- `created_at`, `updated_at`: timestamps.

### Relationships

One processing record per document.

### Ownership

Ownership is inherited through `document.user`.

### Indexes

Default primary key and one-to-one indexes.

### Lifecycle

Created automatically through a signal when a document is created. Updated by `PDFProcessor`.

## DocumentChunk

### Purpose

Stores text chunks generated from extracted PDF text.

### Fields

- `document`: parent document.
- `chunk_index`: zero-based chunk order.
- `page_number`: source page.
- `content`: chunk text.
- `character_count`: character length.
- `word_count`: word length.
- `created_at`, `updated_at`: timestamps.

### Relationships

Many chunks belong to one document. One chunk can have one `ChunkEmbedding`.

### Ownership

Ownership is inherited through `document.user`.

### Indexes

Includes a uniqueness constraint on `document` and `chunk_index`.

### Lifecycle

Generated after PDF extraction. Old chunks are deleted and recreated when chunking runs for a document.

## ChunkEmbedding

### Purpose

Stores embedding metadata for a chunk. Full vector values are not stored in PostgreSQL.

### Fields

- `chunk`: one-to-one chunk relationship.
- `model_name`: embedding model name.
- `vector_dimension`: embedding vector size.
- `embedding_created_at`: embedding generation timestamp.
- `created_at`, `updated_at`: timestamps.

### Relationships

One embedding metadata record per chunk.

### Ownership

Ownership is inherited through `chunk.document.user`.

### Indexes

Default primary key and one-to-one indexes.

### Lifecycle

Created or updated after embedding generation. Actual vectors are persisted in ChromaDB.

## ChatSession

### Purpose

Groups chat messages for a user and document.

### Fields

- `user`: session owner.
- `document`: chat target document.
- `title`: session title.
- `created_at`, `updated_at`: timestamps.

### Relationships

One user can have many chat sessions. One document can have many chat sessions.

### Ownership

Sessions are always filtered by `user`.

### Indexes

Default primary key and foreign key indexes.

### Lifecycle

Created when a user opens chat for a ready document if no existing session exists.

## ChatMessage

### Purpose

Stores user and assistant messages within a session.

### Fields

- `session`: parent chat session.
- `role`: user or assistant.
- `content`: message body.
- `model_name`: model used for assistant messages.
- `sources`: JSON list of source metadata.
- `created_at`: timestamp.

### Relationships

Many messages belong to one session.

### Ownership

Ownership is inherited through `session.user`.

### Indexes

Default primary key and foreign key indexes.

### Lifecycle

Created on user question and assistant answer. Ordered by `created_at`.
