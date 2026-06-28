class PDFValidationError(Exception):
    """Raised when a PDF fails validation before processing."""


class PDFProcessingError(Exception):
    """Raised when a PDF processing workflow cannot continue."""


class PDFExtractionError(PDFProcessingError):
    """Raised when PDF text extraction fails."""
