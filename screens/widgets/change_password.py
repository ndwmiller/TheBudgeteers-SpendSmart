from kivy.uix.modalview import ModalView
from kivy.properties import ObjectProperty, StringProperty
from kivy.app import App
from kivy.lang import Builder
import os

# Load kv once on import — same pattern as app_shell.py Builder.load_file()
_kv_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "change_password.kv")
Builder.load_file(_kv_path)


class ChangePassword(ModalView):
    # lets you reference the main app or a specific screen
    main_app = ObjectProperty(None)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.main_app = App.get_running_app()

    def clear_error(self):
        # remove error when user types again — matches add_bill.py pattern
        self.ids.error_label.text = ""

    def submit_data(self):
        # get field values
        old_pw     = self.ids.old_pw.text.strip()
        new_pw     = self.ids.new_pw.text.strip()
        confirm_pw = self.ids.confirm_pw.text.strip()

        # fill validation
        if not old_pw or not new_pw or not confirm_pw:
            self.ids.error_label.text = "Please fill in all fields."
            return

        # match validation
        if new_pw != confirm_pw:
            self.ids.error_label.text = "New passwords do not match."
            return

        # length validation
        if len(new_pw) < 6:
            self.ids.error_label.text = "Password must be at least 6 characters."
            return

        # save to sql logic
        # app = App.get_running_app()
        # if not app.db.verify_password(old_pw):
        #     self.ids.error_label.text = "Old password is incorrect."
        #     return
        # app.db.cursor.execute("UPDATE users SET password=?", (new_pw,))
        # app.db.connection.commit()

        self.dismiss()

    def on_open(self):
        # clear fields every time modal opens
        self.ids.old_pw.text     = ""
        self.ids.new_pw.text     = ""
        self.ids.confirm_pw.text = ""
        self.ids.error_label.text = ""
