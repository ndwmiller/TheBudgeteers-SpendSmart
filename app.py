import app_shell
from kivy.app import App
from kivy.core.window import Window
from kivy.properties import StringProperty
import os


class SpendSmartApp(App):
    base_path = StringProperty(os.path.dirname(os.path.abspath(__file__)))

    def build(self):
        self.shell = app_shell.AppShell()
        return self.shell
    
if __name__ == "__main__":
    app = SpendSmartApp()
    app.run()