from datetime import datetime
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

