# Security

## Authentication

DocuMind uses Django authentication. Login is required for dashboard, document, retrieval, answer, and chat pages.

## Authorization

Documents are always queried through ownership-scoped querysets. Users can only access their own documents, chunks, processing records, embeddings, chat sessions, and chat messages.

## User Isolation

Isolation is enforced at the application layer:

- document querysets filter by `user`
- chat sessions filter by `user`
- retrieval requires selected owned document
- Chroma metadata includes `user_id` and `document_id`

## Environment Variables

Configuration is loaded from `.env` with `django-environ`.

Important variables:

- `SECRET_KEY`
- `DEBUG`
- `ALLOWED_HOSTS`
- `DATABASE_URL`
- `GROQ_API_KEY`
- `CORS_ALLOWED_ORIGINS`
- `CSRF_TRUSTED_ORIGINS`

## Secret Management

`.env` is ignored by Git. `.env.example` contains placeholders only.

Production must provide a real `SECRET_KEY` and `GROQ_API_KEY` through deployment environment variables.

## File Upload Validation

The upload pipeline validates:

- file size
- MIME type
- PDF signature
- empty files
- unreadable files

## Production Security Considerations

Production should configure:

- `DEBUG=False`
- secure `SECRET_KEY`
- strict `ALLOWED_HOSTS`
- HTTPS
- secure cookies
- trusted CSRF origins
- persistent database
- controlled media storage
- restricted admin access
- log aggregation
