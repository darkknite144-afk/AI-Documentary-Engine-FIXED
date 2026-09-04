
import json
from typing import Dict, Any, Optional
from groq import Groq

from app.llm.base import LLMProvider
from app.config import settings
from app.utils.logging import setup_logger

logger = setup_logger(__name__)

class GroqProvider(LLMProvider):
    def __init__(self):
        self.api_key = settings.groq_api_key
        self.enabled = bool(self.api_key)
        self.model_id = settings.groq_model
        self.client = Groq(api_key=self.api_key) if self.enabled else None
        if self.enabled:
            logger.info(f"Groq enabled with model: {self.model_id}")
        else:
            logger.warning("Groq API key missing. Provider disabled.")

    def _messages(self, prompt, system_prompt):
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        return messages

    def generate(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        if not self.enabled:
            raise RuntimeError("Groq is disabled: GROQ_API_KEY is missing.")
        completion = self.client.chat.completions.create(
            model=self.model_id,
            messages=self._messages(prompt, system_prompt),
            temperature=0.7,
        )
        text = completion.choices[0].message.content
        if not text:
            raise RuntimeError("Groq returned an empty response.")
        return text

    def generate_json(self, prompt: str, system_prompt: Optional[str] = None) -> Dict[str, Any]:
        if not self.enabled:
            raise RuntimeError("Groq is disabled: GROQ_API_KEY is missing.")
        completion = self.client.chat.completions.create(
            model=self.model_id,
            messages=self._messages(prompt, system_prompt),
            temperature=0.1,
            response_format={"type": "json_object"},
        )
        text = completion.choices[0].message.content
        if not text:
            raise RuntimeError("Groq returned an empty JSON response.")
        return json.loads(text)

    def health_check(self) -> bool:
        return self.enabled
