"""Repository helpers for SQLAlchemy CRUD operations."""
from typing import List, Optional
from datetime import datetime
from backend.db.models import SessionLocal, User, ProfileFact, WatchlistItem, Message, Alert, Document

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

def save_document(user_id: int, kind: str, name: str, content: str) -> Document:
    with SessionLocal() as db:
        # deactivate older docs
        db.query(Document).filter(Document.user_id == user_id).update({"active": False})
        doc = Document(user_id=user_id, kind=kind, name=name, content=content, active=True)
        db.add(doc)
        db.commit()
        db.refresh(doc)
        return doc
