from kivy.app import App
from kivy.uix.screenmanager import Screen
from kivy.properties import BooleanProperty, StringProperty, NumericProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.factory import Factory


class BudgetEditScreen(Screen):
    monthly_budget = StringProperty("0.00")
    has_categories = BooleanProperty(False)
    max_categories = 5

    class BudgetEditCategoryRow(BoxLayout):
        cat_id = NumericProperty(0)
        cat_name = StringProperty('')
        cat_percent = StringProperty('')

        def on_delete(self):
            app = App.get_running_app()
            screen = app.shell.ids.sm.get_screen('budget_edit')
            screen.delete_category(self.cat_id)

    def on_enter(self):
        self.app = App.get_running_app()
        self.monthly_budget = str(self.app.db.get_setting('budget') or '0.00')
        self._original_cat_ids = {cat[0] for cat in self.app.db.get_all_cats()[2:]}
        self._pending_deletions = set()
        self.refresh_category_rows()

    def refresh_category_rows(self):
        categories = self.app.db.get_all_cats()[2:]
        grid = self.ids.categories_grid
        grid.clear_widgets()

        self.has_categories = bool(categories)
        
        for cat in categories:
            cat_id, name, percent = cat
            row = Factory.BudgetEditCategoryRow()
            row.cat_id = cat_id
            row.cat_name = str(name)
            row.cat_percent = str(percent)
            grid.add_widget(row)

    def delete_category(self, cat_id):
        self._pending_deletions.add(cat_id)
        grid = self.ids.categories_grid
        for row in list(grid.children):
            if row.cat_id == cat_id:
                grid.remove_widget(row)
                break
        self.has_categories = bool(grid.children)

    def add_category(self):
        # check against DB count so that staging deletes and adding replacements in the
        # same session can't push the total rows in the DB past the cap
        if len(self.app.db.get_all_cats()[2:]) >= self.max_categories:
            self._show_error(f'Maximum of {self.max_categories} categories allowed.')
            return
        new_id = self.app.db.add_cat('New Category', 0.0)
        row = Factory.BudgetEditCategoryRow()
        row.cat_id = new_id
        row.cat_name = 'New Category'
        row.cat_percent = '0.0'
        grid.add_widget(row)
        self.has_categories = True

    def save_edit(self):
        monthly_amount = self._parse_currency(self.ids.monthly_input.text)
        if monthly_amount <= 0:
            self._show_error("Monthly budget must be greater than 0.")
            return

        grid = self.ids.categories_grid
        rows = list(reversed(grid.children))

        total_percent = sum(self._parse_percent(r.cat_percent) for r in rows)
        if total_percent > 100:
            self._show_error("Total category percent cannot exceed 100%.")
            return

        reserved = {'none', 'income'}
        for row in rows:
            if not row.cat_name.strip():
                self._show_error("Category name cannot be empty.")
                return
            if row.cat_name.strip().lower() in reserved:
                self._show_error(f'"{row.cat_name.strip()}" is a default category name.')
                return

        names = [row.cat_name.strip() for row in rows]
        if len(names) != len(set(names)):
            self._show_error("Category names must be unique.")
            return

        self.ids.error_label.text = ''
        self.app.db.set_setting('budget', str(monthly_amount))
        for cat_id in self._pending_deletions:
            self.app.db.delete_cat(cat_id)
        for row in rows:
            self.app.db.edit_cat(row.cat_id, row.cat_name.strip(), self._parse_percent(row.cat_percent))

        self.app.shell.ids.sm.current = 'budget'

    def cancel_edit(self):
        self.ids.error_label.text = ''
        current_ids = {cat[0] for cat in self.app.db.get_all_cats()[2:]}
        # delete everything added this session regardless of pending-deletion state,
        # so add → stage-for-delete → cancel doesn't leave orphan rows in the DB
        for cat_id in current_ids - self._original_cat_ids:
            self.app.db.delete_cat(cat_id)
        self.app.shell.ids.sm.current = 'budget'

    def _show_error(self, message):
        self.ids.error_label.text = message

    @staticmethod
    def _parse_currency(value):
        cleaned = ''.join(ch for ch in value if ch.isdigit() or ch in '.-')
        try:
            return float(cleaned) if cleaned else 0.0
        except ValueError:
            return 0.0

    @staticmethod
    def _parse_percent(value):
        cleaned = ''.join(ch for ch in value if ch.isdigit() or ch in '.-')
        try:
            return float(cleaned) if cleaned else 0.0
        except ValueError:
            return 0.0
