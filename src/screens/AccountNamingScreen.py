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
        show_info_dialog(
            title="Success!",
            text="Account saved successfully!\n\nYou can now use your wallet.",
            on_close=lambda: self.continue_to_wallet(None),
        )

    def continue_to_wallet(self, dialog):
        """Continue to wallet screen"""
        if dialog:
            dialog.dismiss()

        # Clear input
        if hasattr(self.ids, "account_name_input"):
            self.ids.account_name_input.text = ""

        # Auto-fund via faucet for first account or any newly generated extra wallet
        if (
            self.is_first_account or self.created_new_wallet
        ) and fund_existing_address_sync is not None:
            self._start_funding_then_navigate()
        else:
            # Navigate to wallet screen immediately
            self.manager.current = "wallet_screen"
            # Refresh wallet screen to show new account
            wallet_screen = self.manager.get_screen("wallet_screen")
            if hasattr(wallet_screen, "refresh_account_data"):
                wallet_screen.refresh_account_data()

    def show_error(self, title, message):
        """Show error dialog"""
        show_error_dialog(title=title, text=message)

    def _start_funding_then_navigate(self):
        """Show a short funding dialog and attempt faucet funding, then go to wallet."""
        # Show progress dialog
        progress_dialog = None
        try:
            # Inform user with a non-blocking info dialog
            show_info_dialog(
                title="Funding Wallet",
                text="Requesting XRP Testnet faucet...\nThis may take a few seconds.",
            )
        except Exception:
            pass

        address = getattr(self.wallet, "classic_address", None)
        if not address or fund_existing_address_sync is None:
            # If no address or helper missing, navigate immediately
            progress_dialog.dismiss()
            self.manager.current = "wallet_screen"
            wallet_screen = self.manager.get_screen("wallet_screen")
            if hasattr(wallet_screen, "refresh_account_data"):
                wallet_screen.refresh_account_data()
            return

        # Run the funding in a thread to avoid blocking UI
        def _do_fund():
            try:
                status = fund_existing_address_sync(address)
            except Exception:
                status = "❌ Faucet error - wallet remains unfunded"
            return status

        executor = ThreadPoolExecutor(max_workers=1)
        future = executor.submit(_do_fund)

        def _after_fund(dt):
            try:
                status = future.result(timeout=0)
            except Exception:
                status = "❌ Faucet error - wallet remains unfunded"
            # No persistent progress dialog to dismiss here

            # Optionally inform user of funding status
            show_info_dialog(title="Wallet Ready", text=f"{status}\n\nOpening your wallet...")

            # Navigate to wallet and refresh
            self.manager.current = "wallet_screen"
            wallet_screen = self.manager.get_screen("wallet_screen")
            if hasattr(wallet_screen, "refresh_account_data"):
                wallet_screen.refresh_account_data()
            # Trigger an immediate balance check if available
            try:
                from kivy.clock import Clock as _Clock

                if hasattr(wallet_screen, "check_balance"):
                    _Clock.schedule_once(lambda _dt: wallet_screen.check_balance(dt=0), 0)
            except Exception:
                pass

        # Poll future completion on the next frame until done
        def _poll_future(dt):
            if future.done():
                Clock.unschedule(_poll_future)
                _after_fund(0)

        Clock.schedule_interval(_poll_future, 0.2)

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
