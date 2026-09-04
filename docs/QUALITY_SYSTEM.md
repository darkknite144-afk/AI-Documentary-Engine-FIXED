# Quality System

## Evidence-first principle
Model memory is not evidence. Every factual claim in the final script must be traceable to a fetched source.

## Layers of defense
1. **Fact extraction** — atomic facts pulled from scraped source text.
2. **Independent verification** — dual-model consensus on each fact against the source text.
3. **Conflict detection** — flags contradictions between verified facts.
4. **Final fact-check** — the polished master script is re-checked against the verified knowledge base.

## Quality gate
The `QualityController` requires both the red-team report and the final fact-check to PASS. If either fails, the script enters a repair loop (bounded by `max_rewrite_rounds`) before being marked `NEEDS_REVIEW`.
