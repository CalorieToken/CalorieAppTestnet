"""
Add Trustline Screen - Allows users to add trustlines for test tokens
"""

import shelve

import bcrypt
from cryptography.fernet import Fernet
from kivy.clock import Clock
from kivy.core.clipboard import Clipboard
from kivy.uix.screenmanager import Screen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.textfield import MDTextField
from xrpl.models.amounts import IssuedCurrencyAmount
from xrpl.models.transactions import TrustSet

# XRPL libraries
from xrpl.wallet import Wallet

from src.utils.currency_utils import decode_currency_code
from src.utils.dialogs import show_confirm_dialog, show_error_dialog, show_info_dialog
from src.utils.password_field_utils import create_password_field_with_toggle
from src.utils.robust_transaction import robust_submit_and_wait
from src.utils.storage_paths import WALLET_DATA_PATH

# Import the robust XRPL client manager
from src.utils.xrpl_client_manager import make_request


class AddTrustlineScreen(Screen):
    """Screen for adding trustlines to test tokens"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.dialog = None
        self.selected_currency = None
        self.available_currencies = []

    def on_pre_enter(self, *args):
        """Load all issued currencies when entering screen"""
        self.load_all_currencies()
        self.update_currency_list()

    # Use shared currency decode utility

    def show_manual_input_dialog(self):
        """Show dialog for manual trustline input with paste support"""
        from kivymd.uix.label import MDLabel
        from kivymd.uix.textfield import MDTextField

        content_box = MDBoxLayout(
            orientation="vertical", spacing="12dp", size_hint_y=None, padding="20dp"
        )
        content_box.bind(minimum_height=content_box.setter("height"))

        content_box.add_widget(
            MDLabel(
                text="Paste trustline info (CURRENCY|ISSUER) or enter manually:",
                font_size="13sp",
                halign="left",
                theme_text_color="Custom",
                text_color=(0.20, 0.28, 0.40, 1),
                size_hint_y=None,
                height="40dp",
            )
        )

        paste_field = MDTextField(
            hint_text="Paste or type: CODE|ISSUER_ADDRESS",
            mode="filled",
            multiline=False,
            size_hint_y=None,
            height="56dp",
        )
        content_box.add_widget(paste_field)

        content_box.add_widget(
            MDLabel(text="OR enter separately:", size_hint_y=None, height="28dp")
        )

        currency_field = MDTextField(
            hint_text="Currency Code (e.g., USD)", mode="filled", size_hint_y=None, height="56dp"
        )
        content_box.add_widget(currency_field)

        issuer_field = MDTextField(
            hint_text="Issuer Address (rXXX...)", mode="filled", size_hint_y=None, height="56dp"
        )
        content_box.add_widget(issuer_field)

        self.dialog = show_confirm_dialog(
            title="Manual Trustline Input",
            content=content_box,
            confirm_text="Next",
            cancel_text="Cancel",
            secondary_text="Paste from Clipboard",
            on_secondary=lambda: self.paste_from_clipboard(
                paste_field, currency_field, issuer_field
            ),
            on_confirm=lambda: self.process_manual_input(
                paste_field.text, currency_field.text, issuer_field.text
            ),
            dismiss_on_confirm=False,
        )

    def paste_from_clipboard(self, paste_field, currency_field, issuer_field):
        """Parse clipboard content and fill fields"""
        try:
            clipboard_text = Clipboard.paste()

            if "|" in clipboard_text:
                # Parse CURRENCY|ISSUER format
                parts = clipboard_text.strip().split("|")
                if len(parts) >= 2:
                    currency_field.text = parts[0].strip()
                    issuer_field.text = parts[1].strip()
                    paste_field.text = clipboard_text.strip()
            else:
                # Just paste into paste field
                paste_field.text = clipboard_text.strip()

        except Exception as e:
            print(f"Error pasting from clipboard: {e}")

    def process_manual_input(self, paste_text, currency_text, issuer_text):
        """Process manual input and proceed to limit dialog"""
        currency_code = ""
        issuer_address = ""

        # Try to parse from paste field first
        if paste_text and "|" in paste_text:
            parts = paste_text.strip().split("|")
            if len(parts) >= 2:
                currency_code = parts[0].strip().upper()
                issuer_address = parts[1].strip()

        # Fall back to individual fields
        if not currency_code and currency_text:
            currency_code = currency_text.strip().upper()
        if not issuer_address and issuer_text:
            issuer_address = issuer_text.strip()

        # Validate
        if not currency_code or not issuer_address:
            from src.utils.enhanced_dialogs import show_validation_error
            show_validation_error(
                "Missing Required Fields",
                details="Please provide both currency code and issuer address."
            )
            return

        # Validate currency code: 3-12 ASCII or 40-hex
        import re

        is_hex40 = bool(re.fullmatch(r"[0-9A-Fa-f]{40}", currency_code))
        is_ascii = bool(re.fullmatch(r"[A-Za-z0-9]{3,12}", currency_code))
        if not (is_hex40 or is_ascii):
            from src.utils.enhanced_dialogs import show_validation_error
            show_validation_error(
                "Invalid Currency Code",
                details="Currency code must be either:\n• 3-12 characters (letters and numbers only)\n• 40-character hexadecimal code"
            )
            return

        if not issuer_address.startswith("r"):
            from src.utils.enhanced_dialogs import show_validation_error
            show_validation_error(
                "Invalid Issuer Address",
                details="XRPL addresses must start with 'r'"
            )
            return
        
        if len(issuer_address) < 25 or len(issuer_address) > 35:
            from src.utils.enhanced_dialogs import show_validation_error
            show_validation_error(
                "Invalid Issuer Address",
                details="XRPL address length must be 25-35 characters"
            )
            return

        # Create currency dict for compatibility
        self.selected_currency = {
            "code": currency_code,
            "issuer": issuer_address,
            "name": currency_code,  # Use code as name
            "max_supply": 1000000000,  # Default
        }

        # Dismiss and proceed to limit dialog
        if self.dialog:
            self.dialog.dismiss()

        self.show_limit_dialog()

    def load_all_currencies(self):
        """Load all issued currencies from database"""
        try:
            with shelve.open(WALLET_DATA_PATH) as db:
                issued_currencies = db.get("issued_currencies", [])
                self.available_currencies = []

                for curr in issued_currencies:
                    self.available_currencies.append(
                        {
                            "code": curr["code"],
                            "name": curr["name"],
                            "issuer": curr["issuer"],
                            "max_supply": curr.get("max_supply", float("inf")),
                        }
                    )
        except Exception as e:
            print(f"Error loading currencies: {e}")
            self.available_currencies = []

    def update_currency_list(self):
        """Update the UI list of currencies"""
        if not hasattr(self, "ids") or "currency_list" not in self.ids:
            return

        from kivymd.uix.list import ThreeLineListItem

        self.ids.currency_list.clear_widgets()

        if not self.available_currencies:
            # Show empty state
            empty_label = ThreeLineListItem(
                text="No Currencies Available",
                secondary_text="Issue a currency first to add trustlines",
                tertiary_text="",
                theme_text_color="Custom",
                text_color=(0.4, 0.4, 0.4, 1),
            )
            self.ids.currency_list.add_widget(empty_label)
            return

        for currency in self.available_currencies:
            code_disp = decode_currency_code(currency["code"])
            issuer_short = f"{currency['issuer'][:10]}...{currency['issuer'][-8:]}"

            item = ThreeLineListItem(
                text=f"{code_disp} - {currency['name']}",
                secondary_text=f"Issuer: {issuer_short}",
                tertiary_text=f"Max Supply: {currency.get('max_supply', 'Unlimited')}",
                on_release=lambda x, c=currency: self.select_currency(c),
            )
            self.ids.currency_list.add_widget(item)

    def select_currency(self, currency):
        """Select a currency and show limit input dialog"""
        self.selected_currency = currency
        self.show_limit_dialog()

    def show_limit_dialog(self):
        """Show dialog to enter trustline limit"""
        if not self.selected_currency:
            self.show_error_message("No currency selected")
            return
        from kivy.uix.boxlayout import BoxLayout
        from kivymd.uix.label import MDLabel
        from kivymd.uix.textfield import MDTextField

        content_box = MDBoxLayout(
            orientation="vertical", spacing="12dp", size_hint_y=None, padding="20dp"
        )
        content_box.bind(minimum_height=content_box.setter("height"))

        code_val = self.selected_currency["code"]
        issuer_val = self.selected_currency["issuer"]

        content_box.add_widget(
            MDLabel(
                text=f"Currency: {decode_currency_code(code_val)}",
                font_size="15sp",
                halign="left",
                theme_text_color="Custom",
                text_color=(0.20, 0.28, 0.40, 1),
                size_hint_y=None,
                height="28dp",
            )
        )

        issuer_short = f"{issuer_val[:15]}...{issuer_val[-10:]}"
        content_box.add_widget(
            MDLabel(
                text=f"Issuer: {issuer_short}",
                font_size="15sp",
                halign="left",
                theme_text_color="Custom",
                text_color=(0.20, 0.28, 0.40, 1),
                size_hint_y=None,
                height="28dp",
            )
        )

        content_box.add_widget(MDLabel(text="", size_hint_y=None, height="16dp"))

        limit_field = MDTextField(
            hint_text="Limit (default: 1B)",
            mode="fill",
            line_color_focus=(0, 0.55, 0.21, 1),
            fill_color_normal=(0.85, 0.87, 0.93, 1),
            fill_color_focus=(0.91, 0.92, 0.96, 1),
            size_hint_y=None,
            height="56dp",
            input_filter="float",
            helper_text="Enter a positive number or leave empty for 1 billion",
            helper_text_mode="on_focus",
        )
        content_box.add_widget(limit_field)

        # Determine if a trustline already exists to offer removal
        has_line = self.has_existing_trustline(code_val, issuer_val)

        # Build confirm dialog with optional secondary action
        self.dialog = show_confirm_dialog(
            title="Set Trustline Limit",
            content=content_box,
            confirm_text="Next",
            cancel_text="Cancel",
            secondary_text=("Remove Trustline" if has_line else None),
            on_secondary=(
                (lambda: self.show_remove_password_dialog(code_val, issuer_val))
                if has_line
                else None
            ),
            on_confirm=lambda: self.proceed_with_limit(limit_field.text),
            dismiss_on_confirm=False,
        )

    def proceed_with_limit(self, limit_text):
        """Validate limit and show password dialog with enhanced feedback"""
        if not self.selected_currency:
            from src.utils.enhanced_dialogs import show_error
            show_error("No Currency Selected", "Please select a currency before proceeding.")
            return
        
        # Validate limit
        try:
            limit = float(limit_text) if limit_text.strip() else 1000000000
            if limit <= 0:
                # Show error in dialog field
                if hasattr(self, "dialog") and self.dialog:
                    # Find the text field and set error
                    for widget in self.dialog.children:
                        if hasattr(widget, "children"):
                            for child in widget.children:
                                if isinstance(child, MDTextField):
                                    child.error = True
                                    child.helper_text = "Limit must be a positive number"
                                    child.helper_text_mode = "on_error"
                from src.utils.enhanced_dialogs import show_validation_error
                show_validation_error(
                    "Invalid Trust Limit",
                    details="The trust limit must be a positive number greater than 0."
                )
                return
        except ValueError:
            # Show error in dialog field
            if hasattr(self, "dialog") and self.dialog:
                # Find the text field and set error
                for widget in self.dialog.children:
                    if hasattr(widget, "children"):
                        for child in widget.children:
                            if isinstance(child, MDTextField):
                                child.error = True
                                child.helper_text = "Please enter a valid number"
                                child.helper_text_mode = "on_error"
            from src.utils.enhanced_dialogs import show_validation_error
            show_validation_error(
                "Invalid Trust Limit",
                details="Please enter a valid numeric value for the trust limit."
            )
            return

        # Close limit dialog
        if self.dialog:
            self.dialog.dismiss()

        code_val = self.selected_currency["code"]
        issuer_val = self.selected_currency["issuer"]
        
        # Show enhanced confirmation dialog
        from src.utils.enhanced_dialogs import confirm_transaction
        confirm_transaction(
            amount=str(limit),
            currency=decode_currency_code(code_val),
            destination=f"{issuer_val[:10]}...{issuer_val[-8:]}",
            warning="⚠️ This will create a trustline allowing the issuer to send you up to this amount. This transaction cannot be undone.",
            on_confirm=lambda: self.show_password_dialog(code_val, issuer_val, str(limit)),
            on_cancel=None,
            title="Confirm Trustline Creation"
        )

    def add_trustline(self):
        """Legacy method - now handled through currency selection"""
        pass

    def show_password_dialog(self, currency_code, issuer_address, limit):
        """Show password confirmation dialog"""
        # Define the password input field with toggle visibility
        self.password_field_container = create_password_field_with_toggle(hint_text="Password")
        self.password_field = self.password_field_container.password_field

        from kivy.uix.boxlayout import BoxLayout
        from kivymd.uix.label import MDLabel

        # Define a box layout to contain the text
        content_box = MDBoxLayout(
            orientation="vertical", spacing="12dp", size_hint_y=None, padding="20dp"
        )
        content_box.bind(minimum_height=content_box.setter("height"))

        content_box.add_widget(
            MDLabel(
                text=f"Currency: {decode_currency_code(currency_code)}",
                font_size="15sp",
                halign="left",
                theme_text_color="Custom",
                text_color=(0.20, 0.28, 0.40, 1),
                size_hint_y=None,
                height="28dp",
            )
        )
        content_box.add_widget(
            MDLabel(
                text=f"Issuer: {issuer_address[:15]}...{issuer_address[-10:]}",
                font_size="15sp",
                halign="left",
                theme_text_color="Custom",
                text_color=(0.20, 0.28, 0.40, 1),
                size_hint_y=None,
                height="28dp",
            )
        )
        content_box.add_widget(
            MDLabel(
                text=f"Limit: {limit}",
                font_size="15sp",
                halign="left",
                theme_text_color="Custom",
                text_color=(0.20, 0.28, 0.40, 1),
                size_hint_y=None,
                height="28dp",
            )
        )
        content_box.add_widget(MDLabel(text="", size_hint_y=None, height="16dp"))
        content_box.add_widget(self.password_field_container)

        # Confirm dialog
        self.dialog = show_confirm_dialog(
            title="Confirm Trustline Creation",
            content=content_box,
            confirm_text="Create Trustline",
            cancel_text="Cancel",
            on_confirm=lambda: self.perform_trustline_creation(
                currency_code, issuer_address, limit, self.password_field.text
            ),
            dismiss_on_confirm=False,
        )

    def show_remove_password_dialog(self, currency_code, issuer_address):
        """Show password confirmation dialog for removing a trustline"""
        # Reuse password field helper
        self.password_field_container = create_password_field_with_toggle(hint_text="Password")
        self.password_field = self.password_field_container.password_field

        from kivymd.uix.label import MDLabel

        content_box = MDBoxLayout(
            orientation="vertical", spacing="12dp", size_hint_y=None, padding="20dp"
        )
        content_box.bind(minimum_height=content_box.setter("height"))

        content_box.add_widget(
            MDLabel(
                text=f"Currency: {decode_currency_code(currency_code)}",
                font_size="15sp",
                halign="left",
                theme_text_color="Custom",
                text_color=(0.20, 0.28, 0.40, 1),
                size_hint_y=None,
                height="28dp",
            )
        )
        content_box.add_widget(
            MDLabel(
                text=f"Issuer: {issuer_address[:15]}...{issuer_address[-10:]}",
                font_size="15sp",
                halign="left",
                theme_text_color="Custom",
                text_color=(0.20, 0.28, 0.40, 1),
                size_hint_y=None,
                height="28dp",
            )
        )
        content_box.add_widget(
            MDLabel(
                text="This will set the trustline limit to 0. Balance must be 0.",
                font_size="13sp",
                halign="left",
                theme_text_color="Custom",
                text_color=(0.20, 0.28, 0.40, 1),
                size_hint_y=None,
                height="28dp",
            )
        )
        content_box.add_widget(MDLabel(text="", size_hint_y=None, height="16dp"))
        content_box.add_widget(self.password_field_container)

        self.dialog = show_confirm_dialog(
            title="Confirm Trustline Removal",
            content=content_box,
            confirm_text="Remove Trustline",
            cancel_text="Cancel",
            on_confirm=lambda: self.perform_trustline_removal(
                currency_code, issuer_address, self.password_field.text
            ),
            dismiss_on_confirm=False,
        )

    def perform_trustline_creation(self, currency_code, issuer_address, limit, entered_password):
        """Create the trustline transaction"""
        # Load the password hash from the file
        wallet_data = shelve.open(WALLET_DATA_PATH)
        hashed_password = wallet_data.get("password")
        if not hashed_password:
            wallet_data.close()
            self.show_error_message("Password not set. Please set a password first.")
            return

        # Check if the password is correct
        password = entered_password.encode("utf-8")
        if not bcrypt.checkpw(password, hashed_password):
            wallet_data.close()
            self.password_field.hint_text = "Wrong password, try again"
            self.password_field.text = ""
            return

        # Load wallet from accounts model
        try:
            accounts = wallet_data.get("accounts", [])
            idx = wallet_data.get("active_account", 0)

            if not (0 <= idx < len(accounts)):
                wallet_data.close()
                self.show_error_message("No active account found")
                return

            acct = accounts[idx]

            # Build wallet from available credentials with fallbacks
            wallet = None
            seed = None

            # 1) Legacy path: decrypt encrypted_seed with entered_password
            try:
                import base64

                from Crypto.Cipher import AES
                from Crypto.Protocol.KDF import PBKDF2

                encrypted_seed_b64 = acct.get("encrypted_seed")
                if encrypted_seed_b64:
                    encrypted_seed = base64.b64decode(encrypted_seed_b64)
                    key = PBKDF2(entered_password, b"calorie_salt_v1", dkLen=32)
                    cipher = AES.new(key, AES.MODE_EAX, nonce=encrypted_seed[:16])
                    seed = cipher.decrypt(encrypted_seed[16:]).decode("utf-8")
                    wallet = Wallet.from_seed(seed)
            except Exception as e:
                # Continue to next fallback silently
                pass

            # 2) Modern path: decrypt Fernet-encrypted seed with stored encryption_key
            if wallet is None:
                try:
                    encryption_key = wallet_data.get("encryption_key")
                    if encryption_key:
                        f = Fernet(encryption_key)
                        seed_field = acct.get("seed")
                        if seed_field:
                            seed = f.decrypt(seed_field.encode()).decode()
                            wallet = Wallet.from_seed(seed)
                except Exception:
                    # Continue to next fallback
                    pass

            # 3) Keypair fallback: decrypt private_key (Fernet) and use public_key
            if wallet is None:
                try:
                    encryption_key = wallet_data.get("encryption_key")
                    if encryption_key:
                        f = Fernet(encryption_key)
                        enc_priv = acct.get("private_key")
                        pub_key = acct.get("public_key")
                        if enc_priv and pub_key:
                            private_key = f.decrypt(enc_priv.encode()).decode()
                            wallet = Wallet(public_key=pub_key, private_key=private_key)
                except Exception:
                    pass

            if wallet is None:
                wallet_data.close()
                self.show_error_message("Account seed not found")
                return

            wallet_data.close()

            # Dismiss the password dialog
            if self.dialog:
                self.dialog.dismiss()

            # Create TrustSet transaction
            trustline_tx = TrustSet(
                account=wallet.classic_address,
                limit_amount=IssuedCurrencyAmount(
                    currency=currency_code, issuer=issuer_address, value=limit
                ),
            )

            # Submit transaction
            try:
                response = robust_submit_and_wait(trustline_tx, wallet)

                # Extract fee from response (in drops)
                fee_drops = 0
                if hasattr(response, "result") and isinstance(response.result, dict):
                    if "tx_json" in response.result:
                        fee_drops = int(response.result["tx_json"].get("Fee", 0))
                    elif "Fee" in response.result:
                        fee_drops = int(response.result.get("Fee", 0))
                fee_xrp = fee_drops / 1_000_000  # Convert drops to XRP

                if (
                    hasattr(response, "result")
                    and response.result.get("meta", {}).get("TransactionResult") == "tesSUCCESS"
                ):
                    # Save trustline to database
                    self.save_trustline(currency_code, issuer_address, limit)
                    
                    from src.utils.enhanced_dialogs import show_success
                    show_success(
                        "Trustline Created",
                        f"Successfully created trustline for {decode_currency_code(currency_code)}\n\n"
                        f"Issuer: {issuer_address[:10]}...{issuer_address[-10:]}\n"
                        f"Limit: {limit}\n\n"
                        f"Transaction Fee: {fee_xrp:.6f} XRP"
                    )
                    # Return to wallet screen after 2 seconds
                    from kivy.clock import Clock

                    Clock.schedule_once(lambda dt: self.go_back(), 2.0)
                else:
                    error_msg = response.result.get("meta", {}).get(
                        "TransactionResult", "Unknown error"
                    )
                    from src.utils.enhanced_dialogs import show_transaction_error
                    show_transaction_error(
                        f"Transaction failed: {error_msg}",
                        details=f"Fee charged: {fee_xrp:.6f} XRP"
                    )

            except Exception as e:
                from src.utils.enhanced_dialogs import show_transaction_error
                show_transaction_error(
                    "Failed to submit transaction",
                    details=str(e)
                )

        except Exception as e:
            wallet_data.close()
            from src.utils.enhanced_dialogs import show_error
            show_error("Error", str(e))

    def perform_trustline_removal(self, currency_code, issuer_address, entered_password):
        """Remove a trustline by setting its limit to 0 (requires zero balance)"""
        wallet_data = shelve.open(WALLET_DATA_PATH)
        hashed_password = wallet_data.get("password")
        if not hashed_password:
            wallet_data.close()
            self.show_error_message("Password not set. Please set a password first.")
            return

        # Validate password
        password = entered_password.encode("utf-8")
        if not bcrypt.checkpw(password, hashed_password):
            wallet_data.close()
            self.password_field.hint_text = "Wrong password, try again"
            self.password_field.text = ""
            return

        try:
            accounts = wallet_data.get("accounts", [])
            idx = wallet_data.get("active_account", 0)
            if not (0 <= idx < len(accounts)):
                wallet_data.close()
                self.show_error_message("No active account found")
                return

            acct = accounts[idx]
            wallet = None

            # Try Fernet seed first
            try:
                encryption_key = wallet_data.get("encryption_key")
                if encryption_key:
                    f = Fernet(encryption_key)
                    seed_field = acct.get("seed")
                    if seed_field:
                        seed = f.decrypt(seed_field.encode()).decode()
                        wallet = Wallet.from_seed(seed)
            except Exception:
                pass

            # Fallback to keypair
            if wallet is None:
                try:
                    encryption_key = wallet_data.get("encryption_key")
                    if encryption_key:
                        f = Fernet(encryption_key)
                        enc_priv = acct.get("private_key")
                        pub_key = acct.get("public_key")
                        if enc_priv and pub_key:
                            private_key = f.decrypt(enc_priv.encode()).decode()
                            wallet = Wallet(public_key=pub_key, private_key=private_key)
                except Exception:
                    pass

            if wallet is None:
                wallet_data.close()
                self.show_error_message("Account seed not found")
                return

            wallet_data.close()

            # Build TrustSet with limit 0 to clear line (requires no balance)
            trustline_tx = TrustSet(
                account=wallet.classic_address,
                limit_amount=IssuedCurrencyAmount(
                    currency=currency_code, issuer=issuer_address, value="0"
                ),
            )

            if self.dialog:
                self.dialog.dismiss()

            try:
                response = robust_submit_and_wait(trustline_tx, wallet)

                # Extract fee from response (in drops)
                fee_drops = 0
                if hasattr(response, "result") and isinstance(response.result, dict):
                    if "tx_json" in response.result:
                        fee_drops = int(response.result["tx_json"].get("Fee", 0))
                    elif "Fee" in response.result:
                        fee_drops = int(response.result.get("Fee", 0))
                fee_xrp = fee_drops / 1_000_000  # Convert drops to XRP

                if (
                    hasattr(response, "result")
                    and response.result.get("meta", {}).get("TransactionResult") == "tesSUCCESS"
                ):
                    # Remove from local db cache if present
                    self.remove_trustline_local(currency_code, issuer_address)
                    
                    from src.utils.enhanced_dialogs import show_success
                    show_success(
                        "Trustline Removed",
                        f"Successfully removed trustline for {decode_currency_code(currency_code)}\\n\\n"
                        f"Issuer: {issuer_address[:10]}...{issuer_address[-10:]}\\n\\n"
                        f"Transaction Fee: {fee_xrp:.6f} XRP"
                    )
                    Clock.schedule_once(lambda dt: self.go_back(), 2.0)
                else:
                    error_msg = response.result.get("meta", {}).get(
                        "TransactionResult", "Unknown error"
                    )
                    from src.utils.enhanced_dialogs import show_transaction_error
                    show_transaction_error(
                        f"Transaction failed: {error_msg}",
                        details=f"Fee charged: {fee_xrp:.6f} XRP"
                    )
            except Exception as e:
                from src.utils.enhanced_dialogs import show_transaction_error
                show_transaction_error(
                    "Failed to submit transaction",
                    details=str(e)
                )
        except Exception as e:
            try:
                wallet_data.close()
            except Exception:
                pass
            self.show_error_message(f"Error: {str(e)}")

    def has_existing_trustline(self, currency_code, issuer_address):
        """Check if the active account has an existing trustline for currency/issuer"""
        try:
            with shelve.open(WALLET_DATA_PATH) as db:
                accounts = db.get("accounts", [])
                idx = db.get("active_account", 0)
                if not (0 <= idx < len(accounts)):
                    return False
                acct = accounts[idx]
                from xrpl.core.keypairs import derive_classic_address

                my_addr = acct.get("address") or (
                    derive_classic_address(acct.get("public_key", ""))
                    if acct.get("public_key")
                    else None
                )
                if not my_addr:
                    return False

            from xrpl.models.requests import AccountLines

            req = AccountLines(account=my_addr, peer=issuer_address)
            resp = make_request(req)
            if hasattr(resp, "status") and resp.status.name == "SUCCESS":
                lines = resp.result.get("lines", [])
                for line in lines:
                    if line.get("currency", "").upper() == currency_code.upper():
                        return True
            return False
        except Exception:
            return False

    def remove_trustline_local(self, currency_code, issuer_address):
        """Remove trustline entry from local DB cache if it exists"""
        try:
            with shelve.open(WALLET_DATA_PATH, writeback=True) as db:
                trustlines = db.get("trustlines", [])
                new_list = [
                    tl
                    for tl in trustlines
                    if not (
                        tl.get("currency") == currency_code and tl.get("issuer") == issuer_address
                    )
                ]
                if len(new_list) != len(trustlines):
                    db["trustlines"] = new_list
        except Exception:
            pass

    def save_trustline(self, currency_code, issuer_address, limit):
        """Save trustline to database"""
        with shelve.open(WALLET_DATA_PATH) as db:
            # Get or create trustlines list
            trustlines = db.get("trustlines", [])

            # Get active account
            accounts = db.get("accounts", [])
            idx = db.get("active_account", 0)

            if 0 <= idx < len(accounts):
                from xrpl.core.keypairs import derive_classic_address

                account_address = accounts[idx].get("address") or (
                    derive_classic_address(accounts[idx].get("public_key", ""))
                    if accounts[idx].get("public_key")
                    else None
                )

                # Check if trustline already exists
                trustline_exists = False
                for tl in trustlines:
                    if (
                        tl.get("account") == account_address
                        and tl.get("currency") == currency_code
                        and tl.get("issuer") == issuer_address
                    ):
                        trustline_exists = True
                        break

                if not trustline_exists:
                    # Add new trustline
                    trustlines.append(
                        {
                            "account": account_address,
                            "currency": currency_code,
                            "issuer": issuer_address,
                            "limit": limit,
                        }
                    )
                    db["trustlines"] = trustlines

    def show_error_message(self, message):
        """Show error dialog"""
        show_error_dialog("Error", message)

    def show_success_message(self, message):
        """Show success dialog"""
        show_info_dialog("Success", message)

    def go_back(self):
        """Go back to wallet screen"""
        self.manager.current = "wallet_screen"
