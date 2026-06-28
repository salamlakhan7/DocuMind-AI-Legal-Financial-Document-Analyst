from dataclasses import dataclass
import logging

import numpy as np
from sentence_transformers import SentenceTransformer

from .constants import DEFAULT_EMBEDDING_MODEL
from .exceptions import EmbeddingError, EmbeddingModelError


logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class EmbeddingResult:
    chunk_id: int
    vector: list[float]
    model_name: str
    vector_dimension: int


class EmbeddingService:
    def __init__(self, model_name=DEFAULT_EMBEDDING_MODEL, model=None):
        self.model_name = model_name
        self.model = model

    def embed_chunk(self, chunk):
        return self.embed_text(chunk.pk, chunk.content)

    def embed_chunks(self, chunks):
        chunks = list(chunks)
        if not chunks:
            return []

        try:
            texts = [self._clean_text(chunk.content) for chunk in chunks]
            if not any(texts):
                return []
            vectors = self._model().encode(
                texts,
                normalize_embeddings=True,
                convert_to_numpy=True,
            )
            return [
                self._result(chunk.pk, vector)
                for chunk, vector in zip(chunks, vectors, strict=True)
            ]
        except EmbeddingError:
            raise
        except Exception as exc:
            logger.warning(
                "Chunk embedding generation failed.",
                extra={"chunk_count": len(chunks), "model_name": self.model_name},
                exc_info=True,
            )
            raise EmbeddingError("Chunk embedding generation failed.") from exc

    def embed_text(self, chunk_id, text):
        text = self._clean_text(text)
        if not text:
            raise EmbeddingError("Cannot generate an embedding for empty text.")

        try:
            vector = self._model().encode(
                text,
                normalize_embeddings=True,
                convert_to_numpy=True,
            )
            return self._result(chunk_id, vector)
        except EmbeddingError:
            raise
        except Exception as exc:
            logger.warning(
                "Text embedding generation failed.",
                extra={"chunk_id": chunk_id, "model_name": self.model_name},
                exc_info=True,
            )
            raise EmbeddingError("Chunk embedding generation failed.") from exc

    def _model(self):
        if self.model is None:
            try:
                self.model = SentenceTransformer(self.model_name)
            except Exception as exc:
                logger.exception(
                    "Embedding model could not be loaded.",
                    extra={"model_name": self.model_name},
                )
                raise EmbeddingModelError("Embedding model could not be loaded.") from exc
        return self.model

    def _result(self, chunk_id, vector):
        vector = np.asarray(vector, dtype=float).tolist()
        return EmbeddingResult(
            chunk_id=chunk_id,
            vector=vector,
            model_name=self.model_name,
            vector_dimension=len(vector),
        )

    @staticmethod
    def _clean_text(text):
        return (text or "").strip()
