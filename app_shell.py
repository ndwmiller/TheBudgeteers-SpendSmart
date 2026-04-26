from kivy.uix.boxlayout import BoxLayout
from kivy.lang.builder import Builder
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.image import Image
from kivy.clock import Clock
from kivy.app import App
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
    def on_kv_post(self, base_widget):
        screen_manager = self.ids.get('sm')
        if screen_manager:
            screen_manager.bind(current=self._on_screen_change)
            Clock.schedule_once(lambda dt: self._apply_font_size())

    def _on_screen_change(self, *args):
        Clock.schedule_once(lambda dt: self._apply_font_size())

    def _apply_font_size(self):
        app = App.get_running_app()
        if app:
            app.apply_font_size(app.font_setting)

Builder.load_file("app_shell.kv")
