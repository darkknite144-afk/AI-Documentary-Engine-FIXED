from typing import List, Dict, Any, Optional
from app.llm.router import router
from app.llm.base import LLMProvider
from app.config import settings
from app.utils.logging import setup_logger

logger = setup_logger(__name__)

class JudgePanel:
    def __init__(self):
        # Weighted scoring system
        self.weights = {
            "fact_accuracy": 0.25,
            "story_flow": 0.20,
            "retention_power": 0.20,
            "language_naturalness": 0.15,
            "originality": 0.10,
            "structure": 0.10
        }

    def _build_prompt(self, script_text: str, facts_context: str) -> str:
        return f"""
        Evaluate this documentary script draft strictly.

        Verified Facts:
        {facts_context}

        Script Draft:
        {script_text[:4000]}

        Provide a score from 0.0 to 10.0 for the following criteria:
        - 'fact_accuracy': Is it grounded in the provided facts without inventing details?
        - 'story_flow': Does it read like an engaging, natural story (not a motivational speech)?
        - 'retention_power': Will it keep a YouTube audience hooked?
        - 'language_naturalness': Does it sound conversational and human?
        - 'originality': Is the approach fresh?
        - 'structure': Is the pacing smooth?

        Also provide:
        - 'criticism': One sentence on what is wrong.
        - 'praise': One sentence on what works well.

        Return a JSON object with the exact keys: fact_accuracy, story_flow, retention_power, language_naturalness, originality, structure, criticism, praise.
        """

    def _run_single_judge(self, provider: LLMProvider, prompt: str) -> Optional[Dict[str, Any]]:
        try:
            return router.call_provider_json(
                provider,
                prompt,
                system_prompt="You are a strict, objective YouTube script critic. Output valid JSON only."
            )
        except Exception as e:
            logger.warning(f"Judge on {provider.__class__.__name__} failed: {str(e)}")
            return None

    def evaluate_draft(self, draft: Dict[str, Any], facts: List[str]) -> Dict[str, Any]:
        persona = draft.get('persona', 'unknown')
        logger.info(f"Judging draft from persona: {persona}")

        # Extract text for the LLM to read
        sections = draft.get("sections", [])
        script_text = "\n".join([f"{s.get('title')}: {s.get('narration')}" for s in sections])
        facts_context = "\n".join(facts[:15]) if facts else "No facts available."
        prompt = self._build_prompt(script_text, facts_context)

        # A real "panel" needs genuinely independent judges. We ask every
        # currently healthy provider (up to max_judge_agents) instead of a
        # single model, and average their scores. judge_count reflects how
        # many of them actually returned a usable evaluation, which is what
        # the pipeline checks before trusting the result.
        healthy_providers = router.get_healthy_providers(limit=settings.max_judge_agents)
        if not healthy_providers:
            logger.error("No healthy AI providers available to judge this draft.")
            return {"total_score": 0.0, "judge_count": 0, "draft_id": draft.get("draft_id"),
                     "criticism": "No AI providers were available to evaluate this draft."}

        individual_evaluations = []
        for provider in healthy_providers:
            result = self._run_single_judge(provider, prompt)
            if result:
                individual_evaluations.append(result)

        if not individual_evaluations:
            logger.error(f"All judges failed to evaluate draft from {persona}.")
            return {"total_score": 0.0, "judge_count": 0, "draft_id": draft.get("draft_id"),
                     "criticism": "All judges failed to return a valid evaluation."}

        # Average each criterion across the judges that actually responded
        averaged: Dict[str, Any] = {}
        for key in self.weights:
            values = [float(e.get(key, 0.0)) for e in individual_evaluations]
            averaged[key] = sum(values) / len(values)

        total_score = sum(averaged[key] * weight for key, weight in self.weights.items())

        averaged["total_score"] = round(total_score, 2)
        averaged["judge_count"] = len(individual_evaluations)
        averaged["draft_id"] = draft.get("draft_id")
        averaged["criticism"] = individual_evaluations[0].get("criticism", "")
        averaged["praise"] = individual_evaluations[0].get("praise", "")
        logger.info(f"Draft '{persona}' judged by {len(individual_evaluations)} independent model(s), score: {averaged['total_score']}")
        return averaged

    def select_best_draft(self, drafts: List[Dict[str, Any]], facts: List[str]) -> Dict[str, Any]:
        if not drafts:
            logger.error("No drafts provided to judge.")
            return {}

        logger.info(f"Evaluating {len(drafts)} drafts to find the winner...")

        evaluated_drafts = []
        for draft in drafts:
            evaluation = self.evaluate_draft(draft, facts)
            draft["evaluation"] = evaluation
            evaluated_drafts.append(draft)
            logger.info(f"Draft '{draft.get('persona')}' scored: {evaluation.get('total_score')} (judges: {evaluation.get('judge_count')})")

        # Sort drafts by total score in descending order
        evaluated_drafts.sort(key=lambda x: x.get("evaluation", {}).get("total_score", 0.0), reverse=True)

        best_draft = evaluated_drafts[0]
        logger.info(f"Winner selected: {best_draft.get('persona')} (Score: {best_draft.get('evaluation').get('total_score')})")
        return best_draft

judge_panel = JudgePanel()
