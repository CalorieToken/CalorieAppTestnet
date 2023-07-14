# Kivy libraries for the GUI.
from kivy.uix.screenmanager import Screen

# Encryption libraries for password and key encryption.
import logging
logging.basicConfig(level=logging.WARNING)
import string
import shelve
import bcrypt

# First Use Screen
class FirstUseScreen(Screen):
    def create_password(self):
        password = self.ids.password.text
        confirm_password = self.ids.confirm_password.text

        # Check if password meets the conditions for a difficult password
        if not any(char.isupper() for char in password):
            self.ids.password.helper_text = "Password must contain at least one uppercase letter."
            return
        if not any(char.isdigit() for char in password):
            self.ids.password.helper_text = "Password must contain at least one number."
            return
        if not any(char in string.punctuation for char in password):
            self.ids.password.helper_text = "Password must contain at least one symbol."
            return
        if len(password) < 8:
            self.ids.password.helper_text = "Password must be at least 8 characters long."
            return

        # Check if password and confirmation password match
        if password != confirm_password:
            self.ids.confirm_password.helper_text = "Password and confirmation password must match."
            return

        # Hash the password using bcrypt before storing it
        hashed_password = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())

        # Use password to encrypt private keys
        self.wallet_data = shelve.open("wallet_data")
        self.wallet_data["password"] = hashed_password
        self.wallet_data.close()
        self.manager.current = "wallet_setup_screen"