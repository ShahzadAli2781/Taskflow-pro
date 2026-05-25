"""
TaskFlow Pro — Theme System
Central design tokens for dark and light modes.
"""

import customtkinter as ctk

# ══════════════════════════════════════════════════════════════════════════════
#  DESIGN TOKENS
# ══════════════════════════════════════════════════════════════════════════════

DARK = {
    # Backgrounds
    "bg_root":        "#0F1117",
    "bg_sidebar":     "#161B27",
    "bg_card":        "#1E2433",
    "bg_card_hover":  "#252D3F",
    "bg_input":       "#1A2035",
    "bg_modal":       "#1E2433",
    # Text
    "text_primary":   "#F1F5F9",
    "text_secondary": "#94A3B8",
    "text_muted":     "#475569",
    # Accent
    "accent":         "#4F8EF7",
    "accent_hover":   "#6BA3FF",
    "accent_dim":     "#1E3A6E",
    # Status
    "success":        "#22C55E",
    "warning":        "#F59E0B",
    "danger":         "#EF4444",
    "info":           "#3B82F6",
    # Borders
    "border":         "#2D3748",
    "border_focus":   "#4F8EF7",
    # Sidebar accent
    "sidebar_active": "#4F8EF7",
    "sidebar_text":   "#94A3B8",
}

LIGHT = {
    # Backgrounds
    "bg_root":        "#F0F4FF",
    "bg_sidebar":     "#FFFFFF",
    "bg_card":        "#FFFFFF",
    "bg_card_hover":  "#F8FAFF",
    "bg_input":       "#F1F5F9",
    "bg_modal":       "#FFFFFF",
    # Text
    "text_primary":   "#0F172A",
    "text_secondary": "#475569",
    "text_muted":     "#94A3B8",
    # Accent
    "accent":         "#4F8EF7",
    "accent_hover":   "#3B7DE8",
    "accent_dim":     "#DBEAFE",
    # Status
    "success":        "#16A34A",
    "warning":        "#D97706",
    "danger":         "#DC2626",
    "info":           "#2563EB",
    # Borders
    "border":         "#E2E8F0",
    "border_focus":   "#4F8EF7",
    # Sidebar
    "sidebar_active": "#4F8EF7",
    "sidebar_text":   "#475569",
}

# Active theme reference – mutated at runtime
_current: dict = dict(DARK)


def apply(mode: str):
    """Switch active theme tokens and configure CustomTkinter appearance."""
    global _current
    _current = dict(DARK if mode == "dark" else LIGHT)
    ctk.set_appearance_mode(mode)


def c(key: str) -> str:
    """Get a colour token from the active theme."""
    return _current.get(key, "#FF0000")   # red = missing key (debug aid)


# Font helpers ──────────────────────────────────────────────────────────────────
FONT_FAMILY = "Segoe UI" if __import__("sys").platform == "win32" else "SF Pro Display"
MONO_FAMILY = "Consolas"  if __import__("sys").platform == "win32" else "Menlo"


def font(size: int = 13, weight: str = "normal") -> tuple:
    return (FONT_FAMILY, size, weight)


def mono(size: int = 12) -> tuple:
    return (MONO_FAMILY, size)
