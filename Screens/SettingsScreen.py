# Kivy libraries for the GUI.
from kivy.uix.screenmanager import Screen

# Encryption libraries for password and key encryption.
import logging
logging.basicConfig(level=logging.WARNING)

# Settings Screen
class SettingsScreen(Screen):
    def walletscreen(self):
        self.manager.current = "wallet_screen"

    def nftmintscreen(self):
        self.manager.current = "nftmint_screen"

    def createimportwalletscreen(self):
        self.manager.current = "createimportwallet_screen"

    def dextradescreen(self):
        self.manager.current = "dextrade_screen"

    def foodtrackscreen(self):
        self.manager.current = "foodtrack_screen"