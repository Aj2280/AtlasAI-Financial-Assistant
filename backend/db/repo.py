"""Repository helpers for SQLAlchemy CRUD operations."""
from typing import List, Optional, Dict, Any
from datetime import datetime
import re
from backend.db.models import SessionLocal, User, ProfileFact, WatchlistItem, Message, Alert, Document, MarketSnapshot, PortfolioHolding, init_db

def get_or_create_user(tg_id: int, name: str = "") -> User:
    with SessionLocal() as db:
        user = db.query(User).filter(User.tg_id == tg_id).first()
        if not user:
            user = User(
                tg_id=tg_id,
                name=name or "Analyst",
                role="Investor / Analyst",
                timezone="UTC",
                briefing_time="08:00",
                interests="Tech, AI, Cloud, Semiconductors",
                onboarded=True
            )
            db.add(user)
            db.commit()
            db.refresh(user)
            
            # Add initial core watchlist
            for ticker in ["NVDA", "AAPL", "MSFT", "GOOGL", "TSLA"]:
                db.add(WatchlistItem(user_id=user.id, ticker=ticker))
            db.commit()
        elif name and name != "Analyst" and (user.name == "Analyst" or not user.name):
            user.name = name
            db.commit()
            db.refresh(user)
        return user

def all_users() -> List[User]:
    with SessionLocal() as db:
        return db.query(User).all()

def update_user(user_id: int, **kwargs) -> Optional[User]:
    with SessionLocal() as db:
        user = db.query(User).filter(User.id == user_id).first()
        if user:
            for k, v in kwargs.items():
                if hasattr(user, k):
                    setattr(user, k, v)
            db.commit()
            db.refresh(user)
        return user

def get_facts(user_id: int) -> List[str]:
    with SessionLocal() as db:
        facts = db.query(ProfileFact).filter(ProfileFact.user_id == user_id).all()
        return [f.fact for f in facts]

def add_fact(user_id: int, fact: str) -> None:
    with SessionLocal() as db:
        db.add(ProfileFact(user_id=user_id, fact=fact))
        db.commit()

def get_watchlist(user_id: int) -> List[str]:
    with SessionLocal() as db:
        items = db.query(WatchlistItem).filter(WatchlistItem.user_id == user_id).all()
        return [i.ticker for i in items]

def add_to_watchlist(user_id: int, ticker: str) -> bool:
    ticker = ticker.upper().strip()
    with SessionLocal() as db:
        existing = db.query(WatchlistItem).filter(
            WatchlistItem.user_id == user_id,
            WatchlistItem.ticker == ticker
        ).first()
        if not existing:
            db.add(WatchlistItem(user_id=user_id, ticker=ticker))
            db.commit()
            return True
        return False

def remove_from_watchlist(user_id: int, ticker: str) -> bool:
    ticker = ticker.upper().strip()
    with SessionLocal() as db:
        existing = db.query(WatchlistItem).filter(
            WatchlistItem.user_id == user_id,
            WatchlistItem.ticker == ticker
        ).first()
        if existing:
            db.delete(existing)
            db.commit()
            return True
        return False

def recent_messages(user_id: int, limit: int = 10) -> List[Message]:
    with SessionLocal() as db:
        return db.query(Message).filter(Message.user_id == user_id).order_by(Message.created_at.desc()).limit(limit).all()[::-1]

def add_message(user_id: int, role: str, content: str) -> None:
    with SessionLocal() as db:
        db.add(Message(user_id=user_id, role=role, content=content))
        db.commit()

def active_alerts(user_id: Optional[int] = None, type: Optional[str] = None) -> List[Alert]:
    with SessionLocal() as db:
        q = db.query(Alert).filter(Alert.active == True)
        if user_id is not None:
            q = q.filter(Alert.user_id == user_id)
        if type is not None:
            q = q.filter(Alert.type == type)
        return q.all()

def create_alert(user_id: int, type: str, ticker: str = "", threshold_pct: float = 0.0,
                 remind_at: Optional[datetime] = None, note: str = "", meta: str = "") -> Alert:
    with SessionLocal() as db:
        alert = Alert(
            user_id=user_id,
            type=type,
            ticker=ticker.upper().strip(),
            threshold_pct=threshold_pct,
            remind_at=remind_at,
            note=note,
            meta=meta,
            active=True
        )
        db.add(alert)
        db.commit()
        db.refresh(alert)
        return alert

def update_alert(alert_id: int, **kwargs) -> Optional[Alert]:
    with SessionLocal() as db:
        al = db.query(Alert).filter(Alert.id == alert_id).first()
        if al:
            for k, v in kwargs.items():
                if hasattr(al, k):
                    setattr(al, k, v)
            db.commit()
            db.refresh(al)
        return al

def deactivate_alert(alert_id: int) -> None:
    with SessionLocal() as db:
        al = db.query(Alert).filter(Alert.id == alert_id).first()
        if al:
            al.active = False
            db.commit()

def active_document(user_id: int) -> Optional[Document]:
    with SessionLocal() as db:
        return db.query(Document).filter(Document.user_id == user_id, Document.active == True).order_by(Document.created_at.desc()).first()

def get_all_documents(user_id: int, limit: int = 10) -> List[Document]:
    with SessionLocal() as db:
        return db.query(Document).filter(Document.user_id == user_id).order_by(Document.created_at.desc()).limit(limit).all()

def save_document(user_id: int, kind: str, name: str, content: str) -> Document:
    with SessionLocal() as db:
        # deactivate older docs
        db.query(Document).filter(Document.user_id == user_id).update({"active": False})
        doc = Document(user_id=user_id, kind=kind, name=name, content=content, active=True)
        db.add(doc)
        db.commit()
        db.refresh(doc)
        return doc

def record_market_snapshot(quote: Dict[str, Any]) -> None:
    """Saves live real-time market quote to the local database for historical tracking."""
    if not quote or not quote.get("ticker"):
        return
    try:
        with SessionLocal() as db:
            snap = MarketSnapshot(
                ticker=quote["ticker"].upper(),
                name=quote.get("name", quote["ticker"]),
                price=float(quote.get("price", 0.0)),
                change=float(quote.get("change", 0.0)),
                change_pct=float(quote.get("change_pct", 0.0)),
                high=float(quote["high"]) if quote.get("high") else None,
                low=float(quote["low"]) if quote.get("low") else None,
                sparkline=quote.get("sparkline", ""),
                source=quote.get("source", "Finnhub Live Feed")
            )
            db.add(snap)
            db.commit()
    except Exception:
        pass

def get_latest_market_snapshots(limit: int = 15) -> List[MarketSnapshot]:
    with SessionLocal() as db:
        return db.query(MarketSnapshot).order_by(MarketSnapshot.created_at.desc()).limit(limit).all()

def save_portfolio_holding(user_id: int, ticker: str, shares: float, avg_cost: float = 0.0, notes: str = "") -> PortfolioHolding:
    ticker = ticker.upper().strip()
    with SessionLocal() as db:
        existing = db.query(PortfolioHolding).filter(
            PortfolioHolding.user_id == user_id,
            PortfolioHolding.ticker == ticker
        ).first()
        if existing:
            existing.shares = shares
            if avg_cost > 0:
                existing.avg_cost = avg_cost
            if notes:
                existing.notes = notes
            db.commit()
            db.refresh(existing)
            return existing
        else:
            holding = PortfolioHolding(
                user_id=user_id,
                ticker=ticker,
                shares=shares,
                avg_cost=avg_cost,
                notes=notes
            )
            db.add(holding)
            db.commit()
            db.refresh(holding)
            return holding

def get_portfolio_holdings(user_id: int) -> List[PortfolioHolding]:
    with SessionLocal() as db:
        return db.query(PortfolioHolding).filter(PortfolioHolding.user_id == user_id).all()

def auto_extract_and_persist_facts(user_id: int, message_text: str) -> None:
    """Analyzes message for user facts (name, role, holdings, preferences, explicit notes) and saves to persistent database."""
    text_lower = message_text.lower()

    # 1. Explicit remember requests ("Remember that...", "Note that...")
    rem_match = re.search(r"\b(?:remember|note that|keep in mind that|save fact)\s+(.+)$", message_text, re.IGNORECASE)
    if rem_match:
        add_fact(user_id, f"User Note: {rem_match.group(1).strip()}")

    # 2. Name extraction ("My name is Abhishek", "I am Abhishek")
    name_match = re.search(r"\b(?:my name is|i am|call me)\s+([A-Za-z]{2,20})\b", message_text, re.IGNORECASE)
    if name_match:
        cand_name = name_match.group(1).title()
        if cand_name.lower() not in ["an", "a", "the", "looking", "interested", "tracking", "holding"]:
            add_fact(user_id, f"User name: {cand_name}")
            update_user(user_id, name=cand_name)

    # 3. Role extraction ("I am an investor", "I am a founder", "I'm a financial analyst")
    for role_kw in ["investor", "equity analyst", "founder", "student", "finance professional", "trader", "engineer", "venture capitalist", "portfolio manager"]:
        if re.search(r"\b" + re.escape(role_kw) + r"\b", text_lower):
            add_fact(user_id, f"User role: {role_kw.title()}")
            update_user(user_id, role=role_kw.title())
            break
    
    # 4. Holding detection
    holding_match = re.search(r"\b(?:i have|i hold|i bought|holding|bought|own)\s+(\d+(?:\.\d+)?)\s+(?:shares of\s+)?([A-Za-z]{2,5})\b", message_text, re.IGNORECASE)
    if holding_match:
        shares = float(holding_match.group(1))
        ticker = holding_match.group(2).upper()
        if ticker not in ["THE", "FOR", "AND", "SOME", "MORE", "THAT", "TECH", "STOCK", "SHARE"]:
            fact = f"User holds {shares:g} shares of {ticker}"
            add_fact(user_id, fact)
            save_portfolio_holding(user_id, ticker, shares, 0.0, notes="Auto-extracted from conversation")
            add_to_watchlist(user_id, ticker)

    # 5. Risk appetite
    if any(k in text_lower for k in ["risk tolerance", "conservative", "aggressive", "moderate risk", "low risk", "high risk"]):
        if "conservative" in text_lower or "low risk" in text_lower:
            add_fact(user_id, "User has a conservative, low-risk investment style")
        elif "aggressive" in text_lower or "high risk" in text_lower:
            add_fact(user_id, "User has an aggressive, high-growth investment style")
        elif "moderate" in text_lower:
            add_fact(user_id, "User prefers a balanced, moderate-risk approach")

    # 6. Horizon
    if any(k in text_lower for k in ["long-term", "long term", "5 years", "10 years", "retirement"]):
        add_fact(user_id, "User has a long-term multi-year investment horizon")
    elif any(k in text_lower for k in ["short-term", "short term", "day trade", "swing trade", "scalp"]):
        add_fact(user_id, "User focuses on short-term swing trading and momentum")
