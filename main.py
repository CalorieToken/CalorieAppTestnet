
# Kivy libraries for the GUI.
from kivymd.app import MDApp
from kivy.uix.screenmanager import ScreenManager
from kivy.core.window import Window


# Encryption libraries for password and key encryption.
import logging
logging.basicConfig(level=logging.WARNING)
import shelve

# Import screens from Screens folder.
from Screens.WalletScreen import WalletScreen
from Screens.SendXRPScreen import SendXRPScreen
from Screens.SendLipisaScreen import SendLipisaScreen
from Screens.SendCalorieTestScreen import SendCalorieTestScreen
from Screens.NFTMintScreen import NFTMintScreen
from Screens.CreateImportWalletScreen import CreateImportWalletScreen
from Screens.DEXTradeScreen import DEXTradeScreen
from Screens.FoodTrackScreen import FoodTrackScreen
from Screens.SettingsScreen import SettingsScreen
from Screens.IntroScreen import IntroScreen
from Screens.FirstUseScreen import FirstUseScreen
from Screens.WalletSetupScreen import WalletSetupScreen
from Screens.CreateWalletScreen import CreateWalletScreen
from Screens.CreateExtraWalletScreen import CreateExtraWalletScreen
from Screens.ImportExtraKeysScreen import ImportExtraKeysScreen
from Screens.ImportKeysScreen import ImportKeysScreen
from Screens.LoginScreen import LoginScreen

from xrpl.clients import JsonRpcClient

JSON_RPC_URL = "https://s.altnet.rippletest.net:51234"
client = JsonRpcClient(JSON_RPC_URL)

# Declare screens
wallet_screen = WalletScreen(client=client)
sendxrp_screen = SendXRPScreen(client=client)
sendlipisa_screen = SendLipisaScreen(client=client)
sendcalorietest_screen = SendCalorieTestScreen(client=client)
nftmint_screen = NFTMintScreen()
createimportwallet_screen = CreateImportWalletScreen()
dextrade_screen = DEXTradeScreen()
foodtrack_screen = FoodTrackScreen()
settings_screen = SettingsScreen()
intro_screen = IntroScreen()
first_use_screen = FirstUseScreen()
wallet_setup_screen = WalletSetupScreen()
create_wallet_screen = CreateWalletScreen()
create_extrawallet_screen = CreateExtraWalletScreen()
importkeys_screen = ImportKeysScreen()
importextrakeys_screen = ImportExtraKeysScreen()
login_screen = LoginScreen()

# Window size
Window.size = (300, 500)

# Main app class.           
class CalorieAppTestnetV11(MDApp):
    def build(self):
        JSON_RPC_URL = "https://s.altnet.rippletest.net:51234"
        client = JsonRpcClient(JSON_RPC_URL)
        self.title = "CalorieAppTestnetV11"
        self.theme_cls.primary_palette = "Green"
        self.theme_cls.accent_palette = "Green"
        self.theme_cls.material_style = "M2"
        self.load_kv('CalorieAppTestnetV11.kv')
        self.manager = ScreenManager()
        self.intro_screen = IntroScreen(name="intro_screen")
        self.first_use_screen = FirstUseScreen(name="first_use_screen")
        self.wallet_setup_screen = WalletSetupScreen(name="wallet_setup_screen")
        self.create_wallet_screen = CreateWalletScreen(name="create_wallet_screen")
        self.create_extrawallet_screen = CreateExtraWalletScreen(name="create_extrawallet_screen")
        self.importkeys_screen = ImportKeysScreen(name="importkeys_screen")
        self.importextrakeys_screen = ImportExtraKeysScreen(name="importextrakeys_screen")
        self.login_screen = LoginScreen(name="login_screen")
        self.wallet_screen = WalletScreen(client=client, name="wallet_screen")
        self.sendxrp_screen = SendXRPScreen(client=client, name="sendxrp_screen")
        self.sendlipisa_screen = SendLipisaScreen(client=client, name="sendlipisa_screen")
        self.sendcalorietest_screen = SendCalorieTestScreen(client=client, name="sendcalorietest_screen")
        self.nftmint_screen = NFTMintScreen(name="nftmint_screen")
        self.createimportwallet_screen = CreateImportWalletScreen(name="createimportwallet_screen")
        self.dextrade_screen = DEXTradeScreen(name="dextrade_screen")
        self.foodtrack_screen = FoodTrackScreen(name="foodtrack_screen")
        self.settings_screen = SettingsScreen(name="settings_screen")       
        self.manager.add_widget(self.intro_screen)
        self.manager.add_widget(self.first_use_screen)
        self.manager.add_widget(self.wallet_setup_screen)
        self.manager.add_widget(self.create_wallet_screen)
        self.manager.add_widget(self.create_extrawallet_screen)
        self.manager.add_widget(self.importkeys_screen)
        self.manager.add_widget(self.importextrakeys_screen)
        self.manager.add_widget(self.login_screen)
        self.manager.add_widget(self.wallet_screen)
        self.manager.add_widget(self.sendxrp_screen)
        self.manager.add_widget(self.sendlipisa_screen)
        self.manager.add_widget(self.sendcalorietest_screen)
        self.manager.add_widget(self.nftmint_screen)
        self.manager.add_widget(self.createimportwallet_screen)
        self.manager.add_widget(self.dextrade_screen)
        self.manager.add_widget(self.foodtrack_screen)
        self.manager.add_widget(self.settings_screen)
        try:
            self.wallet_data = shelve.open("wallet_data")
            if "password" in self.wallet_data:
                self.manager.current = "login_screen"
            else:
                self.manager.current = "intro_screen"
        except:
            self.manager.current = "intro_screen"
        finally:
            self.wallet_data.close()
        return self.manager
    
    def on_stop(self):
        self.wallet_data.close()
    

if __name__ == "__main__":
    CalorieAppTestnetV11().run()