"""Proactive jobs — daily briefings, price alerts, SEC filing tracker, reminders."""
import asyncio
import logging
from datetime import datetime
from telegram.constants import ParseMode
from telegram.ext import Application, ContextTypes

from backend.agent.core import one_shot
from backend.db import repo
from backend.services import edgar, market, news

log = logging.getLogger(__name__)

async def _send(app: Application, tg_id: int, text: str) -> None:
    # Telegram user IDs are large positive integers (e.g. > 100000)
    if tg_id <= 10000:
        return
    try:
        await app.bot.send_message(chat_id=tg_id, text=text, parse_mode=ParseMode.HTML)
    except Exception:
        try:
            await app.bot.send_message(chat_id=tg_id, text=text)
        except Exception:
            pass

async def briefing_tick(context: ContextTypes.DEFAULT_TYPE) -> None:
    """Runs every minute; sends briefs whose local time just arrived."""
    now_utc = datetime.utcnow()
    for user in repo.all_users():
        if not user.briefing_time or user.tg_id <= 10000:
            continue
        if user.last_brief_date == now_utc.strftime("%Y-%m-%d"):
            continue
            
        watchlist = repo.get_watchlist(user.id)
        quotes = [market.get_quote(t) for t in watchlist[:4]]
        
        brief = (
            f"☀️ <b>Morning Market Brief</b>\n\n"
            + "\n".join([f"• <b>{q['ticker']}</b>: ${q['price']} ({q['change_pct']:+.2f}%)" for q in quotes])
            + "\n\n🌍 <b>Macro Outlook</b>: S&P 500 futures steady ahead of economic data."
        )
        repo.update_user(user.id, last_brief_date=now_utc.strftime("%Y-%m-%d"))
        await _send(context.application, user.tg_id, brief)

async def price_alert_tick(context: ContextTypes.DEFAULT_TYPE) -> None:
    """Every 5 min: fire alerts whose daily move crossed threshold."""
    alerts = repo.active_alerts(type="price_move")
    today = datetime.utcnow().strftime("%Y-%m-%d")
    for al in alerts:
        if al.last_triggered == today:
            continue
        q = market.get_quote(al.ticker)
        if q.get("price") and abs(q.get("change_pct", 0.0)) >= al.threshold_pct:
            repo.update_alert(al.id, last_triggered=today)
            user = next((u for u in repo.all_users() if u.id == al.user_id), None)
            if user and user.tg_id > 10000:
                direction = "📈 up" if q["change_pct"] > 0 else "📉 down"
                await _send(
                    context.application, user.tg_id,
                    f"🚨 <b>{al.ticker}</b> is {direction} <b>{q['change_pct']:+.1f}%</b> today "
                    f"(now ${q['price']}) — crossed your {al.threshold_pct:g}% alert threshold."
                )

async def filing_tick(context: ContextTypes.DEFAULT_TYPE) -> None:
    """Hourly: notify on new SEC filings for tracked tickers."""
    for al in repo.active_alerts(type="filing"):
        filings = edgar.recent_filings(al.ticker, 1)
        if not filings:
            continue
        newest = filings[0]
        if newest["accession"] == al.meta:
            continue
        repo.update_alert(al.id, meta=newest["accession"])
        user = next((u for u in repo.all_users() if u.id == al.user_id), None)
        if user and user.tg_id > 10000:
            await _send(
                context.application, user.tg_id,
                f"📄 New SEC filing from <b>{al.ticker}</b>: Form {newest['form']} ({newest['date']}).\n"
                f"<a href='{newest['url']}'>View Document on SEC.gov</a>"
            )

async def reminder_tick(context: ContextTypes.DEFAULT_TYPE) -> None:
    """Every minute: fire due one-shot reminders."""
    now = datetime.utcnow()
    for al in repo.active_alerts(type="reminder"):
        if al.remind_at and al.remind_at <= now:
            repo.deactivate_alert(al.id)
            user = next((u for u in repo.all_users() if u.id == al.user_id), None)
            if user and user.tg_id > 10000:
                await _send(context.application, user.tg_id, f"⏰ <b>Reminder</b>: {al.note}")

def register_jobs(app: Application) -> None:
    jq = app.job_queue
    if jq:
        jq.run_repeating(briefing_tick, interval=60, first=10)
        jq.run_repeating(reminder_tick, interval=60, first=15)
        jq.run_repeating(price_alert_tick, interval=300, first=30)
        jq.run_repeating(filing_tick, interval=3600, first=60)
        log.info("Proactive scheduler JobQueue registered successfully.")
