import logging

from django.conf import settings

from .exceptions import LLMError


logger = logging.getLogger(__name__)


class GroqLLMClient:
    default_model = "llama-3.3-70b-versatile"

    def __init__(self, api_key=None, model_name=None):
        self.api_key = api_key if api_key is not None else settings.GROQ_API_KEY
        self.model_name = model_name or self.default_model
        self.client = None

    def generate_answer(self, prompt):
        if not self.api_key:
            raise LLMError("GROQ_API_KEY is not configured.")

        try:
            response = self._client().chat.completions.create(
                model=self.model_name,
                messages=[
                    {
                        "role": "system",
                        "content": "You answer only from the provided document context.",
                    },
                    {"role": "user", "content": prompt},
                ],
                temperature=0.1,
                max_tokens=900,
            )
            answer = response.choices[0].message.content.strip()
            if not answer:
                raise LLMError("The language model returned an empty response.")
            return answer
        except LLMError:
            raise
        except Exception as exc:
            logger.warning(
                "Groq answer generation failed.",
                extra={"model_name": self.model_name},
                exc_info=True,
            )
            raise LLMError("Groq answer generation failed.") from exc

    def _client(self):
        if self.client is None:
            try:
                from groq import Groq
            except Exception as exc:
                logger.warning("Groq SDK import failed.", exc_info=True)
                raise LLMError("Groq SDK is not installed.") from exc
            self.client = Groq(api_key=self.api_key)
        return self.client
