from typing import Dict, Any, List, Optional
from app.llm.base import LLMProvider
from app.llm.gemini import GeminiProvider
from app.llm.groq import GroqProvider
from app.llm.openrouter import OpenRouterProvider
from app.config import settings
from app.utils.logging import setup_logger
from app.utils.retry import retry_call
import json

logger = setup_logger(__name__)

class LLMRouter:
    def __init__(self):
        # Initialize providers
        self.gemini = GeminiProvider()
        self.groq = GroqProvider()
        self.openrouter = OpenRouterProvider()

        # Priority fallback chain
        self.default_chain = [self.gemini, self.groq, self.openrouter]

    def _get_healthy_provider(self, preferred: LLMProvider = None) -> LLMProvider:
        if preferred and preferred.health_check():
            return preferred
        for provider in self.default_chain:
            if provider.health_check():
                return provider
        raise RuntimeError("CRITICAL ERROR: No AI providers are configured or healthy.")

    def get_healthy_providers(self, limit: Optional[int] = None) -> List[LLMProvider]:
        """Returns every currently healthy provider, in priority order.

        Used by agents that need genuinely independent evaluations (dual-model
        fact-checking, the judge panel) instead of a single provider with a
        fallback. Pass `limit` to cap how many are returned.
        """
        healthy = [p for p in self.default_chain if p.health_check()]
        if limit is not None:
            healthy = healthy[:limit]
        return healthy

    def call_provider_json(self, provider: LLMProvider, prompt: str, system_prompt: Optional[str] = None,
                            max_attempts: int = 3) -> Dict[str, Any]:
        """Call a *specific* provider's generate_json with retry on transient failures.

        Use this (instead of provider.generate_json directly) whenever a caller
        picked a provider itself via get_healthy_providers(), so transient
        errors (timeouts, rate limits) don't immediately count as that
        provider having failed.
        """
        return retry_call(lambda: provider.generate_json(prompt, system_prompt), max_attempts=max_attempts)

    def generate(self, prompt: str, system_prompt: Optional[str] = None, task: str = "default") -> str:
        provider = self._get_healthy_provider()
        try:
            return retry_call(lambda: provider.generate(prompt, system_prompt), max_attempts=3)
        except Exception as e:
            logger.error(f"Text generation failed on {provider.__class__.__name__}: {str(e)}")
            # Attempt Fallback
            fallback = self._get_healthy_provider(preferred=self.groq)
            return retry_call(lambda: fallback.generate(prompt, system_prompt), max_attempts=2)

    def generate_json(self, prompt: str, system_prompt: Optional[str] = None, task: str = "default") -> Dict[str, Any]:
        """Global method used by ALL agents (Research, Fact Check, Story, etc.)"""
        provider = self._get_healthy_provider()
        try:
            return retry_call(lambda: provider.generate_json(prompt, system_prompt), max_attempts=3)
        except Exception as e:
            logger.warning(f"JSON generation failed on {provider.__class__.__name__}: {str(e)}. Attempting fallback...")
            fallback = self._get_healthy_provider(preferred=self.groq)
            return retry_call(lambda: fallback.generate_json(prompt, system_prompt), max_attempts=2)

    def generate_for_writer(self, prompt: str, system_prompt: str, persona: str) -> Dict[str, Any]:
        """Specialized routing for the 4 independent AI Writers."""
        personas_mapping = {
            "Cinematic": self.openrouter if self.openrouter.health_check() else self.gemini,
            "Investigative": self.groq if self.groq.health_check() else self.gemini,
            "High-Retention": self.gemini,
            "Emotional": self.openrouter if self.openrouter.health_check() else self.gemini
        }
        provider = personas_mapping.get(persona, self.gemini)

        try:
            return retry_call(lambda: provider.generate_json(prompt, system_prompt), max_attempts=3)
        except Exception as e:
            logger.error(f"Writer persona {persona} failed on {provider.__class__.__name__}: {str(e)}. Falling back to Gemini.")
            return retry_call(lambda: self.gemini.generate_json(prompt, system_prompt), max_attempts=2)

router = LLMRouter()
