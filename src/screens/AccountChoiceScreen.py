"""
Account Choice Screen - Choose between Import or Create
This screen is used for both initial setup and adding extra accounts
"""

from kivy.metrics import dp
from kivy.properties import BooleanProperty
from kivy.uix.screenmanager import Screen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel

from src.utils.dialogs import show_error_dialog
from src.utils.storage_paths import WALLET_DATA_PATH


class AccountChoiceScreen(Screen):
    """
    Screen where user chooses between importing or creating a new account.
    Used for both first account and extra accounts.
    """

    show_back_button = BooleanProperty(False)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.is_first_account = True  # Track if this is the first account or extra
        self.return_screen = "wallet_screen"  # Where to go after completion

    def on_enter(self):
        """Called when screen is entered"""
        # Update UI based on whether it's first account or extra
        if hasattr(self.ids, "title_label"):
            if self.is_first_account:
                self.ids.title_label.text = "Welcome! Let's set up your first wallet"
            else:
                self.ids.title_label.text = "Add Another XRPL Account"

        # Set back button visibility based on is_first_account
        self.show_back_button = not self.is_first_account

    def set_context(self, is_first_account=True, return_screen="wallet_screen"):
        """
        Set the context for this screen

        Args:
            is_first_account: True if this is initial setup, False if adding extra account
            return_screen: Screen name to return to after completion
        """
        self.is_first_account = is_first_account
        self.return_screen = return_screen
        self.show_back_button = not is_first_account

    def choose_import(self):
        """User chose to import an existing account"""
        # Navigate to import choice screen (mnemonic or keypair)
        import_choice_screen = self.manager.get_screen("import_choice_screen")
        import_choice_screen.set_context(
            is_first_account=self.is_first_account, return_screen=self.return_screen
        )
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
                is_first_account=self.is_first_account,
                return_screen=self.return_screen,
            )
            self.manager.current = "mnemonic_display_screen"

        except Exception as e:
            print(f"Error generating wallet: {e}")
            show_error_dialog(title="Error", text=f"Failed to generate wallet: {str(e)}")

    def go_back(self):
        """Go back to previous screen"""
        if self.is_first_account:
            # If a password already exists, do NOT go back to the create password screen.
            try:
                import shelve

                with shelve.open(WALLET_DATA_PATH) as db:
                    has_password = "password" in db and db["password"] is not None
            except Exception:
                has_password = False

            if has_password:
                # Route to Wallet Setup hub instead of Create Password screen
                self.manager.current = "wallet_setup_screen"
            else:
                # No password set yet; safe to return to first use/create password
                self.manager.current = "first_use_screen"
        else:
            # For extra accounts, return to the designated screen (usually wallet_screen)
            self.manager.current = self.return_screen
