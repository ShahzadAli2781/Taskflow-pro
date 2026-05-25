"""
TaskFlow Pro — Entry Point
Stable Version (Python 3.14 Compatible)
"""

import os
os.environ["TK_SILENCE_DEPRECATION"] = "1"

import customtkinter as ctk
import tkinter
import sys

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# Python 3.14 Compatibility Fix
try:
    tkinter._default_root = None
except:
    pass

# Ensure imports work
sys.path.insert(0, os.path.dirname(__file__))

from database import initialize_database, UserDB
from ui.theme import apply as apply_theme
from auth import AuthWindow
from dashboard import DashboardWindow


class App:
    """
    Main Application Controller
    """

    def __init__(self):
        initialize_database()

        apply_theme("dark")
        ctk.set_default_color_theme("blue")

        self.root = ctk.CTk()
        self.root.withdraw()

        self._auth_win = None
        self._dash_win = None

    def run(self):
        """
        Start directly with auth window
        """
        self._start_auth()
        self.root.mainloop()

    def _start_auth(self):
        """
        Open authentication window
        """

        saved = UserDB.load_session()

        if saved:
            user = UserDB.get_by_username(saved)

            if user:
                UserDB.update_last_login(user["id"])
                apply_theme(user.get("theme", "dark"))
                self._launch_dashboard(user)
                return

        self._auth_win = AuthWindow(master=self.root, on_success=self._on_login)

    def _on_login(self, user: dict):
        """
        Called after successful login
        """

        apply_theme(user.get("theme", "dark"))

        if self._auth_win:
            self._auth_win.destroy()
            self._auth_win = None

        self._launch_dashboard(user)

    def _launch_dashboard(self, user: dict):

        self._dash_win = DashboardWindow(
            master=self.root,
            user=user,
            on_logout=self._on_logout
        )

    def _on_logout(self):

        UserDB.clear_session()

        if self._dash_win:
            self._dash_win.destroy()
            self._dash_win = None

        apply_theme("dark")

        self._start_auth()


if __name__ == "__main__":
    App().run()