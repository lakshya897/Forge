"""
SQLite Database Handlers for AutonomousAI.
Manages runtime/state.db (session checkpoints, telemetry) and runtime/metrics.db (performance stats).
"""

from pathlib import Path
from typing import Any, Dict, List, Optional
import sqlite3
import json
import time
from utils.config import settings


class RuntimeDB:
    """Manages SQLite transactions for active sessions, checkpoints, and execution traces."""

    @classmethod
    def _get_connection(cls) -> sqlite3.Connection:
        db_path = settings.runtime_db_path
        db_path.parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(str(db_path), timeout=30.0)
        conn.row_factory = sqlite3.Row
        cls._init_tables(conn)
        return conn

    @classmethod
    def _init_tables(cls, conn: sqlite3.Connection) -> None:
        with conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS sessions (
                    session_id TEXT PRIMARY KEY,
                    project_path TEXT,
                    goal TEXT,
                    status TEXT,
                    created_at REAL,
                    updated_at REAL,
                    state_json TEXT
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS checkpoints (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT,
                    stage TEXT,
                    timestamp REAL,
                    state_json TEXT
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS iteration_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT,
                    iteration INTEGER,
                    timestamp REAL,
                    modified_files TEXT,
                    tests_passed INTEGER,
                    confidence REAL,
                    summary TEXT
                )
            """)

    @classmethod
    def save_session(cls, session_id: str, project_path: str, goal: str, status: str, state_dict: Dict[str, Any]) -> None:
        conn = cls._get_connection()
        now = time.time()
        with conn:
            conn.execute("""
                INSERT INTO sessions (session_id, project_path, goal, status, created_at, updated_at, state_json)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(session_id) DO UPDATE SET
                    status=excluded.status,
                    updated_at=excluded.updated_at,
                    state_json=excluded.state_json
            """, (session_id, project_path, goal, status, now, now, json.dumps(state_dict)))
        conn.close()

    @classmethod
    def get_session(cls, session_id: str) -> Optional[Dict[str, Any]]:
        conn = cls._get_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM sessions WHERE session_id = ?", (session_id,))
        row = cur.fetchone()
        conn.close()
        if row:
            res = dict(row)
            try:
                res["state"] = json.loads(res.get("state_json", "{}"))
            except Exception:
                res["state"] = {}
            return res
        return None

    @classmethod
    def save_checkpoint(cls, session_id: str, stage: str, state_dict: Dict[str, Any]) -> None:
        conn = cls._get_connection()
        with conn:
            conn.execute("""
                INSERT INTO checkpoints (session_id, stage, timestamp, state_json)
                VALUES (?, ?, ?, ?)
            """, (session_id, stage, time.time(), json.dumps(state_dict)))
        conn.close()

    @classmethod
    def log_iteration(
        cls,
        session_id: str,
        iteration: int,
        modified_files: List[str],
        tests_passed: bool,
        confidence: float,
        summary: str,
    ) -> None:
        conn = cls._get_connection()
        with conn:
            conn.execute("""
                INSERT INTO iteration_logs (session_id, iteration, timestamp, modified_files, tests_passed, confidence, summary)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (session_id, iteration, time.time(), json.dumps(modified_files), 1 if tests_passed else 0, confidence, summary))
        conn.close()


class MetricsDB:
    """Manages performance metrics and timing statistics in runtime/metrics.db."""

    @classmethod
    def _get_connection(cls) -> sqlite3.Connection:
        db_path = settings.metrics_db_path
        db_path.parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(str(db_path), timeout=30.0)
        conn.row_factory = sqlite3.Row
        cls._init_tables(conn)
        return conn

    @classmethod
    def _init_tables(cls, conn: sqlite3.Connection) -> None:
        with conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS agent_timings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT,
                    agent_name TEXT,
                    duration_ms REAL,
                    timestamp REAL
                )
            """)

    @classmethod
    def log_timing(cls, session_id: str, agent_name: str, duration_ms: float) -> None:
        conn = cls._get_connection()
        with conn:
            conn.execute("""
                INSERT INTO agent_timings (session_id, agent_name, duration_ms, timestamp)
                VALUES (?, ?, ?, ?)
            """, (session_id, agent_name, duration_ms, time.time()))
        conn.close()

    @classmethod
    def get_summary(cls, session_id: Optional[str] = None) -> List[Dict[str, Any]]:
        conn = cls._get_connection()
        cur = conn.cursor()
        if session_id:
            cur.execute("""
                SELECT agent_name, COUNT(*) as count, AVG(duration_ms) as avg_duration, SUM(duration_ms) as total_duration
                FROM agent_timings WHERE session_id = ? GROUP BY agent_name
            """, (session_id,))
        else:
            cur.execute("""
                SELECT agent_name, COUNT(*) as count, AVG(duration_ms) as avg_duration, SUM(duration_ms) as total_duration
                FROM agent_timings GROUP BY agent_name
            """)
        rows = cur.fetchall()
        conn.close()
        return [dict(r) for r in rows]
