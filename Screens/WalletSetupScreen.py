# Kivy libraries for the GUI.
from kivy.uix.screenmanager import Screen

# Encryption libraries for password and key encryption.
import logging
logging.basicConfig(level=logging.WARNING)

# Wallet Setup Screen
class WalletSetupScreen(Screen):
    def create_wallet_screen(self):
        self.manager.current = "create_wallet_screen"
    
    def import_wallet_screen(self):
        self.manager.current = "importkeys_screen"
    