from dataclasses import dataclass
import logging

from apps.documents.models import DocumentChunk

from .exceptions import EmbeddingError, RetrievalError, VectorStoreError


logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class RetrievedChunk:
    chunk_id: int
    document_id: int
    page_number: int
    chunk_index: int
    content: str
    score: float | None


class DocumentRetriever:
    def __init__(self, embedding_service=None, vector_store=None):
        if embedding_service is None:
            from .embeddings import EmbeddingService

            embedding_service = EmbeddingService()
        self.embedding_service = embedding_service
        self.vector_store = vector_store

    def retrieve(self, document, question, top_k=5):
        question = (question or "").strip()
        if not question:
            raise RetrievalError("Enter a question to retrieve relevant chunks.")

        if document.chunk_count == 0:
            raise RetrievalError("This document does not have chunks to search.")

        try:
            query_embedding = self.embedding_service.embed_text(
                chunk_id=0,
                text=question,
            )
            results = self._vector_store().query(
                query_embedding.vector,
                top_k=top_k,
                filters={"document_id": document.pk},
            )
        except EmbeddingError:
            raise
        except VectorStoreError as exc:
            logger.warning(
                "Vector store retrieval failed.",
                extra={"document_id": document.pk},
                exc_info=True,
            )
            raise RetrievalError(str(exc)) from exc
        except Exception as exc:
            logger.warning(
                "Semantic retrieval failed.",
                extra={"document_id": document.pk},
                exc_info=True,
            )
            raise RetrievalError("Semantic retrieval failed.") from exc

        chunk_ids = [
            result["metadata"]["chunk_id"]
            for result in results
            if result.get("metadata", {}).get("chunk_id")
        ]
        if not chunk_ids:
            return []

        chunks_by_id = {
            chunk.pk: chunk
            for chunk in DocumentChunk.objects.filter(
                document=document,
                pk__in=chunk_ids,
            )
        }

        retrieved = []
        for result in results:
            metadata = result["metadata"]
            chunk_id = metadata["chunk_id"]
            chunk = chunks_by_id.get(chunk_id)
            if not chunk:
                continue

            retrieved.append(
                RetrievedChunk(
                    chunk_id=chunk.pk,
                    document_id=document.pk,
                    page_number=chunk.page_number,
                    chunk_index=chunk.chunk_index,
                    content=chunk.content,
                    score=result["score"],
                )
            )

        return retrieved

    def _vector_store(self):
        if self.vector_store is None:
            from .vector_store.chroma_store import ChromaVectorStore

            self.vector_store = ChromaVectorStore()
        return self.vector_store
