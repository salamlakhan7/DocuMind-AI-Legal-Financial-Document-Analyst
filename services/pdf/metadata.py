from pypdf import PdfReader

from .exceptions import PDFProcessingError


class PDFMetadataService:
    def get_page_count(self, document):
        try:
            reader = PdfReader(document.file.path)
            return len(reader.pages)
        except Exception as exc:
            raise PDFProcessingError("Unable to read PDF page count.") from exc

    def get_file_hash(self, document):
        raise NotImplementedError("PDF hashing is not implemented yet.")

    def get_metadata(self, document):
        raise NotImplementedError("PDF metadata extraction is not implemented yet.")
