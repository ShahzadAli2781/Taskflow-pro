"""
TaskFlow Pro — Database Manager
Handles all SQLite operations for users, tasks, and categories.
"""

import sqlite3
import os
import json
from datetime import datetime


DB_PATH = os.path.join(os.path.dirname(__file__), "database", "taskflow.db")


def get_connection():
    """Return a new SQLite connection with row_factory set."""
    conn = sqlite3.connect(DB_PATH, timeout=10.0)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def initialize_database():
    """Create all tables and seed default categories if not present."""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = get_connection()
    cur = conn.cursor()

    #  Users 
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            username    TEXT    NOT NULL UNIQUE,
            password    TEXT    NOT NULL,
            email       TEXT,
            created_at  TEXT    DEFAULT (datetime('now')),
            last_login  TEXT,
            theme       TEXT    DEFAULT 'dark',
            remember_me INTEGER DEFAULT 0
        )
    """)

    #  Categories 
    cur.execute("""
        CREATE TABLE IF NOT EXISTS categories (
            id    INTEGER PRIMARY KEY AUTOINCREMENT,
            name  TEXT    NOT NULL UNIQUE,
            color TEXT    DEFAULT '#4A9EFF',
            icon  TEXT    DEFAULT '📁'
        )
    """)

    #  Tasks 
    cur.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id      INTEGER NOT NULL,
            title        TEXT    NOT NULL,
            description  TEXT,
            category_id  INTEGER,
            priority     TEXT    DEFAULT 'Medium',
            status       TEXT    DEFAULT 'Pending',
            due_date     TEXT,
            created_at   TEXT    DEFAULT (datetime('now')),
            updated_at   TEXT    DEFAULT (datetime('now')),
            completed_at TEXT,
            FOREIGN KEY (user_id)     REFERENCES users(id)      ON DELETE CASCADE,
            FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE SET NULL
        )
    """)

    #  Seed default categories 
    default_categories = [
        ("Work",     "#4A9EFF", "💼"),
        ("Study",    "#A78BFA", "📚"),
        ("Personal", "#34D399", "🏠"),
        ("Shopping", "#FB923C", "🛍️"),
        ("Fitness",  "#F472B6", "🏋️"),
    ]
    cur.executemany(
        "INSERT OR IGNORE INTO categories (name, color, icon) VALUES (?, ?, ?)",
        default_categories,
    )

    conn.commit()
    conn.close()



#  USER OPERATIONS


class UserDB:
    @staticmethod
    def create(username: str, password: str, email: str = "") -> bool:
        try:
            conn = get_connection()
            conn.execute(
                "INSERT INTO users (username, password, email) VALUES (?, ?, ?)",
                (username, password, email),
            )
            conn.commit()
            conn.close()
            return True
        except sqlite3.IntegrityError:
            return False

    @staticmethod
    def get_by_credentials(username: str, password: str):
        conn = get_connection()
        row = conn.execute(
            "SELECT * FROM users WHERE username=? AND password=?",
            (username, password),
        ).fetchone()
        conn.close()
        return dict(row) if row else None

    @staticmethod
    def get_by_username(username: str):
        conn = get_connection()
        row = conn.execute(
            "SELECT * FROM users WHERE username=?", (username,)
        ).fetchone()
        conn.close()
        return dict(row) if row else None

    @staticmethod
    def update_last_login(user_id: int):
        conn = get_connection()
        conn.execute(
            "UPDATE users SET last_login=? WHERE id=?",
            (datetime.now().isoformat(), user_id),
        )
        conn.commit()
        conn.close()

    @staticmethod
    def update_theme(user_id: int, theme: str):
        conn = get_connection()
        conn.execute("UPDATE users SET theme=? WHERE id=?", (theme, user_id))
        conn.commit()
        conn.close()

    @staticmethod
    def save_session(username: str):
        """Persist the remembered username to a tiny JSON file."""
        session_path = os.path.join(os.path.dirname(__file__), "database", "session.json")
        with open(session_path, "w") as f:
            json.dump({"username": username}, f)

    @staticmethod
    def load_session() -> str | None:
        session_path = os.path.join(os.path.dirname(__file__), "database", "session.json")
        if os.path.exists(session_path):
            with open(session_path) as f:
                data = json.load(f)
            return data.get("username")
        return None

    @staticmethod
    def clear_session():
        session_path = os.path.join(os.path.dirname(__file__), "database", "session.json")
        if os.path.exists(session_path):
            os.remove(session_path)



#  TASK OPERATIONS


class TaskDB:
    @staticmethod
    def create(user_id, title, description="", category_id=None,
               priority="Medium", status="Pending", due_date=None) -> int:
        conn = get_connection()
        cur = conn.execute(
            """INSERT INTO tasks
               (user_id, title, description, category_id, priority, status, due_date)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (user_id, title, description, category_id, priority, status, due_date),
        )
        task_id = cur.lastrowid
        conn.commit()
        conn.close()
        return task_id

    @staticmethod
    def get_all(user_id: int, status_filter=None, category_id=None,
                priority_filter=None, search_query=None) -> list[dict]:
        conn = get_connection()
        query = """
            SELECT t.*, c.name AS category_name, c.color AS category_color, c.icon AS category_icon
            FROM tasks t
            LEFT JOIN categories c ON t.category_id = c.id
            WHERE t.user_id = ?
        """
        params = [user_id]
        if status_filter and status_filter != "All":
            query += " AND t.status = ?"
            params.append(status_filter)
        if category_id:
            query += " AND t.category_id = ?"
            params.append(category_id)
        if priority_filter and priority_filter != "All":
            query += " AND t.priority = ?"
            params.append(priority_filter)
        if search_query:
            query += " AND (t.title LIKE ? OR t.description LIKE ?)"
            params += [f"%{search_query}%", f"%{search_query}%"]
        query += " ORDER BY t.created_at DESC"
        rows = conn.execute(query, params).fetchall()
        conn.close()
        return [dict(r) for r in rows]

    @staticmethod
    def update(task_id: int, **kwargs):
        kwargs["updated_at"] = datetime.now().isoformat()
        if kwargs.get("status") == "Completed":
            kwargs.setdefault("completed_at", datetime.now().isoformat())
        cols = ", ".join(f"{k}=?" for k in kwargs)
        vals = list(kwargs.values()) + [task_id]
        conn = get_connection()
        conn.execute(f"UPDATE tasks SET {cols} WHERE id=?", vals)
        conn.commit()
        conn.close()

    @staticmethod
    def delete(task_id: int):
        conn = get_connection()
        conn.execute("DELETE FROM tasks WHERE id=?", (task_id,))
        conn.commit()
        conn.close()

    @staticmethod
    def get_stats(user_id: int) -> dict:
        conn = get_connection()
        rows = conn.execute(
            "SELECT status, COUNT(*) as cnt FROM tasks WHERE user_id=? GROUP BY status",
            (user_id,),
        ).fetchall()
        conn.close()
        stats = {"Total": 0, "Pending": 0, "In Progress": 0, "Completed": 0, "Overdue": 0}
        for r in rows:
            stats[r["status"]] = r["cnt"]
            stats["Total"] += r["cnt"]
        # Auto-detect overdue
        now = datetime.now().date().isoformat()
        conn = get_connection()
        overdue = conn.execute(
            """SELECT COUNT(*) FROM tasks
               WHERE user_id=? AND status != 'Completed'
               AND due_date IS NOT NULL AND due_date < ?""",
            (user_id, now),
        ).fetchone()[0]
        conn.close()
        stats["Overdue"] = overdue
        productivity = (
            round(stats["Completed"] / stats["Total"] * 100) if stats["Total"] else 0
        )
        stats["Productivity"] = productivity
        return stats

    @staticmethod
    def get_category_breakdown(user_id: int) -> list[dict]:
        conn = get_connection()
        rows = conn.execute(
            """SELECT c.name, c.color, COUNT(t.id) as count
               FROM tasks t
               JOIN categories c ON t.category_id = c.id
               WHERE t.user_id=?
               GROUP BY c.id""",
            (user_id,),
        ).fetchall()
        conn.close()
        return [dict(r) for r in rows]

    @staticmethod
    def get_overdue(user_id: int) -> list[dict]:
        now = datetime.now().date().isoformat()
        conn = get_connection()
        rows = conn.execute(
            """SELECT t.*, c.name AS category_name
               FROM tasks t LEFT JOIN categories c ON t.category_id=c.id
               WHERE t.user_id=? AND t.status != 'Completed'
               AND t.due_date IS NOT NULL AND t.due_date < ?""",
            (user_id, now),
        ).fetchall()
        conn.close()
        return [dict(r) for r in rows]



#  CATEGORY OPERATIONS


class CategoryDB:
    @staticmethod
    def get_all() -> list[dict]:
        conn = get_connection()
        rows = conn.execute("SELECT * FROM categories").fetchall()
        conn.close()
        return [dict(r) for r in rows]
