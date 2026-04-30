import sqlite3 as sql
from datetime import datetime, timedelta

class Database:
    def __init__(self, db_path):
        self.connection = sql.connect(db_path)
        self.cursor = self.connection.cursor()
        self.create_tables()
        self._migrate_remove_category_unique()
        self.fill_setstat()
    
    def create_tables(self):
        # transactions table: ID | DATE (YYYY-MM-DD) | NAME | AMOUNT (can be negative)
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT,
            name TEXT,
            amount REAL,
            category_id INTEGER,
            FOREIGN KEY (category_id) REFERENCES categories (id)
        )''')

        # upcoming bills: ID | DATE (YYYY-MM-DD) | NAME | AMOUNT
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS bills (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT,
            name TEXT,
            amount REAL
        )''')

        # categories: ID | NAME | PERCENT (of monthly budget)
        # first entry is always None category, second is always Income. neither to be shown on budget page
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            percent REAL
        )''')
        self.cursor.execute("INSERT OR IGNORE INTO categories (id, name, percent) VALUES (1, ?, ?)", ('None', 0.0))
        self.cursor.execute("INSERT OR IGNORE INTO categories (id, name, percent) VALUES (2, ?, ?)", ('Income', 0.0))
        
        self.connection.commit()

        # settings and monthly budget: KEY (item name) | VALUE
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS setstat (
            key TEXT PRIMARY KEY,
            value TEXT
        )''')

        # goals: ID | NAME | AMOUNT | SAVED | DATE (YYYY-MM-DD)
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS goals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            amount REAL,
            saved REAL,
            date TEXT
        )''')

        self.connection.commit()
    
    # initializes default settings / monthly budget
    def fill_setstat(self):
        default_settings = [
        ('budget', '0'),
        ('theme', 'light'),
        ('font', 'medium'),
        ('alerts', 'True'),
        ('reminders', 'False')
        ]

        query = "INSERT OR IGNORE INTO setstat (key, value) VALUES (?, ?)"

        self.cursor.executemany(query, default_settings)
        self.connection.commit()
    
    def _migrate_remove_category_unique(self):
        self.cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='categories'")
        row = self.cursor.fetchone()
        if row and 'UNIQUE' in row[0]:
            self.cursor.execute('''CREATE TABLE categories_new (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                percent REAL
            )''')
            self.cursor.execute("INSERT INTO categories_new SELECT * FROM categories")
            self.cursor.execute("DROP TABLE categories")
            self.cursor.execute("ALTER TABLE categories_new RENAME TO categories")
            self.connection.commit()
        self.cursor.execute("DELETE FROM categories WHERE name IN ('None', 'Income') AND id > 2")
        self.connection.commit()

    '''**DATE CONVERTERS**'''
    # makes this safely callable from anywhere
    @staticmethod
    def date_to_db(ui_date):
        # converts MM/DD/YYYY to YYYY-MM-DD
        try:
            m, d, y = ui_date.split('/')
            return f"{y}-{m}-{d}"
        except ValueError:
            return ui_date
    # makes this safely callable from anywhere
    @staticmethod
    def date_to_ui(db_date):
        # converts YYYY-MM-DD to MM/DD/YYYY
        try:
            y, m, d = db_date.split('-')
            return f"{m}/{d}/{y}"
        except ValueError:
            return db_date


    '''**INDIVIDUAL GETTERS**'''
    # returns string (e.g., "dark") or None
    # works for budget too. search by name (budget, theme, font, alerts, reminders)
    def get_setting(self, key_name):
        self.cursor.execute("SELECT value FROM setstat WHERE key = ?", (key_name,))
        result = self.cursor.fetchone()
        # returns just the value string or None if not found
        return result[0] if result else None

    def set_setting(self, key_name, value):
        self.cursor.execute("UPDATE setstat SET value = ? WHERE key = ?", (value, key_name))
        self.connection.commit()

    # returns row object. behaves like a dictionary (you can use keys) and a tuple (you can use index numbers)
    # -> {'id': int, 'name': str, 'percent': float}
    # search by ID or name
    def get_cat(self, identifier):
        if isinstance(identifier, int):
            self.cursor.execute("SELECT * FROM categories WHERE id = ?", (identifier,))
        else:
            self.cursor.execute("SELECT * FROM categories WHERE name = ?", (identifier,))
        return self.cursor.fetchone()

    # returns row object. behaves like a dictionary (you can use keys) and a tuple (you can use index numbers)
    # -> {'id': int, 'date': str, 'name': str, 'amount': float, 'category_id': int}
    # search by ID
    def get_transaction(self, trans_id):
        self.cursor.execute("SELECT * FROM transactions WHERE id = ?", (trans_id,))
        return self.cursor.fetchone()

    # returns row object. behaves like a dictionary (you can use keys) and a tuple (you can use index numbers)
    # -> {'id': int, 'date': str, 'name': str, 'amount': float}
    def get_bill(self, bill_id):
        self.cursor.execute("SELECT * FROM bills WHERE id = ?", (bill_id,))
        return self.cursor.fetchone()

    # returns row object. behaves like a dictionary (you can use keys) and a tuple (you can use index numbers)
    # -> {'id': int, 'name': str, 'amount': float, 'saved': float, 'date': str}
    # search by ID or name
    def get_goal(self, identifier):
        if isinstance(identifier, int):
            self.cursor.execute("SELECT * FROM goals WHERE id = ?", (identifier,))
        else:
            self.cursor.execute("SELECT * FROM goals WHERE name = ?", (identifier,))
        return self.cursor.fetchone()
    
    '''**MASS GETTERS'''
    # returns a list of row objects. access via loop: for row in result: print(row['name']). if table is empty, returns an empty list [].
    # row structure: {'id': int, 'date': str, 'name': str, 'amount': float, 'category_id': int}
    def get_all_transactions(self):
        self.cursor.execute("SELECT * FROM transactions ORDER BY date DESC")
        return self.cursor.fetchall()

    # returns a list of row objects. access via loop: for row in result: print(row['name']). if table is empty, returns an empty list [].
    # row structure: {'id': int, 'name': str, 'percent': float}
    def get_all_cats(self):
        self.cursor.execute("SELECT * FROM categories ORDER BY id")
        return self.cursor.fetchall()

    # returns a list of row objects. access via loop: for row in result: print(row['name']). if table is empty, returns an empty list [].
    # fow structure: {'id': int, 'name': str, 'amount': float, 'saved': float, 'date': str}
    def get_all_goals(self):
        self.cursor.execute("SELECT * FROM goals")
        return self.cursor.fetchall()

    # returns a list of row objects. access via loop: for row in result: print(row['name']). if table is empty, returns an empty list [].
    # row structure: {'id': int, 'date': str, 'name': str, 'amount': float}
    def get_all_bills(self):
        self.cursor.execute("SELECT * FROM bills ORDER BY date ASC")
        return self.cursor.fetchall()

    '''**MATH GETTERS**'''
    # takes cat name, returns float of amount remaining in the cat
    def get_cat_total(self, cat_name):
        budget = float(self.get_setting('budget') or 0)
        cat = self.get_cat(cat_name)
        if not cat: return 0
        
        raw_cat_value = budget * (cat[2] / 100)
        
        # sum transactions for this category
        query = '''
            SELECT COALESCE(SUM(t.amount), 0) 
            FROM transactions t
            JOIN categories c ON t.category_id = c.id
            WHERE c.name = ?
        '''
        self.cursor.execute(query, (cat_name,))
        trans_sum = self.cursor.fetchone()[0]
        
        return raw_cat_value + trans_sum
    
    # returns float of sum of cat totals
    def get_curr_budget(self):
        categories = self.get_all_cats()
        total = 0
        for cat in categories:
            total += self.get_cat_total(cat['name'])
        return total
    
    # returns float of sum of all transactions
    def get_big_total(self):
        self.cursor.execute("SELECT COALESCE(SUM(amount), 0) FROM transactions")
        return self.cursor.fetchone()[0]

    # helper function for month sums
    # returns either sum of income or sum of not income (expenses) over last 30 days
    def get_month_sum(self, income=True):
        thirty_days_ago = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
        if income:
            self.cursor.execute(
                "SELECT COALESCE(SUM(amount), 0) FROM transactions WHERE amount > 0 AND date >= ?",
                (thirty_days_ago,)
            )
        else:
            self.cursor.execute(
                "SELECT COALESCE(ABS(SUM(amount)), 0) FROM transactions WHERE amount < 0 AND date >= ?",
                (thirty_days_ago,)
            )
        return self.cursor.fetchone()[0]

    # returns float of sum of income transactions for the last 30 days
    def get_income(self):
        return self.get_month_sum(income=True)

    # returns float of sum of negative transactions for the last 30 days
    def get_expenses(self):
        return self.get_month_sum(income=False)

    # helper function for week sums
    # returns start and end of week with offset 0 being current week and offset 1 being last week 
    def get_week(self, week_offset):
        today = datetime.now()
        start_of_current_week = today - timedelta(days=today.weekday())
        
        target_week_start = start_of_current_week - timedelta(weeks=week_offset)
        target_week_end = target_week_start + timedelta(days=6)
        
        return target_week_start, target_week_end

    # get the week's expenses
    def get_week_expenses(self, week_offset):
        start, end = self.get_week(week_offset)
        start_str = start.strftime("%Y-%m-%d")
        end_str = end.strftime("%Y-%m-%d")
        self.cursor.execute(
            "SELECT COALESCE(SUM(ABS(amount)), 0) FROM transactions WHERE amount < 0 AND date >= ? AND date <= ?",
            (start_str, end_str)
        )
        return self.cursor.fetchone()[0]

    # get the average daily expenses per week
    def get_day_expenses(self, week_offset):
        total = self.get_week_expenses(week_offset)
        return total / 7.0
    
    # get the week's highest spending category
    # returns (name, total_spent) or (None, 0.0) if no data
    def get_high_cat(self, week_offset):
        start, end = self.get_week(week_offset)
        start_str = start.strftime("%Y-%m-%d")
        end_str = end.strftime("%Y-%m-%d")
        # gets catagories from past week with highest spending, and selects the highest one
        query = '''
            SELECT c.name, ABS(SUM(t.amount)) as total
            FROM transactions t
            JOIN categories c ON t.category_id = c.id
            WHERE t.amount < 0
              AND t.date >= ?
              AND t.date <= ?
              AND c.id > 2
            GROUP BY t.category_id
            ORDER BY total DESC
            LIMIT 1
        '''
        self.cursor.execute(query, (start_str, end_str))
        result = self.cursor.fetchone()
        return result if result else (None, 0.0)

    '''**ADD AND EDIT FUNCTIONS**'''
    # --categories--
    # adds a new empty category
    def add_cat(self, name="New Category", percent=0):
        self.cursor.execute("INSERT INTO categories (name, percent) VALUES (?, ?)", (name, percent))
        self.connection.commit()
        return self.cursor.lastrowid
    
    # only updates values that are provided, keeps currents otherwise
    def edit_cat(self, cat_id, name=None, percent=None):
        # get current
        self.cursor.execute("SELECT name, percent FROM categories WHERE id = ?", (cat_id,))
        current = self.cursor.fetchone()
        
        # new value if provided, else keep current
        new_name = name if name is not None else current[0]
        new_percent = percent if percent is not None else current[1]
        
        self.cursor.execute("UPDATE categories SET name = ?, percent = ? WHERE id = ?", (new_name, new_percent, cat_id))
        self.connection.commit()

    # --transactions--
    def add_transaction(self, date, name, category_id, amount):
        self.cursor.execute("INSERT INTO transactions (date, name, category_id, amount) VALUES (?, ?, ?, ?)", (date, name, category_id, amount))
        self.connection.commit()

    # only updates values that are provided, keeps current otherwise
    def edit_transaction(self, trans_id, date=None, name=None, category_id=None, amount=None):
        # get current
        self.cursor.execute("SELECT date, name, category_id, amount FROM transactions WHERE id = ?", (trans_id,))
        curr = self.cursor.fetchone()
        
        # sets values if provided, else keep current
        vals = (
            date if date else curr[0],
            name if name else curr[1],
            category_id if category_id else curr[2],
            amount if amount is not None else curr[3],
            trans_id
        )
        self.cursor.execute("UPDATE transactions SET date=?, name=?, category_id=?, amount=? WHERE id=?", vals)
        self.connection.commit()
    
    # --bills--
    def add_bill(self, name, amount, date):
        self.cursor.execute("INSERT INTO bills (name, amount, date) VALUES (?, ?, ?)", (name, amount, date))
        self.connection.commit()

    # --goals--
    def add_goal(self, name, amount, date):
        self.cursor.execute("INSERT INTO goals (name, amount, saved, date) VALUES (?, ?, 0, ?)", (name, amount, date))
        self.connection.commit()
    
    # only updates values that are provided, keeps current otherwise
    def edit_goal(self, goal_id, name=None, amount=None, saved=None, date=None):
        # get current
        self.cursor.execute("SELECT name, amount, saved, date FROM goals WHERE id = ?", (goal_id,))
        curr = self.cursor.fetchone()
        
        # sets values if provided, else keep current
        vals = (
            name if name else curr[0],
            amount if amount is not None else curr[1],
            saved if saved is not None else curr[2],
            date if date else curr[3],
            goal_id
        )
        self.cursor.execute("UPDATE goals SET name=?, amount=?, saved=?, date=? WHERE id=?", vals)
        self.connection.commit()
    
    # --budget--
    # only updates if value provided, else keep current
    def edit_monthly_budget(self, new_amount):
        current = self.get_setting('budget')
        budget = new_amount if new_amount is not None else current
        self.set_setting('budget', str(budget))

    # --settings--
    # reusable func for toggle settings
    def _toggle_setting(self, key, option_a, option_b):
        current = self.get_setting(key)
        new_val = option_b if current == option_a else option_a
        self.set_setting(key, new_val)

    def swap_theme(self):
        self._toggle_setting('theme', 'dark', 'light')

    def swap_budget_alerts(self):
        self._toggle_setting('alerts', 'True', 'False')

    def swap_bill_reminders(self):
        self._toggle_setting('reminders', 'True', 'False')

    def change_font(self, new_font):
        self.set_setting('font', new_font)

    '''**DELETE FUNCTIONS**'''
    def delete_bill(self, id):
        try:
            self.cursor.execute("DELETE FROM bills WHERE id = ?", (id,))
            self.connection.commit()
            return True
        except:
            self.connection.rollback() # undo changes if something failed
            print('delete bill function failed')
            return False
        
    def delete_transaction(self, id):
        try:
            self.cursor.execute("DELETE FROM transactions WHERE id = ?", (id,))
            self.connection.commit()
            return True
        except:
            self.connection.rollback() # undo changes if something failed
            print('delete transaction function failed')
            return False
        
    def delete_goal(self, id):
        try:
            self.cursor.execute("DELETE FROM goals WHERE id = ?", (id,))
            return True
        except:
            self.connection.rollback() # undo changes if something failed
            print('delete goal function failed')
            return False
        
    def delete_cat(self, id):
        # prevents deletion of hardcoded cats
        if id <= 2:
            print("cannot delete protected system categories (None, Income)")
            return False
        try:
            # changes transacions under that category to None
            self.cursor.execute("UPDATE transactions SET category_id = 1 WHERE category_id = ?", (id,))
            # delete cat
            self.cursor.execute("DELETE FROM categories WHERE id = ?", (id,))
            self.connection.commit()
            return True

        except:
            self.connection.rollback() # undo changes if something failed
            print('delete cat function failed')
            return False


    '''**DATA MANAGEMENT**'''
    # restore default settings
    def restore_defaults(self):
        reset_values = [
        ('0', 'budget'),
        ('light', 'theme'),
        ('medium', 'font'),
        ('True', 'alerts'),
        ('False', 'reminders')
        ]
        for value, key in reset_values:
            self.set_setting(key, value)
    
    # clear all data and restore defaults
    def clear_data(self):
        tables = ['transactions', 'bills', 'goals']
        for table in tables:
            self.cursor.execute(f"DELETE FROM {table}")
        self.cursor.execute("DELETE FROM categories WHERE name NOT IN ('None', 'Income')")
        self.cursor.execute("UPDATE categories SET percent = 0 WHERE name IN ('None', 'Income')")
        self.connection.commit()
        self.fill_setstat()
        self.restore_defaults()

