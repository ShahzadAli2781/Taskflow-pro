"""
TaskFlow Pro — Utility Helpers
Common helper functions used across the application.
"""

import hashlib
import csv
import json
import os
import re
from datetime import datetime, date


EXPORTS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "exports")


# ── Security ───────────────────────────────────────────────────────────────────

def hash_password(password: str) -> str:
    """Return SHA-256 hex digest of the password."""
    return hashlib.sha256(password.encode()).hexdigest()


def validate_password(password: str) -> tuple[bool, str]:
    """Validate password strength. Returns (is_valid, message)."""
    if len(password) < 6:
        return False, "Password must be at least 6 characters."
    return True, ""


def validate_username(username: str) -> tuple[bool, str]:
    if len(username) < 3:
        return False, "Username must be at least 3 characters."
    if not re.match(r"^[A-Za-z0-9_]+$", username):
        return False, "Username can only contain letters, numbers, and underscores."
    return True, ""


# ── Date helpers ───────────────────────────────────────────────────────────────

def format_date(date_str: str | None) -> str:
    if not date_str:
        return "No due date"
    try:
        d = datetime.strptime(date_str, "%Y-%m-%d").date()
        return d.strftime("%b %d, %Y")
    except ValueError:
        return date_str


def is_overdue(due_date_str: str | None, status: str) -> bool:
    if not due_date_str or status == "Completed":
        return False
    try:
        due = datetime.strptime(due_date_str, "%Y-%m-%d").date()
        return due < date.today()
    except ValueError:
        return False


def days_until_due(due_date_str: str | None) -> int | None:
    if not due_date_str:
        return None
    try:
        due = datetime.strptime(due_date_str, "%Y-%m-%d").date()
        return (due - date.today()).days
    except ValueError:
        return None


# ── Export helpers ─────────────────────────────────────────────────────────────

def _ensure_exports_dir():
    os.makedirs(EXPORTS_DIR, exist_ok=True)


def export_to_txt(tasks: list[dict], filename: str = None) -> str:
    _ensure_exports_dir()
    filename = filename or f"tasks_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    path = os.path.join(EXPORTS_DIR, filename)
    with open(path, "w", encoding="utf-8") as f:
        f.write("TaskFlow Pro — Task Export\n")
        f.write(f"Exported: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("=" * 60 + "\n\n")
        for i, t in enumerate(tasks, 1):
            f.write(f"{i}. {t['title']}\n")
            f.write(f"   Status:   {t['status']}\n")
            f.write(f"   Priority: {t['priority']}\n")
            f.write(f"   Category: {t.get('category_name', 'None')}\n")
            f.write(f"   Due Date: {format_date(t.get('due_date'))}\n")
            if t.get("description"):
                f.write(f"   Notes:    {t['description']}\n")
            f.write("\n")
    return path


def export_to_csv(tasks: list[dict], filename: str = None) -> str:
    _ensure_exports_dir()
    filename = filename or f"tasks_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    path = os.path.join(EXPORTS_DIR, filename)
    fields = ["title", "status", "priority", "category_name", "due_date",
              "created_at", "description"]
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(tasks)
    return path


def export_to_json(tasks: list[dict], filename: str = None) -> str:
    _ensure_exports_dir()
    filename = filename or f"tasks_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    path = os.path.join(EXPORTS_DIR, filename)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(tasks, f, indent=2, default=str)
    return path


# ── Priority colour mapping ────────────────────────────────────────────────────

PRIORITY_COLORS = {
    "High":   "#EF4444",
    "Medium": "#F59E0B",
    "Low":    "#22C55E",
}

STATUS_COLORS = {
    "Pending":     "#94A3B8",
    "In Progress": "#3B82F6",
    "Completed":   "#22C55E",
    "Overdue":     "#EF4444",
}
