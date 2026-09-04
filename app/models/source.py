from pydantic import BaseModel, Field
from typing import Optional

class Source(BaseModel):
    source_id: str
    title: str
    url: str
    domain: str
    snippet: str
    content: Optional[str] = None
    source_type: str = "unknown"
    authority_score: float = 0.0
    quality_score: float = 0.0
