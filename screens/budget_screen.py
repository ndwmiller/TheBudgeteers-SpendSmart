from kivy.app import App
from kivy.uix.screenmanager import Screen
from kivy.properties import ListProperty, StringProperty
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.factory import Factory
from kivy.metrics import dp


class BudgetScreen(Screen):
    current_budget = StringProperty("$ XXXX.XX")
    monthly_budget = StringProperty("$ XXXX.XX")
    categories = ListProperty([
        {"name": "Example", "percent": "XX.XX%", "remaining": "$ XXXXX.XX"},
        {"name": "Example", "percent": "XX.XX%", "remaining": "$ XXXXX.XX"},
        {"name": "Example", "percent": "XX.XX%", "remaining": "$ XXXXX.XX"},
        {"name": "Example", "percent": "XX.XX%", "remaining": "$ XXXXX.XX"},
        {"name": "Example", "percent": "XX.XX%", "remaining": "$ XXXXX.XX"},
    ])

    def get_category_value(self, index, key, default=""):
        if index < len(self.categories):
            return self.categories[index].get(key, default)
        return default

    def on_kv_post(self, base_widget):
        self.recalculate_current_budget()
        self.refresh_category_rows()

    def on_categories(self, instance, value):
        self.recalculate_current_budget()
        self.refresh_category_rows()

    def recalculate_current_budget(self):
        total_remaining = 0.0
        for cat in self.categories:
            total_remaining += self._parse_currency(cat.get('remaining', '$ 0.00'))
        self.current_budget = self._format_currency(total_remaining)

    def refresh_category_rows(self):
        grid = self.ids.get('categories_grid')
        if not grid:
            return

        grid.clear_widgets()

        for cat in self.categories:
            row = BoxLayout(
                orientation='horizontal',
                spacing=dp(20),
                size_hint_y=None,
                height=dp(26),
                
            )

            name_label = Label(
                text='• ' + cat.get('name', 'Example'),
                color=(0.32, 0.62, 0.29, 1),
                font_size='16sp',
                bold=False,
                halign='center',
                valign='middle',
                text_size=(0, 0),
                size_hint_x=0.33,
            )
            name_label.bind(size=lambda instance, value: setattr(instance, 'text_size', value))

            percent_col = AnchorLayout(size_hint_x=0.33, anchor_x='center', anchor_y='center')
            percent_chip = Factory.BudgetChipLabel(
                text=cat.get('percent', 'XX.XX%'),
                size_hint=(None, 1),
                width=dp(105),
            )
            percent_col.add_widget(percent_chip)

            remaining_col = AnchorLayout(size_hint_x=0.34, anchor_x='center', anchor_y='center')
            remaining_chip = Factory.BudgetChipLabel(
                text=cat.get('remaining', '$ XXXXX.XX'),
                size_hint=(None, 1),
                width=dp(120),
            )
            remaining_col.add_widget(remaining_chip)

            row.add_widget(name_label)
            row.add_widget(percent_col)
            row.add_widget(remaining_col)
            grid.add_widget(row)

    def open_edit_budget(self):
        app = App.get_running_app()
        app.shell.ids.sm.current = 'budget_edit'
        return None

    @staticmethod
    def _parse_currency(value: str) -> float:
        cleaned = ''.join(ch for ch in value if ch.isdigit() or ch in '.-')
        try:
            return float(cleaned) if cleaned else 0.0
        except ValueError:
            return 0.0

    @staticmethod
    def _format_currency(value: float) -> str:
        return f"$ {value:,.2f}"
