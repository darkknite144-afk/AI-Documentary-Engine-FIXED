from typing import Dict, Any
from app.utils.logging import setup_logger

logger = setup_logger(__name__)

class QualityController:
    def gate_check(self, red_team_report: Dict[str, Any], fact_check_report: Dict[str, Any]) -> str:
        logger.info("Executing Final Quality Gate Check...")
        
        red_team_status = red_team_report.get("status", "NEEDS_REWRITE")
        fact_check_status = fact_check_report.get("status", "FLAGGED")
        
        if red_team_status == "PASS" and fact_check_status == "PASS":
            logger.info("Quality Gate: PASSED. Script is ready for production.")
            return "PASS"
        else:
            logger.warning(f"Quality Gate: FAILED. Red Team: {red_team_status}, Fact Check: {fact_check_status}")
            return "NEEDS_REVIEW"

quality_controller = QualityController()
