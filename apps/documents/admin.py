from django.contrib import admin

from .models import ChunkEmbedding, Document, DocumentChunk, DocumentProcessing


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "user",
        "status",
        "page_count",
        "chunk_count",
        "created_at",
    )
    list_filter = ("status", "created_at", "updated_at")
    search_fields = ("title", "original_filename", "user__username", "user__email")
    readonly_fields = ("created_at", "updated_at")


@admin.register(DocumentProcessing)
class DocumentProcessingAdmin(admin.ModelAdmin):
    list_display = (
        "document",
        "status",
        "processing_time_ms",
        "processing_version",
        "created_at",
    )
    list_filter = ("status", "processing_version", "created_at", "updated_at")
    search_fields = ("document__title", "document__original_filename")
    readonly_fields = ("created_at", "updated_at")


@admin.register(DocumentChunk)
class DocumentChunkAdmin(admin.ModelAdmin):
    list_display = (
        "document",
        "chunk_index",
        "page_number",
        "character_count",
        "word_count",
    )
    list_filter = ("created_at", "updated_at")
    search_fields = ("document__title", "content")
    readonly_fields = ("created_at", "updated_at")


@admin.register(ChunkEmbedding)
class ChunkEmbeddingAdmin(admin.ModelAdmin):
    list_display = (
        "chunk",
        "model_name",
        "vector_dimension",
        "embedding_created_at",
    )
    list_filter = ("model_name", "vector_dimension", "embedding_created_at")
    search_fields = ("chunk__document__title", "chunk__content", "model_name")
    readonly_fields = ("embedding_created_at", "created_at", "updated_at")
