from typing import List, Dict, Any
from app.llm.router import router
from app.utils.logging import setup_logger

logger = setup_logger(__name__)

class AngleGenerator:
    def generate_and_select_angle(self, topic: str, verified_facts: List[str]) -> Dict[str, Any]:
        logger.info(f"Generating story angles for: {topic}")
        
        # Limit context to avoid token limits
        facts_context = "\n".join(verified_facts[:20]) if verified_facts else "No facts available yet."
        
        prompt = f"""
        Topic: {topic}
        Key Facts: {facts_context}

        Generate 5 completely different documentary story angles for this topic. 
        For each angle, provide:
        - 'title': A working title
        - 'focus': The main narrative focus (e.g., emotional, investigative, historical)
        - 'score': A float from 0.0 to 10.0 evaluating its YouTube audience retention potential, curiosity gap, and emotional pull.

        Return a JSON object with an 'angles' array containing these 5 options.
        """
        
        try:
            response = router.generate_json(
                prompt,
                system_prompt="You are a master YouTube documentary strategist.",
                task="writing"
            )
            
            angles = response.get("angles", [])
            if not angles:
                raise ValueError("No angles generated.")
                
            # Sort by score descending and pick the best one
            angles.sort(key=lambda x: float(x.get("score", 0)), reverse=True)
            best_angle = angles[0]
            
            logger.info(f"Selected best angle: {best_angle.get('title')} (Score: {best_angle.get('score')})")
            return best_angle
            
        except Exception as e:
            logger.error(f"Angle generation failed: {str(e)}")
            return {"title": topic, "focus": "General overview", "score": 5.0}

angle_generator = AngleGenerator()
