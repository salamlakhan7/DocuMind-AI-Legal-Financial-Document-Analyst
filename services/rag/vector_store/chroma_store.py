from pathlib import Path
import logging

import chromadb
from chromadb.config import Settings as ChromaSettings
from django.conf import settings

from services.rag.exceptions import VectorStoreError

from .base import BaseVectorStore


logger = logging.getLogger(__name__)


class ChromaVectorStore(BaseVectorStore):
    collection_name = "documind"

    def __init__(self, persist_directory=None, collection_name=None):
        self.persist_directory = Path(persist_directory or settings.BASE_DIR / "vector_store")
        self.collection_name = collection_name or self.collection_name
        try:
            self.persist_directory.mkdir(parents=True, exist_ok=True)
            self.client = chromadb.PersistentClient(
                path=str(self.persist_directory),
                settings=ChromaSettings(anonymized_telemetry=False),
            )
        except Exception as exc:
            logger.warning("ChromaDB client initialization failed.", exc_info=True)
            raise VectorStoreError("Vector database is unavailable.") from exc

    def create_collection(self):
        try:
            return self.client.get_or_create_collection(name=self.collection_name)
        except Exception as exc:
            logger.warning("ChromaDB collection creation failed.", exc_info=True)
            raise VectorStoreError("Vector collection could not be opened.") from exc

    def upsert_embeddings(self, embeddings, chunks):
        embeddings = list(embeddings)
        chunks_by_id = {chunk.pk: chunk for chunk in chunks}

        if not embeddings:
            return 0

        try:
            collection = self.create_collection()
            collection.upsert(
                ids=[self._chunk_vector_id(result.chunk_id) for result in embeddings],
                embeddings=[result.vector for result in embeddings],
                documents=[chunks_by_id[result.chunk_id].content for result in embeddings],
                metadatas=[
                    self._metadata(chunks_by_id[result.chunk_id])
                    for result in embeddings
                ],
            )
        except KeyError as exc:
            logger.warning("Vector upsert received an embedding without a matching chunk.")
            raise VectorStoreError("Vector metadata could not be prepared.") from exc
        except Exception as exc:
            logger.warning(
                "ChromaDB vector upsert failed.",
                extra={"embedding_count": len(embeddings)},
                exc_info=True,
            )
            raise VectorStoreError("Vectors could not be stored.") from exc
        return len(embeddings)

    def delete_document(self, document_id):
        if not self.collection_exists():
            return
        try:
            self.create_collection().delete(where={"document_id": int(document_id)})
        except Exception as exc:
            logger.warning(
                "ChromaDB document vector deletion failed.",
                extra={"document_id": document_id},
                exc_info=True,
            )
            raise VectorStoreError("Document vectors could not be deleted.") from exc

    def delete_chunk(self, chunk_id):
        if not self.collection_exists():
            return
        try:
            self.create_collection().delete(ids=[self._chunk_vector_id(chunk_id)])
        except Exception as exc:
            logger.warning(
                "ChromaDB chunk vector deletion failed.",
                extra={"chunk_id": chunk_id},
                exc_info=True,
            )
            raise VectorStoreError("Chunk vector could not be deleted.") from exc

    def query(self, query_vector, top_k=5, filters=None):
        try:
            collection = self.create_collection()
            response = collection.query(
                query_embeddings=[query_vector],
                n_results=top_k,
                where=filters,
            )
            return self._normalize_query_response(response)
        except Exception as exc:
            logger.warning("ChromaDB vector query failed.", exc_info=True)
            raise VectorStoreError("Vector search failed.") from exc

    def collection_exists(self):
        try:
            collection_names = []
            for collection in self.client.list_collections():
                if isinstance(collection, str):
                    collection_names.append(collection)
                else:
                    collection_names.append(getattr(collection, "name", str(collection)))
            return self.collection_name in collection_names
        except Exception as exc:
            logger.warning("ChromaDB collection lookup failed.", exc_info=True)
            raise VectorStoreError("Vector collection status could not be checked.") from exc

    def count(self):
        if not self.collection_exists():
            return 0
        try:
            return self.create_collection().count()
        except Exception as exc:
            logger.warning("ChromaDB vector count failed.", exc_info=True)
            raise VectorStoreError("Vector count could not be loaded.") from exc

    @staticmethod
    def _chunk_vector_id(chunk_id):
        return f"chunk-{chunk_id}"

    @staticmethod
    def _metadata(chunk):
        document = chunk.document
        return {
            "document_id": document.pk,
            "chunk_id": chunk.pk,
            "page_number": chunk.page_number,
            "chunk_index": chunk.chunk_index,
            "user_id": document.user_id,
            "title": document.title,
        }

    @staticmethod
    def _normalize_query_response(response):
        ids = response.get("ids", [[]])[0]
        metadatas = response.get("metadatas", [[]])[0]
        distances = response.get("distances", [[]])[0]

        normalized = []
        for index, vector_id in enumerate(ids):
            distance = distances[index] if index < len(distances) else None
            normalized.append(
                {
                    "id": vector_id,
                    "metadata": metadatas[index] if index < len(metadatas) else {},
                    "distance": distance,
                    "score": None if distance is None else 1 / (1 + distance),
                }
            )
        return normalized
