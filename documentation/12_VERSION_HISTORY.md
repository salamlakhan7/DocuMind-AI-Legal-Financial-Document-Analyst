# Version History

## Version 1.0

Version 1.0 delivers a complete single-document AI chat workflow.

### Milestones Completed

#### Project Foundation

- Django 5 project initialized.
- Environment-driven settings configured.
- Static, media, templates, and app structure created.
- Django REST Framework installed for future use.

#### Authentication Shell

- Login and logout implemented.
- Dashboard layout created.
- Sidebar navigation added.
- Protected dashboard pages added.

#### Document Management

- `Document` model added.
- PDF upload, list, detail, and delete implemented.
- User ownership enforcement added.
- Media serving configured for development.

#### Processing Architecture

- `DocumentProcessing` model added.
- Processing states added.
- Service package structure created.
- Signals create processing records automatically.

#### PDF Extraction

- `pypdf` integrated.
- Page counting implemented.
- Text extraction implemented.
- Processing metadata updates added.

#### Chunking

- `DocumentChunk` model added.
- Custom chunking service implemented.
- Chunk count stored on documents.
- Chunk previews added to document detail.

#### Embeddings

- Sentence Transformers integrated.
- Chunk embedding metadata model added.
- Vectors generated in memory.
- PostgreSQL stores metadata only.

#### Vector Store

- Vector store interface added.
- ChromaDB implementation added.
- Vectors stored in local persistent Chroma collection.
- Dashboard vector stats added.

#### Retrieval

- Document-scoped semantic retrieval implemented.
- Temporary retrieval page added.
- Retrieved chunks include page, chunk index, score, and content.

#### Grounded Answer Generation

- Prompt builder added.
- Groq client added.
- Answer service added.
- Temporary ask page added.

#### Persistent Chat

- `ChatSession` and `ChatMessage` models added.
- Final document chat UI implemented.
- Chat history page implemented.
- Sources stored with assistant messages.

#### Production Hardening

- Environment configuration improved.
- Custom exceptions expanded.
- Logging added.
- Query usage reviewed.
- Validation improved.
- UI submit feedback added.
