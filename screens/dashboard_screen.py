from kivy.uix.screenmanager import Screen
from .widgets import AddBill
from kivy.factory import Factory

class DashboardScreen(Screen):
    # database access so that you can use app.db.cursor.execute(...)
    # def on_enter(self):
        # app = App.get_running_app()
    
    def trigger_add_bill(self):
        # open the popup and callback add_bill_to_ui method
        popup = AddBill()
        popup.callback = self.add_bill_to_ui
        popup.open()

    def add_bill_to_ui(self, name, amount, date):
        new_bill = Factory.BillElement()
        new_bill.bill_name = name
        new_bill.bill_date = date
        new_bill.bill_amount = amount

        self.ids.bill_container.add_widget(new_bill)