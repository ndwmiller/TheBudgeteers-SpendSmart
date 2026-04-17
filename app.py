from app_shell import AppShell
# from database import databaseClassName
from kivy.app import App
from kivy.core.window import Window
from kivy.properties import StringProperty
import os

# background color constants for themes
DARK_BACK = (0.2, 0.2, 0.2, 1)
LIGHT_BACK = (0.8, 0.8, 0.8, 1)

WINDOW_SIZE = (1920, 1160)
Window.size = WINDOW_SIZE
Window.clearcolor = DARK_BACK

# This makes the window scale correctly
from kivy.uix.scatterlayout import ScatterLayout
class GlobalScaler(ScatterLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.do_translation = False
        self.do_rotation = False
        self.do_scale = False
        Window.bind(on_resize=self.recompute_scale)
        self.design_size = WINDOW_SIZE
    def recompute_scale(self, *args):
        win_w, win_h = Window.size
        des_w, des_h = self.design_size
        self.size = self.design_size 
        scale = min(win_w / des_w, win_h / des_h)
        self.scale = scale
        self.pos = (win_w - des_w * scale) / 2, (win_h - des_h * scale) / 2

class SpendSmartApp(App):
    # keeps path to project root
    base_path = StringProperty(os.path.dirname(os.path.abspath(__file__)))

    def build(self):
        # initialize database here. this is just an example, it may end up looking different
        # db_file = os.path.join(self.base_path, "resources", "data", "databaseName.db") 
        # self.db = databaseClassName(db_file)

        # initialize the UI shell
        root = GlobalScaler()
        self.shell = AppShell()
        self.shell.size_hint = (None, None)
        self.shell.size = WINDOW_SIZE
        
        root.add_widget(self.shell)
        root.recompute_scale()
        return root
    
    # close the conncetion to the DB here
    # def on_stop(self):
        # if hasattr(self, 'db'):
            # self.db.close()
    
    
if __name__ == "__main__":
    SpendSmartApp().run()
