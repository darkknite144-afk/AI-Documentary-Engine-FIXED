
import json
import httpx
from typing import Dict, Any, Optional

from app.llm.base import LLMProvider
from app.config import settings
from app.utils.logging import setup_logger

logger = setup_logger(__name__)

class OpenRouterProvider(LLMProvider):
    def __init__(self):
        self.api_key = settings.openrouter_api_key
        self.enabled = bool(self.api_key)
        self.base_url = "https://openrouter.ai/api/v1/chat/completions"
        self.default_model = settings.openrouter_default_model
        if self.enabled:
            logger.info(f"OpenRouter enabled with model: {self.default_model}")
        else:
            logger.warning("OpenRouter API key missing. Provider disabled.")

    def _make_request(self, messages, specific_model=None, json_mode=False):
        if not self.enabled:
            raise RuntimeError("OpenRouter is disabled: OPENROUTER_API_KEY is missing.")
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/pocketlists/AI-Documentary-Engine-DETAILED",
            "X-Title": "AI Documentary Engine",
        }
        payload = {
            "model": specific_model or self.default_model,
            "messages": messages,
            "temperature": 0.2 if json_mode else 0.7,
        }
        if json_mode:
            payload["response_format"] = {"type": "json_object"}

        with httpx.Client(timeout=90.0) as client:
            response = client.post(self.base_url, headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()
        try:
            text = data["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError) as exc:
            raise RuntimeError(f"OpenRouter returned an unexpected response: {data}") from exc
        if not text:
            raise RuntimeError("OpenRouter returned an empty response.")
        return text

    def generate(self, prompt: str, system_prompt: Optional[str] = None, specific_model: str = None) -> str:
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        return self._make_request(messages, specific_model, False)

    def generate_json(self, prompt: str, system_prompt: Optional[str] = None, specific_model: str = None) -> Dict[str, Any]:
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        text = self._make_request(messages, specific_model, True).strip()
        if text.startswith("```"):
            text = text.split("\n", 1)[-1].rsplit("```", 1)[0]
        return json.loads(text.strip())

    def health_check(self) -> bool:
        return self.enabled
