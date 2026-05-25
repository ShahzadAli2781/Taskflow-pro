"""
TaskFlow Pro — Main Dashboard
SAFE Python 3.14 Compatible Version
"""

import gc

import customtkinter as ctk

from datetime import datetime

from database import (
    TaskDB,
    UserDB,
)

from ui.theme import (
    c,
    font,
    apply as apply_theme,
)

from ui.widgets import (
    StatCard,
    Divider,
    Toast,
    ConfirmDialog,
)

from task_manager import TaskListPanel
from analytics import AnalyticsPanel


# ==========================================
# NAV ITEM
# ==========================================

class NavItem(ctk.CTkFrame):

    def __init__(
        self,
        master,
        icon: str,
        label: str,
        command,
        active: bool = False,
        **kwargs,
    ):

        kwargs.setdefault(
            "fg_color",
            c("bg_sidebar"),
        )

        kwargs.setdefault(
            "corner_radius",
            10,
        )

        super().__init__(
            master,
            **kwargs,
        )

        self._active = active

        self._command = command

        self._icon_label = ctk.CTkLabel(
            self,
            text=icon,
            font=font(18),
            width=28,
        )

        self._icon_label.pack(
            side="left",
            padx=(14, 8),
        )

        self._text_label = ctk.CTkLabel(
            self,
            text=label,
            font=font(13),
            anchor="w",
        )

        self._text_label.pack(
            side="left",
            fill="x",
            expand=True,
            pady=12,
        )

        self._set_active(active)

        # SAFE EVENTS
        widgets = [
            self,
            self._icon_label,
            self._text_label,
        ]

        for w in widgets:

            w.bind(
                "<Button-1>",
                self._click,
            )

            w.bind(
                "<Enter>",
                self._hover_on,
            )

            w.bind(
                "<Leave>",
                self._hover_off,
            )

    def _click(self, _=None):

        try:
            self._command()
        except:
            pass

    def _hover_on(self, _=None):

        if not self._active:

            self.configure(
                fg_color=c("bg_card_hover")
            )

    def _hover_off(self, _=None):

        if not self._active:

            self.configure(
                fg_color=c("bg_sidebar")
            )

    def set_active(self, active: bool):

        self._active = active

        self._set_active(active)

    def _set_active(self, active: bool):

        if active:

            self.configure(
                fg_color=c("accent_dim")
            )

            self._text_label.configure(
                text_color=c("accent"),
                font=font(13, "bold"),
            )

            self._icon_label.configure(
                text_color=c("accent")
            )

        else:

            self.configure(
                fg_color=c("bg_sidebar")
            )

            self._text_label.configure(
                text_color=c("sidebar_text"),
                font=font(13),
            )

            self._icon_label.configure(
                text_color=c("sidebar_text")
            )


# ==========================================
# OVERVIEW PANEL
# ==========================================

class OverviewPanel(ctk.CTkFrame):

    def __init__(
        self,
        master,
        user: dict,
        **kwargs,
    ):

        kwargs.setdefault(
            "fg_color",
            c("bg_root"),
        )

        super().__init__(
            master,
            **kwargs,
        )

        self.user = user

        self._build()

        self.refresh_stats()

    # ======================================

    def _build(self):

        # GREETING
        greeting_frame = ctk.CTkFrame(
            self,
            fg_color=c("bg_root"),
        )

        greeting_frame.pack(
            fill="x",
            padx=24,
            pady=(20, 12),
        )

        self._greeting_label = ctk.CTkLabel(
            greeting_frame,
            text="",
            font=font(24, "bold"),
            text_color=c("text_primary"),
        )

        self._greeting_label.pack(
            side="left"
        )

        # CLOCK
        self._clock_label = ctk.CTkLabel(
            greeting_frame,
            text="",
            font=font(13),
            text_color=c("text_muted"),
        )

        self._clock_label.pack(
            side="right"
        )

        self._update_clock()

        # STATS
        self._stats_grid = ctk.CTkFrame(
            self,
            fg_color=c("bg_root"),
        )

        self._stats_grid.pack(
            fill="x",
            padx=20,
            pady=(0, 20),
        )

        # RECENT TASKS
        ctk.CTkLabel(
            self,
            text="📌 Recent Tasks",
            font=font(16, "bold"),
            text_color=c("text_primary"),
        ).pack(
            anchor="w",
            padx=24,
            pady=(0, 8),
        )

        self._recent_frame = ctk.CTkScrollableFrame(
            self,
            fg_color=c("bg_root"),
            height=300,
        )

        self._recent_frame.pack(
            fill="both",
            expand=True,
            padx=20,
            pady=(0, 16),
        )

        # OVERDUE
        self._overdue_frame = ctk.CTkFrame(
            self,
            fg_color=c("bg_root"),
        )

        self._overdue_frame.pack(
            fill="x",
            padx=20,
            pady=(0, 12),
        )

    # ======================================

    def _update_clock(self):

        if not self.winfo_exists():
            return

        now = datetime.now()

        hour = now.hour

        greeting = (
            "Good Morning"
            if hour < 12
            else (
                "Good Afternoon"
                if hour < 18
                else "Good Evening"
            )
        )

        self._greeting_label.configure(
            text=f"{greeting}, {self.user['username'].capitalize()} 👋"
        )

        self._clock_label.configure(
            text=now.strftime(
                "%A, %b %d  •  %I:%M %p"
            )
        )

        self.after(
            30000,
            self._update_clock,
        )

    # ======================================

    def refresh_stats(self):

        gc.collect()

        for w in self._stats_grid.winfo_children():

            try:
                w.destroy()
            except:
                pass

        stats = TaskDB.get_stats(
            self.user["id"]
        )

        card_data = [

            (
                "Total Tasks",
                stats["Total"],
                c("accent"),
                "",
            ),

            (
                "Completed",
                stats["Completed"],
                c("success"),
                f"{stats['Productivity']}% rate",
            ),

            (
                "In Progress",
                stats["In Progress"],
                c("info"),
                "Active",
            ),

            (
                "Overdue",
                stats["Overdue"],
                c("danger"),
                "Action needed",
            ),
        ]

        for col, (
            label,
            val,
            color,
            sub,
        ) in enumerate(card_data):

            card = StatCard(
                self._stats_grid,
                label,
                val,
                accent=color,
                subtitle=sub,
            )

            card.grid(
                row=0,
                column=col,
                padx=6,
                pady=4,
                sticky="nsew",
            )

        for i in range(4):

            self._stats_grid.columnconfigure(
                i,
                weight=1,
            )

        self._refresh_recent()

        self._refresh_overdue_alert()

    # ======================================

    def _refresh_recent(self):

        for w in self._recent_frame.winfo_children():

            try:
                w.destroy()
            except:
                pass

        tasks = TaskDB.get_all(
            self.user["id"]
        )[:8]

        if not tasks:

            ctk.CTkLabel(
                self._recent_frame,
                text="No tasks yet — add your first!",
                font=font(12),
                text_color=c("text_muted"),
            ).pack(
                pady=20
            )

            return

        from utils.helpers import PRIORITY_COLORS

        for task in tasks:

            row = ctk.CTkFrame(
                self._recent_frame,
                fg_color=c("bg_card"),
                corner_radius=10,
                border_width=1,
                border_color=c("border"),
            )

            row.pack(
                fill="x",
                pady=3,
            )

            icon = (
                "✅"
                if task["status"] == "Completed"
                else (
                    "🔄"
                    if task["status"] == "In Progress"
                    else "⏳"
                )
            )

            ctk.CTkLabel(
                row,
                text=icon,
                font=font(14),
                width=30,
            ).pack(
                side="left",
                padx=10,
                pady=10,
            )

            ctk.CTkLabel(
                row,
                text=task["title"],
                font=font(12),
                text_color=c("text_primary"),
                anchor="w",
            ).pack(
                side="left"
            )

            pri_color = PRIORITY_COLORS.get(
                task["priority"],
                c("accent"),
            )

            ctk.CTkLabel(
                row,
                text=f"● {task['priority']}",
                font=font(10),
                text_color=pri_color,
            ).pack(
                side="right",
                padx=12,
            )

    # ======================================

    def _refresh_overdue_alert(self):

        for w in self._overdue_frame.winfo_children():

            try:
                w.destroy()
            except:
                pass

        overdue = TaskDB.get_overdue(
            self.user["id"]
        )

        if not overdue:
            return

        alert = ctk.CTkFrame(
            self._overdue_frame,
            fg_color=c("danger"),
            corner_radius=10,
        )

        alert.pack(fill="x")

        ctk.CTkLabel(
            alert,
            text=f"⚠️ You have {len(overdue)} overdue task(s).",
            font=font(12, "bold"),
            text_color="#FFFFFF",
        ).pack(
            side="left",
            padx=16,
            pady=10,
        )


# ==========================================
# SETTINGS PANEL
# ==========================================

class SettingsPanel(ctk.CTkFrame):

    def __init__(
        self,
        master,
        user: dict,
        on_theme_change,
        on_logout,
        **kwargs,
    ):

        kwargs.setdefault(
            "fg_color",
            c("bg_root"),
        )

        super().__init__(
            master,
            **kwargs,
        )

        self.user = user

        self._on_theme_change = on_theme_change

        self._on_logout = on_logout

        self._build()

    # ======================================

    def _build(self):

        ctk.CTkLabel(
            self,
            text="Settings",
            font=font(22, "bold"),
            text_color=c("text_primary"),
        ).pack(
            anchor="w",
            padx=24,
            pady=(20, 20),
        )

        # THEME CARD
        card = ctk.CTkFrame(
            self,
            fg_color=c("bg_card"),
            corner_radius=14,
            border_width=1,
            border_color=c("border"),
        )

        card.pack(
            fill="x",
            padx=20,
            pady=(0, 16),
        )

        # PROFILE
        ctk.CTkLabel(
            card,
            text="👤 Profile",
            font=font(14, "bold"),
            text_color=c("text_primary"),
        ).pack(
            anchor="w",
            padx=20,
            pady=(16, 4),
        )

        ctk.CTkLabel(
            card,
            text=f"Username: {self.user['username']}",
            font=font(12),
            text_color=c("text_secondary"),
        ).pack(
            anchor="w",
            padx=28,
        )

        email = (
            self.user.get("email")
            or "—"
        )

        ctk.CTkLabel(
            card,
            text=f"Email: {email}",
            font=font(12),
            text_color=c("text_secondary"),
        ).pack(
            anchor="w",
            padx=28,
            pady=(0, 12),
        )

        Divider(card).pack(
            fill="x",
            padx=16,
        )

        # THEME SWITCH
        theme_row = ctk.CTkFrame(
            card,
            fg_color=c("bg_card"),
        )

        theme_row.pack(
            fill="x",
            padx=20,
            pady=14,
        )

        ctk.CTkLabel(
            theme_row,
            text="🎨 Theme",
            font=font(13, "bold"),
            text_color=c("text_primary"),
        ).pack(
            side="left"
        )

        self._theme_switch = ctk.CTkSwitch(
            theme_row,
            text="Dark Mode",
            font=font(12),
            text_color=c("text_secondary"),
            fg_color=c("border"),
            progress_color=c("accent"),
            command=self._toggle_theme,
        )

        self._theme_switch.pack(
            side="right"
        )

        if self.user.get(
            "theme",
            "dark",
        ) == "dark":

            self._theme_switch.select()

        Divider(card).pack(
            fill="x",
            padx=16,
        )

        # LOGOUT
        logout_btn = ctk.CTkButton(
            card,
            text="🚪 Logout",
            width=160,
            height=38,
            fg_color=c("danger"),
            hover_color="#DC2626",
            font=font(13, "bold"),
            corner_radius=8,
            command=self._logout,
        )

        logout_btn.pack(
            anchor="w",
            padx=20,
            pady=20,
        )

    # ======================================

    def _toggle_theme(self):

        mode = (
            "dark"
            if self._theme_switch.get()
            else "light"
        )

        self._on_theme_change(mode)

    # ======================================

    def _logout(self):

        dlg = ConfirmDialog(
            self,
            "Logout",
            "Are you sure you want to logout?",
            confirm_text="Logout",
            danger=False,
        )

        if dlg.confirmed:

            self._on_logout()


# ==========================================
# MAIN DASHBOARD
# ==========================================

class DashboardWindow(ctk.CTkToplevel):

    PAGES = [
        "Overview",
        "Tasks",
        "Analytics",
        "Settings",
    ]

    ICONS = [
        "🏠",
        "✅",
        "📊",
        "⚙️",
    ]

    def __init__(
        self,
        master,
        user: dict,
        on_logout,
    ):

        super().__init__(master)
        
        self.protocol("WM_DELETE_WINDOW", self._on_close)

        self.user = user

        self.on_logout = on_logout

        self._active_page = "Overview"

        self._nav_items = {}

        self._pages = {}

        self._setup_window()

        self._build_layout()

        self._register_shortcuts()

    def _on_close(self):
        self.master.quit()
        self.destroy()

    # ======================================

    def _setup_window(self):

        self.title("TaskFlow Pro")

        self.geometry("1200x720")

        self.minsize(900, 600)

        self.configure(
            fg_color=c("bg_root")
        )

        self.update_idletasks()

        x = (
            self.winfo_screenwidth()
            - 1200
        ) // 2

        y = (
            self.winfo_screenheight()
            - 720
        ) // 2

        self.geometry(
            f"1200x720+{x}+{y}"
        )

    # ======================================

    def _build_layout(self):

        # SIDEBAR
        self._sidebar = ctk.CTkFrame(
            self,
            width=220,
            fg_color=c("bg_sidebar"),
            corner_radius=0,
        )

        self._sidebar.pack(
            side="left",
            fill="y",
        )

        self._sidebar.pack_propagate(
            False
        )

        self._build_sidebar()

        # CONTENT
        self._content = ctk.CTkFrame(
            self,
            fg_color=c("bg_root"),
            corner_radius=0,
        )

        self._content.pack(
            side="right",
            fill="both",
            expand=True,
        )

        self._build_all_pages()

        self._show_page(
            "Overview"
        )

    # ======================================

    def _build_sidebar(self):

        sb = self._sidebar

        logo = ctk.CTkFrame(
            sb,
            fg_color=c("bg_sidebar"),
            height=72,
        )

        logo.pack(fill="x")

        ctk.CTkLabel(
            logo,
            text="✅ TaskFlow Pro",
            font=font(16, "bold"),
            text_color=c("text_primary"),
        ).pack(
            side="left",
            padx=18,
        )

        Divider(sb).pack(
            fill="x",
            padx=14,
            pady=(0, 12),
        )

        for icon, page in zip(
            self.ICONS,
            self.PAGES,
        ):

            item = NavItem(
                sb,
                icon,
                page,
                command=lambda p=page:
                self._show_page(p),
                active=(page == "Overview"),
            )

            item.pack(
                fill="x",
                padx=10,
                pady=2,
            )

            self._nav_items[page] = item

        # SPACER
        ctk.CTkFrame(
            sb,
            fg_color=c("bg_sidebar"),
        ).pack(
            fill="both",
            expand=True,
        )

        Divider(sb).pack(
            fill="x",
            padx=14,
            pady=8,
        )

        # USER
        user_row = ctk.CTkFrame(
            sb,
            fg_color=c("bg_card"),
            corner_radius=10,
        )

        user_row.pack(
            fill="x",
            padx=12,
            pady=(0, 16),
        )

        ctk.CTkLabel(
            user_row,
            text="👤",
            font=font(20),
            width=38,
        ).pack(
            side="left",
            padx=10,
            pady=10,
        )

        col = ctk.CTkFrame(
            user_row,
            fg_color=c("bg_card"),
        )

        col.pack(side="left")

        ctk.CTkLabel(
            col,
            text=self.user["username"].capitalize(),
            font=font(12, "bold"),
            text_color=c("text_primary"),
        ).pack(
            anchor="w"
        )

    # ======================================

    def _build_all_pages(self):

        self._pages["Overview"] = OverviewPanel(
            self._content,
            self.user,
        )

        self._pages["Tasks"] = TaskListPanel(
            self._content,
            self.user,
        )

        self._pages["Analytics"] = AnalyticsPanel(
            self._content,
            self.user,
        )

        self._pages["Settings"] = SettingsPanel(
            self._content,
            self.user,
            on_theme_change=self._change_theme,
            on_logout=self._do_logout,
        )

    # ======================================

    def _show_page(self, page):

        for name, frame in self._pages.items():

            try:
                frame.pack_forget()
                self._nav_items[name].set_active(False)
            except:
                pass

        self._pages[page].pack(
            fill="both",
            expand=True,
        )

        self._nav_items[page].set_active(
            True
        )

        self._active_page = page

        if page == "Analytics":

            try:
                self._pages["Analytics"].refresh()
            except:
                pass

    # ======================================

    def refresh_stats(self):

        try:
            self._pages["Overview"].refresh_stats()
        except:
            pass

    # ======================================

    def _change_theme(self, mode):

        apply_theme(mode)

        UserDB.update_theme(
            self.user["id"],
            mode,
        )

        Toast.show(
            self,
            f"Switched to {mode} mode.",
            "info",
        )

        self.after(
            400,
            self._rebuild_ui,
        )

    # ======================================

    def _rebuild_ui(self):

        gc.collect()

        self.configure(
            fg_color=c("bg_root")
        )

        for w in self.winfo_children():

            try:
                w.destroy()
            except:
                pass

        self._nav_items = {}

        self._pages = {}

        self._build_layout()

    # ======================================

    def _do_logout(self):

        try:

            UserDB.clear_session()

            self.destroy()

            self.on_logout()

        except:
            pass

    # ======================================

    def _register_shortcuts(self):

        self.bind(
            "<Control-1>",
            lambda _:
            self._show_page("Overview"),
        )

        self.bind(
            "<Control-2>",
            lambda _:
            self._show_page("Tasks"),
        )

        self.bind(
            "<Control-3>",
            lambda _:
            self._show_page("Analytics"),
        )

        self.bind(
            "<Control-comma>",
            lambda _:
            self._show_page("Settings"),
        )