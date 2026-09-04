"""Shared test fixtures/doubles.

There is no real MockLLMProvider in app/llm (an earlier test suite assumed
one existed at app.llm.mock, but that module was never created). Since a
provider test double is only useful for tests, it lives here instead of in
app/ code.
"""
from typing import Dict, Any, Optional
from app.llm.base import LLMProvider


class MockLLMProvider(LLMProvider):
    """Test double conforming to the real LLMProvider interface.

    - healthy=False makes health_check() return False (simulates a missing API key).
    - fail=True makes every call raise, to exercise retry/fallback paths.
    - json_response / text_response control what a successful call returns.
    """

    def __init__(self, json_response: Optional[Dict[str, Any]] = None, text_response: str = "ok",
                 healthy: bool = True, fail: bool = False):
        self.json_response = json_response if json_response is not None else {}
        self.text_response = text_response
        self.healthy = healthy
        self.fail = fail
        self.calls = 0

    def generate(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        self.calls += 1
        if self.fail:
            raise RuntimeError("mock provider failure")
        return self.text_response

    def generate_json(self, prompt: str, system_prompt: Optional[str] = None) -> Dict[str, Any]:
        self.calls += 1
        if self.fail:
            raise RuntimeError("mock provider failure")
        return self.json_response

    def health_check(self) -> bool:
        return self.healthy
