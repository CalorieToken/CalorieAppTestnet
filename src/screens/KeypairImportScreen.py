"""
Keypair Import Screen - Import account using public and private keys
"""

from types import SimpleNamespace

import xrpl
from kivy.core.clipboard import Clipboard
from kivy.uix.screenmanager import Screen
from kivymd.uix.textfield import MDTextField
from xrpl.core.keypairs import derive_classic_address
from xrpl.wallet import Wallet

from src.utils.dialogs import show_error_dialog
from src.utils.storage_paths import WALLET_DATA_PATH
from src.utils.clipboard_utils import secure_copy


class KeypairImportScreen(Screen):
    """
    Screen for importing account using public and private keys.
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.is_first_account = True
        self.return_screen = "wallet_screen"

    def set_context(self, is_first_account=True, return_screen="wallet_screen"):
        """Set the context for this screen"""
        self.is_first_account = is_first_account
        self.return_screen = return_screen

    def import_from_keypair(self):
        """Import wallet from the entered public and private keys"""
        public_key_input = self.ids.get("public_key_input")
        private_key_input = self.ids.get("private_key_input")

        if not public_key_input or not private_key_input:
            self.show_error("Error", "Could not find input fields")
            return

        public_key = public_key_input.text.strip()
        private_key = private_key_input.text.strip()

        if not public_key or not private_key:
            self.show_error("Empty Input", "Please enter both public and private keys")
            return

        try:
            # Build a lightweight wallet-like object without seed
            classic_address = derive_classic_address(public_key)

            # Check if this account already exists
            import shelve

            with shelve.open(WALLET_DATA_PATH) as wallet_data:
                accounts = wallet_data.get("accounts", [])

                # Check if address already exists
                for account in accounts:
                    if account.get("address") == classic_address:
                        self.show_error(
                            "Duplicate Account",
                            f"This account is already imported!\n\nAccount: {classic_address[:10]}...{classic_address[-10:]}",
                        )
                        return

            wallet_like = SimpleNamespace(
                public_key=public_key, private_key=private_key, classic_address=classic_address
            )

            # Navigate to account naming screen
            naming_screen = self.manager.get_screen("account_naming_screen")
            naming_screen.set_account_data(
                wallet=wallet_like,
                mnemonic=None,  # No mnemonic for keypair import
                is_first_account=self.is_first_account,
                return_screen=self.return_screen,
            )
            self.manager.current = "account_naming_screen"

        except Exception as e:
            self.show_error(
                "Import Failed", f"Could not process keys: {str(e)}\n\nPlease check your keys."
            )

    def paste_public_key(self):
        try:
            text = Clipboard.paste()
            if text and "public_key_input" in self.ids:
                self.ids.public_key_input.text = text.strip()
                if "key_action_status" in self.ids:
                    self.ids.key_action_status.text = "📋 Pasted public key"
        except Exception:
            pass

    def paste_private_key(self):
        try:
            text = Clipboard.paste()
            if text and "private_key_input" in self.ids:
                self.ids.private_key_input.text = text.strip()
                if "key_action_status" in self.ids:
                    self.ids.key_action_status.text = "📋 Pasted private key"
        except Exception:
            pass

    def copy_public_key(self):
        try:
            if "public_key_input" in self.ids and self.ids.public_key_input.text:
                Clipboard.copy(self.ids.public_key_input.text.strip())
                if "key_action_status" in self.ids:
                    self.ids.key_action_status.text = "📋 Copied public key"
        except Exception:
            pass

    def copy_private_key(self):
        try:
            if "private_key_input" in self.ids and self.ids.private_key_input.text:
                secure_copy(self.ids.private_key_input.text.strip(), clear_after=30.0)
                if "key_action_status" in self.ids:
                    self.ids.key_action_status.text = "📋 Copied private key"
        except Exception:
            pass

    def show_error(self, title, message):
        """Show error dialog"""
        show_error_dialog(title, message)

    def go_back(self):
        """Go back to import choice screen"""
        # Clear inputs
        if hasattr(self.ids, "public_key_input"):
            self.ids.public_key_input.text = ""
        if hasattr(self.ids, "private_key_input"):
            self.ids.private_key_input.text = ""
        self.manager.current = "import_choice_screen"
