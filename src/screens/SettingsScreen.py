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
        # Load settings toggles from storage
        try:
            with shelve.open(WALLET_DATA_PATH) as wallet_data:
                require_pw = wallet_data.get("settings.require_password_on_start", False)
                hide_bal = wallet_data.get("settings.hide_balances", False)
                offline = wallet_data.get("settings.offline_mode", False)
            # Update toggles if present
            if self.ids.get("require_password_switch") is not None:
                self.ids.require_password_switch.active = bool(require_pw)
            if self.ids.get("hide_balances_switch") is not None:
                self.ids.hide_balances_switch.active = bool(hide_bal)
            if self.ids.get("offline_switch") is not None:
                self.ids.offline_switch.active = bool(offline)
        except Exception:
            pass

    # --- Helpers to persist/load simple settings ---
    def _save_setting(self, key, value):
        try:
            with shelve.open(WALLET_DATA_PATH) as wallet_data:
                settings = wallet_data.get("settings", {}) or {}
                settings[key] = value
                wallet_data["settings"] = settings
        except Exception:
            pass

    def _load_setting(self, key, default=None):
        try:
            with shelve.open(WALLET_DATA_PATH) as wallet_data:
                settings = wallet_data.get("settings", {}) or {}
                return settings.get(key, default)
        except Exception:
            return default

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

        # --- Settings handlers ---
        def on_require_password_toggle(self, active: bool):
            try:
                with shelve.open(WALLET_DATA_PATH) as wallet_data:
                    wallet_data["settings.require_password_on_start"] = bool(active)
                show_info_dialog("Security Updated", "Password requirement on startup has been updated.")
            except Exception:
                pass

        def on_hide_balances_toggle(self, active: bool):
            try:
                with shelve.open(WALLET_DATA_PATH) as wallet_data:
                    wallet_data["settings.hide_balances"] = bool(active)
                # Apply to wallet screen immediately if available
                try:
                    wallet_screen = self.manager.get_screen("wallet_screen") if self.manager else None
                    if wallet_screen and hasattr(wallet_screen, "set_hide_balances"):
                        wallet_screen.set_hide_balances(bool(active))
                except Exception:
                    pass
                show_info_dialog("Privacy Updated", "Balance visibility setting updated.")
            except Exception:
                pass

        def on_offline_mode_toggle(self, active: bool):
            try:
                with shelve.open(WALLET_DATA_PATH) as wallet_data:
                    wallet_data["settings.offline_mode"] = bool(active)
                show_info_dialog("Network Mode", "Offline mode preference saved. Please restart to fully apply.")
            except Exception:
                pass

        def clear_cache(self):
            import os
            import shutil

            removed = 0
            try:
                root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
                for dirpath, dirnames, filenames in os.walk(root_dir):
                    # Remove __pycache__
                    if "__pycache__" in dirnames:
                        cache_path = os.path.join(dirpath, "__pycache__")
                        try:
                            shutil.rmtree(cache_path, ignore_errors=True)
                            removed += 1
                        except Exception:
                            pass
                show_info_dialog("Cache Cleared", f"Cleared {removed} cache folder(s).")
            except Exception:
                show_info_dialog("Cache", "Unable to clear cache. You can safely ignore this.")

        def test_webcam(self):
            try:
                if self.manager:
                    self.manager.current = "camera_scan_screen"
            except Exception:
                pass

    # --- New settings actions ---
    def set_autolock_timeout(self, seconds: int):
        self._save_setting("auto_lock_timeout", int(seconds))
        try:
            show_info_dialog("Security", f"Auto-lock set to {int(seconds)} seconds.")
        except Exception:
            pass

    def on_hide_balances(self, active: bool):
        self._save_setting("hide_balances", 1 if active else 0)
        try:
            show_info_dialog("Privacy", "Balances will be hidden" if active else "Balances will be visible")
        except Exception:
            pass

    def on_camera_enabled(self, active: bool):
        self._save_setting("camera_enabled", 1 if active else 0)
        try:
            show_info_dialog("Permissions", "Camera scanning enabled" if active else "Camera scanning disabled")
        except Exception:
            pass

    def cycle_xrpl_node(self):
        # Simple cycle between known servers
        servers = [
            "https://testnet.xrpl-labs.com",
            "https://s.altnet.rippletest.net:51234",
            "https://testnet.xrplapi.com",
        ]
        current = self._load_setting("xrpl_server", servers[0])
        try:
            idx = (servers.index(current) + 1) % len(servers)
        except ValueError:
            idx = 0
        new_server = servers[idx]
        self._save_setting("xrpl_server", new_server)
        try:
            show_info_dialog("Network", f"Switched XRPL server to:\n{new_server}")
        except Exception:
            pass

    def export_logs(self):
        # Minimal log export stub
        try:
            os.makedirs("logs", exist_ok=True)
            with open(os.path.join("logs", "app.log"), "a", encoding="utf-8") as f:
                f.write("Log export marker from SettingsScreen.export_logs()\n")
            show_info_dialog("Maintenance", "Logs exported to logs/app.log")
        except Exception:
            pass

    def clear_cache(self):
        # Minimal cache clear: remove __pycache__ and *.pyc in src/
        import shutil
        import glob
        try:
            for path in glob.glob("src/**/__pycache__", recursive=True):
                shutil.rmtree(path, ignore_errors=True)
            for pyc in glob.glob("**/*.pyc", recursive=True):
                try:
                    os.remove(pyc)
                except Exception:
                    pass
            show_info_dialog("Maintenance", "Cache cleared")
        except Exception:
            pass

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
