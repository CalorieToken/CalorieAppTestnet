# Kivy libraries for the GUI.
import logging
import shelve

from kivy.uix.screenmanager import Screen

from src.utils.storage_paths import WALLET_DATA_PATH


# Intro Screen
class IntroScreen(Screen):
    def next(self):
        """Handle next button click - check for existing wallet and route accordingly"""
        try:
            with shelve.open(WALLET_DATA_PATH) as wallet_data:
                if "password" in wallet_data:
                    # Existing wallet found - go to login screen
                    self.manager.current = "login_screen"
                else:
                    # No password found - go to first use screen
                    self.manager.current = "first_use_screen"
        except Exception as e:
            logging.warning(f"Could not open wallet_data: {e}")
            # No wallet data file exists - new user, go to first use screen
            self.manager.current = "first_use_screen"
