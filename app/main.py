print("🔥 LOADED app/main.py FROM RENDER 🔥")

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from typing import List
from datetime import datetime, timedelta
import asyncio
import random
import uuid

from app.routes_ai import router as ai_router
from app.schemas import FlowEvent
from app.ws_manager import manager

app = FastAPI(
    title="TradingReflex Backend",
    version="0.1.0"
)

# -------------------------------------------------
# CORS (safe for Bolt + browser)
# -------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],          # OK for now
    allow_credentials=False,      # MUST be False if origins = "*"
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------------------------------------
# Health check
# -------------------------------------------------
@app.get("/health")
def health():
    return {"ok": True}

# -------------------------------------------------
# Register AI routes
# -------------------------------------------------
app.include_router(ai_router)

# -------------------------------------------------
# In-memory flow storage
# -------------------------------------------------
flow_events_history: List[FlowEvent] = []

# -------------------------------------------------
# Flow REST endpoints
# -------------------------------------------------
@app.get("/api/v1/flow/events", response_model=List[FlowEvent])
def get_flow_events():
    return list(reversed(flow_events_history))


@app.get("/api/v1/flow", response_model=List[FlowEvent])
def get_flow_events_alias():
    return list(reversed(flow_events_history))

# -------------------------------------------------
# Flow generator (mock data for MVP)
# -------------------------------------------------
async def generate_option_flow():
    tickers = ["SPY", "TSLA", "NVDA", "AMD"]
    option_types = ["CALL", "PUT"]

    while True:
        days_to_expiry = random.randint(1, 45)
        expiry_date = datetime.utcnow() + timedelta(days=days_to_expiry)
        expiry = expiry_date.strftime("%Y-%m-%d")

        event = FlowEvent(
            id=str(uuid.uuid4()),
            timestamp=datetime.utcnow(),
            ticker=random.choice(tickers),
            option_type=random.choice(option_types),
            strike=round(random.uniform(200, 500), 1),
            expiry=expiry,
            premium_spent=round(random.uniform(250_000, 5_000_000), 2),
            volume=random.randint(500, 5000),
            open_interest=random.randint(100, 3000),
            is_sweep=random.choice([True, False]),
            is_block=random.choice([True, False]),
            conviction_score=random.randint(60, 95),
            why_unusual=[
                "High volume vs OI",
                "Aggressive sweep"
            ],
        )

        # Save event
        flow_events_history.append(event)

        # Keep last 50 only
        if len(flow_events_history) > 50:
            flow_events_history.pop(0)

        # Broadcast only meaningful events
        if event.conviction_score >= 60:
            event_dict = event.model_dump()
            event_dict["timestamp"] = event_dict["timestamp"].isoformat()
            await manager.broadcast_json(event_dict)

            print(
                f"Broadcasted: {event.ticker} "
                f"{event.option_type} {event.strike} "
                f"(conviction={event.conviction_score}, expiry={expiry})"
            )

        await asyncio.sleep(3)

# -------------------------------------------------
# Startup hook
# -------------------------------------------------
@app.on_event("startup")
async def startup_event():
    asyncio.create_task(generate_option_flow())
