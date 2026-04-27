from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.properties import NumericProperty, StringProperty
from kivy.app import App
from kivy.factory import Factory
from kivy.metrics import dp

from database import Database
from kivy.uix.screenmanager import Screen


class GoalRow(BoxLayout):
    goal_name = StringProperty('')
    goal_amount = StringProperty('')
    goal_saved = StringProperty('')
    goal_date = StringProperty('')
    progress_text = StringProperty('')
    progress_ratio = NumericProperty(0.0)

class GoalsScreen(Screen):
    def on_enter(self):
        self.refresh_goals()

    def refresh_goals(self):
        app = App.get_running_app()
        goals = app.db.get_all_goals()
        visible_goals = goals[:5]

        self._goal_lookup = {}

        rows_grid = self.ids.goals_rows_grid
        rows_grid.clear_widgets()

        for goal in visible_goals:
            goal_id, name, amount, saved, date = goal
            amount_value = float(amount or 0)
            saved_value = float(saved or 0)
            progress_ratio = 0.0 if amount_value <= 0 else max(0.0, min(saved_value / amount_value, 1.0))

            self._goal_lookup[str(name)] = goal_id
            rows_grid.add_widget(Factory.GoalRow(
                goal_name=str(name),
                goal_amount=self._format_currency(amount_value),
                goal_saved=self._format_currency(saved_value),
                goal_date=Database.date_to_ui(str(date)),
                progress_text=f"{progress_ratio * 100:.0f}%",
                progress_ratio=progress_ratio,
            ))

        row_height = dp(39)
        header_height = dp(39)
        rows_grid.height = row_height * len(visible_goals)
        self.ids.goals_table.height = header_height + rows_grid.height

        self._refresh_update_spinner(goals)

    def _refresh_update_spinner(self, goals):
        spinner = self.ids.update_goal_spinner
        names = [str(goal[1]) for goal in goals]
        spinner.values = names
        if spinner.text not in names:
            spinner.text = 'Select a goal...'

    def load_goal_into_update_form(self, goal_name):
        if goal_name == 'Select a goal...' or not goal_name:
            return

        app = App.get_running_app()
        goal_id = getattr(self, '_goal_lookup', {}).get(goal_name)
        if goal_id is None:
            return

        goal = app.db.get_goal(goal_id)
        if not goal:
            return

        _, name, amount, saved, date = goal
        self.ids.update_goal_amount.text = self._strip_currency(amount)
        self.ids.update_goal_saved.text = self._strip_currency(saved)
        self.ids.update_goal_date.text = Database.date_to_ui(str(date))

    def add_goal(self):
        name = self.ids.add_goal_name.text.strip()
        amount_text = self.ids.add_goal_amount.text.strip()
        date_text = self.ids.add_goal_date.text.strip()

        if not name or not amount_text or not date_text:
            self._show_error('Please fill in all fields.')
            return

        amount_value = self._parse_currency(amount_text)
        if amount_value <= 0:
            self._show_error('Target amount must be greater than 0.')
            return

        date_error = self.ids.add_goal_date.get_validation_error()
        if date_error:
            self._show_error(date_error)
            return

        app = App.get_running_app()
        app.db.add_goal(name, amount_value, Database.date_to_db(date_text))

        self.ids.add_goal_name.text = ''
        self.ids.add_goal_amount.text = ''
        self.ids.add_goal_date.text = ''
        self.refresh_goals()

    def save_goal(self):
        goal_name = self.ids.update_goal_spinner.text.strip()
        if goal_name == 'Select a goal...' or not goal_name:
            self._show_error('Please select a goal to update.')
            return

        goal_id = getattr(self, '_goal_lookup', {}).get(goal_name)
        if goal_id is None:
            self._show_error('Please select a valid goal.')
            return

        name = goal_name
        amount_text = self.ids.update_goal_amount.text.strip()
        saved_text = self.ids.update_goal_saved.text.strip()
        date_text = self.ids.update_goal_date.text.strip()

        amount_value = self._parse_currency(amount_text)
        saved_value = self._parse_currency(saved_text)

        if amount_value <= 0:
            self._show_error('Target amount must be greater than 0.')
            return

        if saved_value < 0:
            self._show_error('Saved amount cannot be negative.')
            return

        date_error = self.ids.update_goal_date.get_validation_error()
        if date_error:
            self._show_error(date_error)
            return

        app = App.get_running_app()
        app.db.edit_goal(
            goal_id,
            name=name,
            amount=amount_value,
            saved=saved_value,
            date=Database.date_to_db(date_text),
        )
        self.refresh_goals()

    def _show_error(self, message):
        popup = Popup(
            title='Goals Error',
            content=Label(text=message, halign='center', valign='middle'),
            size_hint=(None, None),
            size=(dp(360), dp(180)),
            auto_dismiss=True,
        )
        popup.content.bind(size=lambda instance, value: setattr(instance, 'text_size', value))
        popup.open()

    @staticmethod
    def _parse_currency(value):
        cleaned = ''.join(ch for ch in str(value) if ch.isdigit() or ch in '.-')
        try:
            return float(cleaned) if cleaned else 0.0
        except ValueError:
            return 0.0

    @staticmethod
    def _strip_currency(value):
        numeric_value = GoalsScreen._parse_currency(value)
        return f'{numeric_value:.2f}'

    @staticmethod
    def _format_currency(value):
        return f'$ {float(value):,.2f}'