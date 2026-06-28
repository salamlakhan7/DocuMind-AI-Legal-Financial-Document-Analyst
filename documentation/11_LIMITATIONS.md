# Limitations

## OCR Not Implemented

Image-only PDFs and scanned documents do not produce extractable text unless the PDF already contains a text layer. OCR was excluded from Version 1.0 to keep the initial pipeline focused and stable.

## Streaming Not Implemented

Groq responses are returned after completion. Streaming was deferred to avoid complicating the synchronous template-based chat flow.

## Background Processing Not Implemented

PDF processing, embedding generation, and vector storage run synchronously during upload. This is acceptable for Version 1.0 validation but should move to background jobs for production scale.

## Multi-Document Retrieval Not Implemented

Retrieval is scoped to one selected document. Multi-document retrieval requires additional ranking, filtering, and UI decisions.

## No REST API

The application is template-driven. APIs were intentionally deferred until the core product workflow stabilized.

## Local Chroma Persistence

ChromaDB persists to local disk. Production deployments need reliable persistent storage or a managed vector database.

## Basic Prompt Strategy

Prompt construction is strict and grounded but not yet optimized for advanced citation formatting or complex legal/financial reasoning.

## No Team Permissions

Version 1.0 supports individual users only. There is no organization, workspace, or shared document model.

## No Advanced File Types

Only PDFs are supported.

## No Automated Test Suite

Manual testing was performed. Automated tests should be added before larger production deployments.
