from kivy.uix.screenmanager import Screen
from kivy.properties import ListProperty, StringProperty


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

    def open_edit_budget(self):
        # Hook for future edit-budget flow.
        return None
