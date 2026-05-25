# TaskFlow Pro — Smart To-Do Management System
### A Professional-Grade Desktop Application

---

## 🚀 Quick Start

### 1. Install Python 3.10+
Download from https://python.org/downloads

### 2. Install required packages
```bash
pip install customtkinter Pillow matplotlib
```
Or use the requirements file:
```bash
pip install -r requirements.txt
```

### 3. Run the application
```bash
cd taskflow_pro
python main.py
```

---

## 📁 Project Structure

```
taskflow_pro/
│
├── main.py            ← Entry point (Splash → Auth → Dashboard)
├── auth.py            ← Login & Signup screens
├── dashboard.py       ← Main window + sidebar navigation
├── task_manager.py    ← Task list, task cards, task form dialog
├── analytics.py       ← Charts and productivity stats
├── database.py        ← SQLite ORM (UserDB, TaskDB, CategoryDB)
├── requirements.txt
│
├── ui/
│   ├── theme.py       ← Design tokens (dark/light mode)
│   └── widgets.py     ← Reusable components (cards, badges, dialogs)
│
├── utils/
│   └── helpers.py     ← Hashing, date utils, export (TXT/CSV/JSON)
│
├── database/          ← Auto-created: taskflow.db + session.json
└── exports/           ← Auto-created: exported task files
```

---

## ✨ Features

| Feature | Details |
|---|---|
| Authentication | Login, Signup, Remember Me, Auto-login |
| Task Management | Add / Edit / Delete / Toggle complete |
| Priority Levels | High 🔴 / Medium 🟡 / Low 🟢 |
| Task Status | Pending / In Progress / Completed / Overdue |
| Categories | Work 💼 / Study 📚 / Personal 🏠 / Shopping 🛍️ / Fitness 🏋️ |
| Search & Filter | Real-time search + status + priority filters |
| Analytics | Pie charts, bar charts, productivity score |
| Export | TXT / CSV / JSON |
| Themes | Dark mode 🌙 / Light mode ☀️ |
| Overdue Alerts | Visual warning banner |
| Keyboard Shortcuts | Ctrl+1/2/3/,/N |
| Real-time Clock | Greeting + live clock on dashboard |
| Splash Screen | Branded loading screen |

---

## 🎮 Keyboard Shortcuts

| Shortcut | Action |
|---|---|
| Ctrl + 1 | Overview |
| Ctrl + 2 | Tasks |
| Ctrl + 3 | Analytics |
| Ctrl + , | Settings |
| Ctrl + N | Go to Tasks (to add new) |

---

## 🗃️ Database

SQLite database is auto-created at `database/taskflow.db` on first run.

**Tables:**
- `users` — accounts + theme preference
- `categories` — default 5 categories (seeded automatically)
- `tasks` — all task data with foreign keys

---

## 📦 Dependencies

| Package | Version | Purpose |
|---|---|---|
| customtkinter | ≥ 5.2.0 | Modern GUI framework |
| Pillow | ≥ 10.0.0 | Image support |
| matplotlib | ≥ 3.7.0 | Charts & analytics |

> **Note:** matplotlib is optional. The app runs without it — analytics panel shows an install prompt instead of charts.

---

## 🛠️ Troubleshooting

**"ModuleNotFoundError: No module named 'customtkinter'"**
```bash
pip install customtkinter
```

**Charts not showing**
```bash
pip install matplotlib
```

**App looks blurry on Windows**
Add this before running (or set in Windows display settings):
```python
import ctypes
ctypes.windll.shcore.SetProcessDpiAwareness(1)
```

---

## 🏗️ Architecture

- **OOP** — All screens are CTk classes; DB operations in static methods
- **Separation of concerns** — DB, UI, Business Logic in separate files
- **Theme system** — Single `ui/theme.py` controls all colors via tokens
- **Modular** — Each panel (Overview, Tasks, Analytics, Settings) is independent
- **Error handling** — Graceful fallbacks for missing dependencies

---

*Built with Python 3 + CustomTkinter • Portfolio-ready • MIT License*
