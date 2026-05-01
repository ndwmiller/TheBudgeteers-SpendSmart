from kivy.app import App
from kivy.uix.screenmanager import Screen
from kivy.properties import BooleanProperty, StringProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.factory import Factory


class BudgetScreen(Screen):
    monthly_budget   = StringProperty('0.00')
    # remaining budget is monthly budget minus all expense transactions, income not included
    remaining_budget = StringProperty('0.00')
    has_categories   = BooleanProperty(False)

    class BudgetCategoryRow(BoxLayout):
        cat_name      = StringProperty('')
        cat_percent   = StringProperty('')
        cat_remaining = StringProperty('')

    def on_enter(self):
        self.app = App.get_running_app()
        self.refresh_category_ui()

    def get_remaining_budget(self):
        return f"{App.get_running_app().db.get_rem_budget():.2f}"

    def get_monthly_budget(self):
        return str(App.get_running_app().db.get_setting('budget') or '0.00')

    def refresh_category_ui(self):
        self.monthly_budget   = self.get_monthly_budget()
        self.remaining_budget = self.get_remaining_budget()
        # skip the first two system categories (None and Income)
        categories = self.app.db.get_all_cats()[2:]
        grid = self.ids.categories_grid

        grid.clear_widgets()
        self.has_categories = bool(categories)
        for cat in categories:
            _, name, percent = cat
            row = Factory.BudgetCategoryRow()
            row.cat_name      = str(name)
            row.cat_percent   = str(percent)
            row.cat_remaining = f"{self.app.db.get_cat_total(name):.2f}"
            grid.add_widget(row)

    def open_edit_budget(self):
        app = App.get_running_app()
        app.shell.ids.sm.current = 'budget_edit'
        return None

    @staticmethod
    def _parse_currency(value: str) -> float:
        cleaned = ''.join(ch for ch in value if ch.isdigit() or ch in '.-')
        try:
            return float(cleaned) if cleaned else 0.0
        except ValueError:
            return 0.0

    @staticmethod
    def _format_currency(value: float) -> str:
        return f"$ {value:,.2f}"
