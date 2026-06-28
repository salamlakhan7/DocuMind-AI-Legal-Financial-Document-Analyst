from pathlib import Path

from apps.documents.models import MAX_DOCUMENT_SIZE, PDF_CONTENT_TYPES

from .exceptions import PDFValidationError


class PDFValidator:
    def __init__(self, max_size=MAX_DOCUMENT_SIZE, allowed_content_types=None):
        self.max_size = max_size
        self.allowed_content_types = allowed_content_types or PDF_CONTENT_TYPES

    def validate_document(self, document):
        self.validate_file_exists(document)
        self.validate_extension(document)
        self.validate_mime_type(document)
        self.validate_size(document)
        return True

    def validate_file_exists(self, document):
        if not document.file:
            raise PDFValidationError("Document has no uploaded file.")

        if not document.file.storage.exists(document.file.name):
            raise PDFValidationError("Uploaded file could not be found in storage.")

    def validate_extension(self, document):
        extension = Path(document.original_filename or document.file.name).suffix.lower()
        if extension != ".pdf":
            raise PDFValidationError("Only PDF files can be processed.")

    def validate_mime_type(self, document):
        if document.file_type and document.file_type not in self.allowed_content_types:
            raise PDFValidationError("Document MIME type is not supported.")

    def validate_size(self, document):
        if document.file_size > self.max_size:
            raise PDFValidationError("PDF files must be 10 MB or smaller.")
