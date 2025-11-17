# Kivy libraries for the GUI.
# Encryption libraries for password and key encryption.
import logging
import shelve
from kivy.uix.screenmanager import Screen
from kivymd.uix.list import MDListItem, MDListItemHeadlineText, MDListItemTrailingIcon
from kivymd.uix.textfield import MDTextField

from src.utils.dialogs import show_confirm_dialog, show_info_dialog
from src.utils.storage_paths import WALLET_DATA_PATH

logging.basicConfig(level=logging.WARNING)


# Settings Screen
class SettingsScreen(Screen):
    def on_pre_enter(self, *args):
        # Populate the accounts list each time we enter
        self.refresh_account_list()

    def refresh_account_list(self):
        accounts_list = self.ids.get("accounts_list")
        if not accounts_list:
            return

        # Clear existing items
        accounts_list.clear_widgets()

        # Load accounts from storage
        accounts = []
        active_index = 0
        with shelve.open(WALLET_DATA_PATH) as wallet_data:
            stored_accounts = wallet_data.get("accounts")
            active_index = wallet_data.get("active_account", 0) or 0

            if stored_accounts and isinstance(stored_accounts, list):
                accounts = stored_accounts
            else:
                # Fallback for legacy data: build from primary fields if available
                primary_addr = wallet_data.get("xrp_address")
                if primary_addr:
                    accounts = [
                        {
                            "address": primary_addr,
                            "public_key": wallet_data.get("public_key", ""),
                            "private_key": wallet_data.get("private_key", ""),
                            "name": wallet_data.get("account_name", "Primary Account"),
                        }
                    ]
                    wallet_data["accounts"] = accounts
                    wallet_data["active_account"] = 0

        # Build list items
        for idx, acct in enumerate(accounts):
            name = acct.get("name", f"Account {idx+1}")
            address = acct.get("address", "")
            addr_short = (
                f"{address[:10]}...{address[-10:]}" if address and len(address) > 22 else address
            )
            primary_mark = " (Active)" if idx == active_index else ""

            item_text = (
                f"{name}{primary_mark}\n{addr_short}" if addr_short else f"{name}{primary_mark}"
            )

            item = MDListItem()
            item.add_widget(MDListItemHeadlineText(text=item_text))
            # Use a single trailing control per Material 3 rules
            item.add_widget(
                MDListItemTrailingIcon(
                    icon="dots-vertical", on_release=lambda w, i=idx: self.open_account_actions(i)
                )
            )
            accounts_list.add_widget(item)

    # --- Rename flow ---
    def open_rename_dialog(self, index: int):
        # Find current name
        with shelve.open(WALLET_DATA_PATH) as wallet_data:
            accounts = wallet_data.get("accounts", []) or []
            if index < 0 or index >= len(accounts):
                return
            current_name = accounts[index].get("name", f"Account {index+1}")

        self._rename_field = MDTextField(hint_text="New account name", text=current_name)
        show_confirm_dialog(
            title="Rename Account",
            content=self._rename_field,
            confirm_text="Save",
            cancel_text="Cancel",
            on_confirm=lambda: self._perform_rename(None, index),
            dismiss_on_confirm=True,
        )

    def _perform_rename(self, dialog, index: int):
        new_name = (self._rename_field.text or "").strip()
        if not new_name:
            self._show_toast_dialog("Invalid Name", "Please enter a non-empty name.")
            return

        with shelve.open(WALLET_DATA_PATH) as wallet_data:
            accounts = wallet_data.get("accounts", []) or []
            if index < 0 or index >= len(accounts):
                return

            # Duplicate name check (case-insensitive), excluding current index
            existing_names = [
                a.get("name", "").strip().lower() for i, a in enumerate(accounts) if i != index
            ]
            if new_name.strip().lower() in existing_names:
                self._show_toast_dialog(
                    "Duplicate Name", f"An account named '{new_name}' already exists."
                )
                return

            # Apply rename
            accounts[index]["name"] = new_name
            wallet_data["accounts"] = accounts
            if index == 0:
                wallet_data["account_name"] = new_name

        if dialog:
            dialog.dismiss()
        self.refresh_account_list()

    # --- Delete flow ---
    def open_delete_dialog(self, index: int):
        show_confirm_dialog(
            title="Delete Account",
            text="Are you sure you want to delete this account? This action cannot be undone.",
            confirm_text="Delete",
            cancel_text="Cancel",
            on_confirm=lambda: self._perform_delete(None, index),
            dismiss_on_confirm=True,
        )

    def _perform_delete(self, dialog, index: int):
        with shelve.open(WALLET_DATA_PATH) as wallet_data:
            accounts = wallet_data.get("accounts", []) or []
            active_index = wallet_data.get("active_account", 0) or 0

            if index < 0 or index >= len(accounts):
                return

            # Remove account
            accounts.pop(index)

            if not accounts:
                # No accounts left: reset to new user phase
                # Clear wallet fields
                for key in [
                    "xrp_address",
                    "public_key",
                    "private_key",
                    "seed",
                    "mnemonic",
                    "account_name",
                    "accounts",
                    "active_account",
                    "encryption_key",
                ]:
                    if key in wallet_data:
                        try:
                            del wallet_data[key]
                        except Exception:
                            wallet_data.pop(key, None)

                dialog.dismiss()
                # Navigate to first use screen
                self.manager.current = "first_use_screen"
                return

            # Adjust active index
            if index < active_index:
                active_index -= 1
            elif index == active_index:
                active_index = 0  # default to first account

            # Update primary fields to reflect first account
            first = accounts[0]
            wallet_data["xrp_address"] = first.get("address", "")
            wallet_data["public_key"] = first.get("public_key", "")
            wallet_data["account_name"] = first.get("name", "Primary Account")

            wallet_data["accounts"] = accounts
            wallet_data["active_account"] = active_index

        if dialog:
            dialog.dismiss()
        self.refresh_account_list()

    def open_account_actions(self, index: int):
        # Compact actions dialog: Rename (confirm), Delete (secondary)
        show_confirm_dialog(
            title="Account Actions",
            text="Choose an action for this account.",
            confirm_text="Rename",
            cancel_text="Close",
            secondary_text="Delete",
            on_confirm=lambda: self.open_rename_dialog(index),
            on_secondary=lambda: self.open_delete_dialog(index),
            dismiss_on_confirm=True,
        )

    def _show_toast_dialog(self, title, message):
        show_info_dialog(title=title, text=message)

    def walletscreen(self):
        self.manager.current = "wallet_screen"

    def nftmintscreen(self):
        self.manager.current = "nftmint_screen"

    def createimportwalletscreen(self):
        self.manager.current = "createimportwallet_screen"

    def dextradescreen(self):
        self.manager.current = "dextrade_screen"

    def foodtrackscreen(self):
        self.manager.current = "foodtrack_screen"
