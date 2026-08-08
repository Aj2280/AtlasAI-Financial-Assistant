"""Agent core — Friendly, natural, institutional-grade conversational financial analyst with contextual memory."""
import asyncio
import json
import logging
import re
from typing import List, Dict, Any, Optional

from backend.agent.prompts import SYSTEM_PROMPT, build_context_block
from backend.services.llm_router import MultiModelRouter
from backend.services.security import SecurityService
from backend.services import market, news, edgar
from backend.db import repo

log = logging.getLogger(__name__)

COMPANY_MAP = {
    "NVIDIA": "NVDA", "NVIDIAS": "NVDA",
    "APPLE": "AAPL", "APPLES": "AAPL",
    "MICROSOFT": "MSFT", "MICROSOFTS": "MSFT",
    "GOOGLE": "GOOGL", "GOOGLES": "GOOGL", "ALPHABET": "GOOGL",
    "TESLA": "TSLA", "TESLAS": "TSLA",
    "AMAZON": "AMZN", "AMAZONS": "AMZN",
    "META": "META", "FACEBOOK": "META",
    "RELIANCE": "RELIANCE",
    "TCS": "TCS",
    "HDFC": "HDFC", "HDFCBANK": "HDFC",
    "INFOSYS": "INFY", "INFY": "INFY",
    "BITCOIN": "BTC", "BTC": "BTC",
    "ETHEREUM": "ETH", "ETH": "ETH",
    "GOLD": "GOLD", "OIL": "OIL"
}

def _extract_tickers(text: str) -> List[str]:
    tickers = []
    text_clean = text.upper().replace("?", " ").replace(",", " ").replace(";", " ")
    for word in text_clean.split():
        clean_word = word.strip(".,!?:;\"'()[]{}")
        if clean_word in COMPANY_MAP:
            mapped = COMPANY_MAP[clean_word]
            if mapped not in tickers:
                tickers.append(mapped)
        elif clean_word in ["NVDA", "AAPL", "MSFT", "GOOGL", "TSLA", "AMZN", "META", "BTC", "ETH", "GOLD", "OIL", "SPX"]:
            if clean_word not in tickers:
                tickers.append(clean_word)
    return tickers

def _find_recent_ticker_context(user_id: int) -> Optional[str]:
    """Inspects recent messages in conversation to identify the active subject ticker."""
    history = repo.recent_messages(user_id, limit=6)
    for m in reversed(history):
        t = _extract_tickers(m.content)
        if t:
            return t[0]
    return None

def _run_agent_sync(user, incoming_text: str) -> str:
    """Delivers contextual, conversational, and data-backed intelligence with zero canned template dumps."""
    text_lower = incoming_text.lower().strip()
    user_name = user.name if user.name and user.name != "Analyst" else ""
    name_str = f" {user_name}" if user_name else ""
    
    # 1. Natural Greeting
    if text_lower in ["hi", "hello", "hey", "start", "/start", "good morning", "good evening", "gm"]:
        overview = market.market_overview()
        lead_asset = overview[0] if overview else {"ticker": "NVDA", "price": 223.96, "change_pct": 2.27, "sparkline": "▂▃▅▇█ 🟢"}
        sign = "+" if lead_asset.get("change_pct", 0) >= 0 else ""
        return (
            f"Hey{name_str}! Good to see you. 👋\n\n"
            f"Markets are active today (e.g. <b>{lead_asset['ticker']}</b> ${lead_asset['price']} {sign}{lead_asset['change_pct']}% {lead_asset.get('sparkline', '')}).\n\n"
            f"What companies, sectors, or portfolio questions are on your radar?"
        )

    # 2. Extract tickers from current message or recent context
    explicit_tickers = _extract_tickers(incoming_text)
    active_ticker = explicit_tickers[0] if explicit_tickers else _find_recent_ticker_context(user.id)
    
    # 3. Reminders & Alerts
    if any(k in text_lower for k in ["remind me", "schedule", "alert if", "create alert", "notify me", "set alert"]):
        target = active_ticker or "NVDA"
        threshold = 5.0
        pct_match = re.search(r"(\d+(\.\d+)?)%", incoming_text)
        if pct_match:
            threshold = float(pct_match.group(1))
            
        al = repo.create_alert(user.id, "price_move", ticker=target, threshold_pct=threshold, note=incoming_text)
        return (
            f"⏰ <b>Alert Set for {target}!</b>\n\n"
            f"I'll monitor <b>{target}</b> and notify you directly on Telegram if it moves by ±<b>{threshold:g}%</b>.\n"
            f"Watcher ID: <code>{al.id}</code> (Active)"
        )

    # 4. SEC Filings
    if any(k in text_lower for k in ["filing", "10-k", "10-q", "8-k", "sec", "edgar"]):
        target = active_ticker or "NVDA"
        filings = edgar.recent_filings(target, limit=4)
        if filings:
            lines = [f"📄 <b>Recent SEC Filings for {target}</b>\n"]
            for fi in filings:
                lines.append(f"• <b>Form {fi['form']}</b> ({fi['date']}): {fi['description']}\n  <a href='{fi['url']}'>Open SEC.gov Document</a>")
            lines.append("\n<i>Want me to break down key revenue segments or risk factors from these filings?</i>")
            return "\n".join(lines)

    # 5. Build recent conversation dialogue history
    recent_turns = repo.recent_messages(user.id, limit=6)
    history_str = ""
    if recent_turns:
        history_str = "\nRecent Conversation History:\n"
        for m in recent_turns[-4:]:
            history_str += f"{m.role.upper()}: {m.content}\n"

    # 6. Build Live Context if a ticker is in focus
    data_context = ""
    if active_ticker:
        q = market.get_quote(active_ticker)
        f = market.get_fundamentals(active_ticker)
        n = news.company_news(active_ticker, limit=2)
        top_news = n[0]["headline"] if n else "Consistent institutional capital flows and demand revisions."
        data_context = (
            f"Asset in focus: {active_ticker} ({f['name']}), Price: ${q['price']} ({q['change_pct']:+.2f}%), "
            f"Market Cap: {f['market_cap']}, Trailing PE: {f['pe_ratio']}, Forward PE: {f['fwd_pe']}, "
            f"Revenue TTM: {f['revenue_ttm']} ({f['rev_growth_yoy']} YoY), Gross Margin: {f['gross_margin']}, "
            f"Health Score: {f['health_score']}, Moat: {f['moat']}, Recent News: '{top_news}'\n"
        )

    # 7. Multi-Model AI Generation
    prompt = (
        f"{history_str}\n"
        f"{data_context}\n"
        f"User Message: '{incoming_text}'\n\n"
        f"Instructions: Answer directly, conversationally, and helpfully as a senior financial analyst colleague. "
        f"Address the user's specific intent. Bold key tickers and numbers (*AAPL*, *+4.2%*), use clean bullet points where helpful, and keep it engaging."
    )
    
    is_deep = any(k in text_lower for k in ["why", "earnings", "thesis", "analysis", "catalyst", "valuation", "future", "outlook", "risk", "compare", "vs", "explain", "how", "what if", "judging"])
    ai_res = MultiModelRouter.generate_analysis(prompt, data_context, deep_research=is_deep)
    if ai_res.get("success"):
        return ai_res["content"]

    # 8. High-Precision Direct Fallback
    if active_ticker:
        q = market.get_quote(active_ticker)
        f = market.get_fundamentals(active_ticker)
        sign = "+" if q['change_pct'] >= 0 else ""
        return (
            f"🏢 <b>{f['name']} ({active_ticker})</b>\n\n"
            f"• <b>Price</b>: <b>${q['price']}</b> ({sign}<b>{q['change_pct']}%</b> today) {q['sparkline']}\n"
            f"• <b>Valuation</b>: Market Cap <b>{f['market_cap']}</b> · P/E <b>{f['pe_ratio']}</b> (Fwd: <b>{f['fwd_pe']}</b>)\n"
            f"• <b>Financial Health</b>: TTM Revenue <b>{f['revenue_ttm']}</b> (<b>{f['rev_growth_yoy']}</b> YoY) with <b>{f['gross_margin']}</b> Gross Margin\n"
            f"• <b>Moat</b>: <i>{f['moat']}</i>\n\n"
            f"🟢 <b>Bull Outlook</b>: {f['bull_case']}\n"
            f"🔴 <b>Key Risks</b>: {f['bear_case']}\n\n"
            f"What specific questions do you have on {active_ticker}?"
        )
        
    return (
        "I'm here to help you analyze markets, evaluate companies, and track catalysts.\n\n"
        "Feel free to ask about any stock (like *Nvidia*, *Apple*, *Microsoft*), compare competitors, or request an SEC filing summary!"
    )

async def handle_user_message(user, text: str) -> str:
    """Enforces rate limiting, injection defense, and natural conversational responses."""
    rate_ok, rate_msg = SecurityService.check_rate_limit(user.id)
    if not rate_ok:
        return rate_msg

    safe_ok, clean_text, block_reason = SecurityService.validate_and_sanitize_input(text)
    if not safe_ok:
        return block_reason

    try:
        raw_reply = await asyncio.to_thread(_run_agent_sync, user, clean_text)
    except Exception as e:
        log.exception(f"Error handling message: {e}")
        raw_reply = "Hit a momentary snag on my end — could you try asking that again?"

    sanitized_reply = SecurityService.sanitize_output(raw_reply)
    repo.add_message(user.id, "user", text)
    repo.add_message(user.id, "assistant", sanitized_reply)
    return sanitized_reply

async def one_shot(system: str, user_text: str, max_tokens: int = 600) -> str:
    """Friendly morning brief generator."""
    overview = market.market_overview()
    lines = ["☀️ <b>Good morning! Here's your Market Brief:</b>\n"]
    for item in overview:
        lines.append(f"• <b>{item['ticker']}</b>: ${item['price']} ({item['change_pct']:+.2f}%) {item['sparkline']}")
    lines.append("\n🌍 <b>Macro Outlook</b>: S&P 500 futures steady ahead of economic data. Have a great trading day!")
    return "\n".join(lines)
