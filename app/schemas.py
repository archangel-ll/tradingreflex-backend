from datetime import datetime
from typing import List
from pydantic import BaseModel, Field


class FlowEvent(BaseModel):
    id: str
    timestamp: datetime
    ticker: str
    option_type: str  # CALL or PUT
    strike: float
    expiry: str
    premium_spent: float
    volume: int
    open_interest: int
    is_sweep: bool
    is_block: bool = False
    conviction_score: int
    why_unusual: List[str] = Field(default_factory=list)


class TechnicalsOut(BaseModel):
    ticker: str
    rsi: float
    macd: float
    vwap: float
    support_1: float
    resistance_1: float
    setup_tags: List[str]
    calculated_at: datetime


class NarrativeOut(BaseModel):
    ticker: str
    narrative_text: str
    sentiment: str
    confidence_score: int
    generated_at: datetime
    valid_until: datetime
