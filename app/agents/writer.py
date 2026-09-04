import uuid
from typing import List, Dict, Any
from app.llm.router import router
from app.config import settings
from app.utils.logging import setup_logger

logger = setup_logger(__name__)

class AIWriter:
    def __init__(self):
        # 4 different writing styles to ensure we get a fun and engaging script
        self.personas = {
            "Cinematic": "Focus on vivid visual storytelling, pacing, contrast, and dramatic sequencing.",
            "Investigative": "Focus on revealing the evidence step-by-step, building mystery and logical deduction.",
            "High-Retention": "Focus on fast pacing, constant curiosity loops, rhetorical questions, and punchy sentences.",
            "Emotional": "Focus on the human element, stakes, empathy, and emotional resonance of the protagonist."
        }

    def write_draft(self, persona_name: str, framework: Dict[str, Any], hook: Dict[str, Any], facts: List[str], duration_mins: int) -> Dict[str, Any]:
        logger.info(f"Writing script draft using '{persona_name}' persona...")
        
        style_instruction = self.personas.get(persona_name, self.personas["Cinematic"])
        target_words = duration_mins * 150 # Assuming average 150 words per minute narration
        
        # Prepare context
        facts_context = "\n".join(facts) if facts else "No facts provided."
        
        prompt = f"""
        Write a complete documentary script based strictly on the provided facts.
        
        Target Duration: {duration_mins} minutes (~{target_words} words).
        Persona/Style: {style_instruction}
        
        Story Framework:
        - Protagonist: {framework.get('protagonist')}
        - Central Question: {framework.get('central_question')}
        - Climax: {framework.get('climax')}
        
        Approved Hook (Use this exact text or adapt it slightly for the opening):
        {hook.get('script_text')}
        
        Verified Facts to use (DO NOT INVENT DIALOGUE, QUOTES, OR STATISTICS NOT FOUND HERE):
        {facts_context}
        
        Return a JSON object with a 'sections' array. Each section must have:
        - 'section_id': unique string
        - 'title': section title
        - 'narration': The actual spoken script text for the narrator
        - 'visual_idea': What the viewer should see
        - 'estimated_duration': estimated seconds this section takes to speak
        """
        
        system_prompt = f"You are a master YouTube scriptwriter. Do not use generic AI phrases like 'little did he know'. Output valid JSON only."
        
        try:
            response = router.generate_json(prompt, system_prompt, task="writing")
            
            draft = {
                "draft_id": f"draft_{uuid.uuid4().hex[:8]}",
                "persona": persona_name,
                "sections": response.get("sections", []),
                "total_words": sum(len(str(s.get("narration", "")).split()) for s in response.get("sections", []))
            }
            return draft
        except Exception as e:
            logger.error(f"Failed to write draft for {persona_name}: {str(e)}")
            return {"draft_id": "error", "persona": persona_name, "sections": []}

    def generate_multiple_drafts(self, framework: Dict[str, Any], hook: Dict[str, Any], facts: List[str], duration_mins: int) -> List[Dict[str, Any]]:
        drafts = []
        # Limit the number of writers based on config to save API costs
        active_personas = list(self.personas.keys())[:settings.max_writer_agents]
        
        for persona in active_personas:
            draft = self.write_draft(persona, framework, hook, facts, duration_mins)
            if draft.get("sections"):
                drafts.append(draft)
                logger.info(f"Successfully generated draft using {persona} persona.")
                
        return drafts

ai_writer = AIWriter()
