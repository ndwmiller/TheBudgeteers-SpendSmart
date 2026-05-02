from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import Screen
from kivy.properties import NumericProperty, StringProperty
from kivy.app import App
from kivy.factory import Factory

from database import Database


# Max dollar value keeps display from overflowing the table cells.
MAX_AMOUNT = 9_999_999.99
MAX_AMOUNT_TEXT_LENGTH = len(f'{int(MAX_AMOUNT)}.99')


class GoalAmountInput(BoxLayout):
    text = StringProperty('')
    _syncing = False

    def on_text(self, _, value):
        if self._syncing or 'amount_text' not in self.ids:
            return
        text_input = self.ids.amount_text
        if text_input.text != value:
            self._syncing = True
            text_input.text = value
            self._syncing = False

    def sync_text(self, text_input):
        if self._syncing:
            return
        cleaned = GoalsScreen.clean_amount_text(text_input.text)
        self._syncing = True
        if text_input.text != cleaned:
            text_input.text = cleaned
        self.text = cleaned
        self._syncing = False


class GoalRow(BoxLayout):
    goal_name    = StringProperty('')
    goal_amount  = StringProperty('')
    goal_saved   = StringProperty('')
    goal_date    = StringProperty('')
    progress_text  = StringProperty('')
    progress_ratio = NumericProperty(0.0)
    goal_id        = NumericProperty(0)

    def on_delete(self):
        app = App.get_running_app()
        goals_screen = app.shell.ids.sm.get_screen('goals')
        goals_screen.delete_goal(self.goal_id)


class GoalsScreen(Screen):

    def on_enter(self):
        self.refresh_goals()

    def refresh_goals(self):
        app  = App.get_running_app()
        goals = app.db.get_all_goals()

        self._goal_lookup = {}

        rows_grid = self.ids.goals_rows_grid
        rows_grid.clear_widgets()

        for goal in goals:
            goal_id, name, amount, saved, date = goal
            amount_value = float(amount or 0)
            saved_value  = float(saved  or 0)
            progress_ratio = (
                0.0 if amount_value <= 0
                else max(0.0, min(saved_value / amount_value, 1.0))
            )

            self._goal_lookup[str(name)] = goal_id

            row = Factory.GoalRow(
                goal_id       = goal_id,
                goal_name     = str(name),
                goal_amount   = self._format_currency(amount_value),
                goal_saved    = self._format_currency(saved_value),
                goal_date     = Database.date_to_ui(str(date)),
                progress_text = f"{progress_ratio * 100:.0f}%",
                progress_ratio= progress_ratio,
            )
            rows_grid.add_widget(row)

        _multipliers = {'small': 0.92, 'medium': 1.0, 'large': 1.12}
        multiplier = _multipliers.get(getattr(app, 'font_setting', 'medium'), 1.0)
        app.apply_font_size_to_widget(rows_grid, multiplier)

        self._refresh_update_spinner(goals)

    def _refresh_update_spinner(self, goals):
        spinner = self.ids.update_goal_spinner
        names   = [str(goal[1]) for goal in goals]
        spinner.values = names
        if spinner.text not in names:
            spinner.text = 'Select a goal...'
            self.ids.update_goal_amount.text = ''
            self.ids.update_goal_saved.text = ''
            self.ids.update_goal_date.text = ''

    def load_goal_into_update_form(self, goal_name):
        if goal_name == 'Select a goal...' or not goal_name:
            return
        app     = App.get_running_app()
        goal_id = getattr(self, '_goal_lookup', {}).get(goal_name)
        if goal_id is None:
            return
        goal = app.db.get_goal(goal_id)
        if not goal:
            return
        _, name, amount, saved, date = goal
        self.ids.update_goal_amount.text = self._strip_currency(amount)
        self.ids.update_goal_saved.text  = self._strip_currency(saved)
        self.ids.update_goal_date.text   = Database.date_to_ui(str(date))

    # ── Add goal ─────────────────────────────────────────────────
    def add_goal(self):
        self.ids.add_error_label.text = ''

        name        = self.ids.add_goal_name.text.strip()
        amount_text = self.ids.add_goal_amount.text.strip()
        date_text   = self.ids.add_goal_date.text.strip()

        if not name or not amount_text or not date_text:
            self.ids.add_error_label.text = 'Please fill in all fields.'
            return

        amount_value = self._parse_currency(amount_text)
        if amount_value <= 0:
            self.ids.add_error_label.text = 'Target amount must be greater than 0.'
            return

        if amount_value > MAX_AMOUNT:
            self.ids.add_error_label.text = f'Max amount is ${MAX_AMOUNT:,.0f}.'
            return

        date_error = self.ids.add_goal_date.get_validation_error()
        if date_error:
            self.ids.add_error_label.text = date_error
            return

        app = App.get_running_app()
        existing_names = [str(g[1]) for g in app.db.get_all_goals()]
        if name in existing_names:
            self.ids.add_error_label.text = 'A goal with that name already exists.'
            return
        app.db.add_goal(name, amount_value, Database.date_to_db(date_text))

        self.ids.add_goal_name.text   = ''
        self.ids.add_goal_amount.text = ''
        self.ids.add_goal_date.text   = ''
        self.refresh_goals()

    # ── Save / update goal ────────────────────────────────────────
    def save_goal(self):
        self.ids.update_error_label.text = ''

        goal_name = self.ids.update_goal_spinner.text.strip()
        if goal_name == 'Select a goal...' or not goal_name:
            self.ids.update_error_label.text = 'Please select a goal to update.'
            return

        goal_id = getattr(self, '_goal_lookup', {}).get(goal_name)
        if goal_id is None:
            self.ids.update_error_label.text = 'Please select a valid goal.'
            return

        amount_text = self.ids.update_goal_amount.text.strip()
        saved_text  = self.ids.update_goal_saved.text.strip()
        date_text   = self.ids.update_goal_date.text.strip()

        amount_value = self._parse_currency(amount_text)
        saved_value  = self._parse_currency(saved_text)

        if amount_value <= 0:
            self.ids.update_error_label.text = 'Target amount must be greater than 0.'
            return

        if amount_value > MAX_AMOUNT:
            self.ids.update_error_label.text = f'Max amount is ${MAX_AMOUNT:,.0f}.'
            return

        if saved_value < 0:
            self.ids.update_error_label.text = 'Saved amount cannot be negative.'
            return

        if saved_value > MAX_AMOUNT:
            self.ids.update_error_label.text = f'Max amount is ${MAX_AMOUNT:,.0f}.'
            return

        date_error = self.ids.update_goal_date.get_validation_error()
        if date_error:
            self.ids.update_error_label.text = date_error
            return

        app = App.get_running_app()
        app.db.edit_goal(
            goal_id,
            name   = goal_name,
            amount = amount_value,
            saved  = saved_value,
            date   = Database.date_to_db(date_text),
        )
        self.refresh_goals()

    # ── Delete goal ───────────────────────────────────────────────
    def delete_goal(self, goal_id):
        app = App.get_running_app()
        if app.db.delete_goal(goal_id):
            self.refresh_goals()

    @staticmethod
    def clean_amount_text(value):
        raw = str(value)
        cleaned = []
        dot_seen = False
        decimal_count = 0
        integer_count = 0
        max_integer_digits = len(str(int(MAX_AMOUNT)))

        for char in raw:
            if char.isdigit():
                if dot_seen:
                    if decimal_count >= 2:
                        continue
                    decimal_count += 1
                else:
                    if integer_count >= max_integer_digits:
                        continue
                    integer_count += 1
                cleaned.append(char)
            elif char == '.' and not dot_seen:
                dot_seen = True
                cleaned.append(char)

            if len(cleaned) >= MAX_AMOUNT_TEXT_LENGTH:
                break

        return ''.join(cleaned)

    # ── Helpers ───────────────────────────────────────────────────
    @staticmethod
    def _parse_currency(value):
        cleaned = GoalsScreen.clean_amount_text(value)
        try:
            return float(cleaned) if cleaned else 0.0
        except ValueError:
            return 0.0

    @staticmethod
    def _strip_currency(value):
        return f'{GoalsScreen._parse_currency(value):.2f}'

    @staticmethod
    def _format_currency(value):
        return f'$ {float(value):,.2f}'
