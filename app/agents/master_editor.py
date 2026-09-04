import uuid
from typing import List, Dict, Any, Optional
from app.llm.router import router
from app.utils.logging import setup_logger

logger = setup_logger(__name__)

class MasterEditor:
    def create_master_script(self, best_draft: Dict[str, Any], facts: List[str], language: str = "Hinglish",
                              repair_notes: Optional[str] = None) -> Dict[str, Any]:
        logger.info(f"Master Editor is polishing the script. Target language: {language}")
        
        # Extract judge's notes and the raw draft
        evaluation = best_draft.get("evaluation", {})
        criticism = evaluation.get("criticism", "Make the pacing smoother and more engaging.")
        if repair_notes:
            # Called during a QA repair round: this is the previously master-edited
            # script (not the original writer draft), plus red-team/fact-check feedback.
            criticism = f"{criticism}\nQuality review flagged this script for a repair pass. Fix these specific issues:\n{repair_notes}"
        sections = best_draft.get("sections", [])
        
        # Format the draft for the AI to read
        draft_text = "\n\n".join([f"[{s.get('section_id', 'id')}] {s.get('title', 'title')}\nNarration: {s.get('narration', '')}\nVisual: {s.get('visual_idea', '')}" for s in sections])
        facts_context = "\n".join(facts[:20]) if facts else "No facts provided."
        
        prompt = f"""
        You are the Master Editor. Polish this script draft into the final master script.
        
        Target Language: {language}
        (If Hinglish, it MUST sound like a highly natural, conversational YouTube storyteller. DO NOT use formal, robotic translation. E.g., Use "Us din sab kuch badal gaya..." instead of "Us din sab kuch parivartit ho gaya...").
        
        Judge's Criticism to Fix: {criticism}
        
        Verified Facts (DO NOT invent new facts, quotes, or statistics):
        {facts_context}
        
        Current Draft:
        {draft_text}
        
        Return a JSON object with a 'master_sections' array. 
        Each object in the array must contain:
        - 'section_id': Keep the original ID
        - 'title': Keep or slightly improve the title
        - 'narration': The completely polished, rewritten narration in {language}
        - 'visual_idea': Keep or improve the visual direction
        - 'estimated_duration': (integer) estimated seconds
        """
        
        system_prompt = "You are an elite YouTube script editor. You fix pacing, apply natural language, and strictly adhere to verified facts. Output valid JSON only."
        
        try:
            # Using 'writing' task to prioritize creative but accurate models
            response = router.generate_json(prompt, system_prompt, task="writing")
            
            master_script = {
                "script_id": f"script_{uuid.uuid4().hex[:8]}",
                "original_persona": best_draft.get("persona"),
                "language": language,
                "sections": response.get("master_sections", sections),
                "status": "MASTER_EDITED"
            }
            logger.info("Master script created successfully.")
            return master_script
            
        except Exception as e:
            logger.error(f"Master Editor failed: {str(e)}")
            # Fallback to the original best draft if the edit fails
            best_draft["status"] = "FALLBACK_UNEDITED"
            return best_draft

master_editor = MasterEditor()
