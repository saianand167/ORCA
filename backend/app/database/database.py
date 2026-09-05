import sqlite3
import json
import time
from pathlib import Path
from typing import List, Dict, Any, Optional
from ..core.config import settings

DB_FILE = settings.BASE_DIR / "orca.db"

_initialized = False

def init_db():
    global _initialized
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Conversations table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS conversations (
        id TEXT PRIMARY KEY,
        user_type TEXT,
        location_id TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
    # Messages table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        conversation_id TEXT,
        sender TEXT,
        message TEXT,
        response_json TEXT,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (conversation_id) REFERENCES conversations(id)
    )
    """)
    
    # Data cache table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS data_cache (
        cache_key TEXT PRIMARY KEY,
        data_json TEXT,
        data_quality TEXT,
        updated_at REAL
    )
    """)
    
    conn.commit()
    conn.close()
    _initialized = True

def get_db_connection():
    global _initialized
    if not _initialized:
        init_db()
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn


# Cache helpers
def get_cached_data(cache_key: str, max_age_seconds: int = 900) -> Optional[Dict[str, Any]]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT data_json, data_quality, updated_at FROM data_cache WHERE cache_key = ?", (cache_key,))
    row = cursor.fetchone()
    conn.close()
    if row:
        updated_at = row["updated_at"]
        if time.time() - updated_at <= max_age_seconds:
            try:
                data = json.loads(row["data_json"])
                data["_data_quality"] = row["data_quality"]
                return data
            except Exception:
                return None
    return None

def get_any_cached_data(cache_key: str) -> Optional[tuple[Dict[str, Any], int]]:
    """Returns (cached_data, age_in_seconds) regardless of max age, or None if not found."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT data_json, data_quality, updated_at FROM data_cache WHERE cache_key = ?", (cache_key,))
    row = cursor.fetchone()
    conn.close()
    if row:
        try:
            data = json.loads(row["data_json"])
            age = int(time.time() - row["updated_at"])
            return data, age
        except Exception:
            return None
    return None

def set_cached_data(cache_key: str, data: Dict[str, Any], quality: str = "CACHED"):
    conn = get_db_connection()
    cursor = conn.cursor()
    now = time.time()
    cursor.execute("""
    INSERT INTO data_cache (cache_key, data_json, data_quality, updated_at)
    VALUES (?, ?, ?, ?)
    ON CONFLICT(cache_key) DO UPDATE SET
        data_json = excluded.data_json,
        data_quality = excluded.data_quality,
        updated_at = excluded.updated_at
    """, (cache_key, json.dumps(data), quality, now))
    conn.commit()
    conn.close()

def save_chat_turn(conversation_id: str, user_type: str, location_id: str, user_message: str, response_data: Dict[str, Any]):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
    INSERT INTO conversations (id, user_type, location_id, updated_at)
    VALUES (?, ?, ?, CURRENT_TIMESTAMP)
    ON CONFLICT(id) DO UPDATE SET
        user_type = excluded.user_type,
        location_id = excluded.location_id,
        updated_at = CURRENT_TIMESTAMP
    """, (conversation_id, user_type, location_id))
    
    cursor.execute("""
    INSERT INTO messages (conversation_id, sender, message, response_json)
    VALUES (?, 'user', ?, ?)
    """, (conversation_id, user_message, json.dumps(response_data)))
    
    conn.commit()
    conn.close()

def get_conversation_history(conversation_id: str, limit: int = 6) -> List[Dict[str, Any]]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
    SELECT sender, message, response_json, timestamp FROM messages 
    WHERE conversation_id = ? ORDER BY id ASC LIMIT ?
    """, (conversation_id, limit))
    rows = cursor.fetchall()
    conn.close()
    history = []
    for r in rows:
        history.append({
            "sender": r["sender"],
            "message": r["message"],
            "timestamp": r["timestamp"]
        })
    return history
