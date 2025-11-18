# Kivy libraries for the GUI.
# Encryption libraries for password and key encryption.
import logging

from kivy.uix.screenmanager import Screen
from kivymd.uix.button import MDIconButton

logging.basicConfig(level=logging.WARNING)
import shelve

import bcrypt

from src.utils.storage_paths import WALLET_DATA_PATH


# Login Screen
class LoginScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.password_visible = False

    def toggle_password_visibility(self):
        """Toggle password visibility and update the eye icon"""
        self.password_visible = not self.password_visible

        # Toggle the password field visibility
        if hasattr(self.ids, "password_input"):
            self.ids.password_input.password = not self.password_visible

        # Update the eye icon
        if hasattr(self.ids, "password_toggle_icon"):
            if self.password_visible:
                self.ids.password_toggle_icon.icon = "eye-off"
            else:
                self.ids.password_toggle_icon.icon = "eye"

    def check_login(self):
        """Check login - alias for login() method for KV file compatibility"""
        self.login()

    def login(self):
        # Load the password hash from the file
        wallet_data = shelve.open(WALLET_DATA_PATH)
        hashed_password = wallet_data.get("password")
        wallet_data.close()

        # Check if the password is correct
        password = self.ids.password_input.text.encode("utf-8")
        if not bcrypt.checkpw(password, hashed_password):

            self.ids.password_input.hint_text = "Wrong password, try again"
            return

        # Navigate based on new accounts model (preferred) or legacy
        with shelve.open(WALLET_DATA_PATH) as db:
            accounts = db.get("accounts")
            if accounts and isinstance(accounts, list) and len(accounts) > 0:
                # Go straight to wallet using active account
                self.manager.current = "wallet_screen"
                wallet_screen = self.manager.get_screen("wallet_screen")
                wallet_screen.refresh_account_data()

                # Enable navigation drawer since user is now logged in
                from kivymd.app import MDApp

                app = MDApp.get_running_app()
                if hasattr(app, "enable_navigation_drawer"):
                    app.enable_navigation_drawer()
                wallet_screen.on_pre_enter()
                return

            # Legacy fallback: check for public_key* entries
            keys_available = [key for key in db.keys() if key.startswith("public_key")]
            if keys_available:
                selected_key = keys_available[0]
                self.manager.current = "wallet_screen"
                wallet_screen = self.manager.get_screen("wallet_screen")
                wallet_screen.set_selected_key(selected_key)

                from kivymd.app import MDApp

                app = MDApp.get_running_app()
                if hasattr(app, "enable_navigation_drawer"):
                    app.enable_navigation_drawer()
                wallet_screen.on_pre_enter()
                return

        # If no accounts or legacy keys, route to account choice to set up first account
        account_choice_screen = self.manager.get_screen("account_choice_screen")
        account_choice_screen.set_context(is_first_account=True, return_screen="wallet_screen")
        self.manager.current = "account_choice_screen"
