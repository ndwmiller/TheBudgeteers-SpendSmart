from kivy.uix.screenmanager import Screen
from .widgets import AddBill
from kivy.factory import Factory

class DashboardScreen(Screen):
    # database access so that you can use app.db.cursor.execute(...)
    # def on_enter(self):
        # app = App.get_running_app()
    
    def trigger_add_bill(self):
        # just use placeholder data for now 
        # here is where we'll call the add bill popup and get real inputs
        placeholder_name = "Example"
        placeholder_date = "XX/XX/XXXX"
        placeholder_amount = "XXX.XX"

        # 1. Create the widget from the KV template
        new_bill = Factory.BillElement()
        
        # 2. Update its properties
        new_bill.bill_name = placeholder_name
        new_bill.bill_date = placeholder_date
        new_bill.bill_amount = placeholder_amount

        # 3. Add it to the scrollable container via ID
        self.ids.bill_container.add_widget(new_bill)

    pass