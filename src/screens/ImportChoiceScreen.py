"""
Import Choice Screen - Choose between importing mnemonic or keypair
"""

from kivy.uix.screenmanager import Screen
from kivymd.uix.label import MDLabel


class ImportChoiceScreen(Screen):
    """
    Screen where user chooses between importing from mnemonic or keypair.
    Used for both first account and extra accounts.
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.is_first_account = True
        self.return_screen = "wallet_screen"

    def set_context(self, is_first_account=True, return_screen="wallet_screen"):
        """Set the context for this screen"""
        self.is_first_account = is_first_account
        self.return_screen = return_screen

    def choose_mnemonic_import(self):
        """User chose to import from 12-word mnemonic"""
        import_screen = self.manager.get_screen("mnemonic_import_screen")
        import_screen.set_context(
            is_first_account=self.is_first_account, return_screen=self.return_screen
        )
        self.manager.current = "mnemonic_import_screen"

    def choose_keypair_import(self):
        """User chose to import from keypair (seed/secret)"""
        # Navigate to keypair import screen
        keypair_screen = self.manager.get_screen("keypair_import_screen")
        keypair_screen.set_context(
            is_first_account=self.is_first_account, return_screen=self.return_screen
        )
        self.manager.current = "keypair_import_screen"

    def go_back(self):
        """Go back to the correct hub depending on flow.
        - First account flow: return to AccountChoice
        - Extra account flow: return to Create/Import Wallet hub
        """
        if self.is_first_account:
            self.manager.current = "account_choice_screen"
        else:
            self.manager.current = "createimportwallet_screen"
