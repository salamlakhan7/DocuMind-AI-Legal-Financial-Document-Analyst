from pathlib import Path

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.text import get_valid_filename


MAX_DOCUMENT_SIZE = 10 * 1024 * 1024
PDF_CONTENT_TYPES = {"application/pdf", "application/x-pdf"}


def validate_pdf_upload(uploaded_file):
    if uploaded_file.size == 0:
        raise ValidationError("The uploaded PDF is empty.")

    if uploaded_file.size > MAX_DOCUMENT_SIZE:
        raise ValidationError("PDF files must be 10 MB or smaller.")

    content_type = getattr(uploaded_file, "content_type", "")
    if content_type and content_type not in PDF_CONTENT_TYPES:
        raise ValidationError("Only PDF files are allowed.")

    try:
        current_position = uploaded_file.tell()
        uploaded_file.seek(0)
        signature = uploaded_file.read(4)
        uploaded_file.seek(current_position)
    except Exception as exc:
        raise ValidationError("The uploaded PDF could not be read.") from exc

    if signature != b"%PDF":
        raise ValidationError("The uploaded file does not appear to be a valid PDF.")


class DocumentQuerySet(models.QuerySet):
    def for_user(self, user):
        return self.filter(user=user)


class Document(models.Model):
    class Status(models.TextChoices):
        UPLOADED = "uploaded", "Uploaded"
        PROCESSING = "processing", "Processing"
        READY = "ready", "Ready"
        FAILED = "failed", "Failed"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="documents",
    )
    title = models.CharField(max_length=255)
    file = models.FileField(upload_to="documents/", validators=[validate_pdf_upload])
    original_filename = models.CharField(max_length=255)
    file_size = models.PositiveIntegerField()
    file_type = models.CharField(max_length=100)
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.UPLOADED,
    )
    page_count = models.PositiveIntegerField(null=True, blank=True)
    chunk_count = models.PositiveIntegerField(default=0)
    error_message = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = DocumentQuerySet.as_manager()

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.title

    def clean(self):
        super().clean()
        if self.file:
            validate_pdf_upload(self.file)

    def save(self, *args, **kwargs):
        if self.file and not self.original_filename:
            self.original_filename = get_valid_filename(Path(self.file.name).name)
        super().save(*args, **kwargs)


class DocumentProcessing(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        PROCESSING = "processing", "Processing"
        COMPLETED = "completed", "Completed"
        FAILED = "failed", "Failed"

    document = models.OneToOneField(
        Document,
        on_delete=models.CASCADE,
        related_name="processing",
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
    )
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    processing_time_ms = models.PositiveIntegerField(null=True, blank=True)
    processing_version = models.CharField(max_length=20, default="v1")
    error_message = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.document.title} processing"


class DocumentChunk(models.Model):
    document = models.ForeignKey(
        Document,
        on_delete=models.CASCADE,
        related_name="chunks",
    )
    chunk_index = models.PositiveIntegerField()
    page_number = models.PositiveIntegerField()
    content = models.TextField()
    character_count = models.PositiveIntegerField()
    word_count = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["chunk_index"]
        constraints = [
            models.UniqueConstraint(
                fields=["document", "chunk_index"],
                name="unique_document_chunk_index",
            )
        ]

    def __str__(self):
        return f"{self.document.title} chunk {self.chunk_index}"


class ChunkEmbedding(models.Model):
    chunk = models.OneToOneField(
        DocumentChunk,
        on_delete=models.CASCADE,
        related_name="embedding",
    )
    model_name = models.CharField(max_length=255)
    vector_dimension = models.PositiveIntegerField()
    embedding_created_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["chunk__document", "chunk__chunk_index"]

    def __str__(self):
        return f"Embedding for {self.chunk}"
