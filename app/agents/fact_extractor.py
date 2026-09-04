import uuid
from typing import List
from app.llm.router import router
from app.models.fact import Fact
from app.models.source import Source
from app.utils.logging import setup_logger

logger = setup_logger(__name__)

class FactExtractor:
    def extract_facts(self, source: Source) -> List[Fact]:
        logger.info(f"Extracting facts from source: {source.url}")
        
        # Use full content if available, otherwise fallback to search snippet
        text_to_analyze = source.content if source.content else source.snippet
        if not text_to_analyze or len(text_to_analyze.strip()) < 10:
            return []
            
        prompt = f"""
        Extract isolated, atomic facts from the following text. Do NOT invent information.
        Text: {text_to_analyze}
        
        Return a JSON object with a 'facts' array. Each item must have:
        - 'claim': A single factual statement
        - 'date': Date if mentioned, else 'unknown'
        - 'location': Location if mentioned, else 'unknown'
        - 'confidence': Float between 0.0 and 1.0 representing how strongly the text states this.
        """
        
        try:
            response = router.generate_json(
                prompt, 
                system_prompt="You are a precise, evidence-based fact extractor. Output valid JSON only.", 
                task="research"
            )
            extracted = response.get("facts", [])
            
            facts = []
            for item in extracted:
                fact = Fact(
                    fact_id=f"fact_{uuid.uuid4().hex[:8]}",
                    claim=item.get("claim", ""),
                    date=item.get("date", "unknown"),
                    location=item.get("location", "unknown"),
                    source_ids=[source.source_id],
                    confidence=float(item.get("confidence", 0.8)),
                    status="UNVERIFIED"
                )
                facts.append(fact)
            return facts
        except Exception as e:
            logger.error(f"Fact extraction failed for {source.url}: {str(e)}")
            return []

fact_extractor = FactExtractor()
