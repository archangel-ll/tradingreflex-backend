from fastapi import APIRouter, Query
from datetime import datetime, timedelta
from app.schemas import TechnicalsOut, NarrativeOut

router = APIRouter(prefix="/api/v1", tags=["ai"])


@router.get("/technicals/{ticker}", response_model=TechnicalsOut)
def get_technicals(ticker: str):
    now = datetime.utcnow()

    return TechnicalsOut(
        ticker=ticker.upper(),
        rsi=62.4,
        macd=1.23,
        vwap=897.50,
        support_1=885.00,
        resistance_1=920.00,
        setup_tags=[
            "⚡ VWAP Reclaim",
            "📈 Momentum Breakout"
        ],
        calculated_at=now,
    )


@router.get("/narratives", response_model=NarrativeOut)
def get_narrative(ticker: str = Query(...)):
    now = datetime.utcnow()

    return NarrativeOut(
        ticker=ticker.upper(),
        narrative_text=(
            f"{ticker.upper()}: Buyers active after unusual options activity. "
            "Momentum holds above VWAP; watch continuation or rejection near resistance."
        ),
        sentiment="bullish",
        confidence_score=72,
        generated_at=now,
        valid_until=now + timedelta(minutes=10),
    )
