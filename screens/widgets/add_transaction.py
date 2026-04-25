import os

from kivy.lang import Builder
from kivy.properties import ObjectProperty
from kivy.uix.popup import Popup

Builder.load_file(os.path.join(os.path.dirname(__file__), "add_transaction.kv"))


class AddTransaction(Popup):
    screen = ObjectProperty(None)

    def clear_error(self):
        if "error_label" in self.ids:
            self.ids.error_label.text = ""

    def on_open(self):
        self.clear_error()

        if "category_spinner" in self.ids and self.screen:
            self.ids.category_spinner.values = self.screen.categories[1:]
            self.ids.category_spinner.text = "Category"

    def validate_and_submit(self):
        date = self.ids.date_input.text.strip()
        name = self.ids.name_input.text.strip()
        category = self.ids.category_spinner.text.strip()
        amount = self.ids.amount_input.text.strip()

        if not date or not name or not amount or category == "Category":
            self.ids.error_label.text = "Please fill in all fields."
            return

        try:
            amount = float(amount)
        except ValueError:
            self.ids.error_label.text = "Invalid amount format."
            return

        date_error = self.ids.date_input.get_validation_error()
        if date_error:
            self.ids.error_label.text = date_error
            return

        if self.screen:
            self.screen.add_transaction(date, name, category, amount)

        self.dismiss()