# Kivy libraries for the GUI.
import shelve

from kivy.uix.screenmanager import Screen
from kivymd.app import MDApp
from kivymd.uix.button import MDIconButton


# Create/Import Wallet Screen
class CreateImportWalletScreen(Screen):

    def on_pre_enter(self):
        """Check if user has existing wallets and handle navigation accordingly"""
        # The main app will handle navigation drawer enable/disable
        # based on wallet existence in the on_screen_change method
        pass

    def create_extrawallet_screen(self):
        # Generate new wallet with mnemonic and go directly to display screen
        from src.utils.mnemonic_manager import generate_wallet_with_mnemonic

        try:
            wallet, mnemonic = generate_wallet_with_mnemonic()

            # Navigate to mnemonic display screen
            display_screen = self.manager.get_screen("mnemonic_display_screen")
            display_screen.setup_mnemonic_display(
                wallet=wallet,
                mnemonic=mnemonic,
                source_screen=self.name,
                is_first_account=False,
                return_screen="wallet_screen",
                created_new_wallet=True,
            )
            self.manager.current = "mnemonic_display_screen"

        except Exception as e:
            print(f"Error generating wallet: {e}")

    def import_extrawallet_screen(self):
        # Route to ImportChoiceScreen for unified flow
        import_choice = self.manager.get_screen("import_choice_screen")
        import_choice.set_context(is_first_account=False, return_screen="wallet_screen")
        self.manager.current = "import_choice_screen"

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
