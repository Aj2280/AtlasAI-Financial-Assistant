"""Real-Time Financial Sectors Engine.
Tracks and provides institutional-grade live performance, leaders, and rotation metrics
across all 11 GICS financial sectors, plus Crypto, Macro & Commodities.
"""
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime

from backend.services import market
from backend.services.redis_service import RedisService
from backend.db import repo

log = logging.getLogger(__name__)

# Comprehensive 11 GICS Sectors + Crypto & Macro
ALL_SECTORS = [
    {
        "id": "tech",
        "name": "Information Technology",
        "etf": "XLK",
        "description": "Semiconductors, Cloud Software, Enterprise Hardware & AI Compute",
        "leaders": ["NVDA", "AAPL", "MSFT", "GOOGL"],
        "weight": "31.2%",
        "benchmark_pe": "34.5x"
    },
    {
        "id": "financials",
        "name": "Financial Services & Banking",
        "etf": "XLF",
        "description": "Universal Banks, Asset Managers, Payment Rails & Insurance",
        "leaders": ["JPM", "BAC", "MS", "GS"],
        "weight": "13.4%",
        "benchmark_pe": "16.2x"
    },
    {
        "id": "healthcare",
        "name": "Healthcare & Biotechnology",
        "etf": "XLV",
        "description": "Pharmaceuticals, GLP-1 Weight Loss, Medical Devices & Care",
        "leaders": ["LLY", "UNH", "JNJ", "ABBV"],
        "weight": "11.8%",
        "benchmark_pe": "21.8x"
    },
    {
        "id": "energy",
        "name": "Energy, Oil & Natural Gas",
        "etf": "XLE",
        "description": "Integrated Supermajors, Refining, LNG & Offshore Equipment",
        "leaders": ["XOM", "CVX", "COP", "SLB"],
        "weight": "3.8%",
        "benchmark_pe": "12.4x"
    },
    {
        "id": "discretionary",
        "name": "Consumer Discretionary & EV",
        "etf": "XLY",
        "description": "E-Commerce, Electric Mobility, Luxury Goods & Entertainment",
        "leaders": ["AMZN", "TSLA", "HD", "MCD"],
        "weight": "10.4%",
        "benchmark_pe": "27.6x"
    },
    {
        "id": "staples",
        "name": "Consumer Staples & Retail",
        "etf": "XLP",
        "description": "Packaged Food, Household Goods, Big Box Retail & Beverages",
        "leaders": ["COST", "PG", "KO", "WMT"],
        "weight": "5.9%",
        "benchmark_pe": "22.1x"
    },
    {
        "id": "communication",
        "name": "Communication & Digital Media",
        "etf": "XLC",
        "description": "Social Media Platforms, Streaming, Advertising & Telecom",
        "leaders": ["META", "GOOGL", "NFLX", "DIS"],
        "weight": "9.1%",
        "benchmark_pe": "24.3x"
    },
    {
        "id": "industrials",
        "name": "Industrials, Defense & Aerospace",
        "etf": "XLI",
        "description": "Heavy Machinery, Defense Prime Contractors, Logistics & Rail",
        "leaders": ["CAT", "GE", "BA", "RTX"],
        "weight": "8.5%",
        "benchmark_pe": "23.0x"
    },
    {
        "id": "materials",
        "name": "Materials, Mining & Chemicals",
        "etf": "XLB",
        "description": "Industrial Chemicals, Copper & Lithium Miners, Packaging",
        "leaders": ["LIN", "FCX", "GOLD", "NEM"],
        "weight": "2.3%",
        "benchmark_pe": "19.5x"
    },
    {
        "id": "utilities",
        "name": "Utilities & Clean Grid Power",
        "etf": "XLU",
        "description": "Electric Utilities, Nuclear Power, Renewable Energy Infrastructure",
        "leaders": ["NEE", "SO", "DUK", "CEG"],
        "weight": "2.4%",
        "benchmark_pe": "18.8x"
    },
    {
        "id": "realestate",
        "name": "Real Estate & Data Center REITs",
        "etf": "XLRE",
        "description": "Data Centers, Logistics Warehouses, Tower Infrastructure & Commercial",
        "leaders": ["PLD", "AMT", "EQIX", "SPG"],
        "weight": "2.1%",
        "benchmark_pe": "31.2x"
    },
    {
        "id": "crypto",
        "name": "Digital Assets & Cryptocurrency",
        "etf": "BTC",
        "description": "Layer 1 Blockchains, Decentralized Finance & Digital Gold",
        "leaders": ["BTC", "ETH", "SOL"],
        "weight": "Global Asset Class",
        "benchmark_pe": "N/A"
    },
    {
        "id": "macro",
        "name": "Global Macro & Commodities",
        "etf": "SPX",
        "description": "Equities Index, Crude Oil, Precious Metals & Treasury Yields",
        "leaders": ["SPX", "GOLD", "OIL", "BTC"],
        "weight": "Macro Baseline",
        "benchmark_pe": "22.5x"
    }
]

from concurrent.futures import ThreadPoolExecutor

def _process_single_sector(sec: Dict[str, Any]) -> Dict[str, Any]:
    """Processes quotes and sentiment for a single sector."""
    etf_quote = market.get_quote(sec["etf"])
    change_pct = etf_quote.get("change_pct", 0.0)
    
    # Calculate momentum status
    if change_pct >= 1.5:
        sentiment = "Strong Inflow 🔥"
        sentiment_tag = "bullish"
    elif change_pct > 0.2:
        sentiment = "Moderate Accumulation 🟢"
        sentiment_tag = "positive"
    elif change_pct >= -0.5:
        sentiment = "Neutral / Consolidating ⚖️"
        sentiment_tag = "neutral"
    else:
        sentiment = "Capital Outflow / Defensive 🔴"
        sentiment_tag = "bearish"

    # Fetch top leaders quotes
    leader_quotes = []
    for l_ticker in sec["leaders"][:3]:
        l_q = market.get_quote(l_ticker)
        leader_quotes.append({
            "ticker": l_ticker,
            "price": l_q.get("price", 150.0),
            "change_pct": l_q.get("change_pct", 0.0),
            "sparkline": l_q.get("sparkline", "")
        })

    return {
        "id": sec["id"],
        "name": sec["name"],
        "etf": sec["etf"],
        "etf_price": etf_quote.get("price", 100.0),
        "change_pct": change_pct,
        "sparkline": etf_quote.get("sparkline", "▂▄▆ 🟢"),
        "weight": sec["weight"],
        "benchmark_pe": sec["benchmark_pe"],
        "description": sec["description"],
        "sentiment": sentiment,
        "sentiment_tag": sentiment_tag,
        "leaders": leader_quotes
    }

def get_all_sectors_performance() -> List[Dict[str, Any]]:
    """Returns real-time performance, momentum, and leading constituents for all sectors."""
    cached = RedisService.get_json("sectors:overview")
    if cached:
        return cached

    with ThreadPoolExecutor(max_workers=8) as executor:
        sector_results = list(executor.map(_process_single_sector, ALL_SECTORS))

    # Cache for 60 seconds
    RedisService.set_json("sectors:overview", sector_results, ttl=60)
    return sector_results

def get_sector_by_id(sector_id: str) -> Optional[Dict[str, Any]]:
    """Returns detailed real-time metrics for a specific financial sector."""
    all_sec = get_all_sectors_performance()
    for s in all_sec:
        if s["id"].lower() == sector_id.lower() or s["etf"].lower() == sector_id.lower():
            return s
    return None

def find_sector_for_ticker(ticker: str) -> Optional[Dict[str, Any]]:
    """Determines which sector a ticker belongs to."""
    t_clean = ticker.upper()
    for sec in ALL_SECTORS:
        if t_clean in sec["leaders"] or sec["etf"] == t_clean:
            return sec
    return None

def get_sector_rotation_summary() -> str:
    """Produces a synthesized institutional market sector rotation summary."""
    sectors = get_all_sectors_performance()
    sorted_by_perf = sorted(sectors, key=lambda x: x["change_pct"], reverse=True)
    top_leaders = sorted_by_perf[:3]
    top_laggards = sorted_by_perf[-3:]

    lines = ["📊 **Institutional Sector Rotation & Market Breadth**\n"]
    lines.append("🏆 **Top Performing Sectors Today:**")
    for s in top_leaders:
        sign = "+" if s['change_pct'] >= 0 else ""
        lines.append(f"• **{s['name']}** ({s['etf']}): **{sign}{s['change_pct']}%** · _{s['sentiment']}_")

    lines.append("\n⚠️ **Lagging / Outflow Sectors:**")
    for s in top_laggards:
        sign = "+" if s['change_pct'] >= 0 else ""
        lines.append(f"• **{s['name']}** ({s['etf']}): **{sign}{s['change_pct']}%** · _{s['sentiment']}_")

    return "\n".join(lines)
