# Kivy libraries for the GUI.
# Encryption libraries for password and key encryption.
import logging
import json
import shelve

from kivy.clock import Clock
from kivy.core.clipboard import Clipboard
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import Screen
from kivymd.uix.label import MDLabel
from kivymd.uix.textfield import MDTextField

import bcrypt

# XRPL libraries for xrpl functionality
import xrpl
from Crypto.Cipher import AES
from Crypto.Protocol.KDF import PBKDF2
from xrpl.clients import JsonRpcClient
from xrpl.core.binarycodec.exceptions import XRPLBinaryCodecException
from xrpl.core.keypairs import derive_classic_address
from xrpl.models.requests import AccountInfo, AccountTx
from xrpl.models.requests.account_objects import AccountObjects
from xrpl.models.transactions import Payment
from xrpl.transaction import submit_and_wait  # noqa: F401
from xrpl.wallet import Wallet

from src.utils.currency_utils import decode_currency_code
from src.utils.dialogs import show_confirm_dialog, show_error_dialog, show_info_dialog
from src.utils.robust_transaction import get_transaction_status_message, robust_submit_and_wait
from src.utils.storage_paths import WALLET_DATA_PATH
from src.utils.token_config import get_token_config
from src.utils.validators import parse_issued_amount
from src.utils.xrpl_client_manager import is_online, make_request

JSON_RPC_URL = "https://testnet.xrpl-labs.com"
client = JsonRpcClient(JSON_RPC_URL)
logging.basicConfig(level=logging.WARNING)


# Generic Send TestToken Screen
class SendTestTokenScreen(Screen):
    """
    Generic screen for sending any test token.
    Token details are loaded from token_config.py based on token_id.
    """

    def __init__(self, client, token_id=None, **kwargs):
        super().__init__(**kwargs)
        self.client = client
        self.token_id = token_id
        self.token_config = None
        # Fallback fields for dynamic trustlines
        self.currency_code = None
        self.issuer_address = None

    def set_token(self, token_id):
        """Set the token to display/send"""
        self.token_id = token_id
        self.token_config = get_token_config(token_id)

    # Removed local decode helper; using shared utility

    def _get_currency_code(self):
        if self.token_config and self.token_config.get("currency_code"):
            return self.token_config["currency_code"]
        return self.currency_code

    def _get_issuer(self):
        if self.token_config and self.token_config.get("issuer"):
            return self.token_config["issuer"]
        return self.issuer_address

    def _get_token_name(self):
        if self.token_config and self.token_config.get("name"):
            return self.token_config["name"]
        code = self._get_currency_code() or "Token"
        return decode_currency_code(code)

    def on_pre_enter(self):
        # Load token configuration if not already loaded
        if self.token_id and not self.token_config:
            self.token_config = get_token_config(self.token_id)

        # Ensure we have usable token details from config or dynamic fields
        if not self._get_currency_code() or not self._get_issuer():
            self.show_error_message("Token details missing (currency/issuer).")
            return

        # Resolve current account from new accounts model first, fallback to legacy
        self.public_key = None
        try:
            with shelve.open(WALLET_DATA_PATH) as db:
                if "accounts" in db:
                    accounts = db.get("accounts", [])
                    idx = db.get("active_account", 0)
                    if 0 <= idx < len(accounts):
                        self.public_key = accounts[idx].get("public_key")
                else:
                    selected_key = self.manager.get_screen("wallet_screen").selected_key
                    if selected_key and selected_key in db:
                        self.public_key = db[selected_key]
        except Exception:
            self.public_key = None

        if not self.public_key:
            return

        # Derive classic address
        try:
            test_wallet_address = derive_classic_address(self.public_key)
            self.xrp_address.text = test_wallet_address
        except Exception:
            self.xrp_address.text = ""

        # Update header title with token name
        app_header = self.ids.get("app_header")
        if app_header:
            app_header.title = f"Send {self._get_token_name()}"

        # Check if we're in offline mode
        try:
            from src.core.app import OFFLINE_MODE

            offline_mode = OFFLINE_MODE
        except Exception:
            offline_mode = self.client is None

        # Only start balance checking if not in offline mode and online
        if not offline_mode and is_online():
            self.check_balance_token(dt=0)
            Clock.schedule_interval(self.check_balance_token, 33)
        else:
            if "token_balance" in self.ids:
                self.ids.token_balance.text = "Offline Mode"
            for i in range(1, 21):
                lbl = self._get_tx_label(i)
                if lbl:
                    lbl.text = "Offline Mode"

    def on_leave(self):
        # Unschedule balance checking when leaving screen
        try:
            Clock.unschedule(self.check_balance_token)
        except Exception:
            pass

    def show_error_message(self, message):
        # Wrap existing calls to use centralized helper
        self.dialog = show_error_dialog(text=message)

    def check_trustline(self, destination):
        currency_code = self._get_currency_code()
        if not currency_code:
            return False

        acct_objects = AccountObjects(
            account=destination,
            ledger_index="validated",
            type="state",
            deletion_blockers_only=False,
            limit=100,
        )
        response = make_request(acct_objects)
        data = getattr(response, "result", {}) if hasattr(response, "result") else {}
        lines = data.get("account_objects", [])

        currenciescheck = {}
        for obj in lines:
            if isinstance(obj, dict) and "Balance" in obj and isinstance(obj["Balance"], dict):
                cur = obj["Balance"].get("currency")
                if cur:
                    currenciescheck[cur] = cur
        return currency_code in currenciescheck

    def check_address(self, destination):
        # Basic format checks first
        if not destination or len(destination) < 25 or not destination.startswith("r"):
            return (False, False, "Invalid address format")

        acct_info = AccountInfo(
            account=destination,
            ledger_index="validated",
            strict=True,
        )
        try:
            response = self.client.request(acct_info)
            if (
                getattr(response, "status", None) == "success"
                or getattr(getattr(response, "status", None), "name", None) == "SUCCESS"
            ):
                return (True, True, None)
            else:
                return (True, False, "unfunded")
        except Exception:
            return (True, None, "network_error")

    def send_token(self):
        # Ensure token details exist (config or dynamic)
        currency_code = self._get_currency_code()
        issuer = self._get_issuer()
        token_name = self._get_token_name()
        if not currency_code or not issuer:
            self.show_error_message("Token not configured correctly")
            return

        amount_str = self.ids["amount_token_input"].text
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
            issued_value = parse_issued_amount(amount_str)
            # Store for use during perform_send
            self._issued_amount_value = issued_value
        except Exception:
            self.show_error_message("Enter a valid amount.")
            return

        # Check for a valid destination address
        is_valid_format, account_exists, error_msg = self.check_address(destination)
        if not is_valid_format:
            self.show_error_message("Enter a valid destination address.")
            return

        # For issued tokens, destination must be an activated account
        if account_exists is False and error_msg == "unfunded":
            show_info_dialog(
                title="Destination Not Activated",
                text=(
                    "The destination account is not activated.\n\n"
                    "IOU/token payments cannot activate new accounts.\n\n"
                    "Please fund the destination with XRP first and create the required trustline, then try again."
                ),
            )
            return

        try:
            has_trustline = self.check_trustline(destination)
        except Exception:
            self.show_error_message("Could not verify trustline. Please try again.")
            return
        if not has_trustline:
            # Provide helpful dialog with copyable issuer/currency details
            issuer = issuer
            currency = currency_code

            def _copy_details():
                details = f"Issuer: {issuer}\nCurrency: {currency}"
                try:
                    Clipboard.copy(details)
                except Exception:
                    pass

            show_confirm_dialog(
                title="No Trustline Found",
                text=(
                    f"The destination does not have a trustline for {token_name}.\n\n"
                    f"Please ask the recipient to add the trustline first.\n\n"
                    f"Issuer: {issuer}\nCurrency: {currency}"
                ),
                confirm_text="OK",
                cancel_text="Close",
                secondary_text="Copy Details",
                on_secondary=_copy_details,
            )
            return

        # Define the password input field with toggle visibility (shared helper)
        from src.utils.password_field_utils import create_password_field_with_toggle

        self.password_field_container = create_password_field_with_toggle(
            hint_text="Enter your password"
        )
        self.password_field = self.password_field_container.password_field

        # Add extra context for token send confirmation
        currency_display = decode_currency_code(currency_code)
        issuer_display = issuer

        Amount = MDLabel(text=f"Amount: {self._issued_amount_value}")
        Amount.font_size = "13sp"
        Destination = MDLabel(text=f"Destination: {destination}")
        Destination.font_size = "12sp"
        CurrencyLbl = MDLabel(text=f"Currency: {currency_display}")
        CurrencyLbl.font_size = "12sp"
        IssuerLbl = MDLabel(text=f"Issuer: {issuer_display}")
        IssuerLbl.font_size = "12sp"

        # Define a concise content layout
        content_box = BoxLayout(orientation="vertical", padding=(12, 12, 12, 12))
        # Tiny hint when token comes from dynamic trustline
        if not self.token_config:
            hint_lbl = MDLabel(
                text="Dynamic token from trustline",
                font_size="11sp",
                theme_text_color="Custom",
                text_color=(0.31, 0.36, 0.66, 1),
            )
            content_box.add_widget(hint_lbl)
        content_box.add_widget(Amount)
        content_box.add_widget(Destination)
        content_box.add_widget(CurrencyLbl)
        content_box.add_widget(IssuerLbl)
        content_box.add_widget(self.password_field_container)
        content_box.ids["password_field"] = self.password_field

        # Use centralized confirm dialog with custom content and no auto-dismiss
        self.dialog = show_confirm_dialog(
            title=f"Confirm {token_name} Payment",
            content=content_box,
            confirm_text="Send",
            cancel_text="Cancel",
            on_confirm=lambda: self.perform_send(self.password_field.text),
            dismiss_on_confirm=False,
        )

    def perform_send(self, entered_password):
        # Token details already validated in send_token

        # Load the password hash from the file
        wallet_data = shelve.open(WALLET_DATA_PATH)
        hashed_password = wallet_data.get("password")
        wallet_data.close()

        # Check if the password is correct
        password = entered_password.encode("utf-8")
        if not bcrypt.checkpw(password, hashed_password):
            self.password_field.hint_text = "Wrong password, try again"
            self.password_field.text = ""
            return

        try:
            # Prefer new accounts model; fallback to legacy selected_key
            self.public_key = None
            self.private_key = None
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
                show_error_dialog(title="Error", text="Unable to access keys for the active account.")
                return

            def wallet_from_kp():
                classic_address = derive_classic_address(self.public_key)
                wallet = Wallet(public_key=self.public_key, private_key=self.private_key)
                return wallet

            test_wallet = wallet_from_kp()

            my_tx_payment = Payment(
                account=test_wallet.classic_address,
                amount=xrpl.models.amounts.issued_currency_amount.IssuedCurrencyAmount(
                    currency=self._get_currency_code(),
                    issuer=self._get_issuer(),
                    value=str(
                        getattr(self, "_issued_amount_value", self.ids["amount_token_input"].text)
                    ),
                ),
                destination=self.ids.destination_input.text,
            )
            # Sign and submit the transaction via robust helper
            try:
                tx_response = robust_submit_and_wait(my_tx_payment, test_wallet)
                # Friendly status message
                status_message = get_transaction_status_message(tx_response)
                # Determine success/failure
                if hasattr(tx_response, "result") and "meta" in tx_response.result:
                    tx_result = tx_response.result["meta"].get("TransactionResult", "Unknown")
                    # Dismiss dialog before showing message
                    self.dialog.dismiss()
                    if tx_result == "tesSUCCESS":
                        show_info_dialog(title="Success", text=status_message)
                    else:
                        show_error_dialog(title="Transaction Failed", text=status_message)
                else:
                    # Dismiss dialog and show unknown status
                    self.dialog.dismiss()
                    show_error_dialog(title="Transaction Status", text=status_message)
            except Exception as tx_error:
                self.dialog.dismiss()
                show_error_dialog(
                    title="Submission Error", text=f"Failed to submit transaction: {tx_error}"
                )
                return

            self.wallet_data.close()
        except XRPLBinaryCodecException as e:
            self.wallet_data.close()
            self.password_field.hint_text = "XRPLBinaryCodecException Error"

    def check_balance_token(self, dt):
        # Ensure token info present
        if not self._get_currency_code():
            return

        try:
            self.wallet_data = shelve.open(WALLET_DATA_PATH)
            self.public_key = self.wallet_data[
                self.manager.get_screen("wallet_screen").selected_key
            ]

            def wallet_from_kp():
                classic_address = derive_classic_address(self.public_key)
                return classic_address

            test_wallet_address = wallet_from_kp()

            # Get token balance
            try:
                acct_objects = AccountObjects(
                    account=test_wallet_address,
                    ledger_index="validated",
                    type="state",
                    deletion_blockers_only=False,
                    limit=100,
                )
                response = make_request(acct_objects)

                if hasattr(response, "status") and response.status.name == "SUCCESS":
                    data = response.result

                    tokensvalue = dict()
                    currenciescheck = dict()

                    if "account_objects" in data and data["account_objects"]:
                        for currencies in data["account_objects"]:
                            if (
                                "Balance" in currencies
                                and isinstance(currencies["Balance"], dict)
                                and "currency" in currencies["Balance"]
                            ):
                                currency = currencies["Balance"]["currency"]
                                value = currencies["Balance"]["value"]
                                tokensvalue[currency] = value
                                currenciescheck[currency] = currency

                    # Check for our token
                    if self._get_currency_code() in currenciescheck:
                        value = format(float(tokensvalue[self._get_currency_code()]), ".2f")
                        if "token_balance" in self.ids:
                            self.ids.token_balance.text = value
                    else:
                        if "token_balance" in self.ids:
                            self.ids.token_balance.text = f"No {self._get_token_name()} Trustline"
                elif hasattr(response, "result") and "error" in response.result:
                    error_code = response.result["error"]
                    if error_code == "actNotFound":
                        if "token_balance" in self.ids:
                            self.ids.token_balance.text = "Account not funded"
                    else:
                        if "token_balance" in self.ids:
                            self.ids.token_balance.text = f"No {self._get_token_name()} Trustline"
                else:
                    if "token_balance" in self.ids:
                        self.ids.token_balance.text = f"No {self._get_token_name()} Trustline"
            except Exception as tokens_error:
                print(f"SendTestToken - Error getting token balance: {tokens_error}")
                if "token_balance" in self.ids:
                    self.ids.token_balance.text = f'No {self.token_config["name"]} Trustline'

            # Transaction History
            try:
                tx_info = AccountTx(
                    account=test_wallet_address, ledger_index_min=-1, ledger_index_max=-1, limit=20
                )
                response2 = make_request(tx_info)

                if hasattr(response2, "status") and response2.status.name == "SUCCESS":
                    data2 = response2.result

                    if "transactions" in data2 and data2["transactions"]:
                        for i, transaction in enumerate(data2["transactions"]):
                            if i >= 20:
                                break

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

                                tx_type = tx.get("TransactionType", "Unknown")
                                amount_text = "Amount not specified"
                                direction = ""

                                if tx_type == "Payment":
                                    if "Amount" in tx:
                                        amount = tx["Amount"]
                                        if isinstance(amount, str) and amount.isdigit():
                                            xrp_amount = format(int(amount) / 1e6, ".2f")
                                            amount_text = f"Amount XRP: {xrp_amount}"
                                        elif isinstance(amount, dict) and "value" in amount:
                                            # Check if it's our token
                                            if (self._get_currency_code() or "") in amount.get(
                                                "currency", ""
                                            ):
                                                value = format(float(amount["value"]), ".2f")
                                                amount_text = (
                                                    f"Amount {self._get_token_name()}: {value}"
                                                )
                                            else:
                                                curr = amount.get("currency", "Unknown")
                                                curr = decode_currency_code(curr)
                                                amount_text = (
                                                    f"Amount {curr}: {amount.get('value', '0')}"
                                                )
                                        else:
                                            amount_text = f"Payment - Amount: {amount}"

                                    if "Account" in tx and "Destination" in tx:
                                        if tx["Account"] == test_wallet_address:
                                            direction = " (Sent)"
                                        elif tx["Destination"] == test_wallet_address:
                                            direction = " (Received)"

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

                                label.text = amount_text + direction

                        for j in range(len(data2["transactions"]), 20):
                            lbl = self._get_tx_label(j + 1)
                            if lbl:
                                lbl.text = ""
                    else:
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
                print(f"SendTestToken - Error getting transactions: {tx_error}")
                for i in range(1, 21):
                    lbl = self._get_tx_label(i)
                    if lbl:
                        lbl.text = ""
            self.wallet_data.close()
        except Exception as e:
            print(e)
            self.wallet_data.close()
            if "token_balance" in self.ids:
                self.ids.token_balance.text = "Error: Could not get balance"

    def _get_tx_label(self, index: int):
        try:
            card = self.ids.get("transactions_card")
            if card and hasattr(card, "ids"):
                return card.ids.get(f"transaction{index}")
        except Exception:
            pass
        return self.ids.get(f"transaction{index}")

    def backto_wallet(self):
        self.manager.current = "wallet_screen"
