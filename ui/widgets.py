"""
TaskFlow Pro — Custom Widgets
Reusable UI components used across the application.
"""

import customtkinter as ctk
from ui.theme import c, font


# ══════════════════════════════════════════════════════════════════════════════
#  STAT CARD
# ══════════════════════════════════════════════════════════════════════════════

class StatCard(ctk.CTkFrame):
    """A coloured card that shows a label, big number, and optional subtitle."""

    def __init__(self, master, label: str, value: str | int,
                 accent: str = None, subtitle: str = "", **kwargs):
        kwargs.setdefault("corner_radius", 16)
        kwargs.setdefault("fg_color", c("bg_card"))
        super().__init__(master, **kwargs)
        self.configure(border_width=1, border_color=c("border"))

        accent = accent or c("accent")

        # Left colour bar
        bar = ctk.CTkFrame(self, width=4, fg_color=accent, corner_radius=2)
        bar.pack(side="left", fill="y", padx=(0, 12))

        inner = ctk.CTkFrame(self, fg_color="transparent")
        inner.pack(side="left", fill="both", expand=True, pady=14, padx=(0, 14))

        ctk.CTkLabel(inner, text=label, font=font(11), text_color=c("text_secondary")).pack(anchor="w")
        ctk.CTkLabel(inner, text=str(value), font=font(28, "bold"), text_color=c("text_primary")).pack(anchor="w")
        if subtitle:
            ctk.CTkLabel(inner, text=subtitle, font=font(10), text_color=c("text_muted")).pack(anchor="w")

    def update_value(self, value):
        # Rebuild is simplest; call from outside if needed
        pass


# ══════════════════════════════════════════════════════════════════════════════
#  PILL BADGE
# ══════════════════════════════════════════════════════════════════════════════

class PillBadge(ctk.CTkLabel):
    """Rounded pill badge for priority / status display."""

    def __init__(self, master, text: str, color: str, **kwargs):
        super().__init__(
            master,
            text=f"  {text}  ",
            font=font(10, "bold"),
            text_color="#FFFFFF",
            fg_color=color,
            corner_radius=20,
            **kwargs,
        )


# ══════════════════════════════════════════════════════════════════════════════
#  SEARCH BAR
# ══════════════════════════════════════════════════════════════════════════════

class SearchBar(ctk.CTkFrame):
    def __init__(self, master, on_change=None, placeholder="Search tasks…", **kwargs):
        kwargs.setdefault("fg_color", c("bg_input"))
        kwargs.setdefault("corner_radius", 10)
        super().__init__(master, **kwargs)
        self.configure(border_width=1, border_color=c("border"))

        ctk.CTkLabel(self, text="🔍", font=font(14)).pack(side="left", padx=(10, 4))
        self._var = ctk.StringVar()
        self._entry = ctk.CTkEntry(
            self,
            textvariable=self._var,
            placeholder_text=placeholder,
            border_width=0,
            fg_color="transparent",
            font=font(13),
            text_color=c("text_primary"),
        )
        self._entry.pack(side="left", fill="x", expand=True, padx=(0, 8), pady=6)

        if on_change:
            self._var.trace_add("write", lambda *_: on_change(self._var.get()))

    @property
    def value(self) -> str:
        return self._var.get()

    def clear(self):
        self._var.set("")


# ══════════════════════════════════════════════════════════════════════════════
#  ICON BUTTON
# ══════════════════════════════════════════════════════════════════════════════

class IconButton(ctk.CTkButton):
    """Small square button with an emoji icon and no text."""

    def __init__(self, master, icon: str, command=None, tooltip: str = "",
                 size: int = 32, fg: str = None, **kwargs):
        fg = fg or c("bg_card")
        super().__init__(
            master,
            text=icon,
            command=command,
            width=size,
            height=size,
            corner_radius=8,
            fg_color=fg,
            hover_color=c("bg_card_hover"),
            font=font(16),
            **kwargs,
        )


# ══════════════════════════════════════════════════════════════════════════════
#  DIVIDER
# ══════════════════════════════════════════════════════════════════════════════

class Divider(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        kwargs.setdefault("height", 1)
        kwargs.setdefault("fg_color", c("border"))
        super().__init__(master, **kwargs)


# ══════════════════════════════════════════════════════════════════════════════
#  CONFIRM DIALOG
# ══════════════════════════════════════════════════════════════════════════════

class ConfirmDialog(ctk.CTkToplevel):
    """Modal confirmation dialog; result stored in .confirmed."""

    def __init__(self, master, title: str, message: str,
                 confirm_text: str = "Delete", danger: bool = True):
        super().__init__(master)
        self.title(title)
        self.geometry("380x160")
        self.resizable(False, False)
        self.grab_set()
        self.configure(fg_color=c("bg_modal"))

        self.confirmed = False

        ctk.CTkLabel(self, text=title, font=font(15, "bold"),
                     text_color=c("text_primary")).pack(pady=(20, 4))
        ctk.CTkLabel(self, text=message, font=font(12),
                     text_color=c("text_secondary"), wraplength=340).pack(pady=(0, 16))

        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack()

        ctk.CTkButton(
            btn_frame, text="Cancel", width=110, fg_color=c("bg_card"),
            text_color=c("text_primary"), hover_color=c("bg_card_hover"),
            command=self.destroy,
        ).pack(side="left", padx=6)

        btn_color = c("danger") if danger else c("accent")
        ctk.CTkButton(
            btn_frame, text=confirm_text, width=110,
            fg_color=btn_color, hover_color=c("accent_hover") if not danger else "#DC2626",
            command=self._confirm,
        ).pack(side="left", padx=6)

        self.wait_window()

    def _confirm(self):
        self.confirmed = True
        self.destroy()


# ══════════════════════════════════════════════════════════════════════════════
#  TOAST NOTIFICATION
# ══════════════════════════════════════════════════════════════════════════════

class Toast:
    """Temporary notification banner at the bottom of a window."""

    @staticmethod
    def show(master, message: str, kind: str = "info", duration_ms: int = 3000):
        color_map = {
            "info":    c("accent"),
            "success": c("success"),
            "warning": c("warning"),
            "error":   c("danger"),
        }
        color = color_map.get(kind, c("accent"))

        banner = ctk.CTkFrame(master, fg_color=color, corner_radius=10, height=40)
        banner.place(relx=0.5, rely=0.96, anchor="s")
        ctk.CTkLabel(banner, text=message, font=font(12), text_color="#FFFFFF").pack(
            padx=20, pady=8
        )
        master.after(duration_ms, banner.destroy)
