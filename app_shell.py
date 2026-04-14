from kivy.uix.boxlayout import BoxLayout
from kivy.lang.builder import Builder
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.image import Image
from screens import DashboardScreen, BudgetScreen, GoalsScreen, TransactionsScreen, SettingsScreen
from kivy.properties import BooleanProperty, StringProperty

class AppShell(BoxLayout):
    pass

Builder.load_file("app_shell.kv")
