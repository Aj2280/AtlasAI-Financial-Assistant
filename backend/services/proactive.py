"""Proactive Financial Intelligence Engine:
Delivers Morning Market Briefs, Evening Summaries, Material Earnings & Catalyst Alerts,
and SEC Regulatory Dissections with strict 'Why It Matters' synthesis and noise suppression.
"""
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
from zoneinfo import ZoneInfo

from backend.db import repo
from backend.services import market, sectors, news, edgar
from backend.services.llm_router import MultiModelRouter
from backend.services.redis_service import RedisService

log = logging.getLogger(__name__)

PROACTIVE_SYNTHESIS_PROMPT = """You are Atlas, an elite senior financial analyst delivering proactive, executive-grade financial intelligence to an investor.
Your goal is to save the user hours of reading by synthesizing complex market moves, macroeconomic events, sector flows, and company catalysts into crisp, actionable intelligence.

## Proactive Delivery Guidelines:
1. Explain "WHY It Matters": Never just forward raw headlines or list stock prices. Explain the transmission mechanism — how this affects valuation multiples, gross margins, cash flows, pricing power, or macro liquidity.
2. Structure & Scannability: Use clean Markdown headers, bold metrics (**$223.96**, **+4.2%**, **34x P/E**), and bullet points (•).
3. Quality Over Frequency: Focus strictly on high-conviction insights and material drivers.
4. Multilingual & Time-Aware: Maintain a polished, senior-colleague tone matching the user's language and timezone.
5. No Raw HTML: Use Markdown formatting only.
"""

def generate_morning_brief(user) -> str:
    """Generates comprehensive Morning Market Brief before trading sessions."""
    user_tz_str = getattr(user, 'timezone', None) or 'Asia/Kolkata'
    try:
        now_user = datetime.now(ZoneInfo(user_tz_str))
    except Exception:
        now_user = datetime.utcnow()
        user_tz_str = 'UTC'

    time_header = now_user.strftime("%A, %B %d, %Y - %I:%M %p %Z")
    
    # 1. Macro & Broad Market Indicators
    macro_benchmarks = ["SPX", "NDX", "GOLD", "OIL", "BTC", "US10Y", "DXY"]
    macro_data = [market.get_quote(t) for t in macro_benchmarks]
    macro_summary_lines = [f"• **{m['name']} ({m['ticker']})**: ${m['price']} ({m['change_pct']:+.2f}%) {m.get('sparkline', '')}" for m in macro_data]

    # 2. Sector Rotation Snapshot
    sector_perf = sectors.get_all_sectors_performance()
    leaders = [s for s in sector_perf if s['change_pct'] > 0][:3]
    laggards = [s for s in reversed(sector_perf) if s['change_pct'] < 0][:3]
    
    sec_lead_str = ", ".join([f"{s['name']} ({s['etf']}: {s['change_pct']:+.2f}%)" for s in leaders]) if leaders else "Defensive consolidation"
    sec_lag_str = ", ".join([f"{s['name']} ({s['etf']}: {s['change_pct']:+.2f}%)" for s in laggards]) if laggards else "Broad-based resilience"

    # 3. Personalized Watchlist & Portfolio Holdings
    watchlist = repo.get_watchlist(user.id)
    holdings = repo.get_portfolio_holdings(user.id)
    tracked_tickers = list(dict.fromkeys([h.ticker for h in holdings] + watchlist))
    if not tracked_tickers:
        tracked_tickers = ["NVDA", "AAPL", "MSFT", "TSLA", "BTC"]

    tracked_quotes = [market.get_quote(t) for t in tracked_tickers[:6]]
    tracked_lines = []
    for q in tracked_quotes:
        f = market.get_fundamentals(q['ticker'])
        n = news.company_news(q['ticker'], limit=1)
        headline = f" — _{n[0]['headline']}_" if n else ""
        tracked_lines.append(f"• **{q['ticker']}**: ${q['price']} ({q['change_pct']:+.2f}%) | P/E {f.get('pe_ratio', 'N/A')}{headline}")

    # 4. Top General Market News
    gen_news = news.general_market_news(limit=3)
    news_lines = [f"• {item['headline']} ({item['source']})" for item in gen_news]

    # 5. Build Comprehensive Synthesis Context
    context_text = f"""
MORNING BRIEFING CONTEXT:
Local Time: {time_header} (Timezone: {user_tz_str})

Global Macro & Commodities:
{chr(10).join(macro_summary_lines)}

Sector Rotation:
- Leading Inflows: {sec_lead_str}
- Lagging Outflows: {sec_lag_str}

User Watchlist & Portfolio Assets:
{chr(10).join(tracked_lines)}

Top Market Headlines:
{chr(10).join(news_lines)}
"""

    prompt = (
        "Synthesize a polished, high-impact Morning Market Brief for the investor based on the context above.\n"
        "Include:\n"
        "1. ☀️ **Morning Market Brief Header & Macro Pulse** (What global yields, dollar, and commodity trends indicate for today's risk appetite)\n"
        "2. 🔄 **Sector Rotation Dynamics** (Where institutional capital is flowing and why)\n"
        "3. 📊 **Watchlist & Portfolio Focus** (Key price action and catalysts for the user's specific assets)\n"
        "4. 🎯 **Key Catalysts to Watch Today** (Economic data releases, Fed expectations, or earnings)\n"
        "5. 💡 **The Bottom Line (Why It Matters)** (1-2 sentences of actionable institutional perspective)"
    )

    ai_res = MultiModelRouter.generate_analysis(prompt, data_context=context_text, deep_research=True)
    if ai_res.get("success"):
        return ai_res["content"]

    # Fallback Direct Template
    return (
        f"☀️ **Morning Market Brief** · _{time_header}_\n\n"
        f"🌍 **Macro Backdrop & Risk Appetite**:\n"
        f"{chr(10).join(macro_summary_lines[:4])}\n\n"
        f"🔄 **Sector Rotation**: Leaders: **{sec_lead_str}** | Laggards: **{sec_lag_str}**\n\n"
        f"📊 **Watchlist & Portfolio Assets**:\n"
        f"{chr(10).join(tracked_lines[:4])}\n\n"
        f"💡 **Why It Matters**: Yield curve stability and technology capital allocation continue to dictate broad market direction."
    )

def generate_evening_summary(user) -> str:
    """Generates comprehensive Evening Market Summary post-session."""
    user_tz_str = getattr(user, 'timezone', None) or 'Asia/Kolkata'
    try:
        now_user = datetime.now(ZoneInfo(user_tz_str))
    except Exception:
        now_user = datetime.utcnow()
        user_tz_str = 'UTC'

    time_header = now_user.strftime("%A, %B %d, %Y - %I:%M %p %Z")

    # 1. Closing Quotes & Benchmarks
    benchmarks = ["SPX", "NDX", "GOLD", "OIL", "BTC"]
    closing_data = [market.get_quote(t) for t in benchmarks]
    close_lines = [f"• **{c['name']}**: ${c['price']} ({c['change_pct']:+.2f}%) {c.get('sparkline', '')}" for c in closing_data]

    # 2. Sector Closing Performance
    sector_perf = sectors.get_all_sectors_performance()
    leaders = [s for s in sector_perf if s['change_pct'] > 0][:3]
    laggards = [s for s in reversed(sector_perf) if s['change_pct'] < 0][:3]

    # 3. User Portfolio Holdings & Watchlist Closing Status
    watchlist = repo.get_watchlist(user.id)
    holdings = repo.get_portfolio_holdings(user.id)
    tracked_tickers = list(dict.fromkeys([h.ticker for h in holdings] + watchlist))
    if not tracked_tickers:
        tracked_tickers = ["NVDA", "AAPL", "MSFT", "TSLA", "BTC"]

    tracked_quotes = [market.get_quote(t) for t in tracked_tickers[:6]]
    tracked_lines = []
    for q in tracked_quotes:
        f = market.get_fundamentals(q['ticker'])
        tracked_lines.append(f"• **{q['ticker']}**: ${q['price']} ({q['change_pct']:+.2f}%) | 24h Range: ${q.get('low', 'N/A')} - ${q.get('high', 'N/A')}")

    context_text = f"""
EVENING SUMMARY CONTEXT:
Local Time: {time_header}

Market Close:
{chr(10).join(close_lines)}

Sector Closing Flows:
- Top Outperformers: {', '.join([s['name'] + ' (' + str(s['change_pct']) + '%)' for s in leaders]) if leaders else 'Broad market decline'}
- Top Underperformers: {', '.join([s['name'] + ' (' + str(s['change_pct']) + '%)' for s in laggards]) if laggards else 'No severe lagging sectors'}

User Holdings & Watchlist Session Results:
{chr(10).join(tracked_lines)}
"""

    prompt = (
        "Generate a high-conviction Evening Market Summary for the investor based on the closing data.\n"
        "Structure:\n"
        "1. 🌙 **Evening Market Summary Header & Closing Scorecard**\n"
        "2. 🔍 **What Moved Markets Today (The 'Why')** (Deconstruct the primary drivers: earnings, yields, macro prints, or sector rebalancing)\n"
        "3. 💼 **Your Portfolio & Watchlist Session Wrap** (Clear breakdown of gains/losses and noteworthy volume)\n"
        "4. 🌅 **Tomorrow's Setup & After-Hours Developments** (Key earnings reports or overnight economic catalysts to watch)\n"
        "5. 💡 **Strategic Takeaway** (1 concise sentence on actionable risk or opportunity)"
    )

    ai_res = MultiModelRouter.generate_analysis(prompt, data_context=context_text, deep_research=True)
    if ai_res.get("success"):
        return ai_res["content"]

    return (
        f"🌙 **Evening Market Summary** · _{time_header}_\n\n"
        f"📈 **Session Closing Scorecard**:\n"
        f"{chr(10).join(close_lines)}\n\n"
        f"💼 **Your Tracked Assets**:\n"
        f"{chr(10).join(tracked_lines[:4])}\n\n"
        f"💡 **Why It Matters**: Today's session reflected rotational positioning into high-quality balance sheets ahead of upcoming corporate earnings and central bank commentary."
    )

def evaluate_material_catalyst(ticker: str, threshold_pct: float = 3.0) -> Optional[str]:
    """Quality-Gated Catalyst & Volatility Dissection:
    Returns an actionable breakdown if a material event or threshold move occurred;
    returns None (SILENCE) if there is no significant development.
    """
    ticker = ticker.upper().strip()
    q = market.get_quote(ticker)
    change_pct = abs(q.get("change_pct", 0.0))

    # Check for recent news or material headlines
    comp_news = news.company_news(ticker, limit=2)
    has_breaking_news = False
    headline_text = ""
    if comp_news:
        keywords = ["earnings", "revenue", "profit", "sec", "investigation", "fda", "merger", "acquisition", "deal", "guidance", "upgrade", "downgrade", "target", "patent", "ceo", "cfo", "lawsuit", "tariff"]
        for n in comp_news:
            h_low = n.get("headline", "").lower()
            if any(k in h_low for k in keywords):
                has_breaking_news = True
                headline_text = n.get("headline", "")
                break

    # NOISE SUPPRESSION GATE: If price move is small AND no high-impact news, REMAIN SILENT
    if change_pct < threshold_pct and not has_breaking_news:
        return None

    f = market.get_fundamentals(ticker)
    sec_info = sectors.find_sector_for_ticker(ticker)
    sec_name = sec_info['name'] if sec_info else "Global Equities"
    sign = "+" if q.get("change_pct", 0) >= 0 else ""

    context = (
        f"ASSET: {ticker} ({f['name']})\n"
        f"Sector: {sec_name}\n"
        f"Live Price: ${q['price']} ({sign}{q['change_pct']}%)\n"
        f"Fundamentals: Market Cap {f['market_cap']}, Trailing P/E {f['pe_ratio']}, Forward P/E {f['fwd_pe']}, Revenue TTM {f['revenue_ttm']} ({f['rev_growth_yoy']})\n"
        f"Moat: {f['moat']}\n"
        f"Catalyst Headline: '{headline_text}'" if headline_text else "Catalyst: Significant institutional order flow and volume surge."
    )

    prompt = (
        f"Generate a high-conviction Material Catalyst Alert for {ticker}.\n"
        f"Deconstruct:\n"
        f"1. 🚨 **Material Catalyst Alert: {ticker}** (${q['price']} | {sign}{q['change_pct']}%)\n"
        f"2. **What Happened**: (Concise 1-2 sentence event summary)\n"
        f"3. **Why It Matters**: (Deep fundamental explanation of the impact on gross margins, multiples, growth rate, or competitive moat)\n"
        f"4. **Key Levels & Next Catalysts**: (Key price zones or upcoming milestones to watch)"
    )

    ai_res = MultiModelRouter.generate_analysis(prompt, data_context=context, deep_research=True)
    if ai_res.get("success"):
        return ai_res["content"]

    return (
        f"🚨 **Material Catalyst Alert: {ticker}**\n\n"
        f"**{f['name']} ({ticker})** has moved **{sign}{q['change_pct']}%** today to **${q['price']}** {q.get('sparkline', '')}.\n\n"
        f"• **Headline**: _{headline_text or 'Substantial volume breakout and momentum acceleration'}_\n"
        f"• **Why It Matters**: In the **{sec_name}** sector, price discovery at these levels tests **{f['moat']}** while valuations hold at **{f['pe_ratio']}** Trailing P/E.\n"
        f"• **Next Watch**: Monitor intraday support/resistance around key psychological levels."
    )

def analyze_sec_regulatory_event(ticker: str, form_type: str, date: str, description: str, url: str) -> Optional[str]:
    """Dissects SEC EDGAR Form 8-K, 10-Q, or 10-K disclosures with 'Why It Matters' analysis."""
    ticker = ticker.upper().strip()
    
    # Filter non-material routine forms
    if form_type not in ["8-K", "10-Q", "10-K", "SC 13D", "4"]:
        return None

    f = market.get_fundamentals(ticker)
    q = market.get_quote(ticker)

    context = (
        f"COMPANY: {f['name']} ({ticker})\n"
        f"SEC Form Type: Form {form_type} (Filed: {date})\n"
        f"Official Description: {description}\n"
        f"Current Price: ${q['price']} ({q['change_pct']:+.2f}%)\n"
        f"Market Cap: {f['market_cap']}, Valuation: {f['pe_ratio']} Trailing P/E\n"
        f"Official URL: {url}"
    )

    prompt = (
        f"Analyze this official SEC filing for {ticker}.\n"
        f"1. 📄 **SEC Regulatory Intelligence: {ticker} (Form {form_type})**\n"
        f"2. **Filing Summary**: What material disclosures or financial updates were submitted to the SEC.\n"
        f"3. **Why It Matters**: Balance sheet impact, corporate governance, revenue recognition, or risk factor implications.\n"
        f"4. **Direct Link**: Provide clickable link to read the official document on SEC.gov."
    )

    ai_res = MultiModelRouter.generate_analysis(prompt, data_context=context, deep_research=True)
    if ai_res.get("success"):
        return ai_res["content"]

    return (
        f"📄 **SEC Regulatory Intelligence: {ticker} (Form {form_type})**\n\n"
        f"**{f['name']}** submitted an official **Form {form_type}** on {date}.\n\n"
        f"• **Disclosure**: _{description}_\n"
        f"• **Why It Matters**: Form {form_type} provides audited insights into operational performance, material agreements, and corporate capital structure.\n"
        f"• **Document Link**: [View Filing on SEC.gov]({url})"
    )
