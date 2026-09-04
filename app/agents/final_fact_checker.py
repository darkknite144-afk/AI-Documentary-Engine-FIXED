from typing import List, Dict, Any
from app.llm.router import router
from app.utils.logging import setup_logger

logger = setup_logger(__name__)

class FinalFactChecker:
    def verify_script(self, master_script: Dict[str, Any], facts: List[str]) -> Dict[str, Any]:
        logger.info("Running final fact-check on the polished script...")
        
        sections = master_script.get("sections", [])
        script_text = "\n".join([s.get('narration', '') for s in sections])
        facts_context = "\n".join(facts[:20]) if facts else "No facts available."
        
        prompt = f"""
        Perform a strict final fact-check on this script.
        
        Verified Knowledge Base:
        {facts_context}
        
        Final Script:
        {script_text[:4000]}
        
        Check if EVERY major claim in the script is supported by the Knowledge Base.
        
        Return a JSON object with:
        - 'status': "PASS" or "FLAGGED"
        - 'unsupported_claims': Array of specific sentences that are unsupported or fabricated.
        """
        
        system_prompt = "You are the final quality gatekeeper. Do not allow any hallucinations. Output valid JSON only."
        
        try:
            report = router.generate_json(prompt, system_prompt, task="judging")
            logger.info(f"Final Fact Check Status: {report.get('status', 'FLAGGED')}")
            return report
        except Exception as e:
            logger.error(f"Final fact check failed: {str(e)}")
            return {"status": "FLAGGED", "unsupported_claims": ["Error during verification."]}

final_fact_checker = FinalFactChecker()
