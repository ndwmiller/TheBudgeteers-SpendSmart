from kivy.uix.screenmanager import Screen
from kivy.app import App
from kivy.lang import Builder
from kivy.properties import StringProperty
import os

# Load this screen's kv — same pattern as app_shell.py Builder.load_file()
_kv_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "settings_screen.kv")
Builder.load_file(_kv_path)

# Import AFTER Builder.load_file so change_password.kv is loaded
# before ChangePassword() is ever instantiated (fixes the crash)
from screens.widgets import ChangePassword


class SettingsScreen(Screen):
    # database access so that you can use app.db.cursor.execute(...)
    # def on_enter(self):
    #     app = App.get_running_app()

    current_theme = StringProperty('dark')

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

    def set_font_size(self, size_name):
        # app = App.get_running_app()
        # app.db.cursor.execute("UPDATE settings SET font_size=?", (size_name,))
        # app.db.connection.commit()
        pass

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

    def clear_data(self):
        # app = App.get_running_app()
        # app.db.cursor.execute("DELETE FROM transactions")
        # app.db.cursor.execute("DELETE FROM budgets")
        # app.db.connection.commit()
        pass

    def reset_defaults(self):
        from kivy.core.window import Window
        Window.clearcolor = (0.302, 0.302, 0.302, 1)
        self.current_theme = 'dark'
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

    def open_change_password(self):
        popup = ChangePassword()
        popup.open()
