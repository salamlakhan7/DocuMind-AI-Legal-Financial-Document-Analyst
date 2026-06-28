from dataclasses import dataclass
import logging

from apps.documents.models import Document
from services.llm.exceptions import LLMError
from services.llm.groq_client import GroqLLMClient

from .exceptions import RetrievalError
from .prompt_builder import PromptBuilder
from .retriever import DocumentRetriever


logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class AnswerSource:
    page_number: int
    chunk_index: int
    score: float | None
    content_preview: str


@dataclass(frozen=True)
class AnswerResult:
    question: str
    answer: str
    sources: list[AnswerSource]
    model_name: str
    retrieved_count: int


class DocumentAnswerService:
    def __init__(self, retriever=None, prompt_builder=None, llm_client=None):
        self.retriever = retriever or DocumentRetriever()
        self.prompt_builder = prompt_builder or PromptBuilder()
        self.llm_client = llm_client or GroqLLMClient()

    def answer(self, document, question, user, top_k=5):
        question = (question or "").strip()
        if not question:
            raise RetrievalError("Enter a question to generate an answer.")

        if document.user_id != user.pk and not Document.objects.for_user(user).filter(pk=document.pk).exists():
            raise RetrievalError("You do not have access to this document.")

        retrieved_chunks = self.retriever.retrieve(
            document=document,
            question=question,
            top_k=top_k,
        )
        prompt = self.prompt_builder.build(question, retrieved_chunks)

        try:
            answer = self.llm_client.generate_answer(prompt)
        except LLMError:
            logger.warning(
                "LLM answer generation failed.",
                extra={"document_id": document.pk, "user_id": user.pk},
                exc_info=True,
            )
            raise

        return AnswerResult(
            question=question,
            answer=answer,
            sources=[
                AnswerSource(
                    page_number=chunk.page_number,
                    chunk_index=chunk.chunk_index,
                    score=chunk.score,
                    content_preview=chunk.content[:300],
                )
                for chunk in retrieved_chunks
            ],
            model_name=self.llm_client.model_name,
            retrieved_count=len(retrieved_chunks),
        )
