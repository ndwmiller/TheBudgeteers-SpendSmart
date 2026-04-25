from kivy.uix.modalview import ModalView
from kivy.properties import ObjectProperty
from kivy.app import App
from database import Database

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
        if len(name) > 11:
            self.ids.error_label.text = "Name cannot exceed 11 characters"
            return

        # amount validation
        try:
            float(amount)
            
            # check for decimals beyond two places
            if len(amount.split('.')[-1]) > 2 and '.' in amount:
                self.ids.error_label.text = "Maximum 2 decimal places allowed."
                return

        except ValueError:
            self.ids.error_label.text = "Invalid amount format."
            return

        if float(amount) > float(99999):
            self.ids.error_label.text = "Bill amount cannot exceed $99,999.99"
            return
        
        # date avlidation
        date_error = self.ids.date_input.get_validation_error()
        if date_error:
            self.ids.error_label.text = date_error
            return

        # send to dashboard
        if self.callback:
            self.callback(name, amount, Database.date_to_db(date))
        
        self.dismiss()