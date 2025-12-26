# Trading Reflex Backend

FastAPI backend application.

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the server:
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## Endpoints

- `GET /health` - Health check endpoint returning `{"ok": true}`
- `WS /ws/flow` - WebSocket endpoint for flow

## Development

The server runs on port 8000 by default. You can access:
- API docs: http://localhost:8000/docs
- Alternative docs: http://localhost:8000/redoc

