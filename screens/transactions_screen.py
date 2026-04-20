from kivy.properties import ListProperty, ObjectProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import Screen

from .widgets.add_transaction import AddTransaction
from .widgets.edit_transaction import EditTransaction


class TransactionsScreen(Screen):
    transactions_data = ListProperty([])
    categories = ListProperty(["All", "Food", "Transport", "Shopping", "Bills", "Health", "Other"])

    def on_enter(self):
        self.setup_filter()
        self.load_transactions()

    def setup_filter(self):
        if "filter_spinner" in self.ids:
            self.ids.filter_spinner.values = self.categories
            if self.ids.filter_spinner.text not in self.categories:
                self.ids.filter_spinner.text = "All"

    def load_transactions(self, *args):
        if "transactions_rows" not in self.ids:
            return

        rows_container = self.ids.transactions_rows
        rows_container.clear_widgets()

        search_text = self.ids.search_input.text.strip().lower() if "search_input" in self.ids else ""
        selected_category = self.ids.filter_spinner.text.strip() if "filter_spinner" in self.ids else "All"

        filtered_transactions = []

        for row in self.transactions_data:
            transaction_id, date, name, category, amount = row

            matches_search = (
                search_text in str(date).lower()
                or search_text in str(name).lower()
                or search_text in str(category).lower()
                or search_text in str(amount).lower()
            )

            matches_category = selected_category == "All" or category == selected_category

            if matches_search and matches_category:
                filtered_transactions.append(row)

        for row in filtered_transactions:
            row_widget = TransactionRow()
            row_widget.row_data = row
            row_widget.parent_screen = self
            rows_container.add_widget(row_widget)

    def add_transaction(self, date, name, category, amount):
        new_id = 1
        if self.transactions_data:
            new_id = max(row[0] for row in self.transactions_data) + 1

        updated = list(self.transactions_data)
        updated.append([new_id, date, name, category, float(amount)])
        self.transactions_data = updated
        self.load_transactions()

    def update_transaction(self, transaction_id, date, name, category, amount):
        updated = []
        for row in self.transactions_data:
            if row[0] == transaction_id:
                updated.append([transaction_id, date, name, category, float(amount)])
            else:
                updated.append(row)

        self.transactions_data = updated
        self.load_transactions()

    def delete_row(self, transaction_id):
        self.transactions_data = [row for row in self.transactions_data if row[0] != transaction_id]
        self.load_transactions()

    def open_add_popup(self):
        popup = AddTransaction()
        popup.screen = self
        popup.open()

    def open_edit_popup(self, row_data):
        popup = EditTransaction()
        popup.screen = self
        popup.transaction_id = row_data[0]
        popup.set_transaction_data(row_data)
        popup.open()


class TransactionRow(BoxLayout):
    row_data = ListProperty([])
    parent_screen = ObjectProperty(None)