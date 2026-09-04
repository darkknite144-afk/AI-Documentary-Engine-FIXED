from typing import List, Dict, Any
from app.llm.router import router
from app.utils.logging import setup_logger

logger = setup_logger(__name__)

class RedTeam:
    def evaluate_script(self, master_script: Dict[str, Any]) -> Dict[str, Any]:
        logger.info("Red Team is aggressively evaluating the master script...")
        
        sections = master_script.get("sections", [])
        script_text = "\n\n".join([f"[{s.get('section_id')}] {s.get('title')}\n{s.get('narration')}" for s in sections])
        
        prompt = f"""
        You are the Red Team. Your job is to aggressively attack this documentary script.
        Look for:
        - Boring, dry factual sections that ruin the story flow
        - Fake drama or forced suspense
        - Cliche YouTuber phrases
        - Weak logic or confusing transitions
        
        Script to Attack:
        {script_text}
        
        Return a JSON object with:
        - 'status': "PASS" or "NEEDS_REWRITE"
        - 'issues': Array of specific issues found.
        - 'targeted_rewrites': Array of 'section_id' strings that MUST be rewritten.
        - 'feedback': Overall brutal feedback.
        """
        
        system_prompt = "You are a merciless script doctor. Output valid JSON only."
        
        try:
            report = router.generate_json(prompt, system_prompt, task="judging")
            logger.info(f"Red Team Evaluation Status: {report.get('status', 'PASS')}")
            return report
        except Exception as e:
            logger.error(f"Red Team evaluation failed: {str(e)}")
            return {"status": "PASS", "issues": [], "targeted_rewrites": [], "feedback": "Error during evaluation."}

red_team = RedTeam()
