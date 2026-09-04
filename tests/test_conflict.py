from app.models.fact import Fact
from app.agents.conflict_detector import conflict_detector
from app.llm.router import router
from tests.conftest import MockLLMProvider


def test_detect_conflicts_skips_llm_call_with_fewer_than_two_facts():
    facts = [Fact(fact_id="f1", claim="Event happened in 1990", status="VERIFIED")]
    assert conflict_detector.detect_conflicts(facts) == []


def test_detect_conflicts_parses_llm_response(monkeypatch):
    facts = [
        Fact(fact_id="f1", claim="The bridge opened in 1990", status="VERIFIED"),
        Fact(fact_id="f2", claim="The bridge opened in 1991", status="VERIFIED"),
    ]
    mock_response = {"conflicts": [
        {"type": "date_conflict", "description": "Different opening years", "fact_ids": ["f1", "f2"]}
    ]}
    good = MockLLMProvider(json_response=mock_response)
    monkeypatch.setattr(router, "default_chain", [good])

    conflicts = conflict_detector.detect_conflicts(facts)
    assert len(conflicts) == 1
    assert conflicts[0]["type"] == "date_conflict"


def test_detect_conflicts_returns_empty_on_llm_failure(monkeypatch):
    facts = [
        Fact(fact_id="f1", claim="A", status="VERIFIED"),
        Fact(fact_id="f2", claim="B", status="VERIFIED"),
    ]
    dead = MockLLMProvider(healthy=False)
    monkeypatch.setattr(router, "default_chain", [dead])
    monkeypatch.setattr(router, "groq", dead)
    assert conflict_detector.detect_conflicts(facts) == []
