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
    # string properties let the kv labels update reactively whenever refresh_dashboard runs
    remaining_balance   = StringProperty('0.00')
    stat_income         = StringProperty('0.00')
    stat_expenses       = StringProperty('0.00')
    stat_budget         = StringProperty('0')
    stat_day_this       = StringProperty('0.00')
    stat_week_this      = StringProperty('0.00')
    stat_high_name_this = StringProperty('Empty')
    stat_high_amt_this  = StringProperty('0.00')
    stat_day_last       = StringProperty('0.00')
    stat_week_last      = StringProperty('0.00')
    stat_high_name_last = StringProperty('Empty')
    stat_high_amt_last  = StringProperty('0.00')

    def on_enter(self):
        self.app = App.get_running_app()
        # schedule one frame out so all widget ids are bound before we try to access them
        Clock.schedule_once(lambda dt: self.refresh_dashboard())
        Clock.schedule_once(lambda dt: self.maybe_show_notifications())

    class BillElement(BoxLayout):
        db_id       = NumericProperty(0)
        bill_name   = StringProperty("")
        bill_amount = StringProperty("")
        bill_date   = StringProperty("")

        def on_delete(self):
            app = App.get_running_app()
            dashboard = app.shell.ids.sm.get_screen('dashboard')
            dashboard.remove_bill_from_ui(self.db_id)

    class CatElement(BoxLayout):
        cat_name   = StringProperty("")
        cat_amount = StringProperty("")

    def trigger_add_bill(self):
        popup = AddBill()
        popup.callback = self.add_bill_to_ui
        popup.open()

    def refresh_dashboard(self):
        db = self.app.db

        # update all stat properties so the kv labels re-render with fresh data
        self.remaining_balance   = f"{db.get_big_total():.2f}"
        self.stat_income         = f"{db.get_income():.2f}"
        self.stat_expenses       = f"{db.get_expenses():.2f}"
        self.stat_budget         = str(db.get_setting('budget') or '0')

        self.stat_day_this       = f"{db.get_day_expenses(0):.2f}"
        self.stat_week_this      = f"{db.get_week_expenses(0):.2f}"
        high_name, high_amt      = db.get_high_cat(0)
        self.stat_high_name_this = high_name or 'Empty'
        self.stat_high_amt_this  = f"{high_amt:.2f}"

        self.stat_day_last       = f"{db.get_day_expenses(1):.2f}"
        self.stat_week_last      = f"{db.get_week_expenses(1):.2f}"
        high_name, high_amt      = db.get_high_cat(1)
        self.stat_high_name_last = high_name or 'Empty'
        self.stat_high_amt_last  = f"{high_amt:.2f}"

        # rebuild bills list
        bill_container = self.ids.bill_container
        bill_container.clear_widgets()
        for b in db.get_all_bills():
            # bills table returns columns in this order: id, date, name, amount
            bill_id, date, name, amount = b
            new_bill = Factory.BillElement()
            new_bill.db_id       = bill_id
            new_bill.bill_name   = str(name)
            new_bill.bill_date   = Database.date_to_ui(str(date))
            new_bill.bill_amount = f"{float(amount):.2f}"
            bill_container.add_widget(new_bill)

        # rebuild category remaining amounts
        cat_container = self.ids.cat_container
        cat_container.clear_widgets()
        # skip the first two system categories (None and Income)
        user_cats = db.get_all_cats()[2:]
        if not user_cats:
            placeholder = Factory.CatElement()
            placeholder.cat_name   = "None"
            placeholder.cat_amount = "0.00"
            cat_container.add_widget(placeholder)
        else:
            for c in user_cats:
                _, name, _ = c
                new_cat = Factory.CatElement()
                new_cat.cat_name   = str(name)
                new_cat.cat_amount = f"{db.get_cat_total(name):.2f}"
                cat_container.add_widget(new_cat)
        # spacer pushes the category rows to the top of the container
        cat_container.add_widget(Widget(size_hint_y=1))

    def add_bill_to_ui(self, name, amount, date):
        # amount comes in as a string from the popup, cast to float before storing
        self.app.db.add_bill(name, float(amount), date)
        self.refresh_dashboard()

    def remove_bill_from_ui(self, id):
        deleted = self.app.db.delete_bill(id)
        self.refresh_dashboard()
        if not deleted:
            print(f"couldn't delete bill with id: {id}")

    def maybe_show_notifications(self):
        messages = []

        if self.app.alerts_enabled:
            budget   = float(self.app.db.get_setting('budget') or 0)
            expenses = float(self.app.db.get_expenses() or 0)
            if budget > 0 and expenses > budget:
                messages.append(
                    f"Budget alert: this month's expenses (${expenses:.2f}) are over budget (${budget:.2f})."
                )

        if self.app.reminders_enabled:
            today           = datetime.now().date()
            upcoming_cutoff = today + timedelta(days=7)
            due_bills = []
            for bill in self.app.db.get_all_bills():
                try:
                    # bill[1] is the date column, bill[2] is the name column
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
