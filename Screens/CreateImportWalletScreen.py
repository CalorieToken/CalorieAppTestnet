# Kivy libraries for the GUI.
from kivy.uix.screenmanager import Screen

# Create/Import Wallet Screen
class CreateImportWalletScreen(Screen):

    def create_extrawallet_screen(self):
        self.manager.current = "create_extrawallet_screen"
    
    def import_extrawallet_screen(self):
        self.manager.current = "importextrakeys_screen"

    def walletscreen(self):
        self.manager.current = "wallet_screen"

    def nftmintscreen(self):
        self.manager.current = "nftmint_screen"

    def dextradescreen(self):
        self.manager.current = "dextrade_screen"

    def foodtrackscreen(self):
        self.manager.current = "foodtrack_screen"

    def settingsscreen(self):
        self.manager.current = "settings_screen"