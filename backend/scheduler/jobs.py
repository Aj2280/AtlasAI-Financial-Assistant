"""Proactive Intelligent JobQueue:
Delivers scheduled Morning Briefs (08:00), Evening Summaries (18:00),
Material Catalyst & Earnings Dissections, and SEC Regulatory Alerts with strict Noise Suppression.
"""
import asyncio
import logging
from datetime import datetime
from zoneinfo import ZoneInfo
from telegram.constants import ParseMode
from telegram.ext import Application, ContextTypes

from backend.db import repo
from backend.services import proactive, edgar, market

log = logging.getLogger(__name__)

async def _send_markdown(app: Application, tg_id: int, text: str) -> None:
    """Sends clean markdown formatted proactive notification to Telegram user."""
    if tg_id <= 10000:
        return
    try:
        await app.bot.send_message(chat_id=tg_id, text=text, parse_mode=ParseMode.MARKDOWN)
    except Exception:
        try:
            await app.bot.send_message(chat_id=tg_id, text=text)
        except Exception as e:
            log.warning(f"Failed to send proactive message to tg_id {tg_id}: {e}")

async def briefing_tick(context: ContextTypes.DEFAULT_TYPE) -> None:
    """Runs every minute; checks user local timezone and delivers Morning Briefs (08:00) or Evening Summaries (18:00)."""
    for user in repo.all_users():
        if user.tg_id <= 10000:
            continue
            
        user_tz_str = getattr(user, 'timezone', None) or 'Asia/Kolkata'
        try:
            now_local = datetime.now(ZoneInfo(user_tz_str))
        except Exception:
            now_local = datetime.utcnow()
            
        today_date_str = now_local.strftime("%Y-%m-%d")
        current_time_hm = now_local.strftime("%H:%M")
        
        # User defined morning brief time (default 08:00)
        morning_target = user.briefing_time or "08:00"
        evening_target = "18:00"

        # 1. Morning Market Briefing Trigger
        if current_time_hm == morning_target and user.last_brief_date != f"morning_{today_date_str}":
            brief_content = proactive.generate_morning_brief(user)
            repo.update_user(user.id, last_brief_date=f"morning_{today_date_str}")
            await _send_markdown(context.application, user.tg_id, brief_content)

        # 2. Evening Market Summary Trigger
        elif current_time_hm == evening_target and user.last_brief_date != f"evening_{today_date_str}":
            summary_content = proactive.generate_evening_summary(user)
            repo.update_user(user.id, last_brief_date=f"evening_{today_date_str}")
            await _send_markdown(context.application, user.tg_id, summary_content)

async def price_alert_tick(context: ContextTypes.DEFAULT_TYPE) -> None:
    """Runs every 5 minutes: Quality-gated catalyst & earnings watcher with noise suppression."""
    today = datetime.utcnow().strftime("%Y-%m-%d")
    
    for user in repo.all_users():
        if user.tg_id <= 10000:
            continue
            
        watchlist = repo.get_watchlist(user.id)
        holdings = repo.get_portfolio_holdings(user.id)
        all_tickers = list(dict.fromkeys([h.ticker for h in holdings] + watchlist))
        
        for ticker in all_tickers[:6]:
            alert_content = proactive.evaluate_material_catalyst(ticker, threshold_pct=3.0)
            if alert_content:
                # Deduplicate: Only send once per asset per day unless multiple distinct alerts
                alert_key = f"catalyst_{ticker}_{today}"
                cached = getattr(user, 'last_brief_date', '')
                if cached != alert_key:
                    await _send_markdown(context.application, user.tg_id, alert_content)

async def filing_tick(context: ContextTypes.DEFAULT_TYPE) -> None:
    """Runs hourly: Evaluates material SEC Form 8-K, 10-Q, 10-K regulatory disclosures."""
    for user in repo.all_users():
        if user.tg_id <= 10000:
            continue
            
        watchlist = repo.get_watchlist(user.id)
        for ticker in watchlist[:5]:
            filings = edgar.recent_filings(ticker, limit=1)
            if not filings:
                continue
                
            latest = filings[0]
            # Check if this filing was already analyzed
            active_alerts = repo.active_alerts(user_id=user.id, type="filing")
            matching_alert = next((a for a in active_alerts if a.ticker == ticker), None)
            
            if matching_alert and matching_alert.meta == latest["accession"]:
                continue
                
            analysis = proactive.analyze_sec_regulatory_event(
                ticker,
                latest["form"],
                latest["date"],
                latest["description"],
                latest["url"]
            )
            
            if analysis:
                if matching_alert:
                    repo.update_alert(matching_alert.id, meta=latest["accession"])
                await _send_markdown(context.application, user.tg_id, analysis)

async def reminder_tick(context: ContextTypes.DEFAULT_TYPE) -> None:
    """Runs every minute: Fires user scheduled calendar/earnings reminders."""
    now = datetime.utcnow()
    for al in repo.active_alerts(type="reminder"):
        if al.remind_at and al.remind_at <= now:
            repo.deactivate_alert(al.id)
            user = next((u for u in repo.all_users() if u.id == al.user_id), None)
            if user and user.tg_id > 10000:
                await _send_markdown(context.application, user.tg_id, f"⏰ **Scheduled Alert & Reminder**\n\n{al.note}")

def register_jobs(app: Application) -> None:
    """Registers proactive intelligence jobs with APScheduler JobQueue."""
    jq = app.job_queue
    if jq:
        jq.run_repeating(briefing_tick, interval=60, first=10)
        jq.run_repeating(reminder_tick, interval=60, first=15)
        jq.run_repeating(price_alert_tick, interval=300, first=30)
        jq.run_repeating(filing_tick, interval=3600, first=60)
        log.info("Proactive Intelligent JobQueue registered successfully.")
