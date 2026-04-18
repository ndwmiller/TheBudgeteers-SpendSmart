from kivy.uix.modalview import ModalView
from kivy.properties import ObjectProperty
from kivy.app import App

class AddBill(ModalView):
    # adds the UI element in dashboard
    callback = ObjectProperty(None)

    def clear_error(self):
        # remove error when user types again
        self.ids.error_label.text = ""

    def validate_and_submit(self):
        # get ID values
        name = self.ids.name_input.text.strip()
        amount = self.ids.amount_input.text.strip()
        date = self.ids.date_input.text.strip()

        # name validation
        if not name or not amount or not date:
            self.ids.error_label.text = "Please fill in all fields."
            return

        # amount validation
        try:
            float(amount)
        except ValueError:
            self.ids.error_label.text = "Invalid amount format."
            return
        
        # date avlidation
        date_error = self.ids.date_input.get_validation_error()
        if date_error:
            self.ids.error_label.text = date_error
            return

        # send to dashboard
        if self.callback:
            self.callback(name, amount, date)
        
        self.dismiss()