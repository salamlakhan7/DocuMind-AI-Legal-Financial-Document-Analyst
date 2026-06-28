from dataclasses import dataclass
import logging
from pathlib import Path

from pypdf import PdfReader

from .exceptions import PDFExtractionError, PDFProcessingError


logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class PDFExtractedPage:
    page_number: int
    text: str


@dataclass(frozen=True)
class PDFExtractionResult:
    page_count: int
    full_text: str
    pages: list[PDFExtractedPage]


class PDFTextExtractor:
    def extract(self, document):
        try:
            file_path = Path(document.file.path)
        except (AttributeError, NotImplementedError, ValueError) as exc:
            raise PDFProcessingError("PDF file path is not available.") from exc

        if not file_path.exists():
            raise PDFProcessingError("PDF file could not be found.")

        try:
            reader = PdfReader(str(file_path))
            page_count = len(reader.pages)
            if page_count == 0:
                raise PDFExtractionError("The uploaded PDF does not contain any pages.")

            pages = []

            for index, page in enumerate(reader.pages, start=1):
                try:
                    raw_text = page.extract_text() or ""
                except Exception:
                    logger.warning(
                        "Failed to extract text from PDF page.",
                        extra={"document_id": document.pk, "page_number": index},
                        exc_info=True,
                    )
                    raw_text = ""
                text = self._clean_text(raw_text)
                pages.append(PDFExtractedPage(page_number=index, text=text))

            full_text = "\n\n".join(page.text for page in pages if page.text).strip()
            if not full_text:
                logger.info(
                    "PDF processed with no extractable text.",
                    extra={"document_id": document.pk, "page_count": page_count},
                )

            return PDFExtractionResult(
                page_count=page_count,
                full_text=full_text,
                pages=pages,
            )
        except PDFProcessingError:
            raise
        except Exception as exc:
            logger.warning(
                "PDF text extraction failed.",
                extra={"document_id": getattr(document, "pk", None)},
                exc_info=True,
            )
            raise PDFExtractionError("PDF text extraction failed. The file may be corrupted or unsupported.") from exc

    @staticmethod
    def _clean_text(text):
        lines = [line.strip() for line in text.splitlines()]
        cleaned_lines = [line for line in lines if line]
        return "\n".join(cleaned_lines).strip()
