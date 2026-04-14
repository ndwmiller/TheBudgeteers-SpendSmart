from kivy.uix.screenmanager import Screen
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.behaviors import ButtonBehavior
from kivy.properties import StringProperty
from .widgets import AddCategory

class BudgetScreen(Screen):
    # database access so that you can use app.db.cursor.execute(...)
    # def on_enter(self):
        # app = App.get_running_app()
    pass