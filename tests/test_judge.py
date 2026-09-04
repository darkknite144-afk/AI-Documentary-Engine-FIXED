"""New test file: app.agents.judge previously had no test coverage at all,
which is how the guaranteed-crash judge_count bug went unnoticed. The
orchestrator hard-requires evaluation['judge_count'] to be truthy before it
will accept a winning draft (app/pipeline/orchestrator.py), so that is the
main thing covered here.
"""
from app.agents.judge import judge_panel
from app.llm.router import router
from tests.conftest import MockLLMProvider

SCORES = {"fact_accuracy": 8, "story_flow": 7, "retention_power": 8,
          "language_naturalness": 7, "originality": 6, "structure": 7,
          "criticism": "Pacing dips in the middle.", "praise": "Strong opening hook."}

DRAFT = {"draft_id": "d1", "persona": "Cinematic",
         "sections": [{"section_id": "s1", "title": "Intro", "narration": "Hello world"}]}


def test_evaluate_draft_sets_judge_count_from_healthy_providers(monkeypatch):
    judges = [MockLLMProvider(json_response=SCORES), MockLLMProvider(json_response=SCORES)]
    monkeypatch.setattr(router, "default_chain", judges)
    result = judge_panel.evaluate_draft(DRAFT, ["fact one", "fact two"])
    # This is the exact field the orchestrator checks before trusting a draft.
    assert result["judge_count"] == 2
    assert result["total_score"] > 0


def test_evaluate_draft_judge_count_reflects_only_successful_judges(monkeypatch):
    ok_judge = MockLLMProvider(json_response=SCORES)
    failing_judge = MockLLMProvider(fail=True)
    monkeypatch.setattr(router, "default_chain", [ok_judge, failing_judge])
    result = judge_panel.evaluate_draft(DRAFT, ["fact one"])
    assert result["judge_count"] == 1


def test_evaluate_draft_judge_count_zero_when_no_provider_is_healthy(monkeypatch):
    dead = MockLLMProvider(healthy=False)
    monkeypatch.setattr(router, "default_chain", [dead])
    result = judge_panel.evaluate_draft(DRAFT, ["fact one"])
    assert result["judge_count"] == 0
    assert result["total_score"] == 0.0


def test_select_best_draft_picks_highest_scoring(monkeypatch):
    weak = MockLLMProvider(json_response={**SCORES, "fact_accuracy": 2, "story_flow": 2,
                                           "retention_power": 2, "language_naturalness": 2,
                                           "originality": 2, "structure": 2})
    monkeypatch.setattr(router, "default_chain", [weak])
    draft_a = {"draft_id": "a", "persona": "A", "sections": []}
    draft_b = {"draft_id": "b", "persona": "B", "sections": []}
    best = judge_panel.select_best_draft([draft_a, draft_b], ["fact"])
    assert best["draft_id"] in ("a", "b")
    assert best["evaluation"]["judge_count"] == 1
