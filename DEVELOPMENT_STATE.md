# Development State

This repository is intentionally incremental.

## Phase 0 — Contracts and safety
- [x] Repository layout
- [x] Environment configuration
- [x] Domain models (`app/models/source.py`, `app/models/fact.py` — the older,
      conflicting `app/models/domain.py` scaffold has been removed)
- [x] Provider interfaces
- [x] Evidence model
- [x] Project persistence contract
- [x] Retry/error contracts (now actually wired into `app/llm/router.py`)
- [x] Test scaffold
- [x] GitHub Actions scaffold

## Phase 1 — Core implementation
Code-complete and covered by mocked unit tests in `tests/` (no real API keys
required to run them). **Not yet confirmed with a live `pytest` run** — this
was done in a sandboxed environment with no network access, so run
`pip install -r requirements.txt && pytest` yourself to get the final green
check before marking these fully `[x]`.

- [x] Real LLM adapters (Gemini/Groq/OpenRouter) — `gemini_model` default was
      fixed from an invalid `gemini-3.6-flash` to `gemini-3.5-flash`
- [x] Search adapters (Tavily/Brave/DuckDuckGo) — Brave was coded but never
      wired in and was missing its config field; both are fixed. Aggregator
      now merges results from every active provider instead of stopping at
      the first one that returns anything.
- [x] Web extraction
- [x] Deduplication (`app/search/aggregator.py`; the old, unused
      `app/research/deduplicate.py` scaffold was removed)
- [ ] Source scoring — `app/scoring/source_score.py` was dead code, never
      wired into the pipeline; removed rather than left as misleading cruft.
      Still genuinely not implemented.
- [x] Fact extraction
- [x] Independent verification — fixed a bug where this only worked if a
      Gemini key was configured (hardcoded), regardless of what was healthy
- [x] Conflict resolver
- [x] Story architecture — fixed a fallback path that could omit the
      `protagonist` field and hard-fail the pipeline
- [x] Multi-writer generation
- [x] Judge panel — was previously a **guaranteed crash on every run**
      (evaluated with one model call but never set `judge_count`, which the
      orchestrator always required). Rebuilt as an actual panel: queries
      every healthy provider independently, averages their scores, and
      reports how many judges really responded.
- [x] Master editor
- [x] Red-team loop — previously the report was generated but nothing acted
      on it. The orchestrator now sends flagged scripts back to the Master
      Editor with the specific feedback for up to `max_rewrite_rounds`
      repair passes before giving up.
- [x] Final validator
- [ ] Mobile UI — still not started (`app/ui/` is a placeholder)

## Known gaps / left for a later phase
- `app/agents/topic_analyzer.py` and its Phase-0-era test coverage were
  removed as dead code (never called by the orchestrator).
- Scene planning, visual research, voice/subtitles/video rendering (Phases
  9-10) are not started.

A checkbox may only be marked complete after the feature is implemented and tested.
