import os
import asyncio
import logging
from typing import Dict, Any, Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
from telegram.ext import ApplicationBuilder, MessageHandler, CommandHandler, filters

from backend.db.models import init_db
from backend.db import repo
from backend.agent.core import handle_user_message
from backend.bot import handlers
from backend.scheduler.jobs import register_jobs
from backend.services import market

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
log = logging.getLogger("atlas_main")

# Initialize SQLite database
init_db()

app = FastAPI(title="Atlas AI Financial Assistant", version="2.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "8834152991:AAH5aL2O-GhH18GOEjyPkLP_f7gySVkPFM0").strip()

class ChatRequest(BaseModel):
    telegram_id: Optional[int] = 1001
    content: str
    channel: Optional[str] = "text"

@app.get("/")
def read_root():
    return {
        "service": "Atlas AI Conversational Financial Analyst",
        "status": "online",
        "version": "2.0",
        "architecture": "Telegram + SQLAlchemy + JobQueue + Finnhub + OpenRouter + SEC EDGAR"
    }

@app.post("/api/chat")
async def chat_endpoint(req: ChatRequest):
    user = repo.get_or_create_user(req.telegram_id, "Analyst")
    response_text = await handle_user_message(user, req.content)
    watchlist = repo.get_watchlist(user.id)
    facts = repo.get_facts(user.id)
    
    return {
        "response": response_text,
        "intent": "financial_qa",
        "tickers_referenced": watchlist[:3],
        "sources": ["Finnhub Live Market API", "OpenRouter AI Engine", "SEC EDGAR Official Feed"],
        "channel": req.channel,
        "user_profile": {
            "name": user.name,
            "role": user.role,
            "watchlist": watchlist,
            "facts": facts,
            "briefing_time": user.briefing_time
        }
    }

@app.get("/api/profile/{tg_id}")
def get_profile(tg_id: int):
    user = repo.get_or_create_user(tg_id, "Analyst")
    return {
        "id": user.id,
        "telegram_id": user.tg_id,
        "name": user.name,
        "role": user.role,
        "briefing_time": user.briefing_time,
        "watchlist": repo.get_watchlist(user.id),
        "facts": repo.get_facts(user.id),
        "active_alerts": [
            {"id": a.id, "type": a.type, "ticker": a.ticker, "threshold": a.threshold_pct, "active": a.active}
            for a in repo.active_alerts(user_id=user_id)
        ] if hasattr(user, 'id') else []
    }

@app.get("/api/market/quote/{ticker}")
def get_quote_api(ticker: str):
    return market.get_quote(ticker)

@app.get("/api/telegram/bot-status")
def bot_status():
    return {
        "bot_username": "@Atlas39bot",
        "status": "connected",
        "polling": True
    }

async def start_telegram_bot():
    """Background async Telegram long-polling daemon with JobQueue."""
    if not TELEGRAM_BOT_TOKEN:
        log.warning("No TELEGRAM_BOT_TOKEN provided; skipping Telegram bot polling.")
        return

    try:
        tg_app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
        
        # Register Telegram Command and Event Handlers
        tg_app.add_handler(CommandHandler("start", handlers.on_start))
        tg_app.add_handler(CommandHandler("watchlist", handlers.on_watchlist))
        tg_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handlers.on_text))
        tg_app.add_handler(MessageHandler(filters.VOICE | filters.AUDIO, handlers.on_voice))
        tg_app.add_handler(MessageHandler(filters.PHOTO, handlers.on_photo))
        tg_app.add_handler(MessageHandler(filters.Document.ALL, handlers.on_document))
        tg_app.add_error_handler(handlers.on_error)
        
        # Register Proactive JobQueue
        register_jobs(tg_app)
        
        log.info("Starting Telegram Bot long-polling daemon (@Atlas39bot)...")
        await tg_app.initialize()
        await tg_app.start()
        await tg_app.updater.start_polling(drop_pending_updates=True)
    except Exception as e:
        log.exception(f"Telegram Bot polling error: {e}")

@app.on_event("startup")
async def on_startup():
    # Start Telegram bot in background asyncio task
    asyncio.create_task(start_telegram_bot())

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
