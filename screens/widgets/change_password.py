from kivy.uix.modalview import ModalView
from kivy.properties import ObjectProperty
from kivy.app import App

class ChangePassword(ModalView):
    # lets you reference the main app or a specific screen
    main_app = ObjectProperty(None)

    # constructor so that modal view actually shows up
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.main_app = App.get_running_app()

    def submit_data(self):
        # save to sql logic
        self.dismiss()

    def on_open(self):
        # on open popup logic
        pass