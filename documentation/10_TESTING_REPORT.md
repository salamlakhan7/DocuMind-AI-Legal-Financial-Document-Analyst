# Testing Report

This report documents manual validation scenarios used during Version 1.0 development.

## Resume PDF

### Expected Behavior

- Upload succeeds.
- Text extraction succeeds.
- Chunks are generated.
- Embeddings and vectors are created.
- Questions about resume content retrieve relevant chunks.

### Observed Result

The resume PDF was processed through the document pipeline and made available for retrieval and chat.

## Legal Agreement PDF

### Expected Behavior

- Upload succeeds.
- Contract text is extracted.
- Clause-related questions return relevant pages and chunks.
- Answers include grounded source references.

### Observed Result

The legal agreement validated the primary business use case for document-grounded answer generation.

## Admission Form PDF

### Expected Behavior

- Structured form text is extracted when available.
- Retrieval works for fields present in extracted text.
- Missing fields are handled without unsupported claims.

### Observed Result

The admission form validated behavior on form-like PDFs.

## Image-Only PDF

### Expected Behavior

- Upload may succeed if the file is a valid PDF.
- Extraction returns no text if no selectable text exists.
- Chunk count may be zero.
- Chat should not be available unless chunks exist.

### Observed Result

Image-only PDFs are handled gracefully, but OCR is not available in Version 1.0.

## Empty PDF

### Expected Behavior

- Empty uploaded files are rejected.
- PDFs with zero pages fail processing with a clear error.

### Observed Result

Validation and extraction error handling prevent crashes and expose safe user-facing errors.

## Unknown Question

### Expected Behavior

- Retrieval may return low-relevance chunks.
- Prompt instructs the model to say the document does not contain enough information when context is insufficient.

### Observed Result

The prompt behavior is designed to reduce unsupported claims.

## Retrieval Validation

### Expected Behavior

- Retrieval is scoped to one document.
- Results include page number, chunk index, score, and content.

### Observed Result

The retrieval test page confirms semantic search returns document-scoped chunks.

## Source Validation

### Expected Behavior

- Assistant answers include source previews from retrieved chunks.
- Sources include page and chunk references.

### Observed Result

Sources are persisted with assistant messages and displayed in chat.

## Chat Persistence

### Expected Behavior

- User message is saved.
- Assistant message is saved.
- Sources and model name are saved.
- Reopening the chat shows prior conversation.

### Observed Result

Chat sessions and messages persist and can be reopened through conversation history.
