
import traceback
from app.pipeline.state import PipelineState
from app.storage.json_store import project_store
from app.utils.logging import setup_logger
from app.config import settings

from app.agents.research_director import research_director
from app.search.aggregator import search_aggregator
from app.research.web_fetcher import web_fetcher
from app.models.source import Source
from app.agents.fact_extractor import fact_extractor
from app.agents.fact_checker import fact_checker
from app.agents.conflict_detector import conflict_detector
from app.agents.angle_generator import angle_generator
from app.agents.story_architect import story_architect
from app.agents.hook_generator import hook_generator
from app.agents.writer import ai_writer
from app.agents.judge import judge_panel
from app.agents.master_editor import master_editor
from app.agents.red_team import red_team
from app.agents.final_fact_checker import final_fact_checker
from app.agents.quality_controller import quality_controller

logger = setup_logger(__name__)

class PipelineOrchestrator:
    def run_pipeline(self, topic: str, duration_mins: int = 5, language: str = "Hinglish") -> str:
        state = PipelineState(topic=topic)
        state.status = "RUNNING"
        project_store.save_project(state)
        logger.info(f"🚀 START: {topic}")

        try:
            # 1. Research planning
            state.research_plan = research_director.generate_plan(topic)
            queries = state.research_plan.get("queries", [])
            if len(queries) < 5:
                raise RuntimeError("Research planning produced fewer than 5 queries.")
            logger.info(f"✓ Research plan: {len(queries)} targeted queries")

            # 2. Multi-provider search
            raw_sources = []
            # Use all configured research queries, capped by config.
            for query in queries[:settings.max_research_queries]:
                raw_sources.extend(search_aggregator.execute_search(query, max_total_results=6))
            if not raw_sources:
                raise RuntimeError("Search returned zero relevant sources.")

            # global deduplication by URL
            dedup = {}
            for rs in raw_sources:
                dedup[rs.get("url","")] = rs
            source_objects = []
            for idx, rs in enumerate(list(dedup.values())[:settings.max_sources]):
                source_objects.append(Source(
                    source_id=f"src_{idx}",
                    title=rs.get("title",""),
                    url=rs.get("url",""),
                    domain=rs.get("source", rs.get("domain","unknown")),
                    snippet=rs.get("snippet",""),
                    authority_score=float(rs.get("authority_score",0))
                ))
            logger.info(f"✓ Sources collected: {len(source_objects)}")

            # 2.5 Web extraction
            fetched = 0
            for src in source_objects:
                try:
                    content = web_fetcher.fetch_content(src)
                    if content and len(content) > 200:
                        fetched += 1
                except Exception as e:
                    logger.warning(f"Fetch failed for {src.url}: {e}")
                state.sources.append(src.model_dump())
            if fetched == 0:
                raise RuntimeError("No source page produced usable content.")
            project_store.save_project(state)
            logger.info(f"✓ Web content fetched: {fetched}/{len(source_objects)}")

            # 3. Facts
            all_facts = []
            for src in source_objects:
                try:
                    all_facts.extend(fact_extractor.extract_facts(src))
                except Exception as e:
                    logger.warning(f"Fact extraction failed for {src.url}: {e}")
            if not all_facts:
                raise RuntimeError("Fact extraction returned zero facts.")
            logger.info(f"✓ Raw atomic facts: {len(all_facts)}")

            verified = []
            verified_strings = []
            for fact in all_facts:
                checked = fact_checker.verify_fact(fact, source_objects)
                verified.append(checked)
                if checked.status == "VERIFIED":
                    verified_strings.append(checked.claim)
            if not verified_strings:
                raise RuntimeError("No facts reached VERIFIED status. Script generation is blocked.")
            state.facts = [f.model_dump() for f in verified]
            project_store.save_project(state)
            logger.info(f"✓ Verified facts: {len(verified_strings)}")

            # 4. Conflicts
            state.conflicts = conflict_detector.detect_conflicts(verified)
            logger.info(f"✓ Conflicts detected: {len(state.conflicts)}")
            project_store.save_project(state)

            # 5. Story design
            state.angle = angle_generator.generate_and_select_angle(topic, verified_strings)
            state.framework = story_architect.create_framework(topic, state.angle)
            state.hook = hook_generator.generate_and_select_hook(state.framework, verified_strings)
            if not state.framework.get("protagonist") or not state.hook.get("script_text"):
                raise RuntimeError("Story design produced incomplete output.")
            project_store.save_project(state)

            # 6. Independent writers
            state.drafts = ai_writer.generate_multiple_drafts(
                state.framework, state.hook, verified_strings, duration_mins
            )
            if len(state.drafts) < min(2, settings.max_writer_agents):
                raise RuntimeError(f"Only {len(state.drafts)} writer drafts succeeded.")
            logger.info(f"✓ Writer drafts: {len(state.drafts)}")

            # 7. Independent judge panel
            best = judge_panel.select_best_draft(state.drafts, verified_strings)
            if not best.get("evaluation", {}).get("judge_count"):
                raise RuntimeError("Judge panel produced no independent evaluations.")
            state.best_draft_id = best["draft_id"]
            project_store.save_project(state)

            # 8. Master editor
            state.master_script = master_editor.create_master_script(best, verified_strings, language)
            if not state.master_script.get("sections"):
                raise RuntimeError("Master Editor returned an empty script.")
            project_store.save_project(state)

            # 9. Red team + final fact check
            state.red_team_report = red_team.evaluate_script(state.master_script)
            state.fact_check_report = final_fact_checker.verify_script(
                state.master_script, verified_strings
            )
            state.quality_gate_status = quality_controller.gate_check(
                state.red_team_report, state.fact_check_report
            )
            project_store.save_project(state)

            # 9.5 Repair loop: if QA flagged issues, send the script back to the
            # Master Editor with the specific feedback and re-check, instead of
            # immediately giving up. Bounded by max_rewrite_rounds.
            repair_attempt = 0
            while state.quality_gate_status != "PASS" and repair_attempt < settings.max_rewrite_rounds:
                repair_attempt += 1
                logger.info(f"⚠ Quality gate failed — repair round {repair_attempt}/{settings.max_rewrite_rounds}")

                notes = []
                if state.red_team_report.get("feedback"):
                    notes.append(f"Red team feedback: {state.red_team_report['feedback']}")
                if state.red_team_report.get("issues"):
                    notes.append("Issues to fix: " + "; ".join(state.red_team_report["issues"]))
                if state.fact_check_report.get("unsupported_claims"):
                    notes.append("Remove or correct these unsupported claims: " + "; ".join(state.fact_check_report["unsupported_claims"]))
                repair_notes = "\n".join(notes) or "Quality review flagged issues. Improve pacing, accuracy, and flow."

                state.master_script = master_editor.create_master_script(
                    state.master_script, verified_strings, language, repair_notes=repair_notes
                )
                state.red_team_report = red_team.evaluate_script(state.master_script)
                state.fact_check_report = final_fact_checker.verify_script(
                    state.master_script, verified_strings
                )
                state.quality_gate_status = quality_controller.gate_check(
                    state.red_team_report, state.fact_check_report
                )
                project_store.save_project(state)
                logger.info(f"Repair round {repair_attempt} result: {state.quality_gate_status}")

            state.status = "COMPLETED" if state.quality_gate_status == "PASS" else "NEEDS_REVIEW"
            project_store.save_project(state)
            logger.info(f"🏁 FINISHED: {state.project_id} | {state.status}")
            return state.project_id

        except Exception:
            logger.error("❌ PIPELINE FAILED:\n" + traceback.format_exc())
            state.status = "FAILED"
            project_store.save_project(state)
            raise

orchestrator = PipelineOrchestrator()
