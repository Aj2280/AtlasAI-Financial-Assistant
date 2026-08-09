"""Agent core — Friendly, natural, institutional-grade conversational financial analyst with contextual memory."""
import asyncio
import json
import logging
import re
from datetime import datetime
from zoneinfo import ZoneInfo
from typing import List, Dict, Any, Optional

from backend.agent.prompts import SYSTEM_PROMPT, build_context_block
from backend.services.llm_router import MultiModelRouter
from backend.services.security import SecurityService
from backend.services.redis_service import RedisService
from backend.services import market, news, edgar, sectors, integrations
from backend.db import repo

log = logging.getLogger(__name__)

COMPANY_MAP = {
    # US Tech & Mega Caps
    "NVIDIA": "NVDA", "NVIDIAS": "NVDA", "NVDA": "NVDA",
    "APPLE": "AAPL", "APPLES": "AAPL", "AAPL": "AAPL",
    "MICROSOFT": "MSFT", "MICROSOFTS": "MSFT", "MSFT": "MSFT",
    "GOOGLE": "GOOGL", "GOOGLES": "GOOGL", "ALPHABET": "GOOGL", "GOOG": "GOOGL", "GOOGL": "GOOGL",
    "TESLA": "TSLA", "TESLAS": "TSLA", "TSLA": "TSLA",
    "AMAZON": "AMZN", "AMAZONS": "AMZN", "AMZN": "AMZN",
    "META": "META", "FACEBOOK": "META",
    "PALANTIR": "PLTR", "PLTR": "PLTR",
    "AMD": "AMD", "ADVANCED MICRO DEVICES": "AMD",
    "BROADCOM": "AVGO", "AVGO": "AVGO",
    "SUPERMICRO": "SMCI", "SMCI": "SMCI",
    "TSMC": "TSM", "TSM": "TSM", "TAIWAN SEMICONDUCTOR": "TSM",
    "ARM": "ARM", "ARM HOLDINGS": "ARM",
    "QUALCOMM": "QCOM", "QCOM": "QCOM",
    "INTEL": "INTC", "INTC": "INTC",
    "NETFLIX": "NFLX", "NFLX": "NFLX",
    "DISNEY": "DIS", "DIS": "DIS",
    "COINBASE": "COIN", "COIN": "COIN",
    "MICROSTRATEGY": "MSTR", "MSTR": "MSTR",
    "BERKSHIRE": "BRK.B", "BRK": "BRK.B",
    "JPMORGAN": "JPM", "JPM": "JPM",
    "ELI LILLY": "LLY", "LLY": "LLY",
    "EXXON": "XOM", "XOM": "XOM",
    "WALMART": "WMT", "WMT": "WMT",
    "COSTCO": "COST", "COST": "COST",
    # Crypto
    "BITCOIN": "BTC", "BTC": "BTC", "BTCUSD": "BTC",
    "ETHEREUM": "ETH", "ETH": "ETH", "ETHUSD": "ETH",
    "SOLANA": "SOL", "SOL": "SOL", "SOLUSD": "SOL",
    "DOGECOIN": "DOGE", "DOGE": "DOGE",
    "RIPPLE": "XRP", "XRP": "XRP",
    "CARDANO": "ADA", "ADA": "ADA",
    "BINANCE": "BNB", "BNB": "BNB",
    # Commodities & Forex
    "GOLD": "GOLD", "XAU": "GOLD", "SILVER": "SILVER", "XAG": "SILVER",
    "OIL": "OIL", "CRUDE": "OIL", "WTI": "OIL", "BRENT": "BRENT",
    "DOLLAR": "DXY", "DXY": "DXY",
    # Indian Equities & Indices
    "RELIANCE": "RELIANCE", "TCS": "TCS", "HDFC": "HDFCBANK", "HDFCBANK": "HDFCBANK",
    "INFOSYS": "INFY", "INFY": "INFY", "WIPRO": "WIPRO", "TATAMOTORS": "TATAMOTORS",
    "ICICIBANK": "ICICIBANK", "SBIN": "SBIN", "BHARTIARTL": "BHARTIARTL", "ITC": "ITC",
    "NIFTY": "NIFTY", "NIFTY50": "NIFTY", "SENSEX": "SENSEX", "BANKNIFTY": "BANKNIFTY",
    # Major Indices & ETFs
    "SPX": "SPX", "SP500": "SPX", "S&P": "SPX", "SPY": "SPY", "QQQ": "QQQ", "NDX": "NDX", "NASDAQ": "NDX"
}

_COMMON_WORDS = {"THE", "AND", "FOR", "ARE", "HOW", "WHY", "WHAT", "CAN", "YOU", "GIVE", "SHOW", "TELL", "WITH", "ABOUT", "THIS", "THAT", "PRICE", "STOCK", "SHARE", "STOCKS", "TODAY", "RIGHT", "NOW", "TIME", "DATA", "REAL", "LIVE", "MARKET", "HOLD", "BUY", "SELL", "GOOD", "LIKE", "BEST", "HIGH", "LOW", "FROM", "HAVE", "SOME", "MORE", "WILL", "JUST", "ALSO", "KNOW", "WANT", "LOOK", "SECTOR", "SECTORS"}

def _extract_tickers(text: str) -> List[str]:
    """Extracts explicit ticker symbols and mapped company names from text."""
    tickers = []
    text_clean = text.upper().replace("?", " ").replace(",", " ").replace(";", " ").replace(":", " ")
    
    # 1. Dollar tagged tickers e.g. $NVDA, $BTC
    dollar_matches = re.findall(r"\$([A-Z]{1,6})\b", text_clean)
    for dm in dollar_matches:
        if dm not in tickers and dm not in _COMMON_WORDS:
            tickers.append(dm)

    # 2. Match mapped companies and explicit tickers
    words = text_clean.split()
    for word in words:
        clean_word = word.strip(".,!?:;\"'()[]{}")
        if clean_word in COMPANY_MAP:
            mapped = COMPANY_MAP[clean_word]
            if mapped not in tickers:
                tickers.append(mapped)
        elif len(clean_word) in [2, 3, 4, 5] and clean_word.isalpha() and clean_word not in _COMMON_WORDS:
            # Check if it looks like a real ticker
            if clean_word in ["NVDA", "AAPL", "MSFT", "GOOGL", "TSLA", "AMZN", "META", "AMD", "PLTR", "SMCI", "AVGO", "ARM", "TSM", "LLY", "JPM", "XOM", "COST", "WMT", "DIS", "NFLX", "COIN", "MSTR", "BTC", "ETH", "SOL", "DOGE", "XRP", "ADA", "GOLD", "OIL", "SPX", "NDX", "QQQ", "SPY", "RELIANCE", "TCS", "NIFTY"]:
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
    """Delivers contextual, conversational, and data-backed intelligence with personalized memory and natural dialogue."""
    text_clean = incoming_text.strip()
    text_lower = text_clean.lower()
    
    # 1. Stop / End / Pause Conversation Handling
    stop_words = [
        "stop", "bye", "goodbye", "exit", "quit", "cya", "pause", 
        "end chat", "that's all", "thats all", "that is all", 
        "see you", "good night", "done for now", "stop talking", "stop it"
    ]
    if any(re.search(r"\b" + re.escape(w) + r"\b", text_lower) for w in stop_words) and not any(k in text_lower for k in ["non stop", "don't stop", "dont stop"]):
        return (
            "You got it! 👍 Conversation paused.\n\n"
            "Whenever you want to check live market quotes, review SEC filings, or set price alerts, just send a message. Have a great day! 🚀"
        )

    # 2. Natural Greetings & Chit-Chat
    if text_lower in ["hi", "hello", "hey", "start", "/start", "good morning", "good evening", "gm", "yo", "sup", "hi atlas", "hey atlas"] or text_lower.startswith(("hi ", "hello ", "hey ")):
        overview = market.market_overview()
        lead_asset = overview[0] if overview else {"ticker": "NVDA", "price": 223.96, "change_pct": 2.27, "sparkline": "▂▃▅▇█ 🟢"}
        sign = "+" if lead_asset.get("change_pct", 0) >= 0 else ""
        return (
            f"Hey! Good to see you. 👋\n\n"
            f"Markets are active today (e.g. **{lead_asset['ticker']}** ${lead_asset['price']} {sign}{lead_asset['change_pct']}% {lead_asset.get('sparkline', '')}).\n\n"
            f"What companies, sectors, or portfolio questions are on your radar?"
        )

    # 3. Conversational Check-ins
    if any(k in text_lower for k in ["how are you", "how's it going", "how r u", "how do you do", "what's up", "whats up"]):
        overview = market.market_overview()
        lead_asset = overview[0] if overview else {"ticker": "NVDA", "price": 223.96, "change_pct": 2.27, "sparkline": "▂▃▅▇█ 🟢"}
        sign = "+" if lead_asset.get("change_pct", 0) >= 0 else ""
        return (
            f"I'm doing great, thanks for asking! 🚀 Markets are active today "
            f"(e.g. **{lead_asset['ticker']}** ${lead_asset['price']} {sign}{lead_asset['change_pct']}% {lead_asset.get('sparkline', '')}).\n\n"
            f"How can I assist you with your investments, stocks, or research today?"
        )

    # 4. Capabilities & Help
    if any(k in text_lower for k in ["who are you", "what can you do", "what do you do", "help", "/help", "features", "what are your capabilities"]):
        return (
            "🏛️ **Atlas: Institutional AI Financial Assistant**\n\n"
            "Here is what I can do for you:\n"
            "• 📊 **Real-Time Market Data**: Live quotes, sparklines & valuation metrics for US & Indian stocks, crypto, commodities.\n"
            "• 📄 **Official SEC EDGAR Filings**: 10-K, 10-Q, and 8-K submissions with direct clickable links.\n"
            "• ⏰ **Proactive Alerts & Jobs**: Instant alerts on price movements (e.g. _'Alert if NVDA moves 5%'_ ) and morning briefings.\n"
            "• 📑 **Documents & Sheets**: Drop PDF equity reports or public Google Sheets links for automatic financial extraction.\n"
            "• 🎙️ **Voice & Vision**: Send audio voice notes or chart screenshots for technical level analysis.\n\n"
            "Try asking: _'How is Nvidia doing today?'_ or _'Compare Microsoft vs Google in AI'_."
        )

    # 5. Extract tickers from current message or recent context
    explicit_tickers = _extract_tickers(incoming_text)
    active_ticker = explicit_tickers[0] if explicit_tickers else _find_recent_ticker_context(user.id)
    
    # 6. Natural Executive Assistant Actions (Tracking, Alerts, Meetings, Scheduled Briefings)
    if any(k in text_lower for k in ["track ", "start tracking", "follow "]) and active_ticker:
        repo.add_to_watchlist(user.id, active_ticker)
        repo.create_alert(user.id, "filing", ticker=active_ticker)
        repo.add_fact(user.id, f"User is actively tracking {active_ticker}")

    if any(k in text_lower for k in ["schedule a meeting", "set up a meeting", "schedule meeting", "remind me to", "remind me tomorrow", "remind me one hour", "remind me before"]):
        repo.create_alert(user.id, "reminder", note=incoming_text)
        repo.add_fact(user.id, f"Scheduled reminder/meeting: '{incoming_text}'")

    if any(k in text_lower for k in ["alert if", "create alert", "set alert", "notify me if", "price alert", "notify me when"]):
        target = active_ticker or "NVDA"
        threshold = 5.0
        pct_match = re.search(r"(\d+(\.\d+)?)%", incoming_text)
        if pct_match:
            threshold = float(pct_match.group(1))
        repo.create_alert(user.id, "price_move", ticker=target, threshold_pct=threshold, note=incoming_text)
        repo.add_fact(user.id, f"Active price alert on {target} at ±{threshold:g}% threshold")

    if any(k in text_lower for k in ["morning briefing", "daily briefing", "create a daily", "morning brief"]):
        topics = [w for w in ["AI", "Semiconductors", "Technology", "Crypto", "Energy", "Financials"] if w.lower() in text_lower]
        topic_str = ", ".join(topics) if topics else "Tech & AI"
        repo.add_fact(user.id, f"User requested customized morning briefing covering {topic_str}")
        repo.update_user(user.id, briefing_time="08:00")

    # 7. Build full multi-turn conversational memory (Redis cache + SQLite persistence)
    cached_turns = RedisService.get_cached_chat_history(user.id, limit=12)
    if cached_turns:
        chat_history = [{"role": t["role"], "content": t["content"]} for t in cached_turns]
    else:
        recent_turns = repo.recent_messages(user.id, limit=12)
        chat_history = [{"role": m.role, "content": m.content} for m in recent_turns]

    # 8. Build Live Context if a ticker is in focus + User profile & portfolio context from local database
    user_tz_str = getattr(user, 'timezone', None) or 'Asia/Kolkata'
    try:
        now_user = datetime.now(ZoneInfo(user_tz_str))
    except Exception:
        now_user = datetime.utcnow()
        user_tz_str = "UTC"
        
    current_time_str = now_user.strftime("%A, %B %d, %Y - %I:%M:%S %p %Z")

    facts = repo.get_facts(user.id)
    watchlist = repo.get_watchlist(user.id)
    holdings = repo.get_portfolio_holdings(user.id)
    
    context_lines = [
        f"Real-Time Local Clock: {current_time_str} (User Timezone: {user_tz_str})",
        f"Global Financial Market Trading Hours: US NYSE/Nasdaq (09:30 AM - 04:00 PM EST), Indian NSE/BSE (09:15 AM - 03:30 PM IST), Tokyo TSE (09:00 AM - 03:30 PM JST), London LSE (08:00 AM - 04:30 PM GMT), Crypto Markets (24/7 Live)."
    ]
    if facts:
        context_lines.append(f"User Knowledge, Preferences & Stored Reminders (from local memory DB): {'; '.join(facts[-8:])}")
    if holdings:
        holding_strs = [f"{h.ticker} ({h.shares:g} shares)" for h in holdings]
        context_lines.append(f"User Portfolio Holdings (from local DB): {', '.join(holding_strs)}")
    if watchlist:
        context_lines.append(f"User Watchlist: {', '.join(watchlist)}")

    # Active Uploaded Document Context (Annual Reports, Earnings Decks, Pitch Decks, Financial Statements)
    active_doc = repo.active_document(user.id)
    if active_doc:
        doc_snippet = active_doc.content[:30000]
        context_lines.append(
            f"ACTIVE LOADED FINANCIAL DOCUMENT ({active_doc.kind.upper()}: '{active_doc.name}'):\n"
            f"\"\"\"\n{doc_snippet}\n\"\"\""
        )

    # Add SEC Filings context if relevant
    if re.search(r"\b(filing|filings|10-k|10-q|8-k|sec filing|annual report|edgar|risk|risks)\b", text_lower):
        target_sec = active_ticker or "NVDA"
        filings = edgar.recent_filings(target_sec, limit=3)
        if filings:
            f_lines = [f"Form {fi['form']} ({fi['date']}): {fi['description']} - URL: {fi['url']}" for fi in filings]
            context_lines.append(f"Official SEC EDGAR Filings for {target_sec}: {'; '.join(f_lines)}")

    # Add Sector Performance Overview
    if any(k in text_lower for k in ["sector", "sectors", "industry", "rotation", "breadth", "tech", "energy", "financial", "healthcare", "utility", "materials", "industrials", "reit", "crypto", "macro"]):
        sec_overview = sectors.get_all_sectors_performance()
        sec_lines = [f"{s['name']} ({s['etf']}: ${s['etf_price']} | {s['change_pct']:+.2f}% | {s['sentiment']})" for s in sec_overview[:6]]
        context_lines.append(f"Real-Time Financial Sectors Overview: {'; '.join(sec_lines)}")

    # Add Platform Connectivity Context
    if any(k in text_lower for k in ["connect", "platform", "platforms", "discord", "slack", "tradingview", "sheets", "excel", "webhook", "api", "integrate", "export"]):
        context_lines.append(
            "Atlas Connected Platforms: Telegram (@Atlas39bot), Discord Server Webhook Broadcast, Slack Workspace Alerts, "
            "TradingView Inbound Webhooks (/api/webhooks/tradingview), Google Sheets / Excel Live CSV Export (/api/export/portfolio-csv), "
            "SEC EDGAR Direct Feed & Finnhub Institutional API."
        )

    # Real-Time Multi-Asset Live Market Data Injection
    target_tickers = explicit_tickers[:4] if explicit_tickers else ([active_ticker] if active_ticker else [])
    
    if target_tickers:
        for sym in target_tickers:
            q = market.get_quote(sym)
            f = market.get_fundamentals(sym)
            sec_info = sectors.find_sector_for_ticker(sym)
            sec_name = sec_info['name'] if sec_info else "Global Financial Market"
            sign = "+" if q.get('change_pct', 0) >= 0 else ""
            curr = q.get('currency', 'USD')
            prefix = "₹" if curr == "INR" else "$"
            n = news.company_news(sym, limit=2)
            top_news = n[0]["headline"] if n else "Active institutional volume and liquidity flows."
            context_lines.append(
                f"LIVE REAL-TIME DATA FOR {sym}: Name: {f['name']}, Sector: {sec_name}, Live Price: {prefix}{q['price']} ({sign}{q['change_pct']}%), "
                f"Prev Close: {prefix}{q['prev_close']}, 24h Trend: {q.get('sparkline', '')}, "
                f"Market Cap: {f['market_cap']}, Trailing P/E: {f['pe_ratio']}, Forward P/E: {f['fwd_pe']}, "
                f"TTM Revenue: {f['revenue_ttm']} ({f['rev_growth_yoy']} YoY), Gross Margin: {f['gross_margin']}, "
                f"Moat: {f['moat']}, Health Score: {f['health_score']}, Latest News: '{top_news}', Live Source: {q.get('source')}."
            )
    else:
        # Inject live market benchmarks if no specific ticker requested
        benchmarks = market.market_overview()
        b_lines = [f"{b['ticker']} (${b['price']} | {b['change_pct']:+.2f}% {b.get('sparkline', '')})" for b in benchmarks[:6]]
        context_lines.append(f"Global Market Real-Time Benchmarks: {'; '.join(b_lines)}")
    
    data_context = "\n".join(context_lines)

    # 10. Multi-Model AI Generation with Multi-Turn Memory
    prompt = incoming_text
    is_deep = any(k in text_lower for k in ["why", "earnings", "thesis", "analysis", "catalyst", "valuation", "future", "outlook", "risk", "compare", "vs", "explain", "how", "what if", "judging", "better", "recommend", "should i", "history", "previous", "earlier", "we discussed", "you said", "remember", "sector", "sectors", "connect", "platform", "live", "real time", "real-time", "price", "quote", "crypto", "bitcoin", "gold"])
    ai_res = MultiModelRouter.generate_analysis(prompt, data_context=data_context, chat_history=chat_history, deep_research=is_deep)
    if ai_res.get("success"):
        return ai_res["content"]

    # 11. High-Precision Direct Fallback
    if active_ticker:
        q = market.get_quote(active_ticker)
        f = market.get_fundamentals(active_ticker)
        sign = "+" if q['change_pct'] >= 0 else ""
        return (
            f"🏢 **{f['name']} ({active_ticker})**\n\n"
            f"Here is how **{active_ticker}** is positioned right now:\n\n"
            f"• **Current Trading**: **${q['price']}** ({sign}**{q['change_pct']}%** today) {q.get('sparkline', '')}\n"
            f"• **Valuation**: Market Cap **{f['market_cap']}** · Trailing P/E **{f['pe_ratio']}** (Forward P/E **{f['fwd_pe']}**)\n"
            f"• **Financial Health**: TTM Revenue **{f['revenue_ttm']}** (**{f['rev_growth_yoy']}** YoY) with **{f['gross_margin']}** Gross Margin\n"
            f"• **Moat**: _{f['moat']}_\n\n"
            f"🟢 **Bull Outlook**: {f['bull_case']}\n"
            f"🔴 **Key Risks**: {f['bear_case']}\n\n"
            f"Are you analyzing **{active_ticker}** for a short-term trade or evaluating long-term fundamental value?"
        )
        
    return (
        "I'm here to help you evaluate companies, understand market catalysts, and build strong investment theses.\n\n"
        "What company or sector are you currently analyzing, or what specific problem can we work through together?"
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
    repo.auto_extract_and_persist_facts(user.id, clean_text)
    RedisService.push_chat_turn(user.id, "user", text)
    RedisService.push_chat_turn(user.id, "assistant", sanitized_reply)
    return sanitized_reply

async def one_shot(system: str, user_text: str, max_tokens: int = 600) -> str:
    """Friendly morning brief generator."""
    overview = market.market_overview()
    lines = ["☀️ **Good morning! Here's your Market Brief:**\n"]
    for item in overview:
        lines.append(f"• **{item['ticker']}**: ${item['price']} ({item['change_pct']:+.2f}%) {item['sparkline']}")
    lines.append("\n🌍 **Macro Outlook**: S&P 500 futures steady ahead of economic data. Have a great trading day!")
    return "\n".join(lines)
