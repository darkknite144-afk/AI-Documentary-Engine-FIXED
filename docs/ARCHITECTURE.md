# Architecture

## Layers

### `app/models/`
Pydantic domain models (`Source`, `Fact`). No business logic.

### `app/llm/`
LLM provider abstraction. `base.py` defines the interface; `gemini.py`, `groq.py`, `openrouter.py` implement it. `router.py` handles health-check-based fallback and retry.

### `app/search/`
Search provider abstraction. `base.py` defines the interface; `tavily.py`, `brave.py`, `duckduckgo.py` implement it. `aggregator.py` merges, deduplicates, and ranks results from all active providers.

### `app/research/`
`web_fetcher.py` — downloads and cleans source page content for the LLM.

### `app/agents/`
All the AI agents: research director, fact extractor, fact checker, conflict detector, angle generator, story architect, hook generator, writers, judge panel, master editor, red team, final fact checker, quality controller.

### `app/pipeline/`
`state.py` — the `PipelineState` model persisted to disk.
`orchestrator.py` — runs the full pipeline end-to-end.

### `app/storage/`
`json_store.py` — persists `PipelineState` to JSON files.

### `app/utils/`
`logging.py` and `retry.py` — shared utilities.
