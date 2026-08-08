"""SQLAlchemy models — users, memory, watchlist, alerts, documents."""
from datetime import datetime
import os
from sqlalchemy import (
    BigInteger, Boolean, Column, DateTime, Float, ForeignKey, Integer,
    String, Text, create_engine
)
from sqlalchemy.orm import declarative_base, sessionmaker

DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///atlas_financial.db")

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    tg_id = Column(BigInteger, unique=True, index=True, nullable=False)
    name = Column(String(120), default="")
    role = Column(String(120), default="")          # investor / analyst / founder
    timezone = Column(String(64), default="UTC")     # e.g. Asia/Kolkata, America/New_York
    briefing_time = Column(String(5), default="08:00") # "HH:MM" 24h
    interests = Column(Text, default="Tech, AI, Semiconductors, Cloud")
    onboarded = Column(Boolean, default=True)
    last_brief_date = Column(String(10), default="") # YYYY-MM-DD dedupe
    created_at = Column(DateTime, default=datetime.utcnow)


class ProfileFact(Base):
    """Long-term memory: compounding facts learned about the user."""
    __tablename__ = "profile_facts"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    fact = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class WatchlistItem(Base):
    __tablename__ = "watchlist"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    ticker = Column(String(16), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class Message(Base):
    """Short-term memory: conversation history."""
    __tablename__ = "messages"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    role = Column(String(12), nullable=False)   # user | assistant
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class Alert(Base):
    """price_move | filing | reminder"""
    __tablename__ = "alerts"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    type = Column(String(20), nullable=False)
    ticker = Column(String(16), default="")
    threshold_pct = Column(Float, default=0.0)
    remind_at = Column(DateTime, nullable=True)      # UTC, for reminders
    note = Column(Text, default="")
    meta = Column(Text, default="")                  # e.g. last seen filing accession
    active = Column(Boolean, default=True)
    last_triggered = Column(String(10), default="")  # YYYY-MM-DD dedupe
    created_at = Column(DateTime, default=datetime.utcnow)


class Document(Base):
    """Uploaded PDFs / analyzed Google Sheets. The latest is 'active' for Q&A."""
    __tablename__ = "documents"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    kind = Column(String(10), nullable=False)   # pdf | sheet
    name = Column(String(255), default="")
    content = Column(Text, default="")
    active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)


connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)

def init_db() -> None:
    Base.metadata.create_all(engine)
