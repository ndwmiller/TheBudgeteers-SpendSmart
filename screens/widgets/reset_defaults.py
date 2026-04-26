from kivy.uix.modalview import ModalView
from kivy.properties import ObjectProperty
from kivy.lang import Builder
import os

_kv_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "reset_defaults.kv")
Builder.load_file(_kv_path)


class ResetDefaults(ModalView):
    callback = ObjectProperty(None)

    def submit_data(self):
        if self.callback:
            self.callback()
        self.dismiss()
