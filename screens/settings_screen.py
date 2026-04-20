from kivy.uix.screenmanager import Screen
from kivy.app import App
from kivy.lang import Builder
from kivy.properties import StringProperty
import os

# Load the kv file once when this module is first imported.
_kv_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "settings_screen.kv")
Builder.load_file(_kv_path)

# Import AFTER Builder.load_file so that change_password.kv is also loaded
# before ChangePassword() is ever instantiated.
from screens.widgets import ChangePassword


class SettingsScreen(Screen):
    """
    Settings screen for SpendSmart.
    Author: Sakhi Hussain
    """

    current_theme = StringProperty('dark')

    # ── Lifecycle ────────────────────────────────────────────────
    def on_enter(self):
        # Sync UI state from DB / app state here when ready
        # app = App.get_running_app()
        # self.ids.budget_toggle.active = app.db.get_setting('budget_alerts')
        pass

    # ── Theme ────────────────────────────────────────────────────
    def set_theme(self, theme):
        from kivy.core.window import Window
        self.current_theme = theme
        if theme == 'light':
            Window.clearcolor = (0.8, 0.8, 0.8, 1)
        else:
            Window.clearcolor = (0.302, 0.302, 0.302, 1)
        # app = App.get_running_app()
        # app.db.cursor.execute("UPDATE settings SET theme=?", (theme,))
        # app.db.connection.commit()

    # ── Font size ────────────────────────────────────────────────
    def set_font_size(self, size_name):
        # app = App.get_running_app()
        # app.db.cursor.execute("UPDATE settings SET font_size=?", (size_name,))
        # app.db.connection.commit()
        pass

    # ── Notifications ────────────────────────────────────────────
    def toggle_budget_alerts(self, active):
        # app = App.get_running_app()
        # app.db.cursor.execute("UPDATE settings SET budget_alerts=?", (int(active),))
        # app.db.connection.commit()
        pass

    def toggle_bill_reminders(self, active):
        # app = App.get_running_app()
        # app.db.cursor.execute("UPDATE settings SET bill_reminders=?", (int(active),))
        # app.db.connection.commit()
        pass

    # ── Data management ──────────────────────────────────────────
    def clear_data(self):
        # app = App.get_running_app()
        # app.db.cursor.execute("DELETE FROM transactions")
        # app.db.cursor.execute("DELETE FROM budgets")
        # app.db.connection.commit()
        pass

    def reset_defaults(self):
        self.set_theme('dark')
        self.ids.dark_mode_cb.active  = True
        self.ids.light_mode_cb.active = False
        self.ids.font_spinner.text    = 'Medium'
        self.ids.budget_toggle.active = True
        self.ids.bill_toggle.active   = False

    def delete_account(self):
        # app = App.get_running_app()
        # app.db.cursor.execute("DELETE FROM users")
        # app.db.connection.commit()
        # app.root.current = 'login'
        pass

    # ── Password modal ───────────────────────────────────────────
    def open_change_password(self):
        """Instantiate and open the Change Password modal."""
        modal = ChangePassword()
        modal.open()
