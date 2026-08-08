import sqlite3
import os
import json
import uuid
from datetime import datetime, timezone

DB_PATH = os.path.join(os.path.dirname(__file__), "atlas.db")

def get_db_connection():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 1. Users
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id TEXT PRIMARY KEY,
        telegram_id INTEGER UNIQUE NOT NULL,
        display_name TEXT,
        role TEXT,
        onboarding_state TEXT DEFAULT 'in_progress',
        brief_time TEXT DEFAULT '08:00',
        timezone TEXT DEFAULT 'UTC',
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    );
    """)
    
    # 2. Preferences
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS preferences (
        user_id TEXT,
        key TEXT,
        value TEXT,
        updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
        PRIMARY KEY (user_id, key),
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
    );
    """)
    
    # 3. Watchlist Items
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS watchlist_items (
        id TEXT PRIMARY KEY,
        user_id TEXT,
        ticker TEXT NOT NULL,
        sector TEXT,
        reason TEXT,
        added_at TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
    );
    """)
    
    # 4. Alerts
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS alerts (
        id TEXT PRIMARY KEY,
        user_id TEXT,
        ticker TEXT NOT NULL,
        condition TEXT NOT NULL,
        threshold TEXT,
        active INTEGER DEFAULT 1,
        last_triggered_at TEXT,
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
    );
    """)
    
    # 5. Conversations
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS conversations (
        id TEXT PRIMARY KEY,
        user_id TEXT,
        role TEXT NOT NULL,
        channel TEXT DEFAULT 'text',
        content TEXT NOT NULL,
        tool_calls TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
    );
    """)
    
    # 6. Memory Facts
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS memory_facts (
        id TEXT PRIMARY KEY,
        user_id TEXT,
        fact TEXT NOT NULL,
        embedding TEXT,
        source_conversation_id TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
    );
    """)
    
    # 7. Integrations
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS integrations (
        id TEXT PRIMARY KEY,
        user_id TEXT,
        provider TEXT NOT NULL,
        access_token_enc TEXT,
        refresh_token_enc TEXT,
        scopes TEXT,
        connected_at TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
    );
    """)
    
    # 8. Documents
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS documents (
        id TEXT PRIMARY KEY,
        user_id TEXT,
        source TEXT,
        title TEXT NOT NULL,
        doc_type TEXT,
        raw_text TEXT,
        summary TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
    );
    """)
    
    # 9. Briefs Sent
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS briefs_sent (
        id TEXT PRIMARY KEY,
        user_id TEXT,
        brief_type TEXT NOT NULL,
        content TEXT NOT NULL,
        sent_at TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
    );
    """)
    
    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()
    print("Database initialized successfully.")
