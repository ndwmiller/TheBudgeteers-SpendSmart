from kivy.uix.modalview import ModalView
from kivy.properties import ObjectProperty
from kivy.app import App
from kivy.lang import Builder
import os

# Load kv once on import — same pattern as app_shell.py Builder.load_file()
_kv_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "change_password.kv")
Builder.load_file(_kv_path)


class ChangePassword(ModalView):
    # lets you reference the main app or a specific screen
    callback = ObjectProperty(None)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def clear_error(self):
        # remove error message
        self.ids.error_label.text = ""

    def submit_data(self):
        # reset all app data
        # app = App.get_running_app()
        # app.db.cursor.execute("DELETE FROM transactions")
        # app.db.cursor.execute("DELETE FROM budgets")
        # app.db.cursor.execute("DELETE FROM bills")
        # app.db.cursor.execute("DELETE FROM goals")
        # app.db.connection.commit()

        self.dismiss()

    def on_open(self):
        # clear error every time modal opens
        self.ids.error_label.text = ""
