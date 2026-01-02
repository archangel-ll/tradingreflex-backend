from datetime import datetime
from typing import List
from pydantic import BaseModel


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
    conviction_score: int
    why_unusual: list[str]


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
    sentiment: str  # bullish / neutral / bearish
    confidence_score: int
    generated_at: datetime
    valid_until: datetime

