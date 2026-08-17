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

CREATE_PROGRESS_TABLE = """
CREATE TABLE IF NOT EXISTS progress_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    weight_kg REAL NOT NULL,
    recorded_at TEXT NOT NULL
);
"""

CREATE_NUTRITION_TABLE = """
CREATE TABLE IF NOT EXISTS nutrition_logs (
    date TEXT PRIMARY KEY,
    calories INTEGER NOT NULL,
    protein_grams INTEGER NOT NULL
);
"""

CREATE_WORKOUT_TABLE = """
CREATE TABLE IF NOT EXISTS workout_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT NOT NULL,
    workout_type TEXT NOT NULL,
    duration_minutes INTEGER NOT NULL,
    completed BOOLEAN NOT NULL
);
"""



import os

def get_connection(db_path: Optional[str] = None) -> sqlite3.Connection:
    """Creates a new SQLite connection. Row factory set for dict-like access."""
    path = db_path or os.environ.get("FITMIND_DB_PATH") or str(DEFAULT_DB_PATH)
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL;")
    return conn


def init_db(db_path: Optional[str] = None) -> None:
    """Creates the profile table if it doesn't exist. Called once at app startup."""
    conn = get_connection(db_path)
    try:
        conn.execute(CREATE_PROFILE_TABLE)
        conn.execute(CREATE_PROGRESS_TABLE)
        conn.execute(CREATE_NUTRITION_TABLE)
        conn.execute(CREATE_WORKOUT_TABLE)
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

class ProgressRepository:
    """
    Data access layer for the progress history.
    """
    def __init__(self, db_path: Optional[str] = None):
        self._db_path = db_path

    def _conn(self) -> sqlite3.Connection:
        return get_connection(self._db_path)

    def add_entry(self, weight_kg: float, recorded_at: str) -> dict:
        conn = self._conn()
        try:
            cursor = conn.execute(
                "INSERT INTO progress_history (weight_kg, recorded_at) VALUES (?, ?)",
                (weight_kg, recorded_at)
            )
            conn.commit()
            return {
                "id": cursor.lastrowid,
                "weight_kg": weight_kg,
                "recorded_at": recorded_at
            }
        finally:
            conn.close()

    def get_history(self) -> list[dict]:
        """Returns all entries sorted by recorded_at ASC, id ASC."""
        conn = self._conn()
        try:
            rows = conn.execute(
                "SELECT id, weight_kg, recorded_at FROM progress_history "
                "ORDER BY recorded_at ASC, id ASC"
            ).fetchall()
            return [dict(row) for row in rows]
        finally:
            conn.close()

    def delete_entry(self, entry_id: int) -> bool:
        conn = self._conn()
        try:
            cursor = conn.execute("DELETE FROM progress_history WHERE id = ?", (entry_id,))
            conn.commit()
            return cursor.rowcount > 0
        finally:
            conn.close()

    def get_summary(self, goal: Optional[str] = None) -> dict:
        """
        Calculates deterministic summary metrics based on the history.
        Trend is calculated as a linear regression slope in kg/week.
        """
        history = self.get_history()
        
        if not history:
            return {
                "current_weight": None,
                "starting_weight": None,
                "total_change_kg": None,
                "percentage_change": None,
                "trend": "insufficient_data",
                "entries_count": 0,
                "note": "No progress history found."
            }

        starting_weight = history[0]["weight_kg"]
        current_weight = history[-1]["weight_kg"]
        total_change_kg = current_weight - starting_weight
        percentage_change = (total_change_kg / starting_weight) * 100 if starting_weight > 0 else 0.0

        trend = "insufficient_data"
        if len(history) >= 3:
            # Linear regression of weight_kg over time (weeks)
            # x = elapsed time in weeks from the earliest entry
            # y = weight_kg
            try:
                t0 = datetime.fromisoformat(history[0]["recorded_at"].replace("Z", "+00:00")).timestamp()
                
                sum_x = 0.0
                sum_y = 0.0
                sum_xy = 0.0
                sum_x2 = 0.0
                n = len(history)
                
                for entry in history:
                    t = datetime.fromisoformat(entry["recorded_at"].replace("Z", "+00:00")).timestamp()
                    # Convert elapsed seconds to weeks
                    x = (t - t0) / (86400 * 7)
                    y = entry["weight_kg"]
                    
                    sum_x += x
                    sum_y += y
                    sum_xy += x * y
                    sum_x2 += x * x
                
                denominator = (n * sum_x2) - (sum_x * sum_x)
                if denominator == 0:
                    trend = "stable"
                else:
                    slope = ((n * sum_xy) - (sum_x * sum_y)) / denominator
                    if slope < -0.1:
                        trend = "losing"
                    elif slope > 0.1:
                        trend = "gaining"
                    else:
                        trend = "stable"
            except Exception as e:
                logger.error(f"Error calculating trend: {e}")
                trend = "stable"

        note = None
        if goal == "build_muscle":
            note = "Weight history alone is insufficient to track muscle gain, as it cannot distinguish between fat, muscle, and water weight."

        return {
            "current_weight": round(current_weight, 2),
            "starting_weight": round(starting_weight, 2),
            "total_change_kg": round(total_change_kg, 2),
            "percentage_change": round(percentage_change, 2),
            "trend": trend,
            "entries_count": len(history),
            "note": note
        }

class BehaviorRepository:
    def __init__(self, db_path: Optional[str] = None):
        self._db_path = db_path

    def _conn(self) -> sqlite3.Connection:
        return get_connection(self._db_path)

    def log_nutrition(self, date: str, calories: int, protein_grams: int) -> dict:
        conn = self._conn()
        try:
            conn.execute(
                "INSERT OR REPLACE INTO nutrition_logs (date, calories, protein_grams) VALUES (?, ?, ?)",
                (date, calories, protein_grams)
            )
            conn.commit()
            return {"date": date, "calories": calories, "protein_grams": protein_grams}
        finally:
            conn.close()

    def get_nutrition_logs(self, limit: int = 30) -> list[dict]:
        conn = self._conn()
        try:
            rows = conn.execute(
                "SELECT date, calories, protein_grams FROM nutrition_logs "
                "ORDER BY date DESC LIMIT ?", (limit,)
            ).fetchall()
            return [dict(row) for row in rows]
        finally:
            conn.close()

    def delete_nutrition_log(self, date: str) -> bool:
        conn = self._conn()
        try:
            cursor = conn.execute("DELETE FROM nutrition_logs WHERE date = ?", (date,))
            conn.commit()
            return cursor.rowcount > 0
        finally:
            conn.close()

    def log_workout(self, date: str, workout_type: str, duration_minutes: int, completed: bool) -> dict:
        conn = self._conn()
        try:
            cursor = conn.execute(
                "INSERT INTO workout_logs (date, workout_type, duration_minutes, completed) VALUES (?, ?, ?, ?)",
                (date, workout_type, duration_minutes, completed)
            )
            conn.commit()
            return {
                "id": cursor.lastrowid,
                "date": date,
                "workout_type": workout_type,
                "duration_minutes": duration_minutes,
                "completed": completed
            }
        finally:
            conn.close()

    def get_workout_logs(self, limit: int = 30) -> list[dict]:
        conn = self._conn()
        try:
            rows = conn.execute(
                "SELECT id, date, workout_type, duration_minutes, completed FROM workout_logs "
                "ORDER BY date DESC, id DESC LIMIT ?", (limit,)
            ).fetchall()
            result = []
            for row in rows:
                r = dict(row)
                r["completed"] = bool(r["completed"])
                result.append(r)
            return result
        finally:
            conn.close()

    def delete_workout_log(self, log_id: int) -> bool:
        conn = self._conn()
        try:
            cursor = conn.execute("DELETE FROM workout_logs WHERE id = ?", (log_id,))
            conn.commit()
            return cursor.rowcount > 0
        finally:
            conn.close()

    def get_summary(self, today: Optional[str] = None, target_calories: Optional[int] = None, target_protein: Optional[int] = None, target_workouts_per_week: Optional[int] = None) -> dict:
        from datetime import timedelta
        if today is None:
            today = datetime.now().strftime("%Y-%m-%d")
        
        today_date = datetime.strptime(today, "%Y-%m-%d")
        seven_days_ago = (today_date - timedelta(days=6)).strftime("%Y-%m-%d")

        conn = self._conn()
        try:
            nut_rows = conn.execute(
                "SELECT date, calories, protein_grams FROM nutrition_logs "
                "WHERE date >= ? AND date <= ?", (seven_days_ago, today)
            ).fetchall()
            
            logged_nutrition_days = len(nut_rows)
            avg_calories = None
            avg_protein = None
            if logged_nutrition_days > 0:
                avg_calories = sum(r["calories"] for r in nut_rows) / logged_nutrition_days
                avg_protein = sum(r["protein_grams"] for r in nut_rows) / logged_nutrition_days

            work_rows = conn.execute(
                "SELECT id, completed FROM workout_logs "
                "WHERE date >= ? AND date <= ?", (seven_days_ago, today)
            ).fetchall()
            
            logged_workout_count = len(work_rows)
            completed_count = sum(1 for r in work_rows if r["completed"])

            summary = {
                "window_days": 7,
                "nutrition": {
                    "logged_days": logged_nutrition_days,
                    "coverage": round((logged_nutrition_days / 7.0) * 100, 1),
                    "avg_calories": round(avg_calories, 1) if avg_calories is not None else None,
                    "avg_protein": round(avg_protein, 1) if avg_protein is not None else None,
                },
                "workouts": {
                    "logged_count": logged_workout_count,
                    "completed_count": completed_count,
                }
            }
            if target_calories:
                summary["nutrition"]["calorie_target"] = target_calories
                if avg_calories is not None:
                    summary["nutrition"]["calorie_adherence"] = round((avg_calories / target_calories) * 100, 1)
            
            if target_protein:
                summary["nutrition"]["protein_target"] = target_protein
                if avg_protein is not None:
                    summary["nutrition"]["protein_adherence"] = round((avg_protein / target_protein) * 100, 1)

            if target_workouts_per_week is not None:
                summary["workouts"]["target_frequency"] = target_workouts_per_week
                summary["workouts"]["adherence"] = round((completed_count / target_workouts_per_week) * 100, 1) if target_workouts_per_week > 0 else 0.0

            return summary
        finally:
            conn.close()

