print("🔥 LOADED app/main.py FROM RENDER 🔥")

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# IMPORTANT: import AI router
from app.routes_ai import router as ai_router

app = FastAPI(
    title="TradingReflex Backend",
    version="0.1.0"
)

# CORS (Bolt frontend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health():
    return {"ok": True}

# REGISTER AI ROUTES (THIS WAS MISSING IN PROD)
app.include_router(ai_router)
