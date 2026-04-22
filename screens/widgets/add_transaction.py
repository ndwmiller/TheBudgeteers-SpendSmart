import os

from kivy.lang import Builder
from kivy.properties import ObjectProperty
from kivy.uix.popup import Popup

Builder.load_file(os.path.join(os.path.dirname(__file__), "add_transaction.kv"))


class AddTransaction(Popup):
    screen = ObjectProperty(None)

    def on_open(self):
        if "category_spinner" in self.ids and self.screen:
            self.ids.category_spinner.values = self.screen.categories[1:]
            self.ids.category_spinner.text = "Category"

    def add_new_transaction(self):
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
            self.screen.add_transaction(date, name, category, amount)

        self.dismiss()