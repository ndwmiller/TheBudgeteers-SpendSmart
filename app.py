from app_shell import AppShell
# from database import databaseClassName
from kivy.app import App
from kivy.core.window import Window
from kivy.properties import StringProperty
from kivy.uix.floatlayout import FloatLayout
from kivy.graphics import PushMatrix, PopMatrix, Scale, Translate, Color, Rectangle
import os

# background color constants for themes
DARK_BACK = (0.302, 0.302, 0.302, 1)
LIGHT_BACK = (0.8, 0.8, 0.8, 1)

WINDOW_SIZE = (1920, 1160)
Window.size = WINDOW_SIZE
Window.clearcolor = DARK_BACK

# scales the design (1920x1160) to fit any window size.
# uses canvas matrix transforms for rendering and manually inverse-transforms
class GlobalScaler(FloatLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Window.bind(on_resize=self.recompute_scale)
        self.design_size = WINDOW_SIZE
        self._scale = 1.0
        self._offset_x = 0.0
        self._offset_y = 0.0

    def recompute_scale(self, *args):
        win_w, win_h = Window.size
        des_w, des_h = self.design_size
        self.size = (win_w, win_h)
        scale = min(win_w / des_w, win_h / des_h)
        self._scale = scale
        self._offset_x = (win_w - des_w * scale) / 2
        self._offset_y = (win_h - des_h * scale) / 2
        self.canvas.before.clear()
        self.canvas.after.clear()
        with self.canvas.before:
            Color(*DARK_BACK)
            Rectangle(pos=(0, 0), size=(win_w, win_h))
            PushMatrix()
            Translate(self._offset_x, self._offset_y)
            Scale(scale, scale, 1)
        with self.canvas.after:
            PopMatrix()

    # tells Kivy's coordinate system about our canvas scaling.
    def to_local(self, x, y, relative=False):
        if relative:
            return x / self._scale, y / self._scale
        return (x - self._offset_x) / self._scale, (y - self._offset_y) / self._scale

    def to_parent(self, x, y, relative=False):
        if relative:
            return x * self._scale, y * self._scale
        return x * self._scale + self._offset_x, y * self._scale + self._offset_y

    def on_touch_down(self, touch):
        touch.push()
        touch.apply_transform_2d(self.to_local)
        ret = super().on_touch_down(touch)
        touch.pop()
        return ret

    def on_touch_move(self, touch):
        touch.push()
        touch.apply_transform_2d(self.to_local)
        ret = super().on_touch_move(touch)
        touch.pop()
        return ret

    def on_touch_up(self, touch):
        touch.push()
        touch.apply_transform_2d(self.to_local)
        ret = super().on_touch_up(touch)
        touch.pop()
        return ret

class SpendSmartApp(App):
    # keeps path to project root
    base_path = StringProperty(os.path.dirname(os.path.abspath(__file__)))

    def build(self):
        # initialize database
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
