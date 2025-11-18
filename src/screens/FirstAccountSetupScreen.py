"""
First Account Setup Screen - For new users creating their very first account
This screen has NO back button - users must complete account setup
"""

from kivy.uix.screenmanager import Screen

from src.utils.dialogs import show_error_dialog


class FirstAccountSetupScreen(Screen):
    """
    Screen for first-time users to create or import their first account.
    No back button - user must complete setup.
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def choose_import(self):
        """User chose to import an existing account"""
        # Navigate to import choice screen (mnemonic or keypair)
        import_choice_screen = self.manager.get_screen("import_choice_screen")
        import_choice_screen.set_context(is_first_account=True, return_screen="wallet_screen")
        self.manager.current = "import_choice_screen"

    def choose_create(self):
        """User chose to create a new account"""
        # Generate new wallet with mnemonic and go to display screen
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
            )
            self.manager.current = "mnemonic_display_screen"

        except Exception as e:
            print(f"Error generating wallet: {e}")
            show_error_dialog(title="Error", text=f"Failed to generate wallet: {str(e)}")
