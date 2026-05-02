# SpendSmart — TheBudgeteers
## Members: Nathaniel Miller, Sakhi Hussain, Durgesh Yadav, Sterling Jerry
## CSC 317 H002

A desktop personal finance app built with Python and Kivy. Track transactions, set monthly budgets, manage spending categories, monitor bills, and view spending analytics — all stored locally with no account required.

---

## Technology Stack

| Technology | Version |
|---|---|
| Python | 3.12.5 |
| Kivy | 2.3.1 |
| SQLite | built into Python (no install needed) |

> **Platform:** Windows 10/11 (64-bit). The Kivy Windows deps (`angle`, `glew`, `sdl2`) are Windows-only packages.

---

## Prerequisites

- **Python 3.12.x** — download from [python.org](https://www.python.org/downloads/). During installation, check **"Add Python to PATH"**.
- **Git** — to clone the repository.
- A terminal such as Command Prompt, PowerShell, or Git Bash.

---

## Setup

Open a terminal in this folder, then follow the steps below.

### 1. Create a virtual environment

```bash
python -m venv venv
```

### 2. Activate the virtual environment

**Command Prompt:**
```cmd
venv\Scripts\activate
```

**PowerShell:**
```powershell
venv\Scripts\Activate.ps1
```

**Git Bash:**
```bash
source venv/Scripts/activate
```

Your prompt should now show `(venv)` at the start.

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

This installs Kivy and all required Windows graphics drivers. It may take a minute.

### 4. Run the app

```bash
python app.py
```

The app window will open at 1920x1160 and scale down to fit your screen automatically.

---

## First Launch

On first launch the app creates a fresh SQLite database at:

```
resources/data/spendsmart.db
```

This file is ignored by git — each machine keeps its own local data.

The app starts with no transactions or categories. To populate it with sample data (4 categories + 3 weeks of transactions + a $30,000 starting balance), open a Python shell with the venv active and run:

```python
from database import Database
db = Database("resources/data/spendsmart.db")
db.seed_data()
```

`seed_data()` is a no-op if transactions already exist, so it's safe to call more than once.

---

## Project Structure

```
TheBudgeteers-SpendSmart/
├── app.py                    # entry point, app class, global scaling
├── app_shell.py              # root screen manager shell
├── app_shell.kv              # navigation bar and shell layout
├── database.py               # all SQLite logic (Database class)
├── requirements.txt          # pip dependencies
├── resources/
│   ├── styles.kv             # shared KV styles
│   └── data/                 # created at runtime, holds spendsmart.db
└── screens/
    ├── dashboard_screen.py/kv    # home screen with stats and bills
    ├── transactions_screen.py/kv # full transaction list with filters
    ├── budget_screen.py/kv       # monthly budget and category breakdown
    ├── budget_edit_screen.py/kv  # edit monthly budget and categories
    ├── goals_screen.py/kv        # savings goals
    ├── settings_screen.py/kv     # theme, font size, notifications
    └── widgets/                  # reusable popups (add/edit transaction, etc.)
```

---

## Common Issues

**`ModuleNotFoundError: No module named 'kivy'`**
The virtual environment is not active. Run the activate command in step 3 first.

**`venv\Scripts\Activate.ps1 cannot be loaded because running scripts is disabled`**
Run this once in PowerShell as Administrator, then try again:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

**Black window or OpenGL error on launch**
Make sure the `kivy-deps.angle`, `kivy-deps.glew`, and `kivy_deps.sdl2` packages installed correctly. Try reinstalling:
```bash
pip install --force-reinstall kivy-deps.angle kivy-deps.glew kivy_deps.sdl2
```

**App opens but is very small**
The app is designed at 1920x1160 and scales to fit. If it appears tiny, check that your display scaling in Windows Settings is not set above 150%.
