"""
TaskFlow Pro — Task Manager
Task creation/edit dialog + task list panel.
"""

import customtkinter as ctk
from database import TaskDB, CategoryDB
from ui.theme import c, font
from ui.widgets import PillBadge, ConfirmDialog, Toast, SearchBar, IconButton
from utils.helpers import (PRIORITY_COLORS, STATUS_COLORS,
                           format_date, is_overdue, days_until_due,
                           export_to_txt, export_to_csv, export_to_json)
import tkinter.messagebox as mb
import os



#  TASK FORM DIALOG


class TaskFormDialog(ctk.CTkToplevel):
    """Create or edit a task. Closes itself; caller checks .saved."""

    def __init__(self, master, user_id: int, task: dict = None):
        super().__init__(master)
        self.user_id = user_id
        self.task    = task          # None = new task
        self.saved   = False
        self._categories = CategoryDB.get_all()

        self.title("Edit Task" if task else "New Task")
        self.geometry("500x600")
        self.resizable(False, False)
        self.configure(fg_color=c("bg_modal"))
        self.grab_set()
        self._center()
        self._build()

    def _center(self):
        self.update_idletasks()
        x = (self.winfo_screenwidth()  - 500) // 2
        y = (self.winfo_screenheight() - 600) // 2
        self.geometry(f"500x600+{x}+{y}")

    def _build(self):
        # Header
        header = ctk.CTkFrame(self, fg_color=c("accent"), corner_radius=0, height=54)
        header.pack(fill="x")
        header.pack_propagate(False)
        ctk.CTkLabel(
            header,
            text=("✏️  Edit Task" if self.task else "✨  New Task"),
            font=font(16, "bold"), text_color="#FFFFFF",
        ).pack(side="left", padx=20, pady=14)

        # Scrollable body
        body = ctk.CTkScrollableFrame(self, fg_color=c("bg_modal"))
        body.pack(fill="both", expand=True, padx=20, pady=12)

        def _label(text):
            ctk.CTkLabel(body, text=text, font=font(11, "bold"),
                         text_color=c("text_secondary")).pack(anchor="w", pady=(10, 2))

        # Title
        _label("Task Title *")
        self._title_var = ctk.StringVar(value=self.task["title"] if self.task else "")
        ctk.CTkEntry(
            body, textvariable=self._title_var, height=40,
            placeholder_text="What needs to be done?", font=font(13),
            fg_color=c("bg_input"), border_color=c("border"),
            text_color=c("text_primary"), corner_radius=8,
        ).pack(fill="x")

        # Description
        _label("Description")
        self._desc_box = ctk.CTkTextbox(
            body, height=80, font=font(12),
            fg_color=c("bg_input"), border_color=c("border"),
            text_color=c("text_primary"), corner_radius=8,
        )
        self._desc_box.pack(fill="x")
        if self.task and self.task.get("description"):
            self._desc_box.insert("1.0", self.task["description"])

        # Category + Priority row
        row = ctk.CTkFrame(body, fg_color="transparent")
        row.pack(fill="x", pady=(10, 0))

        left_col = ctk.CTkFrame(row, fg_color="transparent")
        left_col.pack(side="left", fill="x", expand=True, padx=(0, 8))
        right_col = ctk.CTkFrame(row, fg_color="transparent")
        right_col.pack(side="left", fill="x", expand=True)

        _label_in = lambda parent, text: ctk.CTkLabel(
            parent, text=text, font=font(11, "bold"),
            text_color=c("text_secondary")
        ).pack(anchor="w", pady=(10, 2))

        # Category
        _label_in(left_col, "Category")
        cat_names  = [cat["name"] for cat in self._categories]
        default_cat = self.task["category_name"] if (self.task and self.task.get("category_name")) else (cat_names[0] if cat_names else "")
        self._cat_var = ctk.StringVar(value=default_cat)
        ctk.CTkComboBox(
            left_col, variable=self._cat_var, values=cat_names,
            font=font(12), fg_color=c("bg_input"),
            button_color=c("accent"), dropdown_fg_color=c("bg_card"),
            text_color=c("text_primary"), corner_radius=8, height=38,
        ).pack(fill="x")

        # Priority
        _label_in(right_col, "Priority")
        self._pri_var = ctk.StringVar(value=self.task["priority"] if self.task else "Medium")
        ctk.CTkComboBox(
            right_col, variable=self._pri_var, values=["High", "Medium", "Low"],
            font=font(12), fg_color=c("bg_input"),
            button_color=c("accent"), dropdown_fg_color=c("bg_card"),
            text_color=c("text_primary"), corner_radius=8, height=38,
        ).pack(fill="x")

        # Status + Due Date row
        row2 = ctk.CTkFrame(body, fg_color="transparent")
        row2.pack(fill="x", pady=(0, 0))

        left2  = ctk.CTkFrame(row2, fg_color="transparent")
        left2.pack(side="left", fill="x", expand=True, padx=(0, 8))
        right2 = ctk.CTkFrame(row2, fg_color="transparent")
        right2.pack(side="left", fill="x", expand=True)

        _label_in(left2, "Status")
        self._status_var = ctk.StringVar(
            value=self.task["status"] if self.task else "Pending"
        )
        ctk.CTkComboBox(
            left2, variable=self._status_var,
            values=["Pending", "In Progress", "Completed"],
            font=font(12), fg_color=c("bg_input"),
            button_color=c("accent"), dropdown_fg_color=c("bg_card"),
            text_color=c("text_primary"), corner_radius=8, height=38,
        ).pack(fill="x")

        _label_in(right2, "Due Date  (YYYY-MM-DD)")
        self._due_var = ctk.StringVar(
            value=self.task["due_date"] if (self.task and self.task.get("due_date")) else ""
        )
        ctk.CTkEntry(
            right2, textvariable=self._due_var, height=38,
            placeholder_text="2025-12-31", font=font(12),
            fg_color=c("bg_input"), border_color=c("border"),
            text_color=c("text_primary"), corner_radius=8,
        ).pack(fill="x")

        # Error
        self._err = ctk.CTkLabel(body, text="", font=font(11), text_color=c("danger"))
        self._err.pack(anchor="w", pady=(8, 0))

        # Footer buttons
        footer = ctk.CTkFrame(self, fg_color=c("bg_card"),
                              corner_radius=0, height=60)
        footer.pack(fill="x", side="bottom")
        footer.pack_propagate(False)

        ctk.CTkButton(
            footer, text="Cancel", width=120, height=38,
            fg_color=c("bg_card"), hover_color=c("bg_card_hover"),
            text_color=c("text_secondary"), corner_radius=8,
            command=self.destroy,
        ).pack(side="left", padx=16, pady=11)

        ctk.CTkButton(
            footer, text="Save Task", width=140, height=38,
            fg_color=c("accent"), hover_color=c("accent_hover"),
            font=font(13, "bold"), corner_radius=8,
            command=self._save,
        ).pack(side="right", padx=16, pady=11)

    def _save(self):
        self._err.configure(text="")
        title = self._title_var.get().strip()
        if not title:
            self._err.configure(text="Task title is required."); return

        # Resolve category id
        cat_name = self._cat_var.get()
        cat_id   = next((cat["id"] for cat in self._categories
                         if cat["name"] == cat_name), None)

        desc    = self._desc_box.get("1.0", "end").strip()
        due     = self._due_var.get().strip() or None
        priority= self._pri_var.get()
        status  = self._status_var.get()

        if self.task:
            TaskDB.update(
                self.task["id"], title=title, description=desc,
                category_id=cat_id, priority=priority,
                status=status, due_date=due,
            )
        else:
            TaskDB.create(self.user_id, title, desc, cat_id, priority, status, due)

        self.saved = True
        self.destroy()



#  TASK CARD  (one row in the list)


class TaskCard(ctk.CTkFrame):
    """A single task row with priority indicator, badges, and action buttons."""

    def __init__(self, master, task: dict, on_edit, on_delete, on_toggle, **kwargs):
        kwargs.setdefault("fg_color", c("bg_card"))
        kwargs.setdefault("corner_radius", 12)
        super().__init__(master, **kwargs)
        self.configure(border_width=1, border_color=c("border"))
        self.task = task
        self._build(on_edit, on_delete, on_toggle)
        self._bind_hover()

    def _build(self, on_edit, on_delete, on_toggle):
        task = self.task
        overdue = is_overdue(task.get("due_date"), task["status"])
        effective_status = "Overdue" if overdue else task["status"]

        # Priority stripe
        pri_color = PRIORITY_COLORS.get(task["priority"], c("accent"))
        ctk.CTkFrame(self, width=4, fg_color=pri_color,
                     corner_radius=2).pack(side="left", fill="y", padx=(0, 0))

        # Checkbox toggle
        is_done = task["status"] == "Completed"
        check_icon = "✅" if is_done else "⬜"
        ctk.CTkButton(
            self, text=check_icon, width=36, height=36,
            fg_color="transparent", hover_color=c("bg_card_hover"),
            font=font(18), command=lambda: on_toggle(task),
        ).pack(side="left", padx=(8, 4))

        # Main content
        mid = ctk.CTkFrame(self, fg_color="transparent")
        mid.pack(side="left", fill="both", expand=True, pady=10)

        title_color = c("text_muted") if is_done else c("text_primary")
        title_label = ctk.CTkLabel(
            mid, text=task["title"], font=font(13, "bold"),
            text_color=title_color, anchor="w",
        )
        title_label.pack(anchor="w")

        # Sub-row: category • due date
        sub = ctk.CTkFrame(mid, fg_color="transparent")
        sub.pack(anchor="w", pady=(2, 0))

        if task.get("category_name"):
            ctk.CTkLabel(
                sub, text=f"{task.get('category_icon','📁')} {task['category_name']}",
                font=font(10), text_color=c("text_muted"),
            ).pack(side="left", padx=(0, 10))

        due_days = days_until_due(task.get("due_date"))
        if due_days is not None:
            due_color = c("danger") if overdue else (c("warning") if due_days <= 2 else c("text_muted"))
            due_str = format_date(task["due_date"])
            ctk.CTkLabel(sub, text=f"📅 {due_str}", font=font(10),
                         text_color=due_color).pack(side="left")

        # Right badges + actions
        right = ctk.CTkFrame(self, fg_color="transparent")
        right.pack(side="right", padx=10)

        PillBadge(right, effective_status,
                  STATUS_COLORS.get(effective_status, c("accent"))).pack(pady=(0, 4))
        PillBadge(right, task["priority"],
                  pri_color).pack()

        # Action icons
        actions = ctk.CTkFrame(self, fg_color="transparent")
        actions.pack(side="right", padx=4)

        IconButton(actions, "✏️", command=lambda: on_edit(task), size=30).pack(pady=2)
        IconButton(actions, "🗑️", command=lambda: on_delete(task), size=30).pack(pady=2)

    def _bind_hover(self):
        def enter(_): self.configure(fg_color=c("bg_card_hover"))
        def leave(_): self.configure(fg_color=c("bg_card"))
        self.bind("<Enter>", enter)
        self.bind("<Leave>", leave)


#  TASK LIST PANEL


class TaskListPanel(ctk.CTkFrame):
    """Full task management panel: toolbar, filters, scrollable list."""

    def __init__(self, master, user: dict, **kwargs):
        kwargs.setdefault("fg_color", c("bg_root"))
        super().__init__(master, **kwargs)
        self.user = user
        self._filter_status   = "All"
        self._filter_priority = "All"
        self._filter_category = None
        self._search_query    = ""
        self._build()
        self.refresh()

    #  Build UI

    def _build(self):
        # Top toolbar
        toolbar = ctk.CTkFrame(self, fg_color="transparent")
        toolbar.pack(fill="x", padx=20, pady=(16, 8))

        ctk.CTkLabel(toolbar, text="My Tasks",
                     font=font(22, "bold"), text_color=c("text_primary")).pack(side="left")

        # Add task button
        ctk.CTkButton(
            toolbar, text="+ New Task", width=130, height=38,
            fg_color=c("accent"), hover_color=c("accent_hover"),
            font=font(13, "bold"), corner_radius=10,
            command=self._open_new_task,
        ).pack(side="right")

        # Export menu
        exp_btn = ctk.CTkOptionMenu(
            toolbar, values=["Export…", "Export TXT", "Export CSV", "Export JSON"],
            width=130, height=38, fg_color=c("bg_card"),
            button_color=c("bg_card"), button_hover_color=c("bg_card_hover"),
            dropdown_fg_color=c("bg_card"), text_color=c("text_secondary"),
            font=font(12), corner_radius=10,
            command=self._handle_export,
        )
        exp_btn.pack(side="right", padx=8)

        # Search + Filters row
        filter_row = ctk.CTkFrame(self, fg_color="transparent")
        filter_row.pack(fill="x", padx=20, pady=(0, 10))

        SearchBar(
            filter_row, on_change=self._on_search, width=260,
        ).pack(side="left", padx=(0, 10))

        # Status filter
        ctk.CTkComboBox(
            filter_row,
            values=["All", "Pending", "In Progress", "Completed"],
            command=self._on_status_filter,
            width=150, height=36, font=font(12),
            fg_color=c("bg_input"), button_color=c("accent"),
            dropdown_fg_color=c("bg_card"), text_color=c("text_primary"),
            corner_radius=8,
        ).pack(side="left", padx=(0, 8))

        # Priority filter
        ctk.CTkComboBox(
            filter_row,
            values=["All", "High", "Medium", "Low"],
            command=self._on_priority_filter,
            width=130, height=36, font=font(12),
            fg_color=c("bg_input"), button_color=c("accent"),
            dropdown_fg_color=c("bg_card"), text_color=c("text_primary"),
            corner_radius=8,
        ).pack(side="left")

        # Task count label
        self._count_label = ctk.CTkLabel(self, text="", font=font(11),
                                          text_color=c("text_muted"))
        self._count_label.pack(anchor="w", padx=22, pady=(0, 6))

        # Scrollable task list
        self._scroll = ctk.CTkScrollableFrame(
            self, fg_color="transparent",
        )
        self._scroll.pack(fill="both", expand=True, padx=16, pady=(0, 10))

    #  Callbacks 

    def _on_search(self, query: str):
        self._search_query = query
        self.refresh()

    def _on_status_filter(self, val: str):
        self._filter_status = val
        self.refresh()

    def _on_priority_filter(self, val: str):
        self._filter_priority = val
        self.refresh()

    def _open_new_task(self):
        dlg = TaskFormDialog(self, self.user["id"])
        self.wait_window(dlg)
        if dlg.saved:
            Toast.show(self.winfo_toplevel(), "Task created!", "success")
            self.refresh()
            self._notify_dashboard()

    def _open_edit_task(self, task: dict):
        dlg = TaskFormDialog(self, self.user["id"], task=task)
        self.wait_window(dlg)
        if dlg.saved:
            Toast.show(self.winfo_toplevel(), "Task updated!", "success")
            self.refresh()
            self._notify_dashboard()

    def _delete_task(self, task: dict):
        dlg = ConfirmDialog(self, "Delete Task",
                            f"Delete \"{task['title']}\"? This cannot be undone.")
        if dlg.confirmed:
            TaskDB.delete(task["id"])
            Toast.show(self.winfo_toplevel(), "Task deleted.", "warning")
            self.refresh()
            self._notify_dashboard()

    def _toggle_task(self, task: dict):
        new_status = "Pending" if task["status"] == "Completed" else "Completed"
        TaskDB.update(task["id"], status=new_status)
        self.refresh()
        self._notify_dashboard()

    def _handle_export(self, choice: str):
        tasks = TaskDB.get_all(self.user["id"])
        if not tasks:
            Toast.show(self.winfo_toplevel(), "No tasks to export.", "warning"); return
        if choice == "Export TXT":
            path = export_to_txt(tasks)
        elif choice == "Export CSV":
            path = export_to_csv(tasks)
        elif choice == "Export JSON":
            path = export_to_json(tasks)
        else:
            return
        Toast.show(self.winfo_toplevel(), f"Saved: {os.path.basename(path)}", "success")

    def _notify_dashboard(self):
        """Signal parent to refresh stats if it has a refresh_stats method."""
        try:
            self.master.master.refresh_stats()
        except Exception:
            pass

    #  Refresh ]

    def refresh(self):
        for w in self._scroll.winfo_children():
            w.destroy()

        tasks = TaskDB.get_all(
            self.user["id"],
            status_filter=self._filter_status,
            priority_filter=self._filter_priority,
            search_query=self._search_query if self._search_query else None,
        )

        self._count_label.configure(text=f"{len(tasks)} task(s) found")

        if not tasks:
            empty = ctk.CTkFrame(self._scroll, fg_color="transparent")
            empty.pack(expand=True, pady=60)
            ctk.CTkLabel(empty, text="🎉", font=font(48)).pack()
            ctk.CTkLabel(empty, text="No tasks here!", font=font(16, "bold"),
                         text_color=c("text_primary")).pack()
            ctk.CTkLabel(empty, text="Click '+ New Task' to get started.",
                         font=font(12), text_color=c("text_muted")).pack()
            return

        for task in tasks:
            card = TaskCard(
                self._scroll, task,
                on_edit=self._open_edit_task,
                on_delete=self._delete_task,
                on_toggle=self._toggle_task,
            )
            card.pack(fill="x", pady=4)
