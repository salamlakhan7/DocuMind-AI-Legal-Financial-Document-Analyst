# Document Processing

## Upload Lifecycle

1. User submits title and PDF.
2. Django form validates required fields.
3. PDF validation checks size, MIME type, signature, and readability.
4. `Document` is saved.
5. `DocumentProcessing` is created by signal.
6. `PDFProcessor` runs synchronously.
7. Document becomes `ready` or `failed`.

## Validation

Validation rejects:

- empty files
- files larger than 10 MB
- unsupported MIME types
- files without `%PDF` signature
- unreadable uploads

## PDF Extraction

`PDFTextExtractor` uses `pypdf` to:

- open the uploaded file
- count pages
- extract text per page
- preserve blank pages as empty text

## Error Handling

Errors are normalized into domain exceptions:

- `PDFValidationError`
- `PDFProcessingError`
- `PDFExtractionError`

Failures are logged without exposing secrets or stack traces to users.

## Chunk Generation

After extraction, `ChunkService` deletes existing chunks, creates new chunk records, and updates `Document.chunk_count`.

## Processing States

Document status:

- uploaded
- processing
- ready
- failed

Processing status:

- pending
- processing
- completed
- failed

## Processing Versioning

`DocumentProcessing.processing_version` defaults to `v1`. This allows future processor changes to identify which processing version handled a document.
