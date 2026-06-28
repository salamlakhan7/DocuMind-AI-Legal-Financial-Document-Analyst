from dataclasses import dataclass
import logging

from django.utils import timezone

from apps.documents.models import ChunkEmbedding

from .embeddings import EmbeddingService
from .exceptions import EmbeddingError


logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class EmbeddingSummary:
    total_chunks: int
    embedded_chunks: int
    failed_chunks: int
    model_name: str
    vector_dimension: int | None
    vectors_stored: int


class ChunkEmbeddingManager:
    def __init__(self, embedding_service=None, vector_store=None):
        self.embedding_service = embedding_service or EmbeddingService()
        self.vector_store = vector_store

    def embed_document(self, document):
        chunks = list(document.chunks.only("id", "document_id", "chunk_index", "page_number", "content"))
        total_chunks = len(chunks)

        if not chunks:
            return EmbeddingSummary(
                total_chunks=0,
                embedded_chunks=0,
                failed_chunks=0,
                model_name=self.embedding_service.model_name,
                vector_dimension=None,
                vectors_stored=0,
            )

        try:
            results = self.embedding_service.embed_chunks(chunks)
        except EmbeddingError:
            raise
        except Exception as exc:
            logger.warning(
                "Document embedding failed.",
                extra={"document_id": document.pk, "chunk_count": total_chunks},
                exc_info=True,
            )
            raise EmbeddingError("Document embedding failed.") from exc

        now = timezone.now()
        chunks_by_id = {chunk.pk: chunk for chunk in chunks}
        for result in results:
            ChunkEmbedding.objects.update_or_create(
                chunk_id=result.chunk_id,
                defaults={
                    "model_name": result.model_name,
                    "vector_dimension": result.vector_dimension,
                    "embedding_created_at": now,
                },
            )

        try:
            vectors_stored = self._vector_store().upsert_embeddings(
                results,
                [chunks_by_id[result.chunk_id] for result in results],
            )
        except Exception as exc:
            logger.warning(
                "Embedding metadata saved but vector upsert failed.",
                extra={"document_id": document.pk, "result_count": len(results)},
                exc_info=True,
            )
            raise EmbeddingError("Vector storage failed after embedding generation.") from exc
        embedded_chunks = len(results)
        vector_dimension = results[0].vector_dimension if results else None

        return EmbeddingSummary(
            total_chunks=total_chunks,
            embedded_chunks=embedded_chunks,
            failed_chunks=total_chunks - embedded_chunks,
            model_name=self.embedding_service.model_name,
            vector_dimension=vector_dimension,
            vectors_stored=vectors_stored,
        )

    def _vector_store(self):
        if self.vector_store is None:
            from .vector_store.chroma_store import ChromaVectorStore

            self.vector_store = ChromaVectorStore()
        return self.vector_store
