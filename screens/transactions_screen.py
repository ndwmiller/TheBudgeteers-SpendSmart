from kivy.properties import ListProperty, ObjectProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import Screen
from kivy.app import App

from database import Database
from .widgets.add_transaction import AddTransaction
from .widgets.edit_transaction import EditTransaction


class TransactionsScreen(Screen):

    def on_enter(self):
        self.setup_filter()
        self.load_transactions()

    def setup_filter(self):
        if "filter_spinner" not in self.ids:
            return
        app = App.get_running_app()
        cats = app.db.get_all_cats()
        # "All" sits first so the spinner defaults to showing everything
        cat_names = ["All"] + [cat[1] for cat in cats]
        self.ids.filter_spinner.values = cat_names
        # reset to "All" if the previously selected category no longer exists
        if self.ids.filter_spinner.text not in cat_names:
            self.ids.filter_spinner.text = "All"

    def load_transactions(self, *args):
        if "transactions_rows" not in self.ids:
            return

        app = App.get_running_app()
        rows_container = self.ids.transactions_rows
        rows_container.clear_widgets()

        search_text = self.ids.search_input.text.strip().lower() if "search_input" in self.ids else ""
        selected_category = self.ids.filter_spinner.text.strip() if "filter_spinner" in self.ids else "All"

        # build a lookup dict once so we don't hit the db for every row
        cats = app.db.get_all_cats()
        cat_map = {cat[0]: cat[1] for cat in cats}

        for trans in app.db.get_all_transactions():
            trans_id, date_db, name, amount, category_id = trans
            cat_name = cat_map.get(category_id, "None")
            # date comes out of the db as yyyy-mm-dd, convert to mm/dd/yyyy for display
            date_ui = Database.date_to_ui(date_db)
            # row format: [id, date (ui), name, category name, amount]
            row = [trans_id, date_ui, name, cat_name, amount]

            matches_search = (
                search_text in date_ui.lower()
                or search_text in str(name).lower()
                or search_text in cat_name.lower()
                or search_text in str(amount).lower()
            )
            matches_category = selected_category == "All" or cat_name == selected_category

            if matches_search and matches_category:
                row_widget = TransactionRow()
                row_widget.row_data = row
                row_widget.parent_screen = self
                rows_container.add_widget(row_widget)

        _multipliers = {'small': 0.92, 'medium': 1.0, 'large': 1.12}
        multiplier = _multipliers.get(getattr(app, 'font_setting', 'medium'), 1.0)
        app.apply_font_size_to_widget(rows_container, multiplier)

    def add_transaction(self, date, name, category, amount):
        app = App.get_running_app()
        cat = app.db.get_cat(category)
        # bail if the category got deleted between when the popup opened and when submit was hit
        if cat is None:
            return
        # date arrives as mm/dd/yyyy from the input, needs to be yyyy-mm-dd for storage
        app.db.add_transaction(Database.date_to_db(date), name, cat[0], float(amount))
        self.load_transactions()

    def update_transaction(self, transaction_id, date, name, category, amount):
        app = App.get_running_app()
        cat = app.db.get_cat(category)
        if cat is None:
            return
        app.db.edit_transaction(transaction_id, Database.date_to_db(date), name, cat[0], float(amount))
        self.load_transactions()

    def delete_row(self, transaction_id):
        app = App.get_running_app()
        app.db.delete_transaction(transaction_id)
        self.load_transactions()

    def open_add_popup(self):
        popup = AddTransaction()
        popup.screen = self
        popup.open()

    def open_edit_popup(self, row_data):
        popup = EditTransaction()
        popup.screen = self
        popup.transaction_id = row_data[0]
        # pre-fill the form before opening so the data is ready when on_open fires
        popup.set_transaction_data(row_data)
        popup.open()


class TransactionRow(BoxLayout):
    row_data = ListProperty([])
    parent_screen = ObjectProperty(None)
