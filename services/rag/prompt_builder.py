class PromptBuilder:
    def build(self, question, retrieved_chunks):
        question = (question or "").strip()
        context = self._format_context(retrieved_chunks)

        return f"""You are DocuMind, an AI assistant for reviewing legal and financial documents.

Answer the user's question using only the provided document context.

Rules:
- Do not answer outside the provided context.
- If the context is insufficient, say: "The document does not contain enough information to answer that."
- Do not make unsupported claims or infer facts not present in the context.
- This is not final legal or financial advice.
- Encourage the user to consult a qualified professional for legal or financial decisions.
- Mention source page/chunk references when possible.

Question:
{question}

Document context:
{context}

Grounded answer:"""

    @staticmethod
    def _format_context(retrieved_chunks):
        if not retrieved_chunks:
            return "No relevant context was retrieved."

        blocks = []
        for chunk in retrieved_chunks:
            score = "N/A" if chunk.score is None else f"{chunk.score:.3f}"
            blocks.append(
                "\n".join(
                    [
                        f"[Page {chunk.page_number}, Chunk {chunk.chunk_index + 1}, Score {score}]",
                        chunk.content,
                    ]
                )
            )
        return "\n\n---\n\n".join(blocks)
