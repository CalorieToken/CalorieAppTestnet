# Kivy libraries for the GUI.
from kivy.uix.screenmanager import Screen

# Encryption libraries for password and key encryption.
import logging
logging.basicConfig(level=logging.WARNING)
import shelve
import shelve
import bcrypt

# Login Screen
class LoginScreen(Screen):
    def login(self):
        # Load the password hash from the file
        wallet_data = shelve.open("wallet_data")
        hashed_password = wallet_data.get("password")
        wallet_data.close()

        # Check if the password is correct
        password = self.ids.password.text.encode("utf-8")
        if not bcrypt.checkpw(password, hashed_password):

            self.password.hint_text = "Wrong password, try again"
            return

        # Navigate to the appropriate screen based on whether the keys are stored
        wallet_data = shelve.open("wallet_data")
        keys_available = [key for key in wallet_data.keys() if key.startswith("keys")]

        if not keys_available:
            wallet_data.close()
            self.manager.current = "wallet_setup_screen"
        else:
            # Determine the selected key based on your logic
            # For example, select the first key if available
            with shelve.open("wallet_data") as self.wallet_data:
                keys_available = [
                    key for key in self.wallet_data.keys() if key.startswith("public_key")
                ]
                if keys_available:
                    selected_key = keys_available[0]
                else:
                    selected_key = None

            # Go to "wallet_screen" and pass the selected key as a parameter
            self.manager.current = "wallet_screen"
            wallet_screen = self.manager.get_screen("wallet_screen")
            wallet_screen.set_selected_key(selected_key)

            # Call the on_pre_enter() method manually to update the address and balances
            wallet_screen.on_pre_enter()

       