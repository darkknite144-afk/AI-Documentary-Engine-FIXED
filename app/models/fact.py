from pydantic import BaseModel, Field
from typing import List

class Fact(BaseModel):
    fact_id: str
    claim: str
    date: str = "unknown"
    location: str = "unknown"
    source_ids: List[str] = Field(default_factory=list)
    confidence: float = 0.0
    status: str = "UNVERIFIED" # Can be: VERIFIED, PROBABLE, DISPUTED, UNVERIFIED
