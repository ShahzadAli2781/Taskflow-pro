"""
TaskFlow Pro — Authentication Screen
SAFE Python 3.14 Compatible Version
"""

import gc
import customtkinter as ctk

from database import (
    UserDB,
    initialize_database,
)

from utils.helpers import (
    hash_password,
    validate_username,
    validate_password,
)

from ui.theme import c, font
from ui.widgets import Toast


class AuthWindow(ctk.CTkToplevel):
    """
    Authentication Window
    """

    def __init__(self, master, on_success):

        super().__init__(master)
        
        self.protocol("WM_DELETE_WINDOW", self._on_close)

        initialize_database()

        self.on_success = on_success

        self._mode = "login"

        self._build_window()

        self._build_layout()

        self._try_auto_login()

    def _on_close(self):
        self.master.quit()
        self.destroy()

    # =====================================
    # WINDOW
    # =====================================

    def _build_window(self):

        self.title(
            "TaskFlow Pro — Sign In"
        )

        self.geometry(
            "900x560"
        )

        self.resizable(
            False,
            False,
        )

        self.configure(
            fg_color=c("bg_root")
        )

        self.update_idletasks()

        x = (
            self.winfo_screenwidth()
            - 900
        ) // 2

        y = (
            self.winfo_screenheight()
            - 560
        ) // 2

        self.geometry(
            f"900x560+{x}+{y}"
        )

    # =====================================
    # LAYOUT
    # =====================================

    def _build_layout(self):

        # LEFT PANEL
        self._left = ctk.CTkFrame(
            self,
            width=420,
            fg_color=c("bg_sidebar"),
            corner_radius=0,
        )

        self._left.pack(
            side="left",
            fill="y",
        )

        self._left.pack_propagate(
            False
        )

        self._build_hero(
            self._left
        )

        # RIGHT PANEL
        self._right = ctk.CTkFrame(
            self,
            fg_color=c("bg_root"),
            corner_radius=0,
        )

        self._right.pack(
            side="right",
            fill="both",
            expand=True,
        )

        self._form_frame = ctk.CTkFrame(
            self._right,
            fg_color=c("bg_root"),
        )

        self._form_frame.place(
            relx=0.5,
            rely=0.5,
            anchor="center",
        )

        self._build_login_form()

    # =====================================
    # HERO
    # =====================================

    def _build_hero(self, parent):

        spacer = ctk.CTkFrame(
            parent,
            height=80,
            fg_color=c("bg_sidebar"),
        )

        spacer.pack()

        ctk.CTkLabel(
            parent,
            text="✅",
            font=font(64),
        ).pack(
            pady=(40, 12)
        )

        ctk.CTkLabel(
            parent,
            text="TaskFlow Pro",
            font=font(28, "bold"),
            text_color=c("text_primary"),
        ).pack()

        ctk.CTkLabel(
            parent,
            text="Smart To-Do Management",
            font=font(14),
            text_color=c("text_secondary"),
        ).pack(
            pady=(4, 30)
        )

        features = [

            (
                "⚡",
                "Lightning fast task management",
            ),

            (
                "📊",
                "Analytics & productivity insights",
            ),

            (
                "🔒",
                "Secure multi-user support",
            ),

            (
                "🌙",
                "Dark & Light themes",
            ),
        ]

        for icon, text in features:

            row = ctk.CTkFrame(
                parent,
                fg_color=c("bg_sidebar"),
            )

            row.pack(
                fill="x",
                padx=40,
                pady=5,
            )

            ctk.CTkLabel(
                row,
                text=icon,
                font=font(14),
                width=28,
            ).pack(side="left")

            ctk.CTkLabel(
                row,
                text=text,
                font=font(12),
                text_color=c("text_secondary"),
            ).pack(
                side="left",
                padx=8,
            )

    # =====================================
    # SAFE FORM CLEAR
    # =====================================

    def _clear_form(self):

        gc.collect()

        for w in self._form_frame.winfo_children():

            try:
                w.destroy()

            except:
                pass

    # =====================================
    # LOGIN FORM
    # =====================================

    def _build_login_form(self):

        self._mode = "login"

        self._clear_form()

        frame = self._form_frame

        ctk.CTkLabel(
            frame,
            text="Welcome back 👋",
            font=font(26, "bold"),
            text_color=c("text_primary"),
        ).grid(
            row=0,
            column=0,
            columnspan=2,
            sticky="w",
            pady=(0, 4),
        )

        ctk.CTkLabel(
            frame,
            text="Sign in to your workspace",
            font=font(13),
            text_color=c("text_secondary"),
        ).grid(
            row=1,
            column=0,
            columnspan=2,
            sticky="w",
            pady=(0, 24),
        )

        # VARIABLES
        self._un_var = ctk.StringVar()

        self._pw_var = ctk.StringVar()

        self._remember_var = ctk.BooleanVar()

        # USERNAME
        ctk.CTkLabel(
            frame,
            text="Username",
            font=font(12, "bold"),
            text_color=c("text_secondary"),
        ).grid(
            row=2,
            column=0,
            columnspan=2,
            sticky="w",
        )

        self._un_entry = ctk.CTkEntry(
            frame,
            textvariable=self._un_var,
            width=320,
            height=42,
            placeholder_text="Enter username",
            font=font(13),
            fg_color=c("bg_input"),
            border_color=c("border"),
            text_color=c("text_primary"),
            corner_radius=10,
        )

        self._un_entry.grid(
            row=3,
            column=0,
            columnspan=2,
            pady=(4, 14),
        )

        # PASSWORD
        ctk.CTkLabel(
            frame,
            text="Password",
            font=font(12, "bold"),
            text_color=c("text_secondary"),
        ).grid(
            row=4,
            column=0,
            columnspan=2,
            sticky="w",
        )

        self._pw_entry = ctk.CTkEntry(
            frame,
            textvariable=self._pw_var,
            width=320,
            height=42,
            placeholder_text="Enter password",
            show="•",
            font=font(13),
            fg_color=c("bg_input"),
            border_color=c("border"),
            text_color=c("text_primary"),
            corner_radius=10,
        )

        self._pw_entry.grid(
            row=5,
            column=0,
            columnspan=2,
            pady=(4, 10),
        )

        # REMEMBER
        remember = ctk.CTkCheckBox(
            frame,
            text="Remember me",
            variable=self._remember_var,
            font=font(12),
            text_color=c("text_secondary"),
            fg_color=c("accent"),
            hover_color=c("accent_hover"),
        )

        remember.grid(
            row=6,
            column=0,
            columnspan=2,
            sticky="w",
            pady=(0, 20),
        )

        # ERROR LABEL
        self._err_label = ctk.CTkLabel(
            frame,
            text="",
            font=font(11),
            text_color=c("danger"),
        )

        self._err_label.grid(
            row=7,
            column=0,
            columnspan=2,
            pady=(0, 6),
        )

        # LOGIN BUTTON
        self._login_btn = ctk.CTkButton(
            frame,
            text="Sign In",
            width=320,
            height=44,
            fg_color=c("accent"),
            hover_color=c("accent_hover"),
            font=font(14, "bold"),
            corner_radius=10,
            command=self._do_login,
        )

        self._login_btn.grid(
            row=8,
            column=0,
            columnspan=2,
            pady=(0, 16),
        )

        self._login_btn.update()

        # SWITCH
        sw = ctk.CTkFrame(
            frame,
            fg_color=c("bg_root"),
        )

        sw.grid(
            row=9,
            column=0,
            columnspan=2,
        )

        ctk.CTkLabel(
            sw,
            text="Don't have an account?",
            font=font(12),
            text_color=c("text_secondary"),
        ).pack(side="left")

        signup_btn = ctk.CTkButton(
            sw,
            text="Sign Up",
            font=font(12, "bold"),
            fg_color=c("bg_root"),
            hover_color="#2B2B2B",
            text_color=c("accent"),
            command=self._build_signup_form,
        )

        signup_btn.pack(
            side="left",
            padx=(6, 0),
        )

        signup_btn.update()

        # ENTER KEY
        self.bind(
            "<Return>",
            lambda _: self._do_login(),
        )

        self._un_entry.focus()

    # =====================================
    # SIGNUP FORM
    # =====================================

    def _build_signup_form(self):

        self._mode = "signup"

        self._clear_form()

        frame = self._form_frame

        ctk.CTkLabel(
            frame,
            text="Create account 🚀",
            font=font(26, "bold"),
            text_color=c("text_primary"),
        ).grid(
            row=0,
            column=0,
            columnspan=2,
            sticky="w",
            pady=(0, 4),
        )

        ctk.CTkLabel(
            frame,
            text="Start organising your tasks today",
            font=font(13),
            text_color=c("text_secondary"),
        ).grid(
            row=1,
            column=0,
            columnspan=2,
            sticky="w",
            pady=(0, 24),
        )

        self._un_var = ctk.StringVar()
        self._em_var = ctk.StringVar()
        self._pw_var = ctk.StringVar()
        self._pw2_var = ctk.StringVar()

        def _field(
            label,
            var,
            row,
            placeholder,
            show="",
        ):

            ctk.CTkLabel(
                frame,
                text=label,
                font=font(12, "bold"),
                text_color=c("text_secondary"),
            ).grid(
                row=row,
                column=0,
                columnspan=2,
                sticky="w",
            )

            e = ctk.CTkEntry(
                frame,
                textvariable=var,
                width=320,
                height=40,
                placeholder_text=placeholder,
                show=show,
                font=font(13),
                fg_color=c("bg_input"),
                border_color=c("border"),
                text_color=c("text_primary"),
                corner_radius=10,
            )

            e.grid(
                row=row + 1,
                column=0,
                columnspan=2,
                pady=(4, 12),
            )

            return e

        _field(
            "Username",
            self._un_var,
            2,
            "Choose a username",
        )

        _field(
            "Email (optional)",
            self._em_var,
            4,
            "your@email.com",
        )

        _field(
            "Password",
            self._pw_var,
            6,
            "Create password",
            "•",
        )

        _field(
            "Confirm Password",
            self._pw2_var,
            8,
            "Repeat password",
            "•",
        )

        self._err_label = ctk.CTkLabel(
            frame,
            text="",
            font=font(11),
            text_color=c("danger"),
        )

        self._err_label.grid(
            row=10,
            column=0,
            columnspan=2,
            pady=(0, 6),
        )

        create_btn = ctk.CTkButton(
            frame,
            text="Create Account",
            width=320,
            height=44,
            fg_color=c("accent"),
            hover_color=c("accent_hover"),
            font=font(14, "bold"),
            corner_radius=10,
            command=self._do_signup,
        )

        create_btn.grid(
            row=11,
            column=0,
            columnspan=2,
            pady=(0, 16),
        )

        create_btn.update()

        sw = ctk.CTkFrame(
            frame,
            fg_color=c("bg_root"),
        )

        sw.grid(
            row=12,
            column=0,
            columnspan=2,
        )

        ctk.CTkLabel(
            sw,
            text="Already have an account?",
            font=font(12),
            text_color=c("text_secondary"),
        ).pack(side="left")

        signin_btn = ctk.CTkButton(
            sw,
            text="Sign In",
            font=font(12, "bold"),
            fg_color=c("bg_root"),
            hover_color="#2B2B2B",
            text_color=c("accent"),
            command=self._build_login_form,
        )

        signin_btn.pack(
            side="left",
            padx=(6, 0),
        )

        signin_btn.update()

        self.bind(
            "<Return>",
            lambda _: self._do_signup(),
        )

    # =====================================
    # ERROR
    # =====================================

    def _set_error(self, msg):

        self._err_label.configure(
            text=msg
        )

    # =====================================
    # LOGIN
    # =====================================

    def _do_login(self):

        self._set_error("")

        username = (
            self._un_var.get().strip()
        )

        password = (
            self._pw_var.get()
        )

        if not username or not password:

            self._set_error(
                "Please fill in all fields."
            )

            return

        user = UserDB.get_by_credentials(
            username,
            hash_password(password),
        )

        if not user:

            self._set_error(
                "Invalid username or password."
            )

            return

        UserDB.update_last_login(
            user["id"]
        )

        if self._remember_var.get():

            UserDB.save_session(
                username
            )

        else:

            UserDB.clear_session()

        self.on_success(user)

    # =====================================
    # SIGNUP
    # =====================================

    def _do_signup(self):

        self._set_error("")

        username = (
            self._un_var.get().strip()
        )

        email = (
            self._em_var.get().strip()
        )

        password = (
            self._pw_var.get()
        )

        confirm = (
            self._pw2_var.get()
        )

        ok, msg = validate_username(
            username
        )

        if not ok:

            self._set_error(msg)

            return

        ok, msg = validate_password(
            password
        )

        if not ok:

            self._set_error(msg)

            return

        if password != confirm:

            self._set_error(
                "Passwords do not match."
            )

            return

        created = UserDB.create(
            username,
            hash_password(password),
            email,
        )

        if not created:

            self._set_error(
                "Username already exists."
            )

            return

        Toast.show(
            self,
            "Account created successfully!",
            "success",
        )

        self.after(
            600,
            self._build_login_form,
        )

    # =====================================
    # AUTO LOGIN
    # =====================================

    def _try_auto_login(self):

        try:

            username = (
                UserDB.load_session()
            )

            if (
                username
                and self._mode == "login"
            ):

                self._un_var.set(
                    username
                )

                self._remember_var.set(
                    True
                )

        except:
            pass