"""
SQLite database module for FitMind.

Provides a lightweight persistence layer using Python's built-in sqlite3.
No ORM — just direct SQL for a single-table, single-user profile store.

WHY SQLITE3 STDLIB:
- Zero additional dependencies
- Single-user local development context
- One table with 7 columns does not warrant an ORM
- Database file is gitignored and trivially deletable for reset
"""

import sqlite3
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

# Default database path — backend/fitmind.db (gitignored by *.db rule)
DEFAULT_DB_PATH = Path(__file__).parent.parent / "fitmind.db"

CREATE_PROFILE_TABLE = """
CREATE TABLE IF NOT EXISTS fitness_profile (
    id INTEGER PRIMARY KEY CHECK (id = 1),
    age INTEGER NOT NULL,
    sex TEXT NOT NULL,
    height_cm REAL NOT NULL,
    weight_kg REAL NOT NULL,
    activity_level TEXT NOT NULL,
    goal TEXT NOT NULL,
    updated_at TEXT NOT NULL
);
"""


def get_connection(db_path: Optional[str] = None) -> sqlite3.Connection:
    """Creates a new SQLite connection. Row factory set for dict-like access."""
    path = db_path or str(DEFAULT_DB_PATH)
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL;")
    return conn


def init_db(db_path: Optional[str] = None) -> None:
    """Creates the profile table if it doesn't exist. Called once at app startup."""
    conn = get_connection(db_path)
    try:
        conn.execute(CREATE_PROFILE_TABLE)
        conn.commit()
        logger.info("Database initialized successfully.")
    finally:
        conn.close()


class ProfileRepository:
    """
    Data access layer for the fitness profile.
    
    All methods open and close their own connections for simplicity.
    With a single-user SQLite setup, connection pooling is unnecessary.
    """

    def __init__(self, db_path: Optional[str] = None):
        self._db_path = db_path

    def _conn(self) -> sqlite3.Connection:
        return get_connection(self._db_path)

    def get_profile(self) -> Optional[dict]:
        """Returns the saved profile as a dict, or None if no profile exists."""
        conn = self._conn()
        try:
            row = conn.execute(
                "SELECT age, sex, height_cm, weight_kg, activity_level, goal, updated_at "
                "FROM fitness_profile WHERE id = 1"
            ).fetchone()
            if row is None:
                return None
            return dict(row)
        finally:
            conn.close()

    def save_profile(
        self,
        age: int,
        sex: str,
        height_cm: float,
        weight_kg: float,
        activity_level: str,
        goal: str,
    ) -> dict:
        """Creates or replaces the single profile. Returns the saved profile dict."""
        updated_at = datetime.now(timezone.utc).isoformat()
        conn = self._conn()
        try:
            conn.execute(
                "INSERT OR REPLACE INTO fitness_profile "
                "(id, age, sex, height_cm, weight_kg, activity_level, goal, updated_at) "
                "VALUES (1, ?, ?, ?, ?, ?, ?, ?)",
                (age, sex, height_cm, weight_kg, activity_level, goal, updated_at),
            )
            conn.commit()
            logger.info("Profile saved.")
            return {
                "age": age,
                "sex": sex,
                "height_cm": height_cm,
                "weight_kg": weight_kg,
                "activity_level": activity_level,
                "goal": goal,
                "updated_at": updated_at,
            }
        finally:
            conn.close()

    def delete_profile(self) -> bool:
        """Deletes the profile. Returns True if a row was deleted, False if nothing existed."""
        conn = self._conn()
        try:
            cursor = conn.execute("DELETE FROM fitness_profile WHERE id = 1")
            conn.commit()
            deleted = cursor.rowcount > 0
            if deleted:
                logger.info("Profile deleted.")
            return deleted
        finally:
            conn.close()
