# helper function for formatting date inputs
from kivy.uix.textinput import TextInput
from datetime import datetime
import re

class DateInput(TextInput):
    def insert_text(self, substring, from_undo=False):
        # only allow numbers
        if not substring.isdigit():
            return
        
        s = self.text + substring
        # adds slashes at 2nd and 5th characters
        if len(s) in [2, 5]:
            substring += '/'
        # limit to 10 characters
        if len(s) > 10:
            return
            
        return super().insert_text(substring, from_undo=from_undo)

    def do_backspace(self, from_undo=False, mode='bkspc'):
        # delete the slash and the number after it on backspace
        if len(self.text) in [3,6]:
            self.text = self.text[:-1]
        return super().do_backspace(from_undo, mode)
    
    def get_validation_error(self):
        val = self.text.strip()
        if not re.match(r"^\d{2}/\d{2}/\d{4}$", val):
            return "Date must be MM/DD/YYYY."
        try:
            datetime.strptime(val, "%m/%d/%Y")
        except ValueError:
            return "Please enter a valid date."
        return None