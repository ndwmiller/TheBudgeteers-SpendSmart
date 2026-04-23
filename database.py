import sqlite3 as sql

class Database:
    def __init__(self, db_path):
        self.connection = sql.connect(db_path)
        self.cursor = self.connection.cursor()
        self.create_tables()
        self.fill_setstat()
    
    def create_tables(self):
        # transactions table: ID | DATE (xx-xx-xxxx) | NAME | AMOUNT (can be negative)
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT,
            name TEXT,
            amount REAL,
            category_id INTEGER,
            FOREIGN KEY (category_id) REFERENCES categories (id)
        )''')

        # upcoming bills: ID | DATE (xx-xx-xxxx) | NAME | AMOUNT
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS bills (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT,
            name TEXT,
            amount REAL
        )''')

        # categories: ID | NAME | PERCENT (of monthly budget)
        # first entry is always income category. not to be shown on budget page
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE,
            percent REAL
        )''')
        self.cursor.execute("INSERT OR IGNORE INTO categories (name, percent) VALUES (?, ?)", ('Income', 0.0))
        self.connection.commit()

        # settings and monthly budget: KEY (item name) | VALUE
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS setstat (
            key TEXT PRIMARY KEY,
            value TEXT
        )''')

        # goals: ID | NAME | AMOUNT | SAVED | DATE (xx-xx-xxxx)
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
        ('theme', 'dark'),
        ('font', 'medium'),
        ('alerts', 'True'),
        ('reminders', 'False')
        ]

        query = "INSERT OR IGNORE INTO setstat (key, value) VALUES (?, ?)"

        self.cursor.executemany(query, default_settings)
        self.connection.commit()
    
    '''**INDIVIDUAL GETTERS**'''
    # returns string (e.g., "dark") or None
    # works for budget too. search by name (budget, theme, font, alerts, reminders)
    def get_setting(self, key_name):
        self.cursor.execute("SELECT value FROM settings WHERE key = ?", (key_name,))
        result = self.cursor.fetchone()
        # returns just the value string or None if not found
        return result[0] if result else None

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
        self.cursor.execute("SELECT * FROM categories")
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
        
        raw_cat_value = budget * (cat['percent'] / 100)
        
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
    def get_bigtotal(self):
        self.cursor.execute("SELECT COALESCE(SUM(amount), 0) FROM transactions")
        return self.cursor.fetchone()[0]

    # returns float of sum of income transactions
    def get_income(self):
        query = '''
            SELECT COALESCE(SUM(t.amount), 0) 
            FROM transactions t
            JOIN categories c ON t.category_id = c.id
            WHERE c.name = 'Income'
        '''
        self.cursor.execute(query)
        return self.cursor.fetchone()[0]

    # returns float of sum of negative transactions
    def get_expenses(self):
        self.cursor.execute("SELECT COALESCE(SUM(amount), 0) FROM transactions WHERE amount < 0")
        return self.cursor.fetchone()[0]

    # these 3 will need today's date i think. will implement later
    def get_day_expenses(self, week):
        pass

    def get_week_expenses(self, week):
        pass

    def get_high_cat(self, week):
        pass





    '''**ADD AND EDIT FUNCTIONS**'''
    # --categories--
    # adds a new empty category
    def add_category(self, name="New Category", percent=0):
        self.cursor.execute("INSERT INTO categories (name, percent) VALUES (?, ?)", (name, percent))
        self.connection.commit()
    
    # only updates values that are provided, keeps currents otherwise
    def edit_category(self, cat_id, name=None, percent=None):
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
        # get current
        self.cursor.execute("SELECT name, percent FROM categories WHERE id = budget")
        current = self.cursor.fetchone()

        # new value if provided, else keep current
        budget = new_amount if new_amount is not None else current[0]

        self.cursor.execute("UPDATE settings SET value = ? WHERE key = ?", (budget, 'budget'))
        self.connection.commit()

    # --settings--
    # reusable func for toggle settings
    def _toggle_setting(self, key, option_a, option_b):
        # get current
        self.cursor.execute("SELECT value FROM settings WHERE key = ?", (key,))
        current = self.cursor.fetchone()[0]

        # swap current with other option
        new_val = option_b if current == option_a else option_a
        self.cursor.execute("UPDATE settings SET value = ? WHERE key = ?", (new_val, key))
        self.connection.commit()

    def swap_theme(self):
        self._toggle_setting('theme', 'dark', 'light')

    def swap_budget_alerts(self):
        self._toggle_setting('alerts', 'True', 'False')

    def swap_bill_reminders(self):
        self._toggle_setting('reminders', 'True', 'False')

    def change_font(self, new_font):
        self.cursor.execute("UPDATE settings SET value = ? WHERE key = ?", (new_font, 'font'))
        self.connection.commit()

    '''**DATA MANAGEMENT**'''
    # restore default settings
    def restore_defaults(self):
        reset_values = [
        ('dark', 'theme'),
        ('medium', 'font'),
        ('True', 'alerts'),
        ('False', 'reminders')
        ]

        query = "UPDATE settings SET value = ? WHERE key = ?"
        
        self.cursor.executemany(query, reset_values)
        self.connection.commit()
    
    # clear all data and restore defaults
    def clear_data(self):
        # Wipe tables
        tables = ['transactions', 'bills', 'categories', 'goals', 'settings']
        for table in tables:
            self.cursor.execute(f"DELETE FROM {table}")
        
        # Re-fill the default settings
        self.connection.commit()
        self.fill_setstat()

