from dataclasses import dataclass
import logging
from time import perf_counter

from django.utils import timezone

from apps.documents.models import Document, DocumentProcessing
from services.rag.chunker import ChunkService
from services.rag.embedding_manager import ChunkEmbeddingManager
from services.rag.exceptions import EmbeddingError

from .exceptions import PDFProcessingError, PDFValidationError
from .extractor import PDFExtractionResult, PDFTextExtractor
from .validator import PDFValidator


logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class PDFProcessingResult:
    document_id: int
    status: str
    processing_version: str
    page_count: int | None
    chunk_count: int
    embedded_chunks: int
    extraction: PDFExtractionResult | None
    message: str


class PDFProcessor:
    def __init__(
        self,
        validator=None,
        extractor=None,
        chunk_service=None,
        embedding_manager=None,
    ):
        self.validator = validator or PDFValidator()
        self.extractor = extractor or PDFTextExtractor()
        self.chunk_service = chunk_service or ChunkService()
        self.embedding_manager = embedding_manager or ChunkEmbeddingManager()

    def process_document(self, document):
        processing, _created = DocumentProcessing.objects.get_or_create(document=document)
        started = perf_counter()

        self._mark_processing(document, processing)

        try:
            self.validator.validate_document(document)
            extraction = self.extractor.extract(document)
            chunks = self.chunk_service.create_chunks(document, extraction)
            embedding_summary = self.embedding_manager.embed_document(document)
        except (PDFValidationError, PDFProcessingError) as exc:
            logger.warning(
                "PDF processing failed.",
                extra={"document_id": document.pk, "reason": exc.__class__.__name__},
                exc_info=True,
            )
            self._mark_failed(document, processing, str(exc), started)
            raise PDFProcessingError(str(exc)) from exc
        except EmbeddingError as exc:
            logger.warning(
                "Embedding generation failed during document processing.",
                extra={"document_id": document.pk},
                exc_info=True,
            )
            self._mark_failed(document, processing, str(exc), started)
            raise PDFProcessingError(str(exc)) from exc
        except Exception as exc:
            error_message = "Document processing failed."
            logger.exception(
                "Unexpected document processing failure.",
                extra={"document_id": document.pk},
            )
            self._mark_failed(document, processing, error_message, started)
            raise PDFProcessingError(error_message) from exc

        self._mark_completed(document, processing, extraction, started)
        logger.info(
            "Document processing completed.",
            extra={
                "document_id": document.pk,
                "page_count": extraction.page_count,
                "chunk_count": len(chunks),
                "embedded_chunks": embedding_summary.embedded_chunks,
            },
        )

        return PDFProcessingResult(
            document_id=document.pk,
            status=processing.status,
            processing_version=processing.processing_version,
            page_count=extraction.page_count,
            chunk_count=len(chunks),
            embedded_chunks=embedding_summary.embedded_chunks,
            extraction=extraction,
            message="PDF extraction, chunking, and embedding completed successfully.",
        )

    @staticmethod
    def _mark_processing(document, processing):
        now = timezone.now()
        document.status = Document.Status.PROCESSING
        document.error_message = ""
        document.save(update_fields=["status", "error_message", "updated_at"])

        processing.status = DocumentProcessing.Status.PROCESSING
        processing.started_at = now
        processing.completed_at = None
        processing.processing_time_ms = None
        processing.error_message = ""
        processing.save(
            update_fields=[
                "status",
                "started_at",
                "completed_at",
                "processing_time_ms",
                "error_message",
                "updated_at",
            ]
        )

    @staticmethod
    def _mark_completed(document, processing, extraction, started):
        processing.completed_at = timezone.now()
        processing.processing_time_ms = int((perf_counter() - started) * 1000)
        processing.status = DocumentProcessing.Status.COMPLETED
        processing.error_message = ""
        processing.save(
            update_fields=[
                "status",
                "completed_at",
                "processing_time_ms",
                "error_message",
                "updated_at",
            ]
        )

        document.status = Document.Status.READY
        document.page_count = extraction.page_count
        document.error_message = ""
        document.save(
            update_fields=[
                "status",
                "page_count",
                "error_message",
                "updated_at",
            ]
        )

    @staticmethod
    def _mark_failed(document, processing, error_message, started):
        processing.completed_at = timezone.now()
        processing.processing_time_ms = int((perf_counter() - started) * 1000)
        processing.status = DocumentProcessing.Status.FAILED
        processing.error_message = error_message
        processing.save(
            update_fields=[
                "status",
                "completed_at",
                "processing_time_ms",
                "error_message",
                "updated_at",
            ]
        )

        document.status = Document.Status.FAILED
        document.chunk_count = document.chunks.count()
        document.error_message = error_message
        document.save(update_fields=["status", "chunk_count", "error_message", "updated_at"])
