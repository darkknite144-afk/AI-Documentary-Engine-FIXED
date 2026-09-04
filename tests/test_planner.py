"""Covers app.agents.research_director, which replaced the old (removed)
app.research.planner.build_research_plan scaffold function."""
from app.agents.research_director import research_director
from app.llm.router import router
from tests.conftest import MockLLMProvider


def test_generate_plan_returns_llm_queries(monkeypatch):
    mock_response = {"topic": "Test Topic", "entities": ["A", "B"],
                      "queries": [f"q{i}" for i in range(15)]}
    good = MockLLMProvider(json_response=mock_response)
    monkeypatch.setattr(router, "default_chain", [good])
    plan = research_director.generate_plan("Test Topic")
    assert len(plan["queries"]) == 15


def test_generate_plan_fallback_meets_orchestrator_minimum(monkeypatch):
    # The orchestrator requires at least 5 queries before proceeding — the
    # fallback path must satisfy that even when every provider is down.
    dead = MockLLMProvider(healthy=False)
    monkeypatch.setattr(router, "default_chain", [dead])
    monkeypatch.setattr(router, "groq", dead)
    plan = research_director.generate_plan("Some Topic")
    assert len(plan["queries"]) >= 5


def test_generate_plan_fallback_on_empty_queries_from_llm(monkeypatch):
    empty = MockLLMProvider(json_response={"topic": "X", "queries": []})
    monkeypatch.setattr(router, "default_chain", [empty])
    plan = research_director.generate_plan("Some Topic")
    assert len(plan["queries"]) >= 5
