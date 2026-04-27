from kivy.uix.modalview import ModalView
from kivy.properties import ObjectProperty
from kivy.app import App
from kivy.lang import Builder
import os

# reset_app_data.kv is not included in app_shell.kv so we load it here
_kv_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "reset_app_data.kv")
Builder.load_file(_kv_path)


class ResetAppData(ModalView):
    callback = ObjectProperty(None)

    def clear_error(self):
        self.ids.error_label.text = ""

    def submit_data(self):
        App.get_running_app().db.clear_data()
        self.dismiss()

    def on_open(self):
        self.ids.error_label.text = ""
