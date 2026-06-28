from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.utils import timezone
from django.views.generic import ListView, TemplateView
import logging

from apps.documents.models import Document
from services.llm.exceptions import LLMError
from services.rag.answer_service import DocumentAnswerService
from services.rag.exceptions import EmbeddingError, RetrievalError

from .models import ChatMessage, ChatSession


logger = logging.getLogger(__name__)


class ReadyDocumentQuerySetMixin(LoginRequiredMixin):
    def get_ready_documents(self):
        return (
            Document.objects.for_user(self.request.user)
            .filter(
                status=Document.Status.READY,
                chunk_count__gt=0,
            )
            .select_related("user")
        )


class ChatHomeView(ReadyDocumentQuerySetMixin, ListView):
    template_name = "chat.html"
    context_object_name = "documents"

    def get_queryset(self):
        return self.get_ready_documents()


class ChatHistoryView(LoginRequiredMixin, ListView):
    template_name = "history.html"
    context_object_name = "sessions"

    def get_queryset(self):
        return (
            ChatSession.objects.filter(user=self.request.user)
            .select_related("document")
            .prefetch_related("messages")
        )


class ChatDocumentView(ReadyDocumentQuerySetMixin, TemplateView):
    template_name = "chat_document.html"

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        self.document = self.get_ready_documents().filter(
            pk=kwargs["document_id"],
        ).first()
        if self.document is None:
            messages.error(request, "This document is not ready for chat.")
            return redirect("chat:home")
        self.session = self.get_or_create_session()
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        messages_qs = self.session.messages.all()
        context["document"] = self.document
        context["session"] = self.session
        context["chat_messages"] = messages_qs
        context["source_count"] = sum(1 for message in messages_qs if message.sources)
        return context

    def post(self, request, *args, **kwargs):
        question = request.POST.get("question", "").strip()
        if not question:
            messages.error(request, "Enter a question before sending.")
            return redirect("chat:document", document_id=self.document.pk)

        ChatMessage.objects.create(
            session=self.session,
            role=ChatMessage.Role.USER,
            content=question,
        )

        try:
            answer_result = DocumentAnswerService().answer(
                document=self.document,
                question=question,
                user=request.user,
                top_k=5,
            )
            ChatMessage.objects.create(
                session=self.session,
                role=ChatMessage.Role.ASSISTANT,
                content=answer_result.answer,
                model_name=answer_result.model_name,
                sources=[
                    {
                        "page_number": source.page_number,
                        "chunk_index": source.chunk_index,
                        "score": source.score,
                        "content_preview": source.content_preview,
                    }
                    for source in answer_result.sources
                ],
            )
            self.touch_session()
        except (LLMError, RetrievalError, EmbeddingError) as exc:
            logger.warning(
                "Chat answer generation failed.",
                extra={
                    "document_id": self.document.pk,
                    "session_id": self.session.pk,
                    "user_id": request.user.pk,
                },
                exc_info=True,
            )
            messages.error(request, str(exc))
            self.touch_session()

        return redirect("chat:document", document_id=self.document.pk)

    def get_or_create_session(self):
        session = (
            ChatSession.objects.filter(
                user=self.request.user,
                document=self.document,
            )
            .prefetch_related("messages")
            .order_by("-updated_at")
            .first()
        )
        if session:
            return session

        return ChatSession.objects.create(
            user=self.request.user,
            document=self.document,
            title=f"Chat about {self.document.title}",
        )

    def touch_session(self):
        self.session.updated_at = timezone.now()
        self.session.save(update_fields=["updated_at"])
