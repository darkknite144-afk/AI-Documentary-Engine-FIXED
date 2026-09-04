from typing import List, Dict, Any
from app.llm.router import router
from app.models.fact import Fact
from app.utils.logging import setup_logger

logger = setup_logger(__name__)

class ConflictDetector:
    def detect_conflicts(self, facts: List[Fact]) -> List[Dict[str, Any]]:
        logger.info(f"Scanning {len(facts)} facts for conflicts...")
        
        if len(facts) < 2:
            return []
        
        # Prepare concise facts list to save tokens
        fact_summaries = []
        for f in facts:
            # We only want to analyze verified or probable facts for conflicts
            if f.status in ["VERIFIED", "PROBABLE"]:
                fact_summaries.append(f"[{f.fact_id}] Claim: {f.claim} (Date: {f.date}, Loc: {f.location})")
            
        if not fact_summaries:
            return []
            
        facts_context = "\n".join(fact_summaries)
        
        prompt = f"""
        Analyze the following extracted facts for logical contradictions or conflicting claims.
        Look for:
        - Date conflicts (different dates for the exact same event)
        - Number/Statistics conflicts
        - Location conflicts
        - Identity conflicts

        Facts:
        {facts_context}

        Return a JSON object with a 'conflicts' array. Each item must have:
        - 'type': type of conflict (e.g., 'date_conflict', 'number_conflict')
        - 'description': detailed explanation of the contradiction
        - 'fact_ids': list of the exact fact IDs involved in the conflict

        If there are no contradictions, return an empty 'conflicts' array.
        """
        
        try:
            response = router.generate_json(
                prompt, 
                system_prompt="You are a precise logic engine designed to find contradictions in data.", 
                task="research"
            )
            conflicts = response.get("conflicts", [])
            
            if conflicts:
                logger.warning(f"Detected {len(conflicts)} potential conflicts in the knowledge base.")
            
            return conflicts
        except Exception as e:
            logger.error(f"Conflict detection failed: {str(e)}")
            return []

conflict_detector = ConflictDetector()
