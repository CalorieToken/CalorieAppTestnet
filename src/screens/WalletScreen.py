# Kivy libraries for the GUI.
import logging
import os

# Encryption libraries for password and key encryption.
import bcrypt
from kivy.clock import Clock
from kivy.core.clipboard import Clipboard
from kivy.metrics import dp
from kivy.properties import ObjectProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import Screen
from kivy.uix.scrollview import ScrollView
from kivy.utils import get_color_from_hex
from kivymd.uix.list import MDList, MDListItem, MDListItemHeadlineText, MDListItemLeadingIcon
from kivymd.uix.textfield import MDTextField

from src.utils.currency_utils import decode_currency_code
from src.utils.dialogs import show_confirm_dialog
from src.utils.performance import debounce, async_operation, lazy_property

logging.basicConfig(level=logging.WARNING)
import shelve
from contextlib import contextmanager

# XRPL libraries for xrpl functionality
import xrpl
from Crypto.Cipher import AES
from Crypto.Protocol.KDF import PBKDF2
from cryptography.fernet import Fernet
from kivy.graphics import Color, Rectangle
from kivy.uix.widget import Widget
from xrpl.core.keypairs import derive_classic_address
from xrpl.models.requests import AccountInfo, AccountTx
from xrpl.models.requests.account_objects import AccountObjects
from xrpl.transaction import submit_and_wait
from xrpl.wallet import Wallet

from src.utils.storage_paths import WALLET_DATA_PATH

# Import the robust XRPL client manager
from src.utils.xrpl_client_manager import get_global_client_manager, is_online, make_request

JSON_RPC_URL = "https://testnet.xrpl-labs.com"  # Use XRPL Labs testnet (more reliable)


# Create client with better timeout handling
@contextmanager
def safe_client():
    """Context manager for safe XRPL client operations with timeout handling"""
    try:
        # Use the robust client manager instead of creating new clients
        client_manager = get_global_client_manager()
        client = client_manager.get_client()
        if client:
            yield client
        else:
            print("No XRPL client available")
            yield None
    except Exception as e:
        print(f"Client connection error: {e}")
        yield None


# Global client with fallback - now uses the robust client manager
try:
    client_manager = get_global_client_manager()
    client = client_manager.get_client()
except Exception as e:
    print(f"Failed to initialize XRPL client: {e}")
    client = None


class WalletScreen(Screen):
    # KV ids (labels) placeholders to satisfy static analysis
    xrp_address = ObjectProperty(None)
    xrp_balance = ObjectProperty(None)

    def __init__(self, client, **kwargs):
        super().__init__(**kwargs)
        self.client = client
        self.wallet_data = None
        self.selected_key: str | None = None
        self.menu = None  # legacy dropdown removed; using MDDialog selector
        self.check_balance_event = None
        self.network_retry_count = 0
        self.max_retries = 3
        self.offline_mode = False
        self.public_key: str | None = None
        self.private_key: str | None = None
        self.account_name: str | None = None
        self.account_dialog = None
        self.hide_balances = False

    def set_address_text(self, address):
        """Helper to set address text on the MDLabel"""
        try:
            label = self.ids.get("xrp_address_label")
            if label:
                label.text = address
        except Exception:
            pass
    
    @lazy_property
    def balance_label(self):
        return self.ids.get("xrp_balance")

    def _update_balance_ui(self, result):
        """Callback to update UI after async balance check.

        Result can be a dict returned by the background task or None (legacy path).
        We defensively re-read current state if result is missing.
        """
        try:
            if isinstance(result, dict) and 'balance' in result:
                if self.balance_label:
                    self.balance_label.text = result['balance']
            else:
                # Fallback: leave existing text untouched or set generic if empty
                if self.balance_label and not self.balance_label.text:
                    self.balance_label.text = "--"
        except Exception:
            pass

    def set_hide_balances(self, hide: bool):
        self.hide_balances = bool(hide)
        try:
            bal = self.ids.get("xrp_balance")
            if bal:
                if self.hide_balances:
                    bal.text = "\u2022\u2022\u2022\u2022"  # ••••
                else:
                    # Leave actual balance; will be refreshed on next update
                    pass
        except Exception:
            pass

    def update_offline_mode(self, offline_mode):
        """Update offline mode status"""
        self.offline_mode = offline_mode

    def set_selected_key(self, selected_key):
        self.selected_key = selected_key

    def menu_open(self, caller):
        """Deprecated dropdown trigger retained for backward compatibility; now forwards to dialog."""
        self.open_account_selector()

    def open_account_selector(self):
        """Open an account selection dialog using non-deprecated components."""
        try:
            print("[UI] Opening account selector dialog...")
            root_box = BoxLayout(
                orientation="vertical", size_hint=(1, None), height=dp(420), padding=(dp(8), dp(6))
            )

            # Load account data once
            accounts_data = []  # list of dicts: {idx, name, addr, label, is_legacy}
            active_index = 0
            with shelve.open(WALLET_DATA_PATH) as db:
                active_index = db.get("active_account", 0)
                if "accounts" in db:
                    accounts = db.get("accounts", [])
                    for idx, acct in enumerate(accounts):
                        name = acct.get("name", f"Account {idx+1}")
                        try:
                            addr = derive_classic_address(acct.get("public_key", ""))
                        except Exception:
                            addr = "Unknown"
                        short_addr = f"{addr[:6]}…{addr[-6:]}" if len(addr) > 14 else addr
                        label = f"{name}  ({short_addr})"
                        accounts_data.append(
                            {
                                "idx": idx,
                                "name": name,
                                "addr": addr,
                                "label": label,
                                "is_legacy": False,
                            }
                        )
                else:
                    # legacy
                    keys_available = [key for key in db.keys() if key.startswith("public_key")]
                    for i, key in enumerate(keys_available):
                        try:
                            addr = derive_classic_address(db[key])
                        except Exception:
                            addr = "Unknown"
                        short_addr = f"{addr[:6]}…{addr[-6:]}" if len(addr) > 14 else addr
                        label = f"Imported: {short_addr}"
                        accounts_data.append(
                            {
                                "idx": i,
                                "name": "Imported key",
                                "addr": addr,
                                "key": key,
                                "label": label,
                                "is_legacy": True,
                            }
                        )

            # Search field
            search = MDTextField(hint_text="Search name or address", mode="filled")
            root_box.add_widget(search)

            # List container
            scroll = ScrollView(size_hint=(1, 1))
            mlist = MDList()
            scroll.add_widget(mlist)
            root_box.add_widget(scroll)

            def populate(filter_text: str = ""):
                mlist.clear_widgets()
                text = (filter_text or "").lower()
                added = 0
                for item in accounts_data:
                    if (
                        text
                        and text not in item["name"].lower()
                        and text not in item["addr"].lower()
                    ):
                        continue
                    label_txt = item["label"]
                    if not item.get("is_legacy") and item["idx"] == active_index:
                        label_txt = f"\u2713  {label_txt}"  # checkmark prefix
                    row = MDListItem()
                    row.add_widget(
                        MDListItemLeadingIcon(
                            icon=(
                                "key-variant" if item.get("is_legacy") else "account-circle-outline"
                            )
                        )
                    )
                    row.add_widget(MDListItemHeadlineText(text=label_txt))
                    if item.get("is_legacy"):
                        row.bind(
                            on_release=lambda w, k=item.get("key"): self._select_legacy_key_dialog(
                                k
                            )
                        )
                    else:
                        row.bind(on_release=lambda w, i=item["idx"]: self._select_account_dialog(i))
                    mlist.add_widget(row)
                    added += 1
                if added == 0:
                    row = MDListItem()
                    row.add_widget(MDListItemLeadingIcon(icon="magnify"))
                    row.add_widget(MDListItemHeadlineText(text="No matches"))
                    mlist.add_widget(row)

            # Bind search
            search.bind(text=lambda inst, val: populate(val))
            populate("")

            from kivymd.uix.dialog import MDDialog, MDDialogContentContainer, MDDialogHeadlineText

            self.account_dialog = MDDialog(
                md_bg_color=get_color_from_hex("#bfc6e0"), size_hint=(0.9, None)
            )
            self.account_dialog.add_widget(MDDialogHeadlineText(text="Select Account"))
            content_container = MDDialogContentContainer()
            content_container.add_widget(root_box)
            self.account_dialog.add_widget(content_container)
            self.account_dialog.open()

            # Auto-dismiss overlay during automated UX tour to avoid obstructing screenshots
            if os.environ.get("UX_TEST_MODE") == "1":
                Clock.schedule_once(self._auto_dismiss_account_dialog, 0.3)
        except Exception as e:
            print(f"[UI] Failed to open account selector dialog: {e}")
            from src.utils.dialogs import show_error_dialog

            try:
                show_error_dialog("Account Selector Error", f"Could not open selector. {e}")
            except Exception:
                pass

    def _select_account_dialog(self, index: int):
        try:
            if self.account_dialog:
                self.account_dialog.dismiss()
                self.account_dialog = None
        except Exception:
            pass
        self.select_account_by_index(index)

    def _auto_dismiss_account_dialog(self, *args):
        try:
            if self.account_dialog:
                self.account_dialog.dismiss()
                self.account_dialog = None
        except Exception:
            pass

    def _select_legacy_key_dialog(self, key: str):
        try:
            if self.account_dialog:
                self.account_dialog.dismiss()
                self.account_dialog = None
        except Exception:
            pass
        self.menu_callback(key)

    def on_key_selected(self, selected_key):
        with shelve.open("wallet_data") as self.wallet_data:
            if selected_key in self.wallet_data:
                try:
                    self.public_key = self.wallet_data[selected_key]
                    private_key_name = selected_key.replace("public", "private")
                    nonce_key_name = selected_key.replace("public", "nonce")
                    salt_key_name = selected_key.replace("public", "salt")

                    # Check if all required keys exist
                    if private_key_name in self.wallet_data:
                        self.private_key = self.wallet_data[private_key_name]
                    else:
                        return

                    if nonce_key_name in self.wallet_data:
                        self.nonce = self.wallet_data[nonce_key_name]
                    else:
                        return

                    if salt_key_name in self.wallet_data:
                        self.salt = self.wallet_data[salt_key_name]
                    else:
                        return

                except KeyError as e:
                    return
                except Exception as e:
                    return

        if self.public_key:

            def wallet_from_kp():
                classic_address = derive_classic_address(self.public_key)
                return classic_address

            test_wallet_address = wallet_from_kp()
            self.set_address_text(test_wallet_address)

            # Reset transaction history display
            for i in range(1, 21):
                lbl = self._get_tx_label(i)
                if lbl:
                    lbl.text = "Loading..."

            # Reset balance display
            self.xrp_balance.text = "Loading..."

            # Clear any existing balance check schedules
            if self.check_balance_event:
                Clock.unschedule(self.check_balance_event)

            # Start balance checking for the new wallet
            if not self.offline_mode and self.client:
                self.check_balance(dt=0)  # Check immediately
                self.check_balance_event = Clock.schedule_interval(self.check_balance, 30)
            else:
                self.xrp_balance.text = "Offline Mode"
                for i in range(1, 21):
                    lbl = self._get_tx_label(i)
                    if lbl:
                        lbl.text = "Offline Mode"

    def menu_callback(self, menu_item):
        self.selected_key = menu_item
        self.on_key_selected(self.selected_key)
        self.menu.dismiss()

        # Force an immediate balance check for the new wallet
        Clock.unschedule(self.check_balance)
        self.check_balance(dt=0)  # Check immediately
        self.check_balance_event = Clock.schedule_interval(self.check_balance, 30)

    def select_account_by_index(self, index: int):
        """Select account by index in new accounts list model."""
        try:
            with shelve.open(WALLET_DATA_PATH, writeback=True) as db:
                accounts = db.get("accounts", [])
                if not accounts:
                    return
                if index < 0 or index >= len(accounts):
                    return
                db["active_account"] = index

            # Close menu first
            if self.menu:
                self.menu.dismiss()

            # Use force_refresh which clears everything and reloads
            self.force_refresh()
        except Exception:
            pass

    def on_pre_enter(self, *args):
        """Called when screen is entered"""
        # Check if we're in offline mode from global settings
        try:
            from src.core.app import OFFLINE_MODE

            self.offline_mode = OFFLINE_MODE
        except Exception:
            self.offline_mode = self.client is None

        # Load account based on new model if available, else legacy
        self.refresh_account_data()

        # Only start balance checking if not in offline mode
        if not self.offline_mode and self.client:
            # Start with normal checking frequency for online mode
            self.check_balance(dt=0)
            Clock.schedule_interval(self.check_balance, 30)  # Check every 30 seconds
            # Refresh trustlines on screen enter
            Clock.schedule_once(lambda dt: self.refresh_trustlines(), 1)
        else:
            # Set offline status immediately
            self.xrp_balance.text = "Offline Mode"
            # Clear transaction history
            for i in range(1, 21):
                lbl = self._get_tx_label(i)
                if lbl:
                    lbl.text = "Offline Mode"

    def on_pre_leave(self, *args):
        """Called when leaving screen"""
        if self.check_balance_event:
            Clock.unschedule(self.check_balance)
            self.check_balance_event = None

    def force_refresh(self):
        """Force refresh all account data - call this after switching accounts"""
        # Clear existing transaction history display
        for i in range(1, 21):
            lbl = self._get_tx_label(i)
            if lbl:
                lbl.text = ""

        # Clear trustlines display
        container = self.ids.get("trustlines_container")
        if container:
            container.clear_widgets()

        # Reload account data FIRST
        self.refresh_account_data()

        # Immediate balance check if online
        if not self.offline_mode and self.client:
            Clock.unschedule(self.check_balance)
            self.check_balance(dt=0)
            Clock.schedule_interval(self.check_balance, 30)
            Clock.schedule_once(lambda dt: self.refresh_trustlines(), 0.5)
        Clock.unschedule(self.check_balance)

    @async_operation(callback='_update_balance_ui')
    def check_balance(self, dt):
        # Check offline mode
        try:
            from src.core.app import OFFLINE_MODE

            general_offline = OFFLINE_MODE
        except Exception as e:
            general_offline = True

        # Quick exit for general offline mode
        if general_offline or not self.client:
            return

        try:
            # Ensure we have a public key selected; try refresh if using new model
            if not self.public_key:
                self.refresh_account_data()
                if not self.public_key:
                    return

            # If we've had too many network failures, reduce checking frequency and show status
            if self.network_retry_count >= self.max_retries:
                self.xrp_balance.text = "Network Issues - Will Retry Later"
                # Only check every 60 seconds instead of 30 when having network issues
                if hasattr(self, "_last_check_time"):
                    import time

                    if time.time() - self._last_check_time < 60:
                        return
                import time

                self._last_check_time = time.time()

            # Load current account (new model preferred)
            with shelve.open("wallet_data") as db:
                if "accounts" in db:
                    accounts = db.get("accounts", [])
                    idx = db.get("active_account", 0)
                    if 0 <= idx < len(accounts):
                        self.public_key = accounts[idx].get("public_key")
                    else:
                        self.public_key = None
                else:
                    if self.selected_key in db:
                        self.public_key = db[self.selected_key]

            def wallet_from_kp():
                classic_address = derive_classic_address(self.public_key)
                return classic_address

            test_wallet_address = wallet_from_kp()

            # Check if client is available using robust client manager
            if not is_online():
                self.xrp_balance.text = "Network Unavailable"
                return

            acct_info = AccountInfo(
                account=test_wallet_address,
                ledger_index="validated",
                strict=True,
            )

            try:
                # Use robust client manager that handles server failover
                response = make_request(acct_info)

                # Reset retry count on successful connection
                self.network_retry_count = 0

                # Check if response is successful and contains account data
                if hasattr(response, "status") and response.status.name == "SUCCESS":
                    data = response.result
                    if "account_data" in data and "Balance" in data["account_data"]:
                        # Divide the balance by 1 million to convert to units of 1
                        balance = format(int(data["account_data"]["Balance"]) / 1e6, ".2f")
                        self.xrp_balance.text = str(balance)
                    else:
                        self.xrp_balance.text = "0.00"
                elif hasattr(response, "result") and "error" in response.result:
                    error_code = response.result["error"]
                    if error_code == "actNotFound":
                        self.xrp_balance.text = "0.00 (Account not funded)"
                    else:
                        self.xrp_balance.text = f"Error: {error_code}"
                else:
                    self.xrp_balance.text = "0.00"
            except Exception as account_error:
                self.network_retry_count += 1

                if self.network_retry_count >= self.max_retries:
                    self.xrp_balance.text = "Network Issues - Trying Alternative Servers"
                else:
                    self.xrp_balance.text = "Connecting..."

            # Transaction History (only if network is working)
            if self.network_retry_count < self.max_retries:
                try:
                    tx_info = AccountTx(
                        account=test_wallet_address,
                        ledger_index_min=-1,  # Search from earliest ledger
                        ledger_index_max=-1,  # Search to latest ledger
                        limit=100,  # Increase limit to get more transactions if available
                    )
                    # Use robust client manager for transaction history
                    response2 = make_request(tx_info)

                    # Check if response is successful
                    if hasattr(response2, "status") and response2.status.name == "SUCCESS":
                        data2 = response2.result

                        # Check if transactions exist
                        if "transactions" in data2 and data2["transactions"]:
                            transactions = data2["transactions"]

                            # Display transactions
                            for i, transaction in enumerate(transactions):
                                if i >= 20:  # Only show first 20 transactions
                                    break

                                # Handle both validated and unvalidated transactions
                                if "tx" in transaction:
                                    tx = transaction["tx"]
                                elif "tx_json" in transaction:
                                    tx = transaction["tx_json"]
                                elif "transaction" in transaction:
                                    tx = transaction["transaction"]
                                else:
                                    tx = transaction

                                label = self._get_tx_label(i + 1)
                                if label:

                                    # Parse transaction amount properly
                                    tx_type = tx.get("TransactionType", "Unknown")
                                    amount_text = ""
                                    direction = ""
                                    direction_icon = ""
                                    peer_address = ""

                                    # Check if this is a Payment transaction
                                    if tx_type == "Payment":
                                        # For Payment transactions, check the Amount field
                                        if "Amount" in tx:
                                            amount = tx["Amount"]
                                            if isinstance(amount, str) and amount.isdigit():
                                                # XRP amount in drops (divide by 1,000,000)
                                                xrp_amount = format(int(amount) / 1e6, ".2f")
                                                amount_text = f"{xrp_amount} XRP"
                                            elif isinstance(amount, dict) and "value" in amount:
                                                # Issued currency/token amount
                                                currency = decode_currency_code(
                                                    amount.get("currency", "Unknown")
                                                )
                                                value = format(float(amount.get("value", 0)), ".2f")
                                                amount_text = f"{value} {currency}"
                                            else:
                                                amount_text = f"Payment"
                                        # Check for DeliverMax (used in some faucet transactions)
                                        elif "DeliverMax" in tx:
                                            deliver_max = tx["DeliverMax"]
                                            if (
                                                isinstance(deliver_max, str)
                                                and deliver_max.isdigit()
                                            ):
                                                xrp_amount = format(int(deliver_max) / 1e6, ".2f")
                                                amount_text = f"{xrp_amount} XRP"
                                            else:
                                                amount_text = f"Payment"
                                        else:
                                            # Check metadata for delivered_amount
                                            if (
                                                "meta" in transaction
                                                and "delivered_amount" in transaction["meta"]
                                            ):
                                                delivered = transaction["meta"]["delivered_amount"]
                                                if (
                                                    isinstance(delivered, str)
                                                    and delivered.isdigit()
                                                ):
                                                    xrp_amount = format(int(delivered) / 1e6, ".2f")
                                                    amount_text = f"{xrp_amount} XRP"
                                                elif isinstance(delivered, dict):
                                                    curr = decode_currency_code(
                                                        delivered.get("currency", "Unknown")
                                                    )
                                                    val = format(
                                                        float(delivered.get("value", 0)), ".2f"
                                                    )
                                                    amount_text = f"{val} {curr}"
                                                else:
                                                    amount_text = "Payment"
                                            else:
                                                amount_text = "Payment"

                                        # Determine direction and peer
                                        if "Account" in tx and "Destination" in tx:
                                            if tx["Account"] == test_wallet_address:
                                                direction_icon = "↑"
                                                direction = "Sent"
                                                peer = tx["Destination"]
                                                peer_address = f"to {peer[:6]}...{peer[-4:]}"
                                            elif tx["Destination"] == test_wallet_address:
                                                direction_icon = "↓"
                                                direction = "Received"
                                                peer = tx["Account"]
                                                peer_address = f"from {peer[:6]}...{peer[-4:]}"

                                    # Handle other transaction types (like faucet funding, NFTs)
                                    elif tx_type in [
                                        "AccountSet",
                                        "OfferCreate",
                                        "OfferCancel",
                                        "TrustSet",
                                        "NFTokenBurn",
                                        "NFTokenMint",
                                        "NFTokenAcceptOffer",
                                        "NFTokenCreateOffer",
                                    ]:
                                        amount_text = f"{tx_type}"
                                        if "Account" in tx:
                                            peer = tx["Account"]
                                            if peer == test_wallet_address:
                                                direction_icon = "•"
                                                peer_address = "by you"
                                            else:
                                                direction_icon = "•"
                                                peer_address = f"{peer[:6]}...{peer[-4:]}"

                                    # For unknown transaction types, try to find amount in metadata
                                    else:
                                        # Check if there's delivered_amount in metadata (common for faucet transactions)
                                        if "meta" in transaction and isinstance(
                                            transaction["meta"], dict
                                        ):
                                            meta = transaction["meta"]
                                            if "delivered_amount" in meta:
                                                delivered = meta["delivered_amount"]
                                                if (
                                                    isinstance(delivered, str)
                                                    and delivered.isdigit()
                                                ):
                                                    xrp_amount = format(int(delivered) / 1e6, ".2f")
                                                    amount_text = f"{xrp_amount} XRP"
                                                    direction_icon = "↓"
                                                    direction = "Received"
                                                elif isinstance(delivered, dict):
                                                    curr = decode_currency_code(
                                                        delivered.get("currency", "Unknown")
                                                    )
                                                    val = format(
                                                        float(delivered.get("value", 0)), ".2f"
                                                    )
                                                    amount_text = f"{val} {curr}"
                                                    direction_icon = "↓"
                                                    direction = "Received"
                                            elif "AffectedNodes" in meta:
                                                # Look for account balance changes in affected nodes
                                                for node in meta["AffectedNodes"]:
                                                    if "ModifiedNode" in node:
                                                        modified = node["ModifiedNode"]
                                                        if (
                                                            modified.get("LedgerEntryType")
                                                            == "AccountRoot"
                                                        ):
                                                            final_fields = modified.get(
                                                                "FinalFields", {}
                                                            )
                                                            previous_fields = modified.get(
                                                                "PreviousFields", {}
                                                            )

                                                            if (
                                                                "Balance" in final_fields
                                                                and "Balance" in previous_fields
                                                            ):
                                                                balance_change = int(
                                                                    final_fields["Balance"]
                                                                ) - int(previous_fields["Balance"])
                                                                if balance_change > 0:
                                                                    xrp_amount = format(
                                                                        balance_change / 1e6, ".2f"
                                                                    )
                                                                    amount_text = (
                                                                        f"{xrp_amount} XRP"
                                                                    )
                                                                    direction_icon = "↓"
                                                                    direction = "Received"
                                                                elif balance_change < 0:
                                                                    xrp_amount = format(
                                                                        abs(balance_change) / 1e6,
                                                                        ".2f",
                                                                    )
                                                                    amount_text = (
                                                                        f"{xrp_amount} XRP"
                                                                    )
                                                                    direction_icon = "↑"
                                                                    direction = "Sent"

                                        # If still no amount found, show transaction type
                                        if not amount_text:
                                            amount_text = f"{tx_type}"
                                            if "Account" in tx:
                                                peer = tx["Account"]
                                                if peer == test_wallet_address:
                                                    direction_icon = "•"
                                                    peer_address = "your tx"
                                                else:
                                                    direction_icon = "•"
                                                    peer_address = f"{peer[:6]}...{peer[-4:]}"

                                    # Set the final label text with icon, amount, and peer
                                    label.text = (
                                        f"{direction_icon} {amount_text} {peer_address}".strip()
                                    )

                            # Clear any remaining unused transaction labels to empty strings
                            for j in range(len(transactions), 20):
                                lbl = self._get_tx_label(j + 1)
                                if lbl:
                                    lbl.text = ""
                        else:
                            # No transactions found - clear all transaction labels to empty strings
                            for i in range(1, 21):
                                lbl = self._get_tx_label(i)
                                if lbl:
                                    lbl.text = ""
                    elif hasattr(response2, "result") and "error" in response2.result:
                        error_code = response2.result["error"]
                        # Clear transaction labels on error to empty strings
                        for i in range(1, 21):
                            lbl = self._get_tx_label(i)
                            if lbl:
                                lbl.text = ""
                    else:
                        for i in range(1, 21):
                            lbl = self._get_tx_label(i)
                            if lbl:
                                lbl.text = ""
                except Exception as tx_error:
                    # Clear transaction labels on error to empty strings
                    for i in range(1, 21):
                        lbl = self._get_tx_label(i)
                        if lbl:
                            lbl.text = ""

            # Note: Token balance display has been removed
            # For new test tokens, configure them in src/utils/token_config.py
            # and add appropriate UI elements to the KV file

            # Nothing else to close here (using context manager)
        except Exception as e:
            self.xrp_balance.text = "Error: Could not get balance"
        # Return current balance text for async callback usage
        return {"balance": getattr(self.xrp_balance, 'text', '')}

    def refresh_account_data(self):
        """Refresh current account selection and UI from storage.
        Prefer the new 'accounts' model; fall back to legacy keys if needed."""
        try:
            with shelve.open("wallet_data") as db:
                if "accounts" in db:
                    accounts = db.get("accounts", [])
                    if not accounts:
                        return
                    idx = db.get("active_account", 0)
                    if idx < 0 or idx >= len(accounts):
                        idx = 0
                    acct = accounts[idx]

                    # Update keys
                    self.public_key = acct.get("public_key")
                    # Decrypt private key if possible
                    enc_priv = acct.get("private_key")
                    enc_key = db.get("encryption_key")
                    try:
                        if enc_priv and enc_key:
                            cipher = Fernet(enc_key)
                            self.private_key = cipher.decrypt(enc_priv.encode()).decode()
                    except Exception:
                        self.private_key = None

                    # Update address and account name
                    if self.public_key:
                        try:
                            addr = derive_classic_address(acct.get("public_key", ""))
                            self.set_address_text(addr)
                        except Exception:
                            self.set_address_text("")
                    name = acct.get("name", "")
                    self.account_name = name
                    # Update title label if present
                    if "wallet_title" in self.ids and name:
                        self.ids.wallet_title.text = f"Account: '{name}'"
                else:
                    # Legacy model: auto-select first public_key*
                    if not self.selected_key:
                        keys_available = [key for key in db.keys() if key.startswith("public_key")]
                        if keys_available:
                            self.selected_key = keys_available[0]
                        else:
                            return
                    if self.selected_key in db:
                        self.public_key = db[self.selected_key]
                        try:
                            addr = derive_classic_address(self.public_key)
                            self.set_address_text(addr)
                        except Exception:
                            self.set_address_text("")
        except Exception:
            pass

    def _get_tx_label(self, index: int):
        try:
            card = self.ids.get("transactions_card")
            if card and hasattr(card, "ids"):
                return card.ids.get(f"transaction{index}")
        except Exception:
            pass
        return self.ids.get(f"transaction{index}")

    # Token send screens are created dynamically via trustline system
    # See refresh_trustlines() and navigate_to_token_send() methods

    def copy_address(self):
        try:
            label = self.ids.get("xrp_address_label")
            Clipboard.copy(label.text if label else "")
        except Exception:
            Clipboard.copy("")

    def refresh_trustlines(self):
        """Refresh and display trustlines for current account"""
        from kivy.uix.boxlayout import BoxLayout
        from kivymd.uix.button import MDIconButton
        from kivymd.uix.label import MDLabel

        # Clear existing trustlines display
        container = self.ids.get("trustlines_container")
        scroll = self.ids.get("trustlines_scroll")
        if not container:
            return

        container.clear_widgets()

        try:
            # Get current account address
            if not self.public_key:
                self.refresh_account_data()
                if not self.public_key:
                    return

            test_wallet_address = derive_classic_address(self.public_key)

            # Check if online
            if not is_online():
                container.add_widget(
                    MDLabel(
                        text="Offline - Cannot load trustlines",
                        halign="center",
                        size_hint_y=None,
                        height="30dp",
                    )
                )
                if scroll:
                    scroll.height = "30dp"
                return

            # Query account lines (trustlines) from XRPL
            from xrpl.models.requests import AccountLines

            acct_lines = AccountLines(account=test_wallet_address, ledger_index="validated")

            response = make_request(acct_lines)

            if hasattr(response, "status") and response.status.name == "SUCCESS":
                lines = response.result.get("lines", [])

                if not lines:
                    container.add_widget(
                        MDLabel(
                            text="No trustlines yet. Click + to add one.",
                            halign="center",
                            font_size="12sp",
                            size_hint_y=None,
                            height="30dp",
                            theme_text_color="Custom",
                            text_color=get_color_from_hex("#505CA9"),
                        )
                    )
                    if scroll:
                        scroll.height = "30dp"
                else:
                    # Display each trustline
                    for line in lines:
                        currency = line.get("currency", "Unknown")
                        display_currency = decode_currency_code(currency)
                        balance = line.get("balance", "0")
                        account = line.get("account", "")  # This is the issuer

                        # Create a row for this trustline
                        row = BoxLayout(
                            orientation="horizontal",
                            size_hint=(1, None),
                            height="44dp",
                            padding=["8dp", "6dp", "8dp", "6dp"],
                            spacing="8dp",
                        )

                        # Currency label (decoded for readability)
                        row.add_widget(
                            MDLabel(
                                text=display_currency[:15],
                                halign="left",
                                size_hint_x=0.35,
                                font_size="12sp",
                                theme_text_color="Custom",
                                text_color=get_color_from_hex("#202443"),
                            )
                        )

                        # Balance label
                        row.add_widget(
                            MDLabel(
                                text=f"{float(balance):.4f}",
                                halign="center",
                                size_hint_x=0.35,
                                font_size="12sp",
                                theme_text_color="Custom",
                                text_color=get_color_from_hex("#008D36"),
                            )
                        )

                        # Send button
                        send_btn = MDIconButton(
                            icon="send",
                            size_hint_x=0.15,
                            theme_icon_size="Custom",
                            icon_size="22sp",
                            theme_icon_color="Custom",
                            icon_color=get_color_from_hex("#505CA9"),
                        )
                        # Bind navigation to send screen for this token
                        send_btn.bind(
                            on_press=lambda x, c=currency, iss=account: self.navigate_to_token_send(
                                c, iss
                            )
                        )
                        row.add_widget(send_btn)

                        # Trade button
                        trade_btn = MDIconButton(
                            icon="arrow-left-right-bold-outline",
                            size_hint_x=0.15,
                            theme_icon_size="Custom",
                            icon_size="22sp",
                            theme_icon_color="Custom",
                            icon_color=get_color_from_hex("#008D36"),
                        )
                        trade_btn.bind(on_press=lambda x: self.dextradescreen())
                        row.add_widget(trade_btn)

                        # Info button (shows issuer)
                        info_btn = MDIconButton(
                            icon="information-outline",
                            size_hint_x=0.10,
                            theme_icon_size="Custom",
                            icon_size="22sp",
                            theme_icon_color="Custom",
                            icon_color=get_color_from_hex("#f9b233"),
                        )
                        info_btn.bind(
                            on_press=lambda x, iss=account, cur=display_currency: self.show_issuer_info(
                                cur, iss
                            )
                        )
                        row.add_widget(info_btn)

                        container.add_widget(row)
                        # subtle divider below each row (drawn as 1dp line)
                        sep = Widget(size_hint=(1, None), height=dp(1))
                        with sep.canvas.before:
                            Color(rgba=get_color_from_hex("#e5e7ef"))
                            rect = Rectangle(pos=sep.pos, size=(sep.width, dp(1)))

                        def _upd_rect(instance, value):
                            rect.pos = sep.pos
                            rect.size = (sep.width, dp(1))

                        sep.bind(pos=_upd_rect, size=_upd_rect)
                        container.add_widget(sep)

                    # Set scroll height based on number of trustlines (max 5 visible)
                    num_lines = min(len(lines), 5)
                    if scroll:
                        scroll.height = f"{num_lines * 44}dp"
            else:
                error_msg = (
                    response.result.get("error", "Unknown error")
                    if hasattr(response, "result")
                    else "Connection error"
                )
                container.add_widget(
                    MDLabel(
                        text=f"Error loading trustlines: {error_msg}",
                        halign="center",
                        size_hint_y=None,
                        height="30dp",
                    )
                )
                if scroll:
                    scroll.height = "30dp"

        except Exception as e:
            print(f"Error refreshing trustlines: {e}")
            container.add_widget(
                MDLabel(text=f"Error: {str(e)}", halign="center", size_hint_y=None, height="30dp")
            )
            if scroll:
                scroll.height = "30dp"

    def navigate_to_token_send(self, currency, issuer):
        """Navigate to token send screen or create it dynamically"""
        # Check if we have a SendTestTokenScreen for this token
        screen_name = f"send_{currency.lower()}_screen"

        try:
            # Try to get existing screen
            screen = self.manager.get_screen(screen_name)
            self.manager.current = screen_name
        except Exception:
            # Create screen dynamically
            from src.screens.SendTestTokenScreen import SendTestTokenScreen

            new_screen = SendTestTokenScreen(
                client=self.client, token_id=currency, name=screen_name
            )
            # Set token configuration
            new_screen.currency_code = currency
            new_screen.issuer_address = issuer
            self.manager.add_widget(new_screen)
            self.manager.current = screen_name

    def show_issuer_info(self, currency, issuer):
        """Show issuer information dialog"""
        show_confirm_dialog(
            title=f"{currency} Trustline Info",
            text=f"Issuer Address:\n{issuer}\n\nClick to copy",
            confirm_text="Copy Address",
            cancel_text="Close",
            on_confirm=lambda: Clipboard.copy(issuer),
            dismiss_on_confirm=True,
        )

    def send_xrp_screen(self):
        self.manager.current = "sendxrp_screen"

    def add_trustline_screen(self):
        self.manager.current = "add_trustline_screen"

    def nftmintscreen(self):
        self.manager.current = "nftmint_screen"

    def createimportwalletscreen(self):
        self.manager.current = "createimportwallet_screen"

    def dextradescreen(self):
        self.manager.current = "dextrade_screen"

    def foodtrackscreen(self):
        self.manager.current = "foodtrack_screen"

    def settingsscreen(self):
        self.manager.current = "settings_screen"
