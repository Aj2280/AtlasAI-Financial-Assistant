"""Agent tools — schemas and execution mappings for financial assistant."""
import json
from datetime import datetime, timedelta
from typing import Any, Dict
from backend.services import market, news, edgar
from backend.db import repo

TOOL_SCHEMAS = [
    {
        "type": "function",
        "function": {
            "name": "get_stock_quote",
            "description": "Fetch real-time stock price, day change, and high/low for a ticker.",
            "parameters": {
                "type": "object",
                "properties": {
                    "ticker": {"type": "string", "description": "Stock ticker symbol, e.g. NVDA, AAPL, MSFT, TSLA"}
                },
                "required": ["ticker"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_company_fundamentals",
            "description": "Get company valuation, market cap, P/E ratio, revenue growth, and profit margins.",
            "parameters": {
                "type": "object",
                "properties": {
                    "ticker": {"type": "string", "description": "Stock ticker symbol"}
                },
                "required": ["ticker"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_company_news",
            "description": "Fetch latest financial news and headlines for a ticker.",
            "parameters": {
                "type": "object",
                "properties": {
                    "ticker": {"type": "string", "description": "Stock ticker symbol"}
                },
                "required": ["ticker"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_sec_filings",
            "description": "Fetch official SEC EDGAR submissions (10-K, 10-Q, Form 4) with direct document links.",
            "parameters": {
                "type": "object",
                "properties": {
                    "ticker": {"type": "string", "description": "Stock ticker symbol"}
                },
                "required": ["ticker"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "create_price_alert",
            "description": "Register a percentage price movement alert for a stock.",
            "parameters": {
                "type": "object",
                "properties": {
                    "ticker": {"type": "string", "description": "Stock ticker symbol"},
                    "threshold_pct": {"type": "number", "description": "Percentage move threshold, e.g. 5.0"}
                },
                "required": ["ticker", "threshold_pct"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "add_watchlist_ticker",
            "description": "Add a stock ticker to the user's personal watchlist.",
            "parameters": {
                "type": "object",
                "properties": {
                    "ticker": {"type": "string", "description": "Stock ticker symbol"}
                },
                "required": ["ticker"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "read_active_document",
            "description": "Read the active uploaded PDF or Google Sheet spreadsheet in the conversation context.",
            "parameters": {"type": "object", "properties": {}}
        }
    }
]

def execute_tool(name: str, args: Dict[str, Any], user) -> str:
    """Execute tool and return clean string output."""
    try:
        if name == "get_stock_quote":
            ticker = args.get("ticker", "NVDA")
            q = market.get_quote(ticker)
            return json.dumps(q)

        elif name == "get_company_fundamentals":
            ticker = args.get("ticker", "NVDA")
            f = market.get_fundamentals(ticker)
            return json.dumps(f)

        elif name == "get_company_news":
            ticker = args.get("ticker", "NVDA")
            n = news.company_news(ticker, limit=4)
            return json.dumps(n)

        elif name == "get_sec_filings":
            ticker = args.get("ticker", "NVDA")
            filings = edgar.recent_filings(ticker, limit=4)
            return json.dumps(filings)

        elif name == "create_price_alert":
            ticker = args.get("ticker", "NVDA")
            pct = float(args.get("threshold_pct", 5.0))
            al = repo.create_alert(user.id, "price_move", ticker=ticker, threshold_pct=pct)
            return f"Alert registered for {ticker} at ±{pct}% (Alert ID: {al.id})"

        elif name == "add_watchlist_ticker":
            ticker = args.get("ticker", "NVDA")
            added = repo.add_to_watchlist(user.id, ticker)
            return f"Added {ticker} to watchlist" if added else f"{ticker} already in watchlist"

        elif name == "read_active_document":
            doc = repo.active_document(user.id)
            if doc:
                return f"Document: {doc.name}\nContent:\n{doc.content[:8000]}"
            return "No active document found."

        return f"Unknown tool: {name}"
    except Exception as e:
        return f"Error executing tool {name}: {str(e)}"
