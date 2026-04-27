from kivy.uix.widget import Widget
from kivy.uix.screenmanager import Screen
from kivy.properties import StringProperty, ListProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.factory import Factory
from kivy.uix.button import Button
from kivy.metrics import dp
from kivy.app import App
from kivy.uix.popup import Popup
from kivy.uix.label import Label


class BudgetEditScreen(Screen):
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
                width=dp(350),
                spacing=dp(8)
            )

            name_input = Factory.BudgetEditNameInput(
                text=cat.get('name', ''),
                foreground_color=(0.32, 0.62, 0.29, 1)
            )
            name_input.bind(text=lambda instance, value, idx=i: self.update_category_name(idx, value))

            percent_input = Factory.BudgetEditCellInput(
                text=cat.get('percent', '0%'),
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

            gap = Widget(size_hint=(None, None), size=(dp(22), dp(26)))
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
            self.categories.append({"name": "", "percent": "0%"})
            self.refresh_category_rows()
        except Exception as e:
            print(f"Add Category error: {e}")

    def save_edit(self):
        """Save changes and return to view screen"""
        app = App.get_running_app()
        try:
            sm = app.shell.ids.sm
            budget_screen = sm.get_screen('budget')

            monthly_amount = self._parse_currency(self.ids.monthly_input.text)
            if monthly_amount <= 0:
                self._show_error("Monthly budget must be greater than 0.")
                return

            normalized_categories = []
            for cat in self.categories:
                name = cat.get('name', '').strip()
                if not name:
                    self._show_error("Category name cannot be empty.")
                    return

                percent_value = self._parse_percent(cat.get('percent', '0%'))
                if percent_value < 0 or percent_value > 100:
                    self._show_error("Each category percent must be between 0 and 100.")
                    return

                normalized_categories.append({
                    'name': name,
                    'percent_value': percent_value,
                    'percent_text': f"{percent_value:.2f}%",
                })

            total_percent = sum(cat['percent_value'] for cat in normalized_categories)
            if total_percent > 100:
                self._show_error("Total category percent cannot exceed 100%.")
                return

            # Update main budget screen with edited data
            budget_screen.monthly_budget = self.ids.monthly_input.text
            saved_categories = []
            for cat in normalized_categories:
                percent_text = cat['percent_text']
                percent_value = cat['percent_value']
                remaining_amount = monthly_amount * (percent_value / 100.0)
                saved_categories.append({
                    "name": cat['name'],
                    "percent": percent_text,
                    "remaining": self._format_currency(remaining_amount),
                })

            budget_screen.categories = saved_categories
            budget_screen.recalculate_current_budget()

            # Go back to view screen
            sm.current = 'budget'
        except Exception as e:
            print(f"Save error: {e}")

    def _show_error(self, message: str):
        popup = Popup(
            title='Invalid Categories',
            content=Label(text=message, halign='center', valign='middle'),
            size_hint=(None, None),
            size=(dp(360), dp(180)),
            auto_dismiss=True,
        )
        popup.content.bind(size=lambda instance, value: setattr(instance, 'text_size', value))
        popup.open()

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
