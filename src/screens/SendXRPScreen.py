# Kivy libraries for the GUI.
# Encryption libraries for password and key encryption.
import logging
import shelve

from kivy.clock import Clock
from kivy.properties import ObjectProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import Screen
from kivymd.uix.label import MDLabel

from src.utils.dialogs import show_confirm_dialog, show_error_dialog, show_info_dialog

import bcrypt
from Crypto.Cipher import AES
from Crypto.Protocol.KDF import PBKDF2
from xrpl.clients import JsonRpcClient
from xrpl.core.binarycodec.exceptions import XRPLBinaryCodecException
from xrpl.core.keypairs import derive_classic_address
from xrpl.models.requests import AccountInfo, AccountTx
from xrpl.models.transactions import Payment
from xrpl.transaction import submit_and_wait  # noqa: F401

# XRPL libraries for xrpl functionality
from xrpl.wallet import Wallet

from src.utils.currency_utils import decode_currency_code
from src.utils.password_field_utils import create_password_field_with_toggle
from src.utils.robust_transaction import get_transaction_status_message, robust_submit_and_wait
from src.utils.storage_paths import WALLET_DATA_PATH

# Import the robust XRPL client manager
from src.utils.xrpl_client_manager import is_online, make_request

JSON_RPC_URL = "https://testnet.xrpl-labs.com"  # Use XRPL Labs testnet (more reliable)
client = JsonRpcClient(JSON_RPC_URL)
logging.basicConfig(level=logging.WARNING)


# Send XRP Screen
class SendXRPScreen(Screen):
    # KV file property references
    xrp_address = ObjectProperty(None)
    xrp_balance = ObjectProperty(None)
    amount_input = ObjectProperty(None)
    destination_input = ObjectProperty(None)

    def __init__(self, client, **kwargs):
        super().__init__(**kwargs)
        self.client = client

    def on_pre_enter(self, *args):
        """Prepare screen with current account address and start balance polling.
        Supports both legacy (selected_key) and new accounts model.
        """
        # Ensure header title is correct
        app_header = self.ids.get("app_header")
        if app_header:
            app_header.title = "Send XRP"

        self.public_key = None
        # Try new accounts model first
        try:
            with shelve.open(WALLET_DATA_PATH) as db:
                if "accounts" in db:
                    accounts = db.get("accounts", [])
                    idx = db.get("active_account", 0)
                    if 0 <= idx < len(accounts):
                        self.public_key = accounts[idx].get("public_key")
                else:
                    # Fallback to legacy selected_key model
                    selected_key = self.manager.get_screen("wallet_screen").selected_key
                    if selected_key and selected_key in db:
                        self.public_key = db[selected_key]
        except Exception:
            self.public_key = None

        if not self.public_key:
            return

        # Derive classic address from public key
        try:
            test_wallet_address = derive_classic_address(self.public_key)
            self.xrp_address.text = test_wallet_address
        except Exception:
            self.xrp_address.text = ""

        # Check if we're in offline mode or if we have no connection
        try:
            from src.core.app import OFFLINE_MODE

            offline_mode = OFFLINE_MODE
        except Exception:
            offline_mode = False

        # Use the global client manager to check connection status
        if not is_online() or offline_mode:
            # Set offline status immediately for faster loading
            self.xrp_balance.text = "Offline Mode"
            # Clear transaction history
            for i in range(1, 21):
                lbl = self._get_tx_label(i)
                if lbl:
                    lbl.text = "Offline Mode"
        else:
            # Online mode - start balance checking with robust client
            self.check_balance(dt=30)
            Clock.schedule_interval(self.check_balance, 30)

    def on_leave(self, *args):
        """Clean up when leaving the screen"""
        # Only unschedule if balance checking was actually started
        try:
            Clock.unschedule(self.check_balance)
        except Exception:
            pass  # In case check_balance was never scheduled due to offline mode

        # Clear input fields when leaving the screen
        if "amount_input" in self.ids:
            self.ids["amount_input"].text = ""
        if "destination_input" in self.ids:
            self.ids["destination_input"].text = ""

    def show_error_message(self, message):
        show_error_dialog("Error", message)

    def show_success_message(self, message):
        show_info_dialog("Success", message)

    def _get_tx_label(self, index: int):
        try:
            card = self.ids.get("transactions_card")
            if card and hasattr(card, "ids"):
                return card.ids.get(f"transaction{index}")
        except Exception:
            pass
        return self.ids.get(f"transaction{index}")

    def check_address(self, destination):
        """Check if a destination address is valid (format check and optional existence check)

        Returns:
            tuple: (is_valid_format, account_exists, error_message)
        """
        # First, validate the address format (basic XRP address validation)
        if not destination or len(destination) < 25:
            return (False, False, "Address is too short")

        if not destination.startswith("r"):
            return (False, False, "XRP addresses must start with 'r'")

        acct_info = AccountInfo(
            account=destination,
            ledger_index="validated",
            strict=True,
        )

        try:
            # Use the robust client manager that handles server failover
            response = make_request(acct_info)
            print("response.status: ", response.status)
            if response.status == "success":
                # Account exists on ledger
                return (True, True, None)
            else:
                # Valid format but account doesn't exist yet (not funded)
                # This is OK - first payment will activate the account
                return (True, False, "unfunded")
        except Exception as e:
            error_str = str(e).lower()
            if "actnotfound" in error_str or "account not found" in error_str:
                # Valid format but unfunded account
                return (True, False, "unfunded")
            else:
                print(f"Error checking address: {e}")
                # Network error - assume valid format and let transaction attempt proceed
                return (True, None, "network_error")

    def send_xrp(self):
        amount = self.ids["amount_input"].text
        destination = self.ids["destination_input"].text

        # Prevent sending to self (same sender and destination)
        try:
            if destination and self.xrp_address and destination.strip() == self.xrp_address.text.strip():
                self.show_error_message("Destination cannot be your own address.")
                return
        except Exception:
            pass

        # Check for a valid amount
        try:
            amount = float(amount)
            if amount <= 0:
                raise ValueError
        except ValueError:
            self.show_error_message("Enter a valid amount.")
            return

        # Check for a valid destination address
        is_valid_format, account_exists, error_msg = self.check_address(destination)

        if not is_valid_format:
            self.show_error_message(f"Invalid destination address.\n{error_msg}")
            return

        # Warn user if sending to unfunded account (but allow it)
        if account_exists is False and error_msg == "unfunded":
            # Check if amount is sufficient to activate account (1 XRP minimum on testnet)
            if amount < 1:
                self.show_error_message(
                    f"Destination account is not yet activated.\n\n"
                    f"The first payment to a new account must be at least 1 XRP to activate it.\n\n"
                    f"You are trying to send {amount} XRP.\n\n"
                    f"Please send at least 1 XRP or choose a different destination."
                )
                return
            else:
                # Amount is sufficient - proceed with helpful message in confirmation
                self.unfunded_destination = True
        else:
            self.unfunded_destination = False

        # Define the password input field with toggle visibility
        self.password_field_container = create_password_field_with_toggle(
            hint_text="Enter your password"
        )
        self.password_field = self.password_field_container.password_field

        # Build concise, M3-style content
        Amount = MDLabel(text=f"Amount: {amount}")
        Amount.font_size = "13sp"
        Destination = MDLabel(text=f"Destination: {destination}")
        Destination.font_size = "12sp"

        # Add warning label if destination is unfunded
        unfunded_warning = None
        if self.unfunded_destination:
            unfunded_warning = MDLabel(
                text="⚠️ Destination is not activated (≥ 1 XRP required)",
                theme_text_color="Custom",
                text_color=(0.98, 0.70, 0.20, 1),
            )
            unfunded_warning.font_size = "11sp"

        content_box = BoxLayout(orientation="vertical", padding=(12, 12, 12, 12))
        content_box.add_widget(Amount)
        content_box.add_widget(Destination)
        if unfunded_warning:
            content_box.add_widget(unfunded_warning)
        content_box.add_widget(self.password_field_container)
        content_box.ids["password_field"] = self.password_field

        # Use centralized confirm dialog with consistent styling and no auto-dismiss
        self.dialog = show_confirm_dialog(
            title="Confirm XRP Payment",
            content=content_box,
            confirm_text="Send",
            cancel_text="Cancel",
            on_confirm=lambda: self.perform_send(self.password_field.text),
            dismiss_on_confirm=False,
        )

    def perform_send(self, entered_password):
        # Load the password hash from the file
        wallet_data = shelve.open(WALLET_DATA_PATH)
        hashed_password = wallet_data.get("password")
        wallet_data.close()

        # Check if the password is correct
        password = entered_password.encode("utf-8")
        if not bcrypt.checkpw(password, hashed_password):
            self.password_field.hint_text = "Wrong password, try again"
            # Clear the password field for retry
            self.password_field.text = ""
            # Don't dismiss dialog - let user try again
            return

        try:
            # Load keys from new accounts model if available, else legacy
            with shelve.open(WALLET_DATA_PATH) as db:
                if "accounts" in db:
                    accounts = db.get("accounts", [])
                    idx = db.get("active_account", 0)
                    if 0 <= idx < len(accounts):
                        acct = accounts[idx]
                        self.public_key = acct.get("public_key")
                        enc_priv = acct.get("private_key")
                        enc_key = db.get("encryption_key")
                        if enc_priv and enc_key:
                            from cryptography.fernet import Fernet

                            try:
                                cipher = Fernet(enc_key)
                                self.private_key = cipher.decrypt(enc_priv.encode()).decode()
                            except Exception:
                                self.private_key = None
                else:
                    # Legacy path uses selected_key and AES decryption
                    selected_key = self.manager.get_screen("wallet_screen").selected_key
                    if not selected_key or selected_key not in db:
                        # Dismiss dialog and return
                        self.dialog.dismiss()
                        return
                    self.public_key = db[selected_key]
                    nonce = db[selected_key.replace("public", "nonce")]
                    encrypted_private_key = db[selected_key.replace("public", "private")]
                    password = db["password"].decode("utf-8").encode("ascii")
                    salt = db[selected_key.replace("public", "salt")]
                    key = PBKDF2(password, salt, dkLen=32, count=100000)
                    cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)
                    private_key = str(cipher.decrypt(encrypted_private_key))
                    self.private_key = private_key[2:68]

            if not self.public_key or not self.private_key:
                self.dialog.dismiss()
                self.show_error_message("Unable to access keys for the active account.")
                return

            def wallet_from_kp():
                classic_address = derive_classic_address(self.public_key)
                # Create wallet object using the Wallet constructor with public and private keys
                wallet = Wallet(public_key=self.public_key, private_key=self.private_key)
                return wallet, classic_address

            test_wallet, test_wallet_address = wallet_from_kp()

            my_tx_payment = Payment(
                account=test_wallet_address,
                amount=str(int(float(self.amount_input.text) * 1000000)),
                destination=self.destination_input.text,
            )

            # Use the robust transaction submission with automatic server failover
            try:
                tx_response = robust_submit_and_wait(my_tx_payment, test_wallet)

                # Get user-friendly status message
                status_message = get_transaction_status_message(tx_response)
                print(status_message)

                # Check if transaction was successful
                if hasattr(tx_response, "result") and "meta" in tx_response.result:
                    tx_result = tx_response.result["meta"].get("TransactionResult", "Unknown")
                    if tx_result == "tesSUCCESS":
                        print("✅ Transaction successful!")
                        # Dismiss the password dialog first
                        self.dialog.dismiss()
                        # Show success message to user
                        self.show_success_message("Transaction completed successfully!")
                    else:
                        print(f"❌ Transaction failed with error: {tx_result}")
                        # Dismiss the password dialog first
                        self.dialog.dismiss()
                        self.show_error_message(f"Transaction failed: {tx_result}")
                else:
                    print("❓ Transaction submitted - status unknown")
                    # Dismiss the password dialog first
                    self.dialog.dismiss()
                    self.show_error_message("Transaction submitted but status unclear")

            except Exception as tx_error:
                print(f"❌ Transaction submission failed: {tx_error}")
                # Dismiss the password dialog first
                self.dialog.dismiss()
                self.show_error_message(f"Failed to submit transaction: {str(tx_error)}")
                return

            # No explicit shelve handle to close here; contexts already closed
        except XRPLBinaryCodecException:
            # No explicit shelve handle to close here; contexts already closed
            # Dismiss the password dialog first
            self.dialog.dismiss()
            self.password_field.hint_text = "XRPLBinaryCodecException Error"

    def check_balance(self, dt):
        """Check balance using robust client manager with automatic failover"""
        try:
            # Load current public key from new accounts model or legacy
            with shelve.open("wallet_data") as db:
                if "accounts" in db:
                    accounts = db.get("accounts", [])
                    idx = db.get("active_account", 0)
                    if 0 <= idx < len(accounts):
                        self.public_key = accounts[idx].get("public_key")
                    else:
                        self.public_key = None
                else:
                    selected_key = self.manager.get_screen("wallet_screen").selected_key
                    if selected_key in db:
                        self.public_key = db[selected_key]
                    else:
                        self.public_key = None

            if not self.public_key:
                self.xrp_balance.text = "No account selected"
                return

            def wallet_from_kp():
                classic_address = derive_classic_address(self.public_key)
                return classic_address

            test_wallet_address = wallet_from_kp()

            acct_info = AccountInfo(
                account=test_wallet_address,
                ledger_index="validated",
                strict=True,
            )

            # Improved error handling for account balance using robust client manager
            try:
                response = make_request(acct_info)

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
                print(f"SendXRP - Error getting balance: {account_error}")
                self.xrp_balance.text = "Network Issue - Retrying..."

            # Transaction History - Improved error handling with robust client
            try:
                tx_info = AccountTx(
                    account=test_wallet_address, ledger_index_min=-1, ledger_index_max=-1, limit=20
                )
                response2 = make_request(tx_info)

                # Check if response is successful
                if hasattr(response2, "status") and response2.status.name == "SUCCESS":
                    data2 = response2.result

                    # Check if transactions exist
                    if "transactions" in data2 and data2["transactions"]:

                        for i, transaction in enumerate(data2["transactions"]):
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
                                amount_text = "Amount not specified"
                                direction = ""

                                # Check if this is a Payment transaction
                                if tx_type == "Payment":
                                    # For Payment transactions, check the Amount field
                                    if "Amount" in tx:
                                        amount = tx["Amount"]
                                        if isinstance(amount, str) and amount.isdigit():
                                            # XRP amount in drops (divide by 1,000,000)
                                            xrp_amount = format(int(amount) / 1e6, ".2f")
                                            amount_text = f"Amount XRP: {xrp_amount}"
                                        elif isinstance(amount, dict) and "value" in amount:
                                            # Issued currency/token amount
                                            currency = amount.get("currency", "Unknown")
                                            value = format(float(amount.get("value", 0)), ".2f")
                                            currency = decode_currency_code(currency)
                                            amount_text = f"Amount {currency}: {value}"
                                        else:
                                            amount_text = f"Payment - Amount: {amount}"
                                    # Check for DeliverMax (used in some faucet transactions)
                                    elif "DeliverMax" in tx:
                                        deliver_max = tx["DeliverMax"]
                                        if isinstance(deliver_max, str) and deliver_max.isdigit():
                                            xrp_amount = format(int(deliver_max) / 1e6, ".2f")
                                            amount_text = f"Amount XRP: {xrp_amount}"
                                        else:
                                            amount_text = f"Payment - DeliverMax: {deliver_max}"
                                    else:
                                        # Check metadata for delivered_amount
                                        if (
                                            "meta" in transaction
                                            and "delivered_amount" in transaction["meta"]
                                        ):
                                            delivered = transaction["meta"]["delivered_amount"]
                                            if isinstance(delivered, str) and delivered.isdigit():
                                                xrp_amount = format(int(delivered) / 1e6, ".2f")
                                                amount_text = f"Amount XRP: {xrp_amount}"
                                            else:
                                                amount_text = f"Payment - delivered: {delivered}"
                                        else:
                                            amount_text = "Payment - Amount unknown"

                                    # Determine direction
                                    if "Account" in tx and "Destination" in tx:
                                        if tx["Account"] == test_wallet_address:
                                            direction = " (Sent)"
                                        elif tx["Destination"] == test_wallet_address:
                                            direction = " (Received)"

                                # Handle other transaction types (like faucet funding)
                                elif tx_type in [
                                    "AccountSet",
                                    "OfferCreate",
                                    "OfferCancel",
                                    "TrustSet",
                                ]:
                                    amount_text = f"{tx_type} transaction"
                                    if "Account" in tx:
                                        if tx["Account"] == test_wallet_address:
                                            direction = " (Sent by you)"
                                        else:
                                            direction = " (Other account)"

                                # For unknown transaction types, try to find amount in metadata
                                else:
                                    # Check if there's delivered_amount in metadata (common for faucet transactions)
                                    if "meta" in transaction and isinstance(
                                        transaction["meta"], dict
                                    ):
                                        meta = transaction["meta"]
                                        if "delivered_amount" in meta:
                                            delivered = meta["delivered_amount"]
                                            if isinstance(delivered, str) and delivered.isdigit():
                                                xrp_amount = format(int(delivered) / 1e6, ".2f")
                                                amount_text = f"Amount XRP: {xrp_amount}"
                                                direction = " (Received)"
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
                                                                    f"Amount XRP: {xrp_amount}"
                                                                )
                                                                direction = " (Received)"
                                                            elif balance_change < 0:
                                                                xrp_amount = format(
                                                                    abs(balance_change) / 1e6, ".2f"
                                                                )
                                                                amount_text = (
                                                                    f"Amount XRP: {xrp_amount}"
                                                                )
                                                                direction = " (Sent)"

                                    # If still no amount found, show transaction type
                                    if amount_text == "Amount not specified":
                                        amount_text = f"{tx_type} transaction"
                                        if "Account" in tx:
                                            if tx["Account"] == test_wallet_address:
                                                direction = " (Your transaction)"
                                            else:
                                                direction = " (External transaction)"

                                # Set the final label text
                                label.text = amount_text + direction

                        # Clear any remaining unused transaction labels to empty strings
                        for j in range(len(data2["transactions"]), 20):
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
                print(f"SendXRP - Error getting transactions: {tx_error}")
                # Clear transaction labels on error to empty strings
                for i in range(1, 21):
                    lbl = self._get_tx_label(i)
                    if lbl:
                        lbl.text = "Network Issue"

        except Exception as e:
            print(f"SendXRP - Overall error in check_balance: {e}")
            self.xrp_balance.text = "Network Issue - Retrying..."

    def backto_wallet(self):
        self.manager.current = "wallet_screen"
