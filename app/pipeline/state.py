import uuid
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime

class PipelineState(BaseModel):
    project_id: str = Field(default_factory=lambda: f"proj_{uuid.uuid4().hex[:8]}")
    topic: str
    status: str = "INITIALIZED"
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = Field(default_factory=lambda: datetime.now().isoformat())
    
    # Research Data
    research_plan: Dict[str, Any] = Field(default_factory=dict)
    sources: List[Dict[str, Any]] = Field(default_factory=list)
    facts: List[Dict[str, Any]] = Field(default_factory=list)
    conflicts: List[Dict[str, Any]] = Field(default_factory=list)
    
    # Story Data
    angle: Dict[str, Any] = Field(default_factory=dict)
    framework: Dict[str, Any] = Field(default_factory=dict)
    hook: Dict[str, Any] = Field(default_factory=dict)
    
    # Script Data
    drafts: List[Dict[str, Any]] = Field(default_factory=list)
    best_draft_id: Optional[str] = None
    master_script: Dict[str, Any] = Field(default_factory=dict)
    
    # Quality Data
    red_team_report: Dict[str, Any] = Field(default_factory=dict)
    fact_check_report: Dict[str, Any] = Field(default_factory=dict)
    quality_gate_status: str = "PENDING"
