
import json
from typing import Dict, Any, Optional
from google import genai
from google.genai import types

from app.llm.base import LLMProvider
from app.config import settings
from app.utils.logging import setup_logger

logger = setup_logger(__name__)

class GeminiProvider(LLMProvider):
    def __init__(self):
        self.api_key = settings.gemini_api_key
        self.enabled = bool(self.api_key)
        self.model_id = settings.gemini_model
        self.client = None
        if self.enabled:
            self.client = genai.Client(api_key=self.api_key)
            logger.info(f"Gemini enabled with model: {self.model_id}")
        else:
            logger.warning("Gemini API key missing. Provider disabled.")

    def _config(self, system_prompt=None, json_mode=False):
        return types.GenerateContentConfig(
            system_instruction=system_prompt if system_prompt else None,
            response_mime_type="application/json" if json_mode else None,
        )

    def generate(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        if not self.enabled:
            raise RuntimeError("Gemini is disabled: GEMINI_API_KEY is missing.")
        response = self.client.models.generate_content(
            model=self.model_id,
            contents=prompt,
            config=self._config(system_prompt, False),
        )
        text = getattr(response, "text", None)
        if not text:
            raise RuntimeError("Gemini returned an empty response.")
        return text

    def generate_json(self, prompt: str, system_prompt: Optional[str] = None) -> Dict[str, Any]:
        if not self.enabled:
            raise RuntimeError("Gemini is disabled: GEMINI_API_KEY is missing.")
        response = self.client.models.generate_content(
            model=self.model_id,
            contents=prompt,
            config=self._config(system_prompt, True),
        )
        text = getattr(response, "text", None)
        if not text:
            raise RuntimeError("Gemini returned an empty JSON response.")
        text = text.strip()
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            # Defensive cleanup for providers/proxies that still return fenced JSON.
            if text.startswith("```"):
                text = text.split("\n", 1)[-1]
                text = text.rsplit("```", 1)[0]
            return json.loads(text.strip())

    def health_check(self) -> bool:
        return self.enabled
