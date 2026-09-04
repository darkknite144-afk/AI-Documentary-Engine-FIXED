from typing import List, Dict, Any
from app.llm.router import router
from app.utils.logging import setup_logger

logger = setup_logger(__name__)

class HookGenerator:
    def generate_and_select_hook(self, framework: Dict[str, Any], verified_facts: List[str]) -> Dict[str, Any]:
        logger.info("Generating cinematic hooks...")
        
        central_q = framework.get("central_question", "")
        climax = framework.get("climax", "")
        facts_context = "\n".join(verified_facts[:10]) if verified_facts else ""
        
        prompt = f"""
        Central Question: {central_q}
        Climax Hint: {climax}
        Supporting Facts: {facts_context}
        
        Write 5 distinct YouTube documentary hooks (the first 15-30 seconds of the script).
        Rules:
        - Must be factually grounded (NO fake clickbait).
        - Must establish a massive curiosity gap.
        - Must start with a visceral detail or contradictory statement.
        
        For each hook, provide:
        - 'script_text': The exact narration text.
        - 'visual_idea': What the viewer sees.
        - 'score': A float from 0.0 to 10.0 based on retention power.
        
        Return a JSON object with a 'hooks' array.
        """
        
        try:
            response = router.generate_json(
                prompt,
                system_prompt="You are a YouTube retention expert specializing in high-impact documentary intros.",
                task="writing"
            )
            
            hooks = response.get("hooks", [])
            if not hooks:
                raise ValueError("No hooks generated.")
                
            # Sort by score and pick the best one
            hooks.sort(key=lambda x: float(x.get("score", 0)), reverse=True)
            best_hook = hooks[0]
            
            logger.info(f"Selected best hook (Score: {best_hook.get('score')})")
            return best_hook
            
        except Exception as e:
            logger.error(f"Hook generation failed: {str(e)}")
            return {
                "script_text": f"This is the incredible story of {framework.get('protagonist', 'our subject')}.",
                "visual_idea": "Title card",
                "score": 5.0
            }

hook_generator = HookGenerator()
