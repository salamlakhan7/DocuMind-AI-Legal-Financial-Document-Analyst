from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import DeleteView, DetailView, FormView, ListView
import logging

from services.pdf.exceptions import PDFProcessingError
from services.pdf.processor import PDFProcessor
from services.rag.exceptions import EmbeddingError, RetrievalError
from services.llm.exceptions import LLMError
from services.rag.answer_service import DocumentAnswerService
from services.rag.retriever import DocumentRetriever

from .forms import DocumentUploadForm
from .models import ChunkEmbedding, Document


logger = logging.getLogger(__name__)


class UserDocumentQuerySetMixin(LoginRequiredMixin):
    model = Document

    def get_queryset(self):
        return Document.objects.for_user(self.request.user).select_related("user")


class DocumentListView(UserDocumentQuerySetMixin, ListView):
    template_name = "documents.html"
    context_object_name = "documents"
    paginate_by = 10


class DocumentUploadView(LoginRequiredMixin, FormView):
    template_name = "document_upload.html"
    form_class = DocumentUploadForm
    success_url = reverse_lazy("documents:list")

    def form_valid(self, form):
        uploaded_file = form.cleaned_data["file"]
        document = form.save(commit=False)
        document.user = self.request.user
        document.original_filename = form.safe_original_filename(uploaded_file)
        document.file_size = uploaded_file.size
        document.file_type = getattr(uploaded_file, "content_type", "") or "application/pdf"
        document.save()

        try:
            PDFProcessor().process_document(document)
            messages.success(self.request, "Document uploaded and processed successfully.")
        except PDFProcessingError as exc:
            logger.warning(
                "Document upload processing failed.",
                extra={"document_id": document.pk, "user_id": self.request.user.pk},
                exc_info=True,
            )
            messages.error(
                self.request,
                f"Document uploaded, but processing failed: {exc}",
            )

        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "Please correct the upload errors and try again.")
        return super().form_invalid(form)


class DocumentDetailView(UserDocumentQuerySetMixin, DetailView):
    template_name = "document_detail.html"
    context_object_name = "document"

    def get_queryset(self):
        return super().get_queryset().prefetch_related("chunks")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["processing"] = getattr(self.object, "processing", None)
        context["chunk_previews"] = self.object.chunks.all()[:3]
        embeddings = ChunkEmbedding.objects.filter(chunk__document=self.object)
        context["embedded_chunks_count"] = embeddings.count()
        latest_embedding = embeddings.order_by("-embedding_created_at").first()
        context["embedding_model"] = latest_embedding.model_name if latest_embedding else None
        context["embedding_dimension"] = (
            latest_embedding.vector_dimension if latest_embedding else None
        )
        return context


class DocumentRetrieveView(UserDocumentQuerySetMixin, DetailView):
    template_name = "document_retrieve.html"
    context_object_name = "document"

    def get_queryset(self):
        return super().get_queryset().prefetch_related("chunks")

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        question = request.POST.get("question", "")
        context = self.get_context_data(object=self.object)
        context["question"] = question

        try:
            context["results"] = DocumentRetriever().retrieve(
                document=self.object,
                question=question,
                top_k=5,
            )
        except (EmbeddingError, RetrievalError) as exc:
            messages.error(request, str(exc))
            context["results"] = []

        return self.render_to_response(context)


class DocumentAskView(UserDocumentQuerySetMixin, DetailView):
    template_name = "document_ask.html"
    context_object_name = "document"

    def get_queryset(self):
        return super().get_queryset().prefetch_related("chunks")

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        question = request.POST.get("question", "")
        context = self.get_context_data(object=self.object)
        context["question"] = question

        try:
            context["answer_result"] = DocumentAnswerService().answer(
                document=self.object,
                question=question,
                user=request.user,
                top_k=5,
            )
        except (LLMError, RetrievalError, EmbeddingError) as exc:
            messages.error(request, str(exc))
            context["answer_result"] = None

        return self.render_to_response(context)


class DocumentDeleteView(UserDocumentQuerySetMixin, DeleteView):
    template_name = "document_confirm_delete.html"
    context_object_name = "document"
    success_url = reverse_lazy("documents:list")

    def form_valid(self, form):
        document = self.get_object()
        document_id = document.pk
        file_name = document.file.name
        storage = document.file.storage
        response = super().form_valid(form)

        try:
            from services.rag.vector_store.chroma_store import ChromaVectorStore

            ChromaVectorStore().delete_document(document_id)
        except Exception:
            logger.warning(
                "Vector cleanup failed after document deletion.",
                extra={"document_id": document_id, "user_id": self.request.user.pk},
                exc_info=True,
            )
            messages.warning(
                self.request,
                "Document deleted, but vector cleanup could not be confirmed.",
            )

        if file_name and storage.exists(file_name):
            storage.delete(file_name)

        messages.success(self.request, "Document deleted successfully.")
        return response
