from dataclasses import dataclass
import re

from apps.documents.models import DocumentChunk

from .constants import DEFAULT_CHUNK_SIZE, DEFAULT_OVERLAP


@dataclass(frozen=True)
class ChunkResult:
    index: int
    page_number: int
    content: str
    character_count: int
    word_count: int


class TextChunker:
    def __init__(self, chunk_size=DEFAULT_CHUNK_SIZE, overlap=DEFAULT_OVERLAP):
        if overlap >= chunk_size:
            raise ValueError("Chunk overlap must be smaller than chunk size.")
        self.chunk_size = chunk_size
        self.overlap = overlap

    def chunk_pages(self, pages):
        chunks = []
        carry = ""

        for page in pages:
            page_text = self._normalize_text(page.text)
            if not page_text:
                continue

            text = self._join_text(carry, page_text)
            page_chunks = self._split_text(text)

            for content in page_chunks:
                chunks.append(
                    ChunkResult(
                        index=len(chunks),
                        page_number=page.page_number,
                        content=content,
                        character_count=len(content),
                        word_count=self._word_count(content),
                    )
                )

            carry = self._tail_overlap(text)

        return chunks

    def _split_text(self, text):
        units = self._semantic_units(text)
        chunks = []
        current = ""

        for unit in units:
            if not unit:
                continue

            if len(unit) > self.chunk_size:
                if current:
                    chunks.append(current.strip())
                    current = ""
                chunks.extend(self._split_long_unit(unit))
                continue

            candidate = self._join_text(current, unit)
            if len(candidate) <= self.chunk_size:
                current = candidate
            else:
                if current:
                    chunks.append(current.strip())
                current = self._join_text(self._tail_overlap(current), unit)

                if len(current) > self.chunk_size:
                    chunks.extend(self._split_long_unit(current))
                    current = ""

        if current:
            chunks.append(current.strip())

        return [chunk for chunk in chunks if chunk]

    def _semantic_units(self, text):
        paragraphs = [part.strip() for part in re.split(r"\n\s*\n", text) if part.strip()]
        units = []

        for paragraph in paragraphs:
            if len(paragraph) <= self.chunk_size:
                units.append(paragraph)
            else:
                units.extend(self._split_sentences(paragraph))

        return units

    @staticmethod
    def _split_sentences(text):
        sentences = re.split(r"(?<=[.!?])\s+", text)
        return [sentence.strip() for sentence in sentences if sentence.strip()]

    def _split_long_unit(self, text):
        chunks = []
        start = 0

        while start < len(text):
            end = min(start + self.chunk_size, len(text))
            if end < len(text):
                boundary = text.rfind(" ", start, end)
                if boundary > start:
                    end = boundary

            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)

            if end >= len(text):
                break

            start = max(end - self.overlap, start + 1)
            while start < len(text) and text[start].isspace():
                start += 1

        return chunks

    def _tail_overlap(self, text):
        text = text.strip()
        if not text or self.overlap <= 0:
            return ""
        if len(text) <= self.overlap:
            return text

        tail_start = max(0, len(text) - self.overlap)
        boundary = text.find(" ", tail_start)
        if boundary != -1:
            tail_start = boundary + 1

        return text[tail_start:].strip()

    @staticmethod
    def _normalize_text(text):
        text = text.replace("\r\n", "\n").replace("\r", "\n")
        lines = [line.strip() for line in text.splitlines()]
        return "\n".join(line for line in lines if line).strip()

    @staticmethod
    def _join_text(left, right):
        left = left.strip()
        right = right.strip()
        if left and right:
            return f"{left}\n\n{right}"
        return left or right

    @staticmethod
    def _word_count(text):
        return len(re.findall(r"\b\w+\b", text))


class ChunkService:
    def __init__(self, chunker=None):
        self.chunker = chunker or TextChunker()

    def create_chunks(self, document, extraction):
        DocumentChunk.objects.filter(document=document).delete()
        chunk_results = self.chunker.chunk_pages(extraction.pages)

        chunks = [
            DocumentChunk(
                document=document,
                chunk_index=result.index,
                page_number=result.page_number,
                content=result.content,
                character_count=result.character_count,
                word_count=result.word_count,
            )
            for result in chunk_results
        ]

        if chunks:
            DocumentChunk.objects.bulk_create(chunks)

        document.chunk_count = len(chunks)
        document.save(update_fields=["chunk_count", "updated_at"])

        return chunk_results
