"""
TaskFlow Pro — Analytics Panel
SAFE Python 3.14 Compatible Version
"""

import gc
import customtkinter as ctk

from database import TaskDB
from ui.theme import c, font
from ui.widgets import StatCard

try:
    import matplotlib

    matplotlib.use("TkAgg")

    import matplotlib.pyplot as plt

    from matplotlib.backends.backend_tkagg import (
        FigureCanvasTkAgg,
    )

    HAS_MPL = True

except ImportError:

    HAS_MPL = False


class AnalyticsPanel(ctk.CTkFrame):

    def __init__(self, master, user: dict, **kwargs):

        kwargs.setdefault(
            "fg_color",
            c("bg_root"),
        )

        super().__init__(
            master,
            **kwargs,
        )

        self.user = user

        self._chart_canvas = None

        self._build()

        self.refresh()

    # ==========================================
    # BUILD UI
    # ==========================================

    def _build(self):

        # Header
        hdr = ctk.CTkFrame(
            self,
            fg_color=c("bg_root"),
        )

        hdr.pack(
            fill="x",
            padx=20,
            pady=(16, 8),
        )

        ctk.CTkLabel(
            hdr,
            text="Analytics & Insights",
            font=font(22, "bold"),
            text_color=c("text_primary"),
        ).pack(side="left")

        refresh_btn = ctk.CTkButton(
            hdr,
            text="Refresh",
            width=110,
            height=36,
            fg_color=c("bg_card"),
            hover_color=c("bg_card_hover"),
            text_color=c("text_secondary"),
            corner_radius=8,
            command=self.refresh,
        )

        refresh_btn.pack(side="right")

        # Stats Frame
        self._stats_frame = ctk.CTkFrame(
            self,
            fg_color=c("bg_root"),
        )

        self._stats_frame.pack(
            fill="x",
            padx=20,
            pady=(0, 16),
        )

        # Chart Frame
        self._chart_frame = ctk.CTkFrame(
            self,
            fg_color=c("bg_root"),
        )

        self._chart_frame.pack(
            fill="both",
            expand=True,
            padx=20,
            pady=(0, 16),
        )

    # ==========================================
    # REFRESH
    # ==========================================

    def refresh(self):

        self._redraw_stats()

        self._redraw_charts()

    # ==========================================
    # STATS
    # ==========================================

    def _redraw_stats(self):

        for w in self._stats_frame.winfo_children():

            try:
                w.destroy()

            except:
                pass

        stats = TaskDB.get_stats(
            self.user["id"]
        )

        cards = [

            (
                "Total Tasks",
                stats["Total"],
                c("accent"),
                "All time",
            ),

            (
                "Completed",
                stats["Completed"],
                c("success"),
                f"{stats['Productivity']}% productivity",
            ),

            (
                "In Progress",
                stats["In Progress"],
                c("info"),
                "Active tasks",
            ),

            (
                "Overdue",
                stats["Overdue"],
                c("danger"),
                "Needs attention",
            ),
        ]

        for col, (
            label,
            value,
            color,
            subtitle,
        ) in enumerate(cards):

            card = StatCard(
                self._stats_frame,
                label,
                value,
                accent=color,
                subtitle=subtitle,
            )

            card.grid(
                row=0,
                column=col,
                padx=6,
                pady=4,
                sticky="nsew",
            )

        for i in range(4):

            self._stats_frame.columnconfigure(
                i,
                weight=1,
            )

    # ==========================================
    # CHARTS
    # ==========================================

    def _redraw_charts(self):

        gc.collect()

        # Safe cleanup
        for w in self._chart_frame.winfo_children():

            try:
                w.destroy()

            except:
                pass

        # Safe chart destroy
        try:

            if self._chart_canvas:

                self._chart_canvas.get_tk_widget().destroy()

                self._chart_canvas = None

        except:
            pass

        # matplotlib missing
        if not HAS_MPL:

            ctk.CTkLabel(
                self._chart_frame,
                text="Install matplotlib:\npip install matplotlib",
                font=font(13),
                text_color=c("text_secondary"),
            ).pack(pady=40)

            return

        stats = TaskDB.get_stats(
            self.user["id"]
        )

        cat_data = TaskDB.get_category_breakdown(
            self.user["id"]
        )

        # Theme
        is_dark = (
            c("bg_root") == "#0F1117"
        )

        bg_fig = (
            "#1E2433"
            if is_dark
            else "#FFFFFF"
        )

        fg_txt = (
            "#F1F5F9"
            if is_dark
            else "#0F172A"
        )

        grid_c = (
            "#2D3748"
            if is_dark
            else "#E2E8F0"
        )

        # Figure
        fig, axes = plt.subplots(
            1,
            2,
            figsize=(10, 4),
        )

        fig.patch.set_facecolor(bg_fig)

        # ==================================
        # PIE CHART
        # ==================================

        ax1 = axes[0]

        ax1.set_facecolor(bg_fig)

        status_labels = [
            "Pending",
            "In Progress",
            "Completed",
        ]

        status_values = [

            stats.get("Pending", 0),

            stats.get("In Progress", 0),

            stats.get("Completed", 0),
        ]

        status_colors = [
            "#94A3B8",
            "#3B82F6",
            "#22C55E",
        ]

        non_zero = [

            (l, v, co)

            for l, v, co in zip(
                status_labels,
                status_values,
                status_colors,
            )

            if v > 0
        ]

        if non_zero:

            labels, values, colors = zip(
                *non_zero
            )

            wedges, texts, autotexts = ax1.pie(

                values,

                labels=labels,

                colors=colors,

                autopct="%1.0f%%",

                startangle=140,

                textprops={
                    "color": fg_txt,
                    "fontsize": 9,
                },

                wedgeprops={
                    "linewidth": 2,
                    "edgecolor": bg_fig,
                },
            )

            for at in autotexts:

                at.set_color(fg_txt)

        else:

            ax1.text(
                0.5,
                0.5,
                "No tasks yet",
                ha="center",
                va="center",
                color=fg_txt,
                fontsize=12,
            )

        ax1.set_title(
            "Task Status",
            color=fg_txt,
            fontsize=12,
            pad=10,
        )

        # ==================================
        # BAR CHART
        # ==================================

        ax2 = axes[1]

        ax2.set_facecolor(bg_fig)

        for spine in ax2.spines.values():

            spine.set_edgecolor(grid_c)

        ax2.tick_params(colors=fg_txt)

        if cat_data:

            names = [
                d["name"]
                for d in cat_data
            ]

            counts = [
                d["count"]
                for d in cat_data
            ]

            colors = [

                d.get(
                    "color",
                    "#4A9EFF",
                )

                for d in cat_data
            ]

            bars = ax2.bar(
                names,
                counts,
                color=colors,
                edgecolor=bg_fig,
                linewidth=1.5,
            )

            ax2.set_xlabel(
                "Category",
                color=fg_txt,
                fontsize=9,
            )

            ax2.set_ylabel(
                "Tasks",
                color=fg_txt,
                fontsize=9,
            )

            ax2.tick_params(
                axis="x",
                colors=fg_txt,
                labelsize=8,
            )

            ax2.tick_params(
                axis="y",
                colors=fg_txt,
                labelsize=8,
            )

            for bar, count in zip(
                bars,
                counts,
            ):

                ax2.text(

                    bar.get_x()
                    + bar.get_width() / 2,

                    bar.get_height() + 0.1,

                    str(count),

                    ha="center",

                    va="bottom",

                    color=fg_txt,

                    fontsize=9,
                )

        else:

            ax2.text(
                0.5,
                0.5,
                "No categories yet",
                ha="center",
                va="center",
                color=fg_txt,
                fontsize=11,
            )

        ax2.set_title(
            "Tasks by Category",
            color=fg_txt,
            fontsize=12,
            pad=10,
        )

        fig.tight_layout(pad=2.5)

        # ==================================
        # SAFE CANVAS
        # ==================================

        try:

            canvas = FigureCanvasTkAgg(
                fig,
                master=self._chart_frame,
            )

            canvas.draw_idle()

            canvas_widget = (
                canvas.get_tk_widget()
            )

            canvas_widget.pack(
                fill="both",
                expand=True,
            )

            self._chart_canvas = canvas

        except Exception as e:

            ctk.CTkLabel(
                self._chart_frame,
                text=f"Chart Error:\n{e}",
                text_color="red",
            ).pack(pady=20)

            return

        # ==================================
        # PRODUCTIVITY BAR
        # ==================================

        prod_frame = ctk.CTkFrame(
            self._chart_frame,
            fg_color="#1E2433",
        )

        prod_frame.pack(
            fill="x",
            pady=(12, 0),
        )

        ctk.CTkLabel(
            prod_frame,
            text=f"🏆 Productivity Score: {stats['Productivity']}%",
            font=font(13, "bold"),
            text_color=c("text_primary"),
        ).pack(
            anchor="w",
            padx=10,
            pady=(10, 6),
        )

        progress = ctk.CTkProgressBar(
            prod_frame,
            width=400,
            height=14,
            corner_radius=8,
            fg_color=c("border"),
            progress_color=c("success"),
        )

        progress.pack(
            anchor="w",
            padx=10,
            pady=(0, 10),
        )

        progress.set(
            stats["Productivity"] / 100
        )