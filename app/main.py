from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import json
import asyncio
import random
import uuid
from datetime import datetime, timedelta

from app.schemas import FlowEvent
from app.ws_manager import manager

# In-memory list to store the last 50 FlowEvent objects
flow_events_history: list[FlowEvent] = []


async def generate_option_flow_event():
    """Generate a realistic option flow event"""
    tickers = ["NVDA", "AMD", "TSLA", "SPY"]
    option_types = ["CALL", "PUT"]
    
    ticker = random.choice(tickers)
    option_type = random.choice(option_types)
    conviction_score = random.randint(55, 95)
    
    # Generate realistic strike prices based on ticker
    # These are approximate current price ranges (will be adjusted randomly)
    base_prices = {
        "NVDA": 500,
        "AMD": 150,
        "TSLA": 250,
        "SPY": 450
    }
    base_price = base_prices[ticker]
    
    # Strike within ±20% of base price, rounded to nearest $0.50 or $1.00
    strike_offset = random.uniform(-0.20, 0.20)
    strike = base_price * (1 + strike_offset)
    if ticker == "SPY":
        strike = round(strike)
    else:
        strike = round(strike * 2) / 2  # Round to nearest $0.50
    
    # Expiry: random date between 1 day and 45 days from now
    days_to_expiry = random.randint(1, 45)
    expiry_date = datetime.now() + timedelta(days=days_to_expiry)
    expiry = expiry_date.strftime("%Y-%m-%d")
    
    # Premium spent: realistic range based on strike and option type
    # Typically 0.5% to 5% of strike price
    premium_multiplier = random.uniform(0.005, 0.05)
    premium_spent = round(strike * premium_multiplier * 100, 2)  # Per contract, assume 100 shares
    
    # Volume: typically 10 to 10,000 contracts
    volume = random.randint(10, 10000)
    
    # Open interest: typically higher than volume, 50 to 50,000
    open_interest = random.randint(max(volume, 50), 50000)
    
    # Is sweep: 30% chance
    is_sweep = random.random() < 0.3
    
    # Generate 2-3 human-readable reasons
    reasons_pool = [
        f"Unusual volume spike: {volume:,} contracts traded vs {open_interest:,} open interest",
        f"Large premium spent: ${premium_spent:,.2f} on {option_type} options",
        f"Strike price {strike} is {('above' if strike > base_price else 'below')} current market price",
        f"Expiry date {expiry} is within {days_to_expiry} days",
        f"High conviction {option_type} activity detected",
        f"Significant {option_type} flow suggests {('bullish' if option_type == 'CALL' else 'bearish')} sentiment",
        f"Open interest of {open_interest:,} indicates strong market interest",
        f"Premium-to-strike ratio of {premium_multiplier*100:.2f}% suggests {('optimistic' if option_type == 'CALL' else 'pessimistic')} outlook"
    ]
    
    num_reasons = random.randint(2, 3)
    why_unusual = random.sample(reasons_pool, num_reasons)
    
    return FlowEvent(
        id=str(uuid.uuid4()),
        timestamp=datetime.now(),
        ticker=ticker,
        option_type=option_type,
        strike=strike,
        expiry=expiry,
        premium_spent=premium_spent,
        volume=volume,
        open_interest=open_interest,
        is_sweep=is_sweep,
        conviction_score=conviction_score,
        why_unusual=why_unusual
    )


async def background_task():
    """Background task that generates and broadcasts option flow events"""
    global flow_events_history
    while True:
        # Wait 1-3 seconds before generating next event
        wait_time = random.uniform(1.0, 3.0)
        await asyncio.sleep(wait_time)
        
        # Generate event
        event = await generate_option_flow_event()
        
        # Add to history (maintain last 50)
        flow_events_history.append(event)
        if len(flow_events_history) > 50:
            flow_events_history.pop(0)
        
        # Only broadcast if conviction_score >= 60
        if event.conviction_score >= 60:
            # Convert to dict and broadcast
            event_dict = event.model_dump()
            # Convert datetime to ISO format string for JSON serialization
            event_dict["timestamp"] = event_dict["timestamp"].isoformat()
            await manager.broadcast_json(event_dict)
            print(f"Broadcasted event: {event.ticker} {event.option_type} {event.strike} (conviction: {event.conviction_score})")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager to start and stop background tasks"""
    # Startup: start background task
    task = asyncio.create_task(background_task())
    print("Background task started")
    yield
    # Shutdown: cancel background task
    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        pass
    print("Background task stopped")


app = FastAPI(lifespan=lifespan)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health():
    """Health check endpoint"""
    return {"ok": True}


@app.get("/api/flow/unusual")
async def get_unusual_flow():
    """Get the last 50 simulated FlowEvent objects"""
    # Convert FlowEvent objects to dicts with ISO format timestamps
    events = []
    for event in flow_events_history:
        event_dict = event.model_dump()
        event_dict["timestamp"] = event_dict["timestamp"].isoformat()
        events.append(event_dict)
    return events


@app.websocket("/ws/flow")
async def websocket_flow(websocket: WebSocket):
    """WebSocket endpoint for flow"""
    await manager.connect(websocket)
    try:
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            try:
                # Parse and validate the incoming data as FlowEvent
                event_data = json.loads(data)
                flow_event = FlowEvent(**event_data)
                # Broadcast the validated event to all connected clients
                await manager.broadcast_json(flow_event.model_dump())
            except json.JSONDecodeError:
                await manager.send_personal_message("Error: Invalid JSON", websocket)
            except Exception as e:
                await manager.send_personal_message(f"Error: {str(e)}", websocket)
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        print("Client disconnected")

