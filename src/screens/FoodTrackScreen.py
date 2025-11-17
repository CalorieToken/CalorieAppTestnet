# Kivy libraries for the GUI.
# Encryption libraries for password and key encryption.
import logging

from kivy.uix.screenmanager import Screen

logging.basicConfig(level=logging.WARNING)


# Food Track Screen
class FoodTrackScreen(Screen):
    def walletscreen(self):
        self.manager.current = "wallet_screen"

    def nftmintscreen(self):
        self.manager.current = "nftmint_screen"

    def createimportwalletscreen(self):
        self.manager.current = "createimportwallet_screen"

    def dextradescreen(self):
        self.manager.current = "dextrade_screen"

    def settingsscreen(self):
        self.manager.current = "settings_screen"
