"""
Database module for TraceBack.
Provides SQLite persistence for raw and normalized network events and investigations.
"""

import sqlite3
import json
from typing import List, Dict, Any, Optional
from datetime import datetime

DB_FILE = "traceback.db"

def get_connection(db_path: str = DB_FILE) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

def init_db(db_path: str = DB_FILE) -> None:
    """Initialize database tables for normalized events and investigations."""
    conn = get_connection(db_path)
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS events (
            id TEXT PRIMARY KEY,
            timestamp TEXT NOT NULL,
            event_type TEXT NOT NULL,
            source_ip TEXT NOT NULL,
            destination_ip TEXT,
            description TEXT,
            raw_details TEXT,
            is_suspicious INTEGER DEFAULT 0,
            correlation_notes TEXT,
            group_id TEXT
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS investigations (
            investigation_id TEXT PRIMARY KEY,
            created_at TEXT NOT NULL,
            name TEXT,
            summary TEXT
        )
    """)
    
    conn.commit()
    conn.close()

def save_events(events: List[Dict[str, Any]], db_path: str = DB_FILE, clear_existing: bool = True) -> None:
    """Persist normalized events to SQLite."""
    init_db(db_path)
    conn = get_connection(db_path)
    cursor = conn.cursor()
    
    if clear_existing:
        cursor.execute("DELETE FROM events")
        
    for ev in events:
        cursor.execute("""
            INSERT OR REPLACE INTO events (
                id, timestamp, event_type, source_ip, destination_ip, 
                description, raw_details, is_suspicious, correlation_notes, group_id
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            str(ev.get("id")),
            str(ev.get("timestamp")),
            ev.get("event_type", ""),
            ev.get("source_ip", ""),
            ev.get("destination_ip"),
            ev.get("description", ""),
            json.dumps(ev.get("raw_details", {})),
            1 if ev.get("is_suspicious") else 0,
            json.dumps(ev.get("correlation_notes", [])),
            ev.get("group_id", "")
        ))
        
    conn.commit()
    conn.close()

def load_events_from_db(db_path: str = DB_FILE) -> List[Dict[str, Any]]:
    """Retrieve normalized events from SQLite."""
    init_db(db_path)
    conn = get_connection(db_path)
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM events ORDER BY timestamp ASC")
    rows = cursor.fetchall()
    
    events = []
    for row in rows:
        events.append({
            "id": row["id"],
            "timestamp": row["timestamp"],
            "event_type": row["event_type"],
            "source_ip": row["source_ip"],
            "destination_ip": row["destination_ip"],
            "description": row["description"],
            "raw_details": json.loads(row["raw_details"]) if row["raw_details"] else {},
            "is_suspicious": bool(row["is_suspicious"]),
            "correlation_notes": json.loads(row["correlation_notes"]) if row["correlation_notes"] else [],
            "group_id": row["group_id"]
        })
        
    conn.close()
    return events

