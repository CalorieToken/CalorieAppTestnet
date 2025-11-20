"""
Account Naming Screen - Add a personal name/label to the account
This is the final step before saving the account
"""

import shelve
from concurrent.futures import ThreadPoolExecutor

from cryptography.fernet import Fernet
from kivy.clock import Clock
from kivy.uix.screenmanager import Screen

from src.utils.dialogs import show_error_dialog, show_info_dialog
from src.utils.storage_paths import WALLET_DATA_PATH

# Faucet funding helper
try:
    from src.utils.faucet_manager import fund_existing_address_sync
except Exception:
    fund_existing_address_sync = None


class AccountNamingScreen(Screen):
    """
    Screen where user adds a personal name/label to their account.
    Final step before saving.
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.wallet = None
        self.mnemonic = None
        self.is_first_account = True
        self.return_screen = "wallet_screen"
        self.created_new_wallet = False

    def set_account_data(
        self,
        wallet,
        mnemonic=None,
        is_first_account=True,
        return_screen="wallet_screen",
        created_new_wallet=False,
    ):
        """
        Set the account data to be saved

        Args:
            wallet: XRPL Wallet object
            mnemonic: List of 12 words (optional, None for keypair imports)
            is_first_account: True if this is the first account
            return_screen: Where to go after saving
        """
        self.wallet = wallet
        self.mnemonic = mnemonic
        self.is_first_account = is_first_account
        self.return_screen = return_screen
        self.created_new_wallet = created_new_wallet

        # Update UI to show account address
        if hasattr(self.ids, "address_label"):
            self.ids.address_label.text = f"Account: {wallet.classic_address}"

    def save_account(self):
        """Save the account with the given name"""
        name_input = self.ids.get("account_name_input")

        if not name_input:
            self.show_error("Error", "Could not find name input field")
            return

        account_name = name_input.text.strip()

        if not account_name:
            self.show_error("Empty Name", "Please enter a name for this account")
            return

        try:
            # Save account to wallet data
            with shelve.open(WALLET_DATA_PATH) as wallet_data:
                # Check for duplicate name
                accounts = wallet_data.get("accounts", [])

                # Check if name already exists
                for account in accounts:
                    if account.get("name", "").lower() == account_name.lower():
                        self.show_error(
                            "Duplicate Name",
                            f"An account named '{account_name}' already exists.\n\nPlease choose a different name.",
                        )
                        return

                # Also check the primary account name if this is not the first account
                if not self.is_first_account:
                    primary_name = wallet_data.get("account_name", "")
                    if primary_name.lower() == account_name.lower():
                        self.show_error(
                            "Duplicate Name",
                            f"An account named '{account_name}' already exists.\n\nPlease choose a different name.",
                        )
                        return

                # Get encryption key
                encryption_key = wallet_data.get("encryption_key")
                if not encryption_key:
                    self.show_error("Error", "No encryption key found. Please restart setup.")
                    return

                cipher = Fernet(encryption_key)

                # Prepare account data
                account_data = {
                    "address": getattr(self.wallet, "classic_address", ""),
                    "public_key": getattr(self.wallet, "public_key", ""),
                    "private_key": cipher.encrypt(
                        getattr(self.wallet, "private_key", "").encode()
                    ).decode(),
                    "name": account_name,
                }
                # Optionally include seed if available (mnemonic-based accounts)
                if hasattr(self.wallet, "seed") and getattr(self.wallet, "seed"):
                    try:
                        account_data["seed"] = cipher.encrypt(self.wallet.seed.encode()).decode()
                    except Exception:
                        pass

                # Add mnemonic if available
                if self.mnemonic:
                    mnemonic_str = " ".join(self.mnemonic)
                    account_data["mnemonic"] = cipher.encrypt(mnemonic_str.encode()).decode()

                # Store account
                if self.is_first_account:
                    # This is the primary account
                    wallet_data["xrp_address"] = self.wallet.classic_address
                    wallet_data["public_key"] = self.wallet.public_key
                    wallet_data["private_key"] = cipher.encrypt(
                        self.wallet.private_key.encode()
                    ).decode()
                    if hasattr(self.wallet, "seed") and getattr(self.wallet, "seed"):
                        try:
                            wallet_data["seed"] = cipher.encrypt(self.wallet.seed.encode()).decode()
                        except Exception:
                            pass
                    wallet_data["account_name"] = account_name

                    if self.mnemonic:
                        mnemonic_str = " ".join(self.mnemonic)
                        wallet_data["mnemonic"] = cipher.encrypt(mnemonic_str.encode()).decode()

                    # Initialize accounts list
                    wallet_data["accounts"] = [account_data]
                    wallet_data["active_account"] = 0
                else:
                    # This is an extra account
                    accounts = wallet_data.get("accounts", [])
                    accounts.append(account_data)
                    wallet_data["accounts"] = accounts
                    # Set this as active account
                    wallet_data["active_account"] = len(accounts) - 1

            # Show success and navigate
            self.show_success()

        except Exception as e:
            self.show_error("Save Failed", f"Could not save account: {str(e)}")

    def show_success(self):
        """Show success message and navigate"""
        # Display a non-blocking success dialog (if available) but do not
        # require user interaction to proceed. Immediately navigate to wallet.
        try:
            show_info_dialog(
                title="Success!",
                text="Account saved successfully!\n\nOpening your wallet...",
            )
        except Exception:
            pass
        # Proceed directly
        self.continue_to_wallet(None)

    def continue_to_wallet(self, dialog):
        """Continue to wallet screen"""
        if dialog:
            dialog.dismiss()

        # Clear input
        if hasattr(self.ids, "account_name_input"):
            self.ids.account_name_input.text = ""

        # Navigate to wallet immediately
        self.manager.current = "wallet_screen"
        wallet_screen = self.manager.get_screen("wallet_screen")
        if hasattr(wallet_screen, "refresh_account_data"):
            wallet_screen.refresh_account_data()

        # Auto-fund via faucet in background (non-blocking)
        if (self.is_first_account or self.created_new_wallet) and fund_existing_address_sync is not None:
            self._start_background_funding(wallet_screen)

    def show_error(self, title, message):
        """Show error dialog"""
        show_error_dialog(title=title, text=message)

    def _start_background_funding(self, wallet_screen):
        """Start faucet funding in background without blocking UI."""
        address = getattr(self.wallet, "classic_address", None)
        if not address or fund_existing_address_sync is None:
            return

        # Show non-blocking progress notification
        from src.utils.enhanced_dialogs import show_progress_dialog
        progress_dialog = show_progress_dialog(
            title="Funding Wallet",
            message="Requesting testnet XRP from faucet...\nThis runs in background."
        )

        # Auto-dismiss progress dialog after 2 seconds
        Clock.schedule_once(lambda dt: progress_dialog.dismiss() if progress_dialog else None, 2.0)

        # Run funding in background thread
        from threading import Thread

        def _do_fund():
            try:
                status = fund_existing_address_sync(address)
            except Exception as e:
                status = f"❌ Faucet error: {str(e)[:50]}"

            # Schedule UI update on main thread
            Clock.schedule_once(
                lambda dt: self._on_funding_complete(status, wallet_screen),
                0
            )

        Thread(target=_do_fund, daemon=True).start()

    def _on_funding_complete(self, status, wallet_screen):
        """Called on main thread after funding completes"""
        # Show brief status notification
        show_info_dialog(
            title="Faucet Update",
            text=status
        )

        # Auto-dismiss after 2 seconds
        # Refresh balance
        if hasattr(wallet_screen, "check_balance"):
            Clock.schedule_once(lambda dt: wallet_screen.check_balance(dt=0), 0.5)

    def go_back(self):
        """Go back to previous screen"""
        # Clear input
        if hasattr(self.ids, "account_name_input"):
            self.ids.account_name_input.text = ""

        # Go back to verification screen if came from mnemonic creation
        # Or import choice if came from import
        if self.mnemonic:
            self.manager.current = "mnemonic_verify_screen"
        else:
            self.manager.current = "import_choice_screen"
