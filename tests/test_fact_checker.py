from app.models.fact import Fact
from app.models.source import Source
from app.agents.fact_checker import fact_checker
from app.llm.router import router
from tests.conftest import MockLLMProvider


def _make_source():
    return Source(source_id="src_0", title="T", url="https://example.com", domain="example.com",
                  snippet="snippet text", content="Full scraped article content confirming the claim.")


def test_verify_fact_is_unverified_when_no_source_matches():
    fact = Fact(fact_id="f1", claim="Something happened", source_ids=["src_missing"])
    result = fact_checker.verify_fact(fact, [_make_source()])
    assert result.status == "UNVERIFIED"


def test_verify_fact_verified_when_both_models_agree(monkeypatch):
    fact = Fact(fact_id="f1", claim="Something happened", source_ids=["src_0"])
    agree = MockLLMProvider(json_response={"status": "VERIFIED", "reasoning": "matches evidence"})
    # This is the fix under test: fact_checker must use whichever providers
    # are actually healthy (via get_healthy_providers), not a hardcoded
    # router.gemini. Neither router.gemini nor router.groq is patched here.
    monkeypatch.setattr(router, "default_chain", [agree, agree])
    result = fact_checker.verify_fact(fact, [_make_source()])
    assert result.status == "VERIFIED"


def test_verify_fact_disputed_when_models_disagree(monkeypatch):
    fact = Fact(fact_id="f1", claim="Something happened", source_ids=["src_0"])
    verified_provider = MockLLMProvider(json_response={"status": "VERIFIED"})
    disputed_provider = MockLLMProvider(json_response={"status": "DISPUTED"})
    monkeypatch.setattr(router, "default_chain", [verified_provider, disputed_provider])
    result = fact_checker.verify_fact(fact, [_make_source()])
    assert result.status == "DISPUTED"


def test_verify_fact_works_with_only_one_provider_configured(monkeypatch):
    # Only one healthy provider (e.g. only Groq configured, no Gemini key).
    # Before the fix, this hard-failed because fact_checker called
    # router.gemini directly regardless of what was actually configured.
    only_one = MockLLMProvider(json_response={"status": "VERIFIED"})
    monkeypatch.setattr(router, "default_chain", [only_one])
    fact = Fact(fact_id="f1", claim="Something happened", source_ids=["src_0"])
    result = fact_checker.verify_fact(fact, [_make_source()])
    assert result.status == "VERIFIED"


def test_verify_fact_unverified_when_no_provider_is_healthy(monkeypatch):
    dead = MockLLMProvider(healthy=False)
    monkeypatch.setattr(router, "default_chain", [dead])
    fact = Fact(fact_id="f1", claim="Something happened", source_ids=["src_0"])
    result = fact_checker.verify_fact(fact, [_make_source()])
    assert result.status == "UNVERIFIED"
