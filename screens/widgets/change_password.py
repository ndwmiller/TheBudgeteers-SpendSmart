from kivy.uix.modalview import ModalView
from kivy.properties import ObjectProperty, StringProperty
from kivy.app import App
from kivy.lang import Builder
import os

# Load the kv file once when this module is first imported.
# This is the same pattern app_shell.py uses: Builder.load_file("app_shell.kv")
_kv_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "change_password.kv")
Builder.load_file(_kv_path)


class ChangePassword(ModalView):
    """
    Change Password modal for SpendSmart Settings.
    Author: Sakhi Hussain
    """

    main_app = ObjectProperty(None)
    error_msg = StringProperty('')

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.main_app = App.get_running_app()

    def on_open(self):
        """Clear all fields and errors every time the modal opens."""
        self.ids.old_pw.text = ''
        self.ids.new_pw.text = ''
        self.ids.confirm_pw.text = ''
        self.error_msg = ''

    def submit_data(self):
        """Validate inputs then save new password."""
        old_pw     = self.ids.old_pw.text.strip()
        new_pw     = self.ids.new_pw.text.strip()
        confirm_pw = self.ids.confirm_pw.text.strip()

        # ── Validation ──────────────────────────────────────────
        if not old_pw or not new_pw or not confirm_pw:
            self.error_msg = 'Please fill in all fields.'
            return

        if new_pw != confirm_pw:
            self.error_msg = 'New passwords do not match.'
            return

        if len(new_pw) < 6:
            self.error_msg = 'Password must be at least 6 characters.'
            return

        # ── Save to DB (uncomment when database.py is wired up) ─
        # app = App.get_running_app()
        # if not app.db.verify_password(old_pw):
        #     self.error_msg = 'Old password is incorrect.'
        #     return
        # app.db.cursor.execute("UPDATE users SET password=?", (new_pw,))
        # app.db.connection.commit()

        self.error_msg = ''
        self.dismiss()
