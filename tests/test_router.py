import pytest
from app.llm.router import router
from tests.conftest import MockLLMProvider


def test_get_healthy_providers_filters_unhealthy(monkeypatch):
    dead = MockLLMProvider(healthy=False)
    alive = MockLLMProvider(healthy=True)
    monkeypatch.setattr(router, "default_chain", [dead, alive])
    healthy = router.get_healthy_providers()
    assert healthy == [alive]


def test_get_healthy_providers_respects_limit(monkeypatch):
    providers = [MockLLMProvider(), MockLLMProvider(), MockLLMProvider()]
    monkeypatch.setattr(router, "default_chain", providers)
    assert len(router.get_healthy_providers(limit=2)) == 2


def test_generate_json_uses_first_healthy_provider(monkeypatch):
    good = MockLLMProvider(json_response={"status": "ok"})
    monkeypatch.setattr(router, "default_chain", [good])
    assert router.generate_json("prompt") == {"status": "ok"}


def test_generate_json_falls_back_when_primary_fails(monkeypatch):
    bad = MockLLMProvider(fail=True, healthy=True)
    good = MockLLMProvider(json_response={"status": "fallback"}, healthy=True)
    monkeypatch.setattr(router, "default_chain", [bad])
    monkeypatch.setattr(router, "groq", good)
    assert router.generate_json("prompt") == {"status": "fallback"}


def test_generate_json_raises_when_nothing_is_healthy(monkeypatch):
    dead = MockLLMProvider(healthy=False)
    monkeypatch.setattr(router, "default_chain", [dead])
    monkeypatch.setattr(router, "groq", dead)
    with pytest.raises(RuntimeError):
        router.generate_json("prompt")


def test_call_provider_json_retries_transient_failures():
    calls = {"n": 0}

    class FlakyProvider(MockLLMProvider):
        def generate_json(self, prompt, system_prompt=None):
            calls["n"] += 1
            if calls["n"] < 2:
                raise RuntimeError("temporary")
            return {"ok": True}

    result = router.call_provider_json(FlakyProvider(), "prompt", max_attempts=3)
    assert result == {"ok": True}
    assert calls["n"] == 2
