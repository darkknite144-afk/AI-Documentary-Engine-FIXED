from typing import List, Dict, Any
from app.llm.router import router
from app.utils.logging import setup_logger

logger = setup_logger(__name__)

class StoryArchitect:
    def create_framework(self, topic: str, angle: Dict[str, Any]) -> Dict[str, Any]:
        logger.info("Creating story architecture framework...")
        
        angle_title = angle.get("title", topic)
        angle_focus = angle.get("focus", "general")
        
        prompt = f"""
        Topic: {topic}
        Selected Angle: {angle_title}
        Narrative Focus: {angle_focus}
        
        Create a detailed documentary story framework. Return a JSON object with:
        - 'protagonist': The main character or central subject
        - 'central_question': The core mystery or question keeping viewers watching
        - 'conflict': The main obstacle
        - 'stakes': What happens if the protagonist fails (or why this matters)
        - 'turning_points': Array of 3 major narrative shifts
        - 'climax': The peak of the story
        - 'emotional_core': The underlying human emotion
        """
        
        try:
            framework = router.generate_json(
                prompt,
                system_prompt="You are an expert Hollywood screenwriter and documentary structuralist.",
                task="writing"
            )
            return framework
        except Exception as e:
            logger.error(f"Story architecture failed: {str(e)}")
            return {
                "protagonist": f"The people and events at the center of {topic}",
                "central_question": f"What is the truth behind {topic}?",
                "conflict": "Unknown",
                "stakes": "Understanding what really happened",
                "turning_points": [],
                "climax": "Resolution of the core question",
                "emotional_core": "Curiosity"
            }

story_architect = StoryArchitect()
