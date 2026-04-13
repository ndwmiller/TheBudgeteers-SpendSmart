from kivy.uix.boxlayout import BoxLayout
from kivy.lang.builder import Builder
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.image import Image
from screens.transactions_screen import HomeScreen
from screens.dashboard_screen import AddPotScreen
from screens.budget_screen import PlantDetailScreen
from screens.settings_screen import SettingsScreen

from kivy.properties import BooleanProperty, StringProperty


Builder.load_file("app_shell.kv")
