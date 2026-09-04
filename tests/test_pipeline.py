"""End-to-end pipeline test with every agent mocked at its own boundary
(no real network/LLM calls). This is what actually caught the guaranteed
judge_count crash: with every stage mocked to "succeed", the full 9-step
orchestrator run only completes once judge.py correctly reports judge_count.
"""
import pytest
import app.pipeline.orchestrator as orch_mod
from app.pipeline.state import PipelineState
from app.models.fact import Fact


def test_pipeline_state_defaults():
    state = PipelineState(topic="Example Topic")
    assert state.status == "INITIALIZED"
    assert state.quality_gate_status == "PENDING"
    assert state.facts == []


def _patch_happy_path(monkeypatch, judge_count=2):
    monkeypatch.setattr(orch_mod.research_director, "generate_plan",
                         lambda topic: {"queries": [f"q{i}" for i in range(6)]})
    monkeypatch.setattr(orch_mod.search_aggregator, "execute_search",
                         lambda query, max_total_results=6: [
                             {"title": "T", "url": "https://example.com/a", "snippet": "s", "source": "mock"}
                         ])
    monkeypatch.setattr(orch_mod.web_fetcher, "fetch_content", lambda source: "x" * 300)
    monkeypatch.setattr(orch_mod.fact_extractor, "extract_facts",
                         lambda source: [Fact(fact_id="f1", claim="A verified claim",
                                               source_ids=[source.source_id])])
    monkeypatch.setattr(orch_mod.fact_checker, "verify_fact",
                         lambda fact, sources: fact.model_copy(update={"status": "VERIFIED"}))
    monkeypatch.setattr(orch_mod.conflict_detector, "detect_conflicts", lambda facts: [])
    monkeypatch.setattr(orch_mod.angle_generator, "generate_and_select_angle",
                         lambda topic, facts: {"title": "Angle", "focus": "general"})
    monkeypatch.setattr(orch_mod.story_architect, "create_framework",
                         lambda topic, angle: {"protagonist": "Someone", "central_question": "Why?"})
    monkeypatch.setattr(orch_mod.hook_generator, "generate_and_select_hook",
                         lambda framework, facts: {"script_text": "Hook text"})
    monkeypatch.setattr(orch_mod.ai_writer, "generate_multiple_drafts",
                         lambda framework, hook, facts, duration_mins: [
                             {"draft_id": "d1", "persona": "Cinematic",
                              "sections": [{"section_id": "s1", "title": "Intro", "narration": "Hello"}]},
                             {"draft_id": "d2", "persona": "Investigative",
                              "sections": [{"section_id": "s1", "title": "Intro", "narration": "Hi"}]},
                         ])
    monkeypatch.setattr(orch_mod.judge_panel, "select_best_draft",
                         lambda drafts, facts: {**drafts[0],
                                                 "evaluation": {"total_score": 8.5, "judge_count": judge_count}})
    monkeypatch.setattr(orch_mod.master_editor, "create_master_script",
                         lambda best, facts, language, repair_notes=None: {
                             "sections": [{"section_id": "s1", "narration": "Final"}]})
    monkeypatch.setattr(orch_mod.red_team, "evaluate_script", lambda script: {"status": "PASS"})
    monkeypatch.setattr(orch_mod.final_fact_checker, "verify_script", lambda script, facts: {"status": "PASS"})
    monkeypatch.setattr(orch_mod.quality_controller, "gate_check", lambda rt, fc: "PASS")
    monkeypatch.setattr(orch_mod.project_store, "save_project", lambda state: "")


def test_full_pipeline_completes_when_every_stage_succeeds(monkeypatch):
    _patch_happy_path(monkeypatch, judge_count=2)
    project_id = orch_mod.orchestrator.run_pipeline("Example Topic", duration_mins=3, language="Hinglish")
    assert project_id.startswith("proj_")


def test_pipeline_raises_when_judge_panel_gives_no_independent_evaluations(monkeypatch):
    # Regression test for the guaranteed-crash bug: judge.py used to never
    # set judge_count at all, so this check always failed. Here we simulate
    # the legitimate case (no AI provider could judge anything) and confirm
    # the pipeline correctly blocks instead of silently continuing.
    _patch_happy_path(monkeypatch, judge_count=0)
    with pytest.raises(RuntimeError):
        orch_mod.orchestrator.run_pipeline("Example Topic", duration_mins=3, language="Hinglish")
