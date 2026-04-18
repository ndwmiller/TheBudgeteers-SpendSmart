# helper function for formatting date inputs
from kivy.uix.textinput import TextInput
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
        # returns error if invalid
        val = self.text.strip()
        
        # regex to only allow proper data format
        date_pattern = r"^\d{2}/\d{2}/\d{4}$"
        if not re.match(date_pattern, val):
            return "Date must be MM/DD/YYYY."
        month, day, year = map(int, val.split('/'))
        if not (1 <= month <= 12 and 1 <= day <= 31):
            return "Please enter a valid date."

        return None # valid date