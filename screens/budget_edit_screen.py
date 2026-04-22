from kivy.uix.widget import Widget
from kivy.uix.screenmanager import Screen
from kivy.properties import StringProperty, ListProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.factory import Factory
from kivy.uix.button import Button
from kivy.metrics import dp
from kivy.app import App


class BudgetEditScreen(Screen):
    current_budget = StringProperty("$ 0.00")
    monthly_budget = StringProperty("$ 0.00")
    max_categories = 5

    # List of categories: each is a dictionary
    categories = ListProperty([])

    def on_enter(self):
        """Called when the edit screen is shown"""
        self.load_data_from_view_screen()

    def load_data_from_view_screen(self):
        """Copy data from the main BudgetScreen"""
        app = App.get_running_app()
        try:
            # Get the main budget view screen
            sm = app.shell.ids.sm
            budget_screen = sm.get_screen('budget')

            self.current_budget = budget_screen.current_budget
            self.monthly_budget = budget_screen.monthly_budget

            # Deep copy categories so we don't modify the original until Save
            self.categories = [cat.copy() for cat in budget_screen.categories]
        except Exception as e:
            print(f"Error loading budget data: {e}")
            # Fallback with example data
            if not self.categories:
                self.categories = [
                    {"name": "Example", "percent": "XX.XX%"},
                    {"name": "Example", "percent": "XX.XX%"},
                    {"name": "Example", "percent": "XX.XX%"},
                    {"name": "Example", "percent": "XX.XX%"},
                ]

        self.refresh_category_rows()

    def refresh_category_rows(self):
        """Dynamically create rows for categories"""
        grid = self.ids.categories_grid
        grid.clear_widgets()

        for i, cat in enumerate(self.categories):
            row = BoxLayout(
                orientation='horizontal',
                size_hint=(None, None),
                height=dp(26),
                width=dp(402),
                spacing=dp(10)
            )

            name_input = Factory.BudgetEditNameInput(
                text=cat.get('name', 'Example'),
                foreground_color=(0.32, 0.62, 0.29, 1)
            )
            name_input.bind(text=lambda instance, value, idx=i: self.update_category_name(idx, value))

            percent_input = Factory.BudgetEditCellInput(
                text=cat.get('percent', 'XX.XX%'),
                multiline=False,
                font_size='16sp',
                halign='center',
                foreground_color=(0.32, 0.62, 0.29, 1)
            )
            percent_input.bind(text=lambda instance, value, idx=i: self.update_category_percent(idx, value))

            delete_btn = Button(
                size_hint=(None, None),
                size=(dp(22), dp(22)),
                background_normal='resources/Images/trash_icon.png',
                background_down='resources/Images/trash_icon.png',
                background_color=(1, 1, 1, 1),
                border=(0, 0, 0, 0)
            )
            delete_btn.bind(on_release=lambda instance, idx=i: self.delete_category(idx))

            gap = Widget(size_hint=(None, None), size=(dp(30), dp(26)))
            row.add_widget(name_input)
            row.add_widget(gap)
            row.add_widget(percent_input)
            row.add_widget(delete_btn)
            grid.add_widget(row)

    def update_category_name(self, index: int, value: str):
        if 0 <= index < len(self.categories):
            self.categories[index]['name'] = value

    def update_category_percent(self, index: int, value: str):
        if 0 <= index < len(self.categories):
            self.categories[index]['percent'] = value

    def delete_category(self, index: int):
        if 0 <= index < len(self.categories):
            del self.categories[index]
            self.refresh_category_rows()

    def add_category(self):
        """Open the Add Category popup"""
        try:
            if len(self.categories) >= self.max_categories:
                return
            self.categories.append({"name": "Example", "percent": "XX.XX%"})
            self.refresh_category_rows()
        except Exception as e:
            print(f"Add Category error: {e}")

    def save_edit(self):
        """Save changes and return to view screen"""
        app = App.get_running_app()
        try:
            sm = app.shell.ids.sm
            budget_screen = sm.get_screen('budget')

            # Update main budget screen with edited data
            budget_screen.current_budget = self.ids.current_input.text
            budget_screen.monthly_budget = self.ids.monthly_input.text
            monthly_amount = self._parse_currency(self.ids.monthly_input.text)
            saved_categories = []
            for cat in self.categories:
                percent_text = cat.get('percent', '0%')
                percent_value = self._parse_percent(percent_text)
                remaining_amount = monthly_amount * (percent_value / 100.0)
                saved_categories.append({
                    "name": cat.get('name', 'Example'),
                    "percent": percent_text,
                    "remaining": self._format_currency(remaining_amount),
                })

            budget_screen.categories = saved_categories

            # Go back to view screen
            sm.current = 'budget'
        except Exception as e:
            print(f"Save error: {e}")

    @staticmethod
    def _parse_currency(value: str) -> float:
        cleaned = ''.join(ch for ch in value if ch.isdigit() or ch in '.-')
        try:
            return float(cleaned) if cleaned else 0.0
        except ValueError:
            return 0.0

    @staticmethod
    def _parse_percent(value: str) -> float:
        cleaned = ''.join(ch for ch in value if ch.isdigit() or ch in '.-')
        try:
            return float(cleaned) if cleaned else 0.0
        except ValueError:
            return 0.0

    @staticmethod
    def _format_currency(value: float) -> str:
        return f"$ {value:,.2f}"

    def cancel_edit(self):
        """Discard changes and go back"""
        app = App.get_running_app()
        try:
            app.shell.ids.sm.current = 'budget'
        except Exception:
            pass
