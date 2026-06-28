# DocuMind Project Overview

## Purpose

DocuMind is an authenticated Django application for uploading legal and financial PDF documents, processing their text, indexing document chunks into a vector database, and generating grounded answers through an LLM using retrieved document context.

The product is designed as a production-oriented Retrieval Augmented Generation (RAG) application with clear separation between web views, document processing, vector storage, retrieval, prompt construction, and LLM integration.

## Business Problem

Legal and financial documents are often long, dense, and difficult to review manually. Users need a controlled way to ask questions against a specific document and receive answers that are grounded in that document rather than general model knowledge.

DocuMind addresses:

- Slow manual review of contracts, forms, financial documents, resumes, and agreements.
- Difficulty finding relevant clauses or facts inside large PDFs.
- Risk of unsupported LLM answers when context is not constrained.
- Need for persistent conversations tied to a document.

## Goals

- Provide secure authenticated document management.
- Validate and process uploaded PDF files.
- Extract text and page counts from PDFs.
- Chunk extracted text into retrieval-friendly units.
- Generate embeddings for chunks.
- Store vectors in ChromaDB with document and ownership metadata.
- Retrieve relevant chunks for a selected document.
- Build grounded prompts from retrieved context.
- Generate answers using Groq.
- Persist chat sessions and messages.

## Scope

Version 1.0 supports single-document chat. A user uploads a PDF, waits for synchronous processing, then chats with that document.

Out of scope for Version 1.0:

- OCR for scanned PDFs.
- Multi-document retrieval.
- Streaming responses.
- Background processing.
- Team accounts or organization-level permissions.
- REST APIs.
- Advanced analytics.

## Functional Modules

- Accounts: login and logout using Django authentication.
- Core: dashboard, settings shell, high-level statistics.
- Documents: upload, validation, metadata, detail, list, delete, processing status.
- Chat: persistent document chat sessions and messages.
- PDF services: validation, extraction, metadata, processing orchestration.
- RAG services: chunking, embeddings, vector storage, retrieval, prompt building, answer orchestration.
- LLM services: Groq client and LLM error handling.

## Non-Functional Requirements

- Secure user isolation.
- Environment-driven configuration.
- Clear service boundaries.
- Replaceable vector store implementation.
- Replaceable LLM client implementation.
- Production-safe error handling.
- No secrets committed to the repository.
- Querysets scoped by authenticated user.
- Upload validation for PDF type and size.

## User Roles

Version 1.0 has one application user role:

- Authenticated user: can upload, process, view, delete, retrieve, and chat with their own documents.

Django admin users can also inspect models through the admin site.

## System Capabilities

- PDF upload and validation.
- PDF text extraction and page counting.
- Text chunk generation with overlap.
- Embedding generation using Sentence Transformers.
- Vector persistence in ChromaDB.
- Document-scoped semantic retrieval.
- Grounded answer generation through Groq.
- Persistent document chat history.

## Current Version

Current release: Version 1.0.

Version 1.0 is a usable single-document AI chat product with persistent conversations.

## Future Vision

Future releases can extend DocuMind into a broader document intelligence platform:

- Background processing with Celery.
- OCR support.
- Multi-document retrieval.
- Streaming answers.
- Document comparison.
- Structured extraction.
- Organization accounts.
- REST APIs.
- Deployment observability.
- Source citation improvements.
