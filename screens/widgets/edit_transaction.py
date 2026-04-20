import os

from kivy.lang import Builder
from kivy.properties import NumericProperty, ObjectProperty
from kivy.uix.popup import Popup

Builder.load_file(os.path.join(os.path.dirname(__file__), "edit_transaction.kv"))


class EditTransaction(Popup):
    screen = ObjectProperty(None)
    transaction_id = NumericProperty(0)

    def on_open(self):
        if "category_spinner" in self.ids and self.screen:
            self.ids.category_spinner.values = self.screen.categories[1:]

    def set_transaction_data(self, row_data):
        self.transaction_id = row_data[0]

        self.ids.date_input.text = str(row_data[1])
        self.ids.name_input.text = str(row_data[2])
        self.ids.category_spinner.text = str(row_data[3])
        self.ids.amount_input.text = str(row_data[4])

    def save_transaction(self):
        date = self.ids.date_input.text.strip()
        name = self.ids.name_input.text.strip()
        category = self.ids.category_spinner.text.strip()
        amount = self.ids.amount_input.text.strip()

        if not date or not name or category == "Category" or not amount:
            print("Please fill all fields.")
            return

        try:
            amount = float(amount)
        except ValueError:
            print("Amount must be a number.")
            return

        if self.screen:
            self.screen.update_transaction(
                self.transaction_id,
                date,
                name,
                category,
                amount
            )

        self.dismiss()