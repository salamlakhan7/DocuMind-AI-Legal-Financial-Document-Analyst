from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView

from apps.documents.models import ChunkEmbedding, Document, DocumentProcessing


class HomeView(TemplateView):
    template_name = "home.html"


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = "dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        documents = Document.objects.for_user(self.request.user)
        processing_records = DocumentProcessing.objects.filter(document__user=self.request.user)
        context["total_documents"] = documents.count()
        context["ready_documents"] = documents.filter(status=Document.Status.READY).count()
        context["failed_documents"] = documents.filter(status=Document.Status.FAILED).count()
        context["processing_documents"] = processing_records.filter(
            status=DocumentProcessing.Status.PROCESSING
        ).count()
        context["completed_processing"] = processing_records.filter(
            status=DocumentProcessing.Status.COMPLETED
        ).count()
        context["failed_processing"] = processing_records.filter(
            status=DocumentProcessing.Status.FAILED
        ).count()
        context["pending_processing"] = processing_records.filter(
            status=DocumentProcessing.Status.PENDING
        ).count()
        total_chunks = sum(documents.values_list("chunk_count", flat=True))
        context["total_chunks"] = total_chunks
        context["average_chunks_per_document"] = (
            round(total_chunks / context["total_documents"], 1)
            if context["total_documents"]
            else 0
        )
        embeddings = ChunkEmbedding.objects.filter(chunk__document__user=self.request.user)
        context["total_embedded_chunks"] = embeddings.count()
        context["documents_with_embeddings"] = (
            embeddings.values("chunk__document_id").distinct().count()
        )
        context.update(self._vector_store_context())
        context["recent_documents"] = documents[:5]
        return context

    @staticmethod
    def _vector_store_context():
        try:
            from services.rag.vector_store.chroma_store import ChromaVectorStore

            vector_store = ChromaVectorStore()
            collection_exists = vector_store.collection_exists()
            collection_size = vector_store.count()
            return {
                "total_vectors": collection_size,
                "vector_db_status": "Connected" if collection_exists else "Ready",
                "vector_collection_size": collection_size,
            }
        except Exception:
            return {
                "total_vectors": 0,
                "vector_db_status": "Unavailable",
                "vector_collection_size": 0,
            }


class SettingsView(LoginRequiredMixin, TemplateView):
    template_name = "settings.html"
