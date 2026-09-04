from typing import Dict, Any
from app.llm.router import router
from app.utils.logging import setup_logger
from app.config import settings

logger = setup_logger(__name__)

class ResearchDirector:
    def generate_plan(self, topic: str) -> Dict[str, Any]:
        logger.info(f"Generating deep research plan for topic: '{topic}'")
        
        prompt = f"""
        Analyze the topic: "{topic}"
        Identify the specific historical entities, people, locations, or events involved.
        DO NOT use generic words like "The Man" or "Company". Focus strictly on the exact subject.
        
        Return a JSON object with:
        - 'topic': the exact refined topic.
        - 'entities': array of specific names/places involved.
        - 'queries': list of 15 highly targeted search engine queries (e.g. "Tsutomu Yamaguchi Hiroshima Nagasaki 1945").
        """
        
        system_prompt = "You are an elite documentary researcher. Output strictly valid JSON. Avoid generic search terms."
        
        try:
            plan = router.generate_json(prompt, system_prompt, task="research")
            if not plan.get("queries"):
                raise ValueError("AI returned empty queries array.")
            return plan
        except Exception as e:
            logger.error(f"Research plan failed: {str(e)}. Using intelligent fallback.")
            # Intelligent fallback to avoid single generic query
            fallback_queries = [
                f"{topic} historical facts",
                f"{topic} timeline of events",
                f"{topic} primary sources evidence",
                f"{topic} biography and details",
                f"{topic} controversies and myths"
            ]
            return {"topic": topic, "categories": ["general"], "queries": fallback_queries}

research_director = ResearchDirector()
