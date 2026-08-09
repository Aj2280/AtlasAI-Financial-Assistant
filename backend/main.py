import os
import asyncio
import logging
from datetime import datetime
from zoneinfo import ZoneInfo
from typing import Dict, Any, Optional
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response, PlainTextResponse
from pydantic import BaseModel
import uvicorn
from telegram.ext import ApplicationBuilder, MessageHandler, CommandHandler, filters

from backend.db.models import init_db
from backend.db import repo
from backend.agent.core import handle_user_message
from backend.bot import handlers
from backend.scheduler.jobs import register_jobs
from backend.services import market, sectors, integrations, proactive, edgar
from backend.services.integrations import PlatformIntegrationHub

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

class ProfileUpdateRequest(BaseModel):
    telegram_id: Optional[int] = 1001
    name: Optional[str] = None
    role: Optional[str] = None
    briefing_time: Optional[str] = None
    timezone: Optional[str] = None

@app.post("/api/profile/update")
def update_profile(req: ProfileUpdateRequest):
    user = repo.get_or_create_user(req.telegram_id, "Analyst")
    updates = {}
    if req.name:
        updates["name"] = req.name
        repo.add_fact(user.id, f"User's name is {req.name}")
    if req.role:
        updates["role"] = req.role
    if req.briefing_time:
        updates["briefing_time"] = req.briefing_time
    if req.timezone:
        updates["timezone"] = req.timezone
    if updates:
        repo.update_user(user.id, **updates)
    return {"status": "success", "user": {"name": user.name, "role": user.role, "timezone": user.timezone}}

@app.get("/api/time")
def get_current_time(tz: str = "Asia/Kolkata"):
    from zoneinfo import ZoneInfo
    try:
        now = datetime.now(ZoneInfo(tz))
    except Exception:
        now = datetime.utcnow()
        tz = "UTC"
    return {
        "timezone": tz,
        "formatted": now.strftime("%A, %B %d, %Y - %I:%M:%S %p %Z"),
        "time": now.strftime("%I:%M:%S %p"),
        "date": now.strftime("%Y-%m-%d"),
        "epoch": int(now.timestamp())
    }

@app.get("/api/profile/{tg_id}")
def get_profile(tg_id: int):
    user = repo.get_or_create_user(tg_id, "Analyst")
    return {
        "id": user.id,
        "telegram_id": user.tg_id,
        "name": user.name,
        "role": user.role,
        "timezone": user.timezone or "Asia/Kolkata",
        "briefing_time": user.briefing_time,
        "watchlist": repo.get_watchlist(user.id),
        "facts": repo.get_facts(user.id),
        "active_alerts": [
            {"id": a.id, "type": a.type, "ticker": a.ticker, "threshold": a.threshold_pct, "active": a.active}
            for a in repo.active_alerts(user_id=user.id)
        ] if hasattr(user, 'id') else []
    }

@app.get("/api/messages/{tg_id}")
def get_conversation_history(tg_id: int, limit: int = 30):
    user = repo.get_or_create_user(tg_id, "Analyst")
    msgs = repo.recent_messages(user.id, limit=limit)
    return {
        "messages": [
            {
                "id": str(m.id),
                "sender": "user" if m.role == "user" else "bot",
                "role": m.role,
                "content": m.content,
                "timestamp": m.created_at.strftime("%I:%M %p") if m.created_at else ""
            }
            for m in msgs
        ]
    }

@app.delete("/api/messages/{tg_id}")
def clear_conversation_history(tg_id: int):
    user = repo.get_or_create_user(tg_id, "Analyst")
    with repo.SessionLocal() as db:
        db.query(repo.Message).filter(repo.Message.user_id == user.id).delete()
        db.commit()
    return {"status": "success", "message": "Conversation history cleared."}

from backend.services.redis_service import RedisService

@app.get("/api/market/quote/{ticker}")
def get_quote_api(ticker: str):
    return market.get_quote(ticker)

@app.get("/api/redis/status")
def get_redis_status():
    return RedisService.get_stats()

@app.post("/api/redis/flush")
def flush_redis():
    client = RedisService.get_client()
    keys = client.keys("*")
    if keys:
        client.delete(*keys)
    return {"status": "success", "flushed_keys": len(keys)}

class BriefTriggerRequest(BaseModel):
    telegram_id: Optional[int] = 1001
    brief_type: Optional[str] = "morning"  # "morning" or "evening"
    force: Optional[bool] = False

@app.post("/api/brief/trigger")
def trigger_brief_api(req: BriefTriggerRequest):
    """Generates and returns an executive Morning Market Brief or Evening Summary with 'Why It Matters' synthesis."""
    user = repo.get_or_create_user(req.telegram_id, "Analyst")
    if req.brief_type == "evening":
        content = proactive.generate_evening_summary(user)
    else:
        content = proactive.generate_morning_brief(user)
        
    return {
        "sent": True,
        "type": req.brief_type,
        "content": content,
        "generated_at": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
    }

class CatalystCheckRequest(BaseModel):
    ticker: str
    threshold_pct: Optional[float] = 3.0

@app.post("/api/proactive/catalyst-check")
def check_catalyst_api(req: CatalystCheckRequest):
    """Quality-gated catalyst & earnings watcher: returns detailed 'Why It Matters' analysis or remains SILENT if noise."""
    result = proactive.evaluate_material_catalyst(req.ticker, threshold_pct=req.threshold_pct)
    return {
        "ticker": req.ticker,
        "material_event_found": result is not None,
        "alert": result,
        "status": "alert_generated" if result else "silent_no_material_event"
    }

class FilingCheckRequest(BaseModel):
    ticker: str

@app.post("/api/proactive/sec-filing-check")
def check_filing_api(req: FilingCheckRequest):
    """Evaluates official SEC Form 8-K / 10-Q disclosures with balance-sheet & catalyst dissection."""
    filings = edgar.recent_filings(req.ticker, limit=1)
    if not filings:
        return {"ticker": req.ticker, "filing_found": False, "analysis": None}
    
    latest = filings[0]
    analysis = proactive.analyze_sec_regulatory_event(
        req.ticker,
        latest["form"],
        latest["date"],
        latest["description"],
        latest["url"]
    )
    return {
        "ticker": req.ticker,
        "filing_found": True,
        "form": latest["form"],
        "date": latest["date"],
        "analysis": analysis
    }

@app.get("/api/database/snapshots")
def get_db_snapshots(limit: int = 15):
    snaps = repo.get_latest_market_snapshots(limit=limit)
    return {
        "snapshots": [
            {
                "id": s.id,
                "ticker": s.ticker,
                "name": s.name,
                "price": s.price,
                "change": s.change,
                "change_pct": s.change_pct,
                "sparkline": s.sparkline,
                "source": s.source,
                "recorded_at": s.created_at.strftime("%I:%M:%S %p") if s.created_at else ""
            }
            for s in snaps
        ]
    }

class HoldingRequest(BaseModel):
    telegram_id: Optional[int] = 1001
    ticker: str
    shares: float
    avg_cost: Optional[float] = 0.0
    notes: Optional[str] = ""

@app.get("/api/database/holdings/{tg_id}")
def get_db_holdings(tg_id: int):
    user = repo.get_or_create_user(tg_id, "Analyst")
    holdings = repo.get_portfolio_holdings(user.id)
    return {
        "holdings": [
            {
                "id": h.id,
                "ticker": h.ticker,
                "shares": h.shares,
                "avg_cost": h.avg_cost,
                "notes": h.notes
            }
            for h in holdings
        ]
    }

@app.post("/api/database/holdings")
def add_or_update_holding(req: HoldingRequest):
    user = repo.get_or_create_user(req.telegram_id, "Analyst")
    holding = repo.save_portfolio_holding(user.id, req.ticker, req.shares, req.avg_cost or 0.0, req.notes or "")
    repo.add_fact(user.id, f"User holds {req.shares:g} shares of {req.ticker.upper()}")
    repo.add_to_watchlist(user.id, req.ticker)
    return {"status": "success", "holding": {"ticker": holding.ticker, "shares": holding.shares, "avg_cost": holding.avg_cost}}

# --- Financial Sectors API ---
@app.get("/api/sectors")
def get_all_sectors():
    """Returns real-time performance, constituents, and rotation sentiment across all financial sectors."""
    return {
        "sectors": sectors.get_all_sectors_performance(),
        "total_sectors": len(sectors.ALL_SECTORS)
    }

@app.get("/api/sectors/{sector_id}")
def get_single_sector(sector_id: str):
    sec = sectors.get_sector_by_id(sector_id)
    if not sec:
        raise HTTPException(status_code=404, detail="Sector not found")
    return sec

@app.get("/api/sectors/rotation/summary")
def get_sector_rotation():
    return {"summary": sectors.get_sector_rotation_summary()}

# --- Platform Integrations & Webhooks API ---
@app.get("/api/integrations")
def get_integrations_status():
    """Returns connectivity and webhook status for all external connected platforms."""
    return {
        "platforms": PlatformIntegrationHub.get_platforms_status()
    }

class DiscordBroadcastRequest(BaseModel):
    title: str = "Market Catalyst Alert"
    description: str
    webhook_url: Optional[str] = None

@app.post("/api/integrations/discord/test")
def test_discord_broadcast(req: DiscordBroadcastRequest):
    res = PlatformIntegrationHub.send_discord_alert(req.title, req.description, webhook_url=req.webhook_url)
    return res

class SlackBroadcastRequest(BaseModel):
    title: str = "Market Catalyst Alert"
    text: str
    webhook_url: Optional[str] = None

@app.post("/api/integrations/slack/test")
def test_slack_broadcast(req: SlackBroadcastRequest):
    res = PlatformIntegrationHub.send_slack_alert(req.title, req.text, webhook_url=req.webhook_url)
    return res

@app.post("/api/webhooks/tradingview")
async def tradingview_webhook(request: Request):
    """Inbound webhook receiver for TradingView Pine Script alerts and automated strategies."""
    try:
        body = await request.json()
    except Exception:
        body = {"raw": await request.body()}
    result = PlatformIntegrationHub.process_tradingview_alert(body)
    return result

@app.get("/api/export/portfolio-csv")
def export_portfolio_csv(tg_id: int = 1001):
    """Exports user portfolio holdings, live market quotes, and sector allocations as downloadable CSV."""
    user = repo.get_or_create_user(tg_id, "Analyst")
    holdings = repo.get_portfolio_holdings(user.id)
    
    csv_lines = ["Ticker,Shares,Current_Price,Total_Value,Today_Change_Pct,Sector,Source"]
    for h in holdings:
        q = market.get_quote(h.ticker)
        price = q.get("price", 0.0)
        chg = q.get("change_pct", 0.0)
        tot = round(h.shares * price, 2)
        sec_info = sectors.find_sector_for_ticker(h.ticker)
        sec_name = sec_info['name'] if sec_info else "Global Equities"
        csv_lines.append(f"{h.ticker},{h.shares},{price},{tot},{chg}%,{sec_name},Atlas Live Engine")

    csv_content = "\n".join(csv_lines)
    return Response(
        content=csv_content,
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=atlas_portfolio_{tg_id}.csv"}
    )

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
    # Initialize SQLite database schema
    repo.init_db()
    # Start Telegram bot in background asyncio task
    asyncio.create_task(start_telegram_bot())

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
