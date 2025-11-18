# Kivy libraries for the GUI.
# Encryption libraries for password and key encryption.
import logging

from kivy.uix.screenmanager import Screen

logging.basicConfig(level=logging.WARNING)


# Wallet Setup Screen
class WalletSetupScreen(Screen):
    def create_wallet_screen(self):
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
                is_first_account=True,
                return_screen="wallet_screen",
                created_new_wallet=True,
            )
            self.manager.current = "mnemonic_display_screen"

        except Exception as e:
            print(f"Error generating wallet: {e}")

    def create_wallet_with_mnemonic(self):
        """Navigate to create wallet screen and generate with mnemonic."""
        self.manager.current = "create_wallet_screen"
        # Get the create wallet screen and call mnemonic generation
        create_screen = self.manager.get_screen("create_wallet_screen")
        # Use Clock to delay execution until screen is fully loaded
        from kivy.clock import Clock

        Clock.schedule_once(lambda dt: create_screen.generate_keys_with_mnemonic(), 0.5)

    def import_wallet_screen(self):
        # Route to ImportChoiceScreen for unified flow
        import_choice = self.manager.get_screen("import_choice_screen")
        import_choice.set_context(is_first_account=True, return_screen="wallet_screen")
        self.manager.current = "import_choice_screen"
