from kivy.uix.boxlayout import BoxLayout
from kivy.lang.builder import Builder
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.image import Image
from screens import DashboardScreen, BudgetScreen, BudgetEditScreen, GoalsScreen, TransactionsScreen, SettingsScreen
from kivy.properties import BooleanProperty, StringProperty

# image button for settings gear
class ImageButton(ButtonBehavior, Image):
    def on_press(self):
        self.opacity = 0.5
        return super().on_press()

    def on_release(self):
        self.opacity = 1.0
        return super().on_release()

class AppShell(BoxLayout):
    pass

Builder.load_file("app_shell.kv")
