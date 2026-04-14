from app_shell import AppShell
# from database import databaseClassName
from kivy.app import App
from kivy.core.window import Window
from kivy.properties import StringProperty
import os


class SpendSmartApp(App):
    # keeps path to project root
    base_path = StringProperty(os.path.dirname(os.path.abspath(__file__)))

    def build(self):
        # initialize database here. this is just an example, it may end up looking different
        # db_file = os.path.join(self.base_path, "resources", "data", "databaseName.db") 
        # self.db = databaseClassName(db_file)

        # initialize the UI shell
        self.shell = AppShell()
        return self.shell
    
    # close the conncetion to the DB here
    # def on_stop(self):
        # if hasattr(self, 'db'):
            # self.db.close()
    
    
if __name__ == "__main__":
    SpendSmartApp().run()