# Deployment Architecture

## Development Architecture

```text
Django dev server
SQLite
Local media/
Local vector_store/
Local .env
Groq API
```

Development uses SQLite by default when `DATABASE_URL` is blank.

## Production Architecture

```text
Web Process
  |
  +--> PostgreSQL
  +--> Persistent media storage
  +--> Persistent Chroma storage
  +--> Groq API
```

## Railway Deployment

Railway can host:

- Django web service
- PostgreSQL database
- environment variables
- persistent volume if available for Chroma/media

If persistent local volumes are not guaranteed, Chroma and media should be moved to managed persistent services.

## PostgreSQL

Set `DATABASE_URL` in the production environment. The same settings file parses this value without code changes.

## Static Files

Static files should be collected using:

```bash
python manage.py collectstatic
```

Production should serve static files through the platform or a static file middleware/storage solution.

## Media

Uploaded PDFs are stored under `media/` locally. Production needs persistent media storage. Railway deployments should not rely on ephemeral disk unless a persistent volume is configured.

## Chroma Persistence

ChromaDB stores local vector data under `vector_store/`. Production must ensure this directory is persistent.

## Environment Variables

Required production variables:

- `SECRET_KEY`
- `DEBUG=False`
- `ALLOWED_HOSTS`
- `DATABASE_URL`
- `GROQ_API_KEY`
- `CSRF_TRUSTED_ORIGINS`

Optional:

- `CORS_ALLOWED_ORIGINS`

## Scaling Considerations

Version 1.0 uses synchronous processing. Large PDFs and embedding generation can block the request process.

Future scaling should add:

- Celery workers
- Redis queue
- managed vector database
- object storage for media
- response streaming
- request timeouts
- monitoring and tracing
