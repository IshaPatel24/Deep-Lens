import sqlite3
import json
import os
import time
from typing import List, Dict, Any

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "deeplens.db")

def init_db():
    """Initializes tables for session storage and evaluations."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Research Session Storage
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sessions (
            id TEXT PRIMARY KEY,
            query TEXT NOT NULL,
            report TEXT,
            verified_data TEXT,
            sources TEXT,
            discarded_count INTEGER,
            timestamp REAL NOT NULL
        )
    """)
    
    # Evaluation Performance Metrics
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS evals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp REAL NOT NULL,
            score_citation REAL NOT NULL,
            score_coverage REAL NOT NULL,
            latency_seconds REAL NOT NULL,
            details TEXT
        )
    """)
    
    conn.commit()
    conn.close()

def save_session(session_id: str, query: str, report: str, verified_data: List[Dict], sources: List[Dict], discarded_count: int):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT OR REPLACE INTO sessions (id, query, report, verified_data, sources, discarded_count, timestamp)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        session_id,
        query,
        report,
        json.dumps(verified_data),
        json.dumps(sources),
        discarded_count,
        time.time()
    ))
    conn.commit()
    conn.close()

def get_session(session_id: str) -> Dict[str, Any]:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM sessions WHERE id = ?", (session_id,))
    row = cursor.fetchone()
    conn.close()
    
    if row:
        return {
            "id": row["id"],
            "query": row["query"],
            "report": row["report"],
            "verified_data": json.loads(row["verified_data"]),
            "sources": json.loads(row["sources"]),
            "discarded_count": row["discarded_count"],
            "timestamp": row["timestamp"]
        }
    return None

def get_all_sessions() -> List[Dict[str, Any]]:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT id, query, discarded_count, timestamp FROM sessions ORDER BY timestamp DESC")
    rows = cursor.fetchall()
    conn.close()
    
    return [
        {
            "id": r["id"],
            "query": r["query"],
            "discarded_count": r["discarded_count"],
            "timestamp": r["timestamp"]
        }
        for r in rows
    ]

def save_eval(score_citation: float, score_coverage: float, latency: float, details: Dict):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    # Store scores as percentages (0–100), and store only the per-question list
    per_question_list = details.get("details", []) if isinstance(details, dict) else details
    cursor.execute("""
        INSERT INTO evals (timestamp, score_citation, score_coverage, latency_seconds, details)
        VALUES (?, ?, ?, ?, ?)
    """, (
        time.time(),
        round(score_citation * 100, 1),
        round(score_coverage * 100, 1),
        round(latency, 2),
        json.dumps(per_question_list)
    ))
    conn.commit()
    conn.close()

def get_evals() -> List[Dict[str, Any]]:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM evals ORDER BY timestamp DESC LIMIT 20")
    rows = cursor.fetchall()
    conn.close()
    
    result = []
    for r in rows:
        raw_details = json.loads(r["details"])
        # Normalise: if the stored value is still the old nested summary dict, unwrap it
        if isinstance(raw_details, dict) and "details" in raw_details:
            per_question = raw_details["details"]
            score_citation = raw_details.get("score_citation", r["score_citation"])
            score_coverage = raw_details.get("score_coverage", r["score_coverage"])
            latency = raw_details.get("latency_seconds", r["latency_seconds"])
        else:
            per_question = raw_details if isinstance(raw_details, list) else []
            # scores already stored as % after the fix
            score_citation = r["score_citation"]
            score_coverage = r["score_coverage"]
            latency = r["latency_seconds"]
        
        result.append({
            "id": r["id"],
            "timestamp": r["timestamp"],
            "score_citation": score_citation,
            "score_coverage": score_coverage,
            "latency_seconds": latency,
            "details": per_question
        })
    return result
