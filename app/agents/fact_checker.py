from typing import List
from app.llm.router import router
from app.models.fact import Fact
from app.models.source import Source
from app.utils.logging import setup_logger

logger = setup_logger(__name__)

class IndependentFactChecker:
    def verify_fact(self, fact: Fact, evidence_sources: List[Source]) -> Fact:
        logger.info(f"Independent Dual-Model Fact-check: {fact.claim[:50]}...")
        
        # Gather the real scraped text from the websites
        evidence_texts = []
        for s in evidence_sources:
            if s.source_id in fact.source_ids:
                text = s.content if s.content else s.snippet
                evidence_texts.append(f"Source [{s.domain}]: {text}")
                
        if not evidence_texts:
            fact.status = "UNVERIFIED"
            return fact
            
        evidence_context = "\n\n".join(evidence_texts)[:15000]
        
        prompt = f"""
        Evaluate this claim based STRICTLY on the provided evidence text.
        Do not use internal training data. If the evidence does not clearly state the claim, mark it UNVERIFIED.
        
        Claim: {fact.claim} (Date: {fact.date}, Location: {fact.location})
        Evidence: {evidence_context}
        
        Return JSON format ONLY:
        {{
            "status": "VERIFIED" | "DISPUTED" | "UNVERIFIED",
            "reasoning": "brief logic"
        }}
        """
        system_prompt = "You are a merciless, evidence-only fact checker."
        
        try:
            # MULTI-AI CONSENSUS LOOP
            # Ask whichever providers are actually configured/healthy right now,
            # instead of hardcoding Gemini as primary. This way fact-checking
            # still works with dual-model consensus if e.g. only Groq +
            # OpenRouter are configured and Gemini has no key.
            healthy_providers = router.get_healthy_providers()
            if not healthy_providers:
                raise RuntimeError("No AI providers are configured or healthy.")

            # 1. Ask Primary Model (highest-priority healthy provider)
            resp_a = router.call_provider_json(healthy_providers[0], prompt, system_prompt)
            status_a = resp_a.get("status", "UNVERIFIED").upper()

            # 2. Ask Secondary Model (next distinct healthy provider) for independent consensus
            if len(healthy_providers) > 1:
                resp_b = router.call_provider_json(healthy_providers[1], prompt, system_prompt)
                status_b = resp_b.get("status", "UNVERIFIED").upper()
            else:
                status_b = status_a # Only one provider configured; single-model check
                
            # 3. Resolve Conflicts between AIs
            if status_a == "VERIFIED" and status_b == "VERIFIED":
                fact.status = "VERIFIED"
            elif status_a == "DISPUTED" or status_b == "DISPUTED":
                fact.status = "DISPUTED"
            else:
                fact.status = "UNVERIFIED"
                
            logger.info(f"Fact [{fact.fact_id}] consensus: {fact.status} (Model A: {status_a}, Model B: {status_b})")
            
        except Exception as e:
            logger.error(f"Fact checking failed for {fact.fact_id}: {str(e)}")
            fact.status = "UNVERIFIED"
            
        return fact

fact_checker = IndependentFactChecker()
