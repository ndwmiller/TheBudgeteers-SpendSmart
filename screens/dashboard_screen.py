from kivy.uix.screenmanager import Screen
from .widgets import AddBill
from kivy.factory import Factory
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.widget import Widget
from kivy.clock import Clock
from kivy.properties import NumericProperty, StringProperty
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from database import Database
from datetime import datetime, timedelta

class DashboardScreen(Screen):
    # database access and loads saved bills
    def on_enter(self):
        self.app = App.get_running_app()
        Clock.schedule_once(lambda dt: self.refresh_dashboard()) # waits 1 frame for the ids to bind
        Clock.schedule_once(lambda dt: self.maybe_show_notifications())

    class BillElement(BoxLayout):
        db_id = NumericProperty(0)
        bill_name = StringProperty("")
        bill_amount = StringProperty("")
        bill_date = StringProperty("")

        def on_delete(self):
            app = App.get_running_app()
            dashboard = app.shell.ids.sm.get_screen('dashboard')
            dashboard.remove_bill_from_ui(self.db_id)

    class CatElement(BoxLayout):
        cat_name = StringProperty("")
        cat_amount = StringProperty("")
    
    def trigger_add_bill(self):
        # open the popup and callback add_bill_to_ui method
        popup = AddBill()
        popup.callback = self.add_bill_to_ui
        popup.open()

    # refresh dashboard UI after changes
    def refresh_dashboard(self):
        # get bill container and wipe old data
        bill_containter = self.ids.bill_container
        bill_containter.clear_widgets()
        # get cat container and wipe old data
        cat_container = self.ids.cat_container
        cat_container.clear_widgets()
        # get current bill data
        all_bills = self.app.db.get_all_bills()
        all_cats = self.app.db.get_all_cats()

        for b in all_bills:
            id, name, amount, date = b
            new_bill = Factory.BillElement()
            new_bill.bill_name = Database.date_to_ui(str(name))
            new_bill.bill_date = str(date)
            new_bill.bill_amount = str(amount)

            # store bill id's for delete function
            new_bill.db_id = id

            self.ids.bill_container.add_widget(new_bill)

        user_cats = all_cats[2:]
        if not user_cats:
            placeholder = Factory.CatElement()
            placeholder.cat_name = "None"
            placeholder.cat_amount = "0.00"
            self.ids.cat_container.add_widget(placeholder)
        else:
            for c in user_cats:
                id, name, _ = c
                new_cat = Factory.CatElement()
                new_cat.cat_name = str(name)
                new_cat.cat_amount = str(self.app.db.get_cat_total(name))
                self.ids.cat_container.add_widget(new_cat)
        spacer = Widget(size_hint_y=1) 
        cat_container.add_widget(spacer)

    def add_bill_to_ui(self, name, amount, date):
        # add bill to db, then refresh bills list to match
        self.app.db.add_bill(name, amount, date)
        self.refresh_dashboard()

    def remove_bill_from_ui(self, id):
        deleted = self.app.db.delete_bill(id)
        self.refresh_dashboard()
        if not deleted:
            print(f"couldn't delete bill with id: {id}")

    def maybe_show_notifications(self):
        messages = []

        if self.app.alerts_enabled:
            budget = float(self.app.db.get_setting('budget') or 0)
            expenses = float(self.app.db.get_expenses() or 0)
            if budget > 0 and expenses > budget:
                messages.append(
                    f"Budget alert: this month's expenses (${expenses:.2f}) are over budget (${budget:.2f})."
                )

        if self.app.reminders_enabled:
            today = datetime.now().date()
            upcoming_cutoff = today + timedelta(days=7)
            due_bills = []
            for bill in self.app.db.get_all_bills():
                try:
                    due_date = datetime.strptime(str(bill[1]), "%Y-%m-%d").date()
                except ValueError:
                    continue
                if today <= due_date <= upcoming_cutoff:
                    due_bills.append(f"{bill[2]} ({due_date.strftime('%m/%d/%Y')})")

            if due_bills:
                messages.append("Upcoming bills: " + ", ".join(due_bills[:3]))

        if messages:
            Popup(
                title="Notifications",
                size_hint=(None, None),
                size=(560, 220),
                content=Label(
                    text="\n\n".join(messages),
                    halign='center',
                    valign='middle',
                    text_size=(520, None),
                ),
            ).open()
    
    def big_total(self):
        return f"{self.app.db.get_big_total():.2f}"

    def monthly_budget(self):
        return str(self.app.db.get_setting('budget'))

    def monthly_income(self):
        return f"{self.app.db.get_income():.2f}"

    def monthly_expenses(self):
        return f"{self.app.db.get_expenses():.2f}"

    def day_expenses_this_week(self):
        return f"{self.app.db.get_day_expenses(0):.2f}"

    def week_expenses_this_week(self):
        return f"{self.app.db.get_week_expenses(0):.2f}"

    def high_cat_name_this_week(self):
        name, _ = self.app.db.get_high_cat(0)
        return name or "Empty"

    def high_cat_amount_this_week(self):
        _, amount = self.app.db.get_high_cat(0)
        return f"{amount:.2f}"

    def day_expenses_last_week(self):
        return f"{self.app.db.get_day_expenses(1):.2f}"

    def week_expenses_last_week(self):
        return f"{self.app.db.get_week_expenses(1):.2f}"

    def high_cat_name_last_week(self):
        name, _ = self.app.db.get_high_cat(1)
        return name or "Empty"

    def high_cat_amount_last_week(self):
        _, amount = self.app.db.get_high_cat(1)
        return f"{amount:.2f}"

    
