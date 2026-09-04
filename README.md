# AI Documentary Story Engine — Detailed Foundation

A research-first, evidence-grounded, multi-agent documentary script production system.

## Design goal

The engine must behave like a small documentary production team:

1. Topic Analyst
2. Research Planner
3. Search Orchestrator
4. Source Collector
5. Source Quality Ranker
6. Evidence Extractor
7. Fact Verifier
8. Conflict Resolver
9. Story Researcher
10. Story Architect
11. Hook Competition
12. Multiple Independent Writers
13. Judge Panel
14. Master Editor
15. Red-Team Reviewer
16. Final Fact Validator
17. Pacing/Language QA
18. Exporter

The system is evidence-first. Model memory is not evidence.

## Target workflow

USER
→ Topic configuration
→ topic analysis
→ research plan
→ multi-query search
→ source collection
→ deduplication
→ source ranking
→ evidence extraction
→ atomic facts
→ independent verification
→ conflict detection
→ targeted re-research
→ story angles
→ story architecture
→ hooks
→ independent drafts
→ judges
→ master edit
→ red-team
→ repair
→ final validation
→ final script + sources + project archive

## Quality principles

- Never invent factual events, quotes, statistics, dialogue or private thoughts.
- Never silently resolve conflicting sources.
- Prefer primary/official/academic evidence where available.
- Separate fact, inference and narrative framing.
- Every important factual claim should be traceable to evidence.
- Use multiple models as independent opinions, not as a voting trick that hides bad evidence.
- Cache expensive operations.
- Retry transient failures.
- Never expose secrets.
- Never mark a feature complete unless it actually works and has tests.

## Future pipeline

The structured final output is designed for:

Script → scene planner → visual research → footage/image search → voice → subtitles → timeline → FFmpeg render.
