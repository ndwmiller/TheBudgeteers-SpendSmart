import os

from kivy.lang import Builder
from kivy.properties import NumericProperty, ObjectProperty
from kivy.uix.popup import Popup

Builder.load_file(os.path.join(os.path.dirname(__file__), "edit_transaction.kv"))


class EditTransaction(Popup):
    screen = ObjectProperty(None)
    transaction_id = NumericProperty(0)

    def clear_error(self):
        if "error_label" in self.ids:
            self.ids.error_label.text = ""

    def on_open(self):
        self.clear_error()

        if "category_spinner" in self.ids and self.screen:
            self.ids.category_spinner.values = self.screen.categories[1:]

    def set_transaction_data(self, row_data):
        self.transaction_id = row_data[0]
        self.ids.date_input.text = str(row_data[1])
        self.ids.name_input.text = str(row_data[2])
        self.ids.category_spinner.text = str(row_data[3])
        self.ids.amount_input.text = str(row_data[4])

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
            self.screen.update_transaction(
                self.transaction_id,
                date,
                name,
                category,
                amount
            )

        self.dismiss()