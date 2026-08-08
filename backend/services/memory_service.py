import uuid
import json
import sqlite3
from datetime import datetime, timezone
from backend.database import get_db_connection

class MemoryService:
    @staticmethod
    def get_or_create_user(telegram_id: int, display_name: str = "Analyst") -> dict:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE telegram_id = ?", (telegram_id,))
        user = cursor.fetchone()
        
        if not user:
            user_id = str(uuid.uuid4())
            cursor.execute(
                """INSERT INTO users (id, telegram_id, display_name, role, onboarding_state, brief_time)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (user_id, telegram_id, display_name, "Investor / Analyst", "in_progress", "08:00")
            )
            # Default watchlists for new user
            default_tickers = [("NVDA", "Semiconductors", "Core AI benchmark"), 
                               ("AAPL", "Consumer Tech", "Flagship tech"),
                               ("MSFT", "Cloud / Enterprise AI", "Enterprise software leader")]
            for ticker, sector, reason in default_tickers:
                cursor.execute(
                    "INSERT INTO watchlist_items (id, user_id, ticker, sector, reason) VALUES (?, ?, ?, ?, ?)",
                    (str(uuid.uuid4()), user_id, ticker, sector, reason)
                )
            conn.commit()
            cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
            user = cursor.fetchone()
            
        conn.close()
        return dict(user)

    @staticmethod
    def update_user_profile(user_id: str, role: str = None, brief_time: str = None, onboarding_state: str = None):
        conn = get_db_connection()
        cursor = conn.cursor()
        if role:
            cursor.execute("UPDATE users SET role = ? WHERE id = ?", (role, user_id))
        if brief_time:
            cursor.execute("UPDATE users SET brief_time = ? WHERE id = ?", (brief_time, user_id))
        if onboarding_state:
            cursor.execute("UPDATE users SET onboarding_state = ? WHERE id = ?", (onboarding_state, user_id))
        conn.commit()
        conn.close()

    @staticmethod
    def get_user_profile_context(user_id: str) -> dict:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
        user_row = cursor.fetchone()
        user = dict(user_row) if user_row else {}

        cursor.execute("SELECT ticker, sector, reason FROM watchlist_items WHERE user_id = ?", (user_id,))
        watchlist = [dict(r) for r in cursor.fetchall()]

        cursor.execute("SELECT fact FROM memory_facts WHERE user_id = ? ORDER BY created_at DESC LIMIT 10", (user_id,))
        facts = [r['fact'] for r in cursor.fetchall()]

        cursor.execute("SELECT key, value FROM preferences WHERE user_id = ?", (user_id,))
        prefs = {r['key']: r['value'] for r in cursor.fetchall()}

        conn.close()
        return {
            "user": user,
            "watchlist": watchlist,
            "facts": facts,
            "preferences": prefs
        }

    @staticmethod
    def add_memory_fact(user_id: str, fact: str, source_conversation_id: str = None):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO memory_facts (id, user_id, fact, source_conversation_id) VALUES (?, ?, ?, ?)",
            (str(uuid.uuid4()), user_id, fact, source_conversation_id)
        )
        conn.commit()
        conn.close()

    @staticmethod
    def add_watchlist_item(user_id: str, ticker: str, sector: str = "Equity", reason: str = "User added"):
        conn = get_db_connection()
        cursor = conn.cursor()
        ticker = ticker.upper().strip()
        cursor.execute("SELECT id FROM watchlist_items WHERE user_id = ? AND ticker = ?", (user_id, ticker))
        if not cursor.fetchone():
            cursor.execute(
                "INSERT INTO watchlist_items (id, user_id, ticker, sector, reason) VALUES (?, ?, ?, ?, ?)",
                (str(uuid.uuid4()), user_id, ticker, sector, reason)
            )
            conn.commit()
        conn.close()

    @staticmethod
    def get_watchlist(user_id: str) -> list:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT ticker, sector, reason FROM watchlist_items WHERE user_id = ?", (user_id,))
        items = [dict(r) for r in cursor.fetchall()]
        conn.close()
        return items

    @staticmethod
    def set_alert(user_id: str, ticker: str, condition: str, threshold: str) -> str:
        conn = get_db_connection()
        cursor = conn.cursor()
        alert_id = str(uuid.uuid4())
        cursor.execute(
            "INSERT INTO alerts (id, user_id, ticker, condition, threshold) VALUES (?, ?, ?, ?, ?)",
            (alert_id, user_id, ticker.upper(), condition, threshold)
        )
        conn.commit()
        conn.close()
        return alert_id
