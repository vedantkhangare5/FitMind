"""
SQLite database module for FitMind.

Provides a lightweight persistence layer using Python's built-in sqlite3.
No ORM — just direct SQL. Now supports multi-user context.
"""

import sqlite3
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional
import os
import shutil

logger = logging.getLogger(__name__)

# Default database path — backend/fitmind.db (gitignored by *.db rule)
DEFAULT_DB_PATH = Path(__file__).parent.parent / "fitmind.db"

CREATE_USERS_TABLE = """
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT UNIQUE NOT NULL,
    hashed_password TEXT NOT NULL,
    created_at TEXT NOT NULL
);
"""

CREATE_PROFILE_TABLE = """
CREATE TABLE IF NOT EXISTS fitness_profile (
    user_id INTEGER PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
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
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    weight_kg REAL NOT NULL,
    recorded_at TEXT NOT NULL
);
"""

CREATE_NUTRITION_TABLE = """
CREATE TABLE IF NOT EXISTS nutrition_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    date TEXT NOT NULL,
    calories INTEGER NOT NULL,
    protein_grams INTEGER NOT NULL,
    UNIQUE(user_id, date)
);
"""

CREATE_WORKOUT_TABLE = """
CREATE TABLE IF NOT EXISTS workout_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    date TEXT NOT NULL,
    workout_type TEXT NOT NULL,
    duration_minutes INTEGER NOT NULL,
    completed BOOLEAN NOT NULL
);
"""

def get_connection(db_path: Optional[str] = None) -> sqlite3.Connection:
    """Creates a new SQLite connection. Row factory set for dict-like access."""
    path = db_path or os.environ.get("FITMIND_DB_PATH") or str(DEFAULT_DB_PATH)
    conn = sqlite3.connect(path, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA synchronous=NORMAL;")
    conn.execute("PRAGMA foreign_keys=ON;")
    return conn

def migrate_v1_to_v2(db_path: Optional[str] = None) -> None:
    """Migrates from single-user (v1) to multi-user (v2)."""
    path = db_path or os.environ.get("FITMIND_DB_PATH") or str(DEFAULT_DB_PATH)
    if not os.path.exists(path):
        return  # Nothing to migrate

    conn = get_connection(db_path)
    try:
        cursor = conn.execute("PRAGMA table_info(fitness_profile)")
        columns = [row["name"] for row in cursor.fetchall()]
        if "user_id" in columns or not columns:
            return  # Already migrated or table doesn't exist yet

        logger.info("Migrating database to V2 (Multi-User)...")
        # Backup first
        backup_path = str(path) + ".bak"
        shutil.copy2(path, backup_path)
        logger.info(f"Database backed up to {backup_path}")

        # Transaction
        conn.execute("BEGIN EXCLUSIVE")
        
        # 1. Create users table
        conn.execute(CREATE_USERS_TABLE)

        # 2. Insert dummy user
        now_str = datetime.now(timezone.utc).isoformat()
        conn.execute(
            "INSERT OR IGNORE INTO users (id, email, hashed_password, created_at) VALUES (1, 'local@fitmind.local', '!', ?)",
            (now_str,)
        )
        user_id = 1

        # 3. Create v2 tables
        conn.execute("CREATE TABLE IF NOT EXISTS fitness_profile_v2 ("
            "user_id INTEGER PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE, "
            "age INTEGER NOT NULL, sex TEXT NOT NULL, height_cm REAL NOT NULL, "
            "weight_kg REAL NOT NULL, activity_level TEXT NOT NULL, goal TEXT NOT NULL, updated_at TEXT NOT NULL"
        ")")
        
        conn.execute("CREATE TABLE IF NOT EXISTS progress_history_v2 ("
            "id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE, "
            "weight_kg REAL NOT NULL, recorded_at TEXT NOT NULL"
        ")")

        conn.execute("CREATE TABLE IF NOT EXISTS nutrition_logs_v2 ("
            "id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE, "
            "date TEXT NOT NULL, calories INTEGER NOT NULL, protein_grams INTEGER NOT NULL, UNIQUE(user_id, date)"
        ")")

        conn.execute("CREATE TABLE IF NOT EXISTS workout_logs_v2 ("
            "id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE, "
            "date TEXT NOT NULL, workout_type TEXT NOT NULL, duration_minutes INTEGER NOT NULL, completed BOOLEAN NOT NULL"
        ")")

        # 4. Copy data
        conn.execute("INSERT INTO fitness_profile_v2 (user_id, age, sex, height_cm, weight_kg, activity_level, goal, updated_at) "
                     "SELECT ?, age, sex, height_cm, weight_kg, activity_level, goal, updated_at FROM fitness_profile WHERE id=1", (user_id,))
        
        conn.execute("INSERT INTO progress_history_v2 (id, user_id, weight_kg, recorded_at) "
                     "SELECT id, ?, weight_kg, recorded_at FROM progress_history", (user_id,))
        
        conn.execute("INSERT INTO nutrition_logs_v2 (user_id, date, calories, protein_grams) "
                     "SELECT ?, date, calories, protein_grams FROM nutrition_logs", (user_id,))
                     
        conn.execute("INSERT INTO workout_logs_v2 (id, user_id, date, workout_type, duration_minutes, completed) "
                     "SELECT id, ?, date, workout_type, duration_minutes, completed FROM workout_logs", (user_id,))

        # 5. Drop old tables
        conn.execute("DROP TABLE fitness_profile")
        conn.execute("DROP TABLE progress_history")
        conn.execute("DROP TABLE nutrition_logs")
        conn.execute("DROP TABLE workout_logs")

        # 6. Rename new tables
        conn.execute("ALTER TABLE fitness_profile_v2 RENAME TO fitness_profile")
        conn.execute("ALTER TABLE progress_history_v2 RENAME TO progress_history")
        conn.execute("ALTER TABLE nutrition_logs_v2 RENAME TO nutrition_logs")
        conn.execute("ALTER TABLE workout_logs_v2 RENAME TO workout_logs")

        conn.commit()
        logger.info("Database migration to V2 complete.")
    except Exception as e:
        conn.rollback()
        logger.error(f"Migration failed: {e}")
        raise
    finally:
        conn.close()

def init_db(db_path: Optional[str] = None) -> None:
    """Creates the profile table if it doesn't exist. Called once at app startup."""
    migrate_v1_to_v2(db_path)
    conn = get_connection(db_path)
    try:
        conn.execute(CREATE_USERS_TABLE)
        conn.execute(CREATE_PROFILE_TABLE)
        conn.execute(CREATE_PROGRESS_TABLE)
        conn.execute(CREATE_NUTRITION_TABLE)
        conn.execute(CREATE_WORKOUT_TABLE)
        conn.commit()
        logger.info("Database initialized successfully.")
    finally:
        conn.close()

class UserRepository:
    def __init__(self, db_path: Optional[str] = None):
        self._db_path = db_path

    def _conn(self) -> sqlite3.Connection:
        return get_connection(self._db_path)

    def get_user_by_email(self, email: str) -> Optional[dict]:
        conn = self._conn()
        try:
            row = conn.execute("SELECT id, email, hashed_password FROM users WHERE email = ?", (email,)).fetchone()
            return dict(row) if row else None
        finally:
            conn.close()

    def create_user(self, email: str, hashed_password: str) -> int:
        conn = self._conn()
        try:
            now = datetime.now(timezone.utc).isoformat()
            cursor = conn.execute("INSERT INTO users (email, hashed_password, created_at) VALUES (?, ?, ?)", (email, hashed_password, now))
            conn.commit()
            return cursor.lastrowid
        finally:
            conn.close()

class ProfileRepository:
    def __init__(self, db_path: Optional[str] = None):
        self._db_path = db_path

    def _conn(self) -> sqlite3.Connection:
        return get_connection(self._db_path)

    def get_profile(self, user_id: int) -> Optional[dict]:
        conn = self._conn()
        try:
            row = conn.execute(
                "SELECT age, sex, height_cm, weight_kg, activity_level, goal, updated_at "
                "FROM fitness_profile WHERE user_id = ?", (user_id,)
            ).fetchone()
            return dict(row) if row else None
        finally:
            conn.close()

    def save_profile(
        self,
        user_id: int,
        age: int,
        sex: str,
        height_cm: float,
        weight_kg: float,
        activity_level: str,
        goal: str,
    ) -> dict:
        updated_at = datetime.now(timezone.utc).isoformat()
        conn = self._conn()
        try:
            conn.execute(
                "INSERT OR REPLACE INTO fitness_profile "
                "(user_id, age, sex, height_cm, weight_kg, activity_level, goal, updated_at) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                (user_id, age, sex, height_cm, weight_kg, activity_level, goal, updated_at),
            )
            conn.commit()
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

    def delete_profile(self, user_id: int) -> bool:
        conn = self._conn()
        try:
            cursor = conn.execute("DELETE FROM fitness_profile WHERE user_id = ?", (user_id,))
            conn.commit()
            return cursor.rowcount > 0
        finally:
            conn.close()

class ProgressRepository:
    def __init__(self, db_path: Optional[str] = None):
        self._db_path = db_path

    def _conn(self) -> sqlite3.Connection:
        return get_connection(self._db_path)

    def add_entry(self, user_id: int, weight_kg: float, recorded_at: str) -> dict:
        conn = self._conn()
        try:
            cursor = conn.execute(
                "INSERT INTO progress_history (user_id, weight_kg, recorded_at) VALUES (?, ?, ?)",
                (user_id, weight_kg, recorded_at)
            )
            conn.commit()
            return {
                "id": cursor.lastrowid,
                "weight_kg": weight_kg,
                "recorded_at": recorded_at
            }
        finally:
            conn.close()

    def get_history(self, user_id: int) -> list[dict]:
        conn = self._conn()
        try:
            rows = conn.execute(
                "SELECT id, weight_kg, recorded_at FROM progress_history "
                "WHERE user_id = ? ORDER BY recorded_at ASC, id ASC", (user_id,)
            ).fetchall()
            return [dict(row) for row in rows]
        finally:
            conn.close()

    def delete_entry(self, user_id: int, entry_id: int) -> bool:
        conn = self._conn()
        try:
            cursor = conn.execute("DELETE FROM progress_history WHERE user_id = ? AND id = ?", (user_id, entry_id))
            conn.commit()
            return cursor.rowcount > 0
        finally:
            conn.close()

    def get_summary(self, user_id: int, goal: Optional[str] = None) -> dict:
        history = self.get_history(user_id)
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
            try:
                t0 = datetime.fromisoformat(history[0]["recorded_at"].replace("Z", "+00:00")).timestamp()
                
                sum_x = 0.0
                sum_y = 0.0
                sum_xy = 0.0
                sum_x2 = 0.0
                n = len(history)
                
                for entry in history:
                    t = datetime.fromisoformat(entry["recorded_at"].replace("Z", "+00:00")).timestamp()
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

    def log_nutrition(self, user_id: int, date: str, calories: int, protein_grams: int) -> dict:
        conn = self._conn()
        try:
            conn.execute(
                "INSERT OR REPLACE INTO nutrition_logs (id, user_id, date, calories, protein_grams) "
                "VALUES (COALESCE((SELECT id FROM nutrition_logs WHERE user_id=? AND date=?), NULL), ?, ?, ?, ?)",
                (user_id, date, user_id, date, calories, protein_grams)
            )
            conn.commit()
            return {"date": date, "calories": calories, "protein_grams": protein_grams}
        finally:
            conn.close()

    def get_nutrition_logs(self, user_id: int, limit: int = 30) -> list[dict]:
        conn = self._conn()
        try:
            rows = conn.execute(
                "SELECT date, calories, protein_grams FROM nutrition_logs "
                "WHERE user_id = ? ORDER BY date DESC LIMIT ?", (user_id, limit)
            ).fetchall()
            return [dict(row) for row in rows]
        finally:
            conn.close()

    def delete_nutrition_log(self, user_id: int, date: str) -> bool:
        conn = self._conn()
        try:
            cursor = conn.execute("DELETE FROM nutrition_logs WHERE user_id = ? AND date = ?", (user_id, date))
            conn.commit()
            return cursor.rowcount > 0
        finally:
            conn.close()

    def log_workout(self, user_id: int, date: str, workout_type: str, duration_minutes: int, completed: bool) -> dict:
        conn = self._conn()
        try:
            cursor = conn.execute(
                "INSERT INTO workout_logs (user_id, date, workout_type, duration_minutes, completed) VALUES (?, ?, ?, ?, ?)",
                (user_id, date, workout_type, duration_minutes, completed)
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

    def get_workout_logs(self, user_id: int, limit: int = 30) -> list[dict]:
        conn = self._conn()
        try:
            rows = conn.execute(
                "SELECT id, date, workout_type, duration_minutes, completed FROM workout_logs "
                "WHERE user_id = ? ORDER BY date DESC, id DESC LIMIT ?", (user_id, limit)
            ).fetchall()
            result = []
            for row in rows:
                r = dict(row)
                r["completed"] = bool(r["completed"])
                result.append(r)
            return result
        finally:
            conn.close()

    def delete_workout_log(self, user_id: int, log_id: int) -> bool:
        conn = self._conn()
        try:
            cursor = conn.execute("DELETE FROM workout_logs WHERE user_id = ? AND id = ?", (user_id, log_id))
            conn.commit()
            return cursor.rowcount > 0
        finally:
            conn.close()

    def get_summary(self, user_id: int, today: Optional[str] = None, target_calories: Optional[int] = None, target_protein: Optional[int] = None, target_workouts_per_week: Optional[int] = None) -> dict:
        from datetime import timedelta
        if today is None:
            today = datetime.now().strftime("%Y-%m-%d")
        
        today_date = datetime.strptime(today, "%Y-%m-%d")
        seven_days_ago = (today_date - timedelta(days=6)).strftime("%Y-%m-%d")

        conn = self._conn()
        try:
            nut_rows = conn.execute(
                "SELECT date, calories, protein_grams FROM nutrition_logs "
                "WHERE user_id = ? AND date >= ? AND date <= ?", (user_id, seven_days_ago, today)
            ).fetchall()
            
            logged_nutrition_days = len(nut_rows)
            avg_calories = None
            avg_protein = None
            if logged_nutrition_days > 0:
                avg_calories = sum(r["calories"] for r in nut_rows) / logged_nutrition_days
                avg_protein = sum(r["protein_grams"] for r in nut_rows) / logged_nutrition_days

            work_rows = conn.execute(
                "SELECT id, completed FROM workout_logs "
                "WHERE user_id = ? AND date >= ? AND date <= ?", (user_id, seven_days_ago, today)
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
