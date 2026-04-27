from kivy.uix.screenmanager import Screen
from kivy.app import App
from kivy.clock import Clock
from kivy.properties import StringProperty

# DO NOT call Builder.load_file here.
# app_shell.kv already has:  #:include screens/settings_screen.kv
# Adding Builder.load_file too causes a double-load which silently
# breaks ALL on_release / on_active callbacks — they fire but root
# resolves to the wrong (duplicate) rule set and nothing happens.

from screens.widgets import ResetAppData, ResetDefaults
from .settings_backend import SettingsBackend


class SettingsScreen(Screen, SettingsBackend):

    current_theme = StringProperty('dark')

    def on_enter(self):
        self.app = App.get_running_app()
        Clock.schedule_once(lambda dt: self.load_settings_from_db())

    def open_reset_app_data(self):
        popup = ResetAppData()
        popup.open()

    def open_reset_defaults(self):
        popup = ResetDefaults()
        popup.callback = self.reset_defaults
        popup.open()
