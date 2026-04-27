from kivy.app import App
from kivy.core.window import Window
from kivy.properties import BooleanProperty, ListProperty, StringProperty
from kivy.uix.floatlayout import FloatLayout
from kivy.graphics import PushMatrix, PopMatrix, Scale, Translate, Color, Rectangle
from kivy import utils as kivy_utils
from kivy.metrics import sp
import os

from database import Database

_ORIGINAL_GET_COLOR_FROM_HEX = kivy_utils.get_color_from_hex

_DARK_THEME_COLOR_MAP = {
    '#4d4d4d': '#2F2F2F',
    '#d7d7d7': '#4D4D4D',
    '#ffffff': '#3D3D3D',
    '#656565': '#E6E6E6',
    '#c8e6c2': '#516951',
    '#daffc8': '#365C35',
    '#abff80': '#4A7A46',
    '#faeaea': '#5B3E3E',
    '#ffd7d7': '#7A4A4A',
}


def themed_get_color_from_hex(hex_value):
    app = App.get_running_app()
    if app and getattr(app, 'theme', 'light') == 'dark':
        mapped = _DARK_THEME_COLOR_MAP.get(str(hex_value).lower(), hex_value)
        return _ORIGINAL_GET_COLOR_FROM_HEX(mapped)
    return _ORIGINAL_GET_COLOR_FROM_HEX(hex_value)


kivy_utils.get_color_from_hex = themed_get_color_from_hex

from app_shell import AppShell

# background color constants for themes
DARK_BACK = (0.302, 0.302, 0.302, 1)
LIGHT_BACK = (0.8, 0.8, 0.8, 1)

WINDOW_SIZE = (1920, 1160)
Window.size = WINDOW_SIZE
Window.clearcolor = DARK_BACK

# scales the design (1920x1160) to fit any window size.
# uses canvas matrix transforms for rendering and manually inverse-transforms
class GlobalScaler(FloatLayout):
    bg_color = ListProperty(DARK_BACK)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Window.bind(on_resize=self.recompute_scale)
        self.bind(bg_color=lambda *args: self.recompute_scale())
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
            Color(*self.bg_color)
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
    # makes the db a property of the app
    db = None
    theme = StringProperty('dark')
    font_setting = StringProperty('medium')
    alerts_enabled = BooleanProperty(True)
    reminders_enabled = BooleanProperty(False)
    # keeps path to project root
    base_path = StringProperty(os.path.dirname(os.path.abspath(__file__)))

    def build(self):
        # sets path for database
        data_dir = os.path.join(os.path.dirname(__file__), "resources", "data")
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)
        
        db_path = os.path.join(data_dir, "spendsmart.db")

        # initialize database
        self.db = Database(db_path)
        self.theme = self.db.get_setting('theme') or 'dark'
        self.font_setting = self.db.get_setting('font') or 'medium'
        self.alerts_enabled = (self.db.get_setting('alerts') != 'False')
        self.reminders_enabled = (self.db.get_setting('reminders') == 'True')


        # initialize the UI shell
        root = GlobalScaler(bg_color=LIGHT_BACK if self.theme == 'light' else DARK_BACK)
        self._scaler = root
        self.shell = AppShell()
        self.shell.size_hint = (None, None)
        self.shell.size = WINDOW_SIZE
        
        root.add_widget(self.shell)
        self.apply_font_size(self.font_setting)
        root.recompute_scale()
        return root

    def apply_theme(self, theme, rebuild=True):
        previous_theme = self.theme
        self.theme = theme
        Window.clearcolor = LIGHT_BACK if theme == 'light' else DARK_BACK
        if self.root:
            self.root.bg_color = LIGHT_BACK if theme == 'light' else DARK_BACK
        if rebuild and previous_theme != theme and self.root:
            self.rebuild_shell()

    def apply_font_size(self, size_name):
        size_name = (size_name or 'medium').lower()
        self.font_setting = size_name
        multiplier_map = {
            'small': 0.92,
            'medium': 1.0,
            'large': 1.12,
        }
        multiplier = multiplier_map.get(size_name, 1.0)
        if getattr(self, 'shell', None):
            self.apply_font_size_to_widget(self.shell, multiplier)

    def apply_notification_settings(self, alerts=None, reminders=None):
        if alerts is not None:
            self.alerts_enabled = alerts
        if reminders is not None:
            self.reminders_enabled = reminders

    def apply_font_size_to_widget(self, widget, multiplier):
        for child in widget.walk():
            if hasattr(child, 'font_size'):
                if not hasattr(child, '_base_font_size'):
                    current = child.font_size
                    if isinstance(current, str):
                        current = sp(current.replace('sp', ''))
                    child._base_font_size = float(current)
                child.font_size = child._base_font_size * multiplier

    def rebuild_shell(self):
        root = self.root if self.root else getattr(self, '_scaler', None)
        if not root or not getattr(self, 'shell', None):
            return

        current_screen = 'dashboard'
        if hasattr(self.shell, 'ids') and 'sm' in self.shell.ids:
            current_screen = self.shell.ids.sm.current

        old_shell = self.shell
        root.remove_widget(old_shell)

        new_shell = AppShell()
        new_shell.size_hint = (None, None)
        new_shell.size = WINDOW_SIZE
        root.add_widget(new_shell)
        self.shell = new_shell
        new_shell.ids.sm.current = current_screen
        self.apply_font_size(self.font_setting)
    
    # close the conncetion to the DB when app closed
    def on_stop(self):
        if self.db:
            self.db.connection.close()
    
    
if __name__ == "__main__":
    SpendSmartApp().run()
