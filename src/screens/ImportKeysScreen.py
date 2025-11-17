# Kivy libraries for the GUI.
# Encryption libraries for password and key encryption.
import logging

from kivy.uix.screenmanager import Screen

from src.utils.dialogs import show_confirm_dialog, show_error_dialog, show_info_dialog

logging.basicConfig(level=logging.WARNING)
import os
import shelve

# Import multi-faucet manager and mnemonic manager
import sys
import traceback
from hashlib import sha512

from Crypto.Cipher import AES
from Crypto.Protocol.KDF import PBKDF2
from Crypto.Random import get_random_bytes
from ecpy.curves import Curve
from ecpy.eddsa import EDDSA
from ecpy.keys import ECPrivateKey

from src.utils.storage_paths import WALLET_DATA_PATH

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from xrpl.clients import JsonRpcClient
from xrpl.core.binarycodec.exceptions import XRPLBinaryCodecException
from xrpl.core.keypairs import derive_classic_address
from xrpl.core.keypairs.ed25519 import PREFIX as ED_PREFIX
from xrpl.models.requests import AccountInfo

# XRPL libraries for xrpl functionality
from xrpl.wallet import Wallet

from src.utils.mnemonic_manager import mnemonic_manager, recover_wallet_from_mnemonic

JSON_RPC_URL = "https://testnet.xrpl-labs.com"  # Use XRPL Labs testnet (more reliable)
client = JsonRpcClient(JSON_RPC_URL)


# Import Keys Screen
class ImportKeysScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.wallet_data = None

    def import_from_mnemonic(self):
        """Import wallet from 12-word mnemonic phrase."""
        from kivymd.uix.boxlayout import MDBoxLayout
        from kivymd.uix.label import MDLabel
        from kivymd.uix.textfield import MDTextField

        # Create mnemonic input dialog
        content = MDBoxLayout(
            orientation="vertical", spacing="10dp", size_hint_y=None, height="300dp"
        )

        content.add_widget(
            MDLabel(
                text="🔐 Enter Your 12-Word Recovery Phrase\n\nEnter the words separated by spaces or with numbers:\n1. word1 2. word2 3. word3...",
                theme_text_color="Primary",
                size_hint_y=None,
                height="100dp",
                text_size=(None, None),
            )
        )

        self.mnemonic_input = MDTextField(
            hint_text="Enter your 12 words here...",
            multiline=True,
            size_hint_y=None,
            height="100dp",
        )
        content.add_widget(self.mnemonic_input)

        content.add_widget(
            MDLabel(
                text="Optional passphrase for additional security:",
                theme_text_color="Secondary",
                size_hint_y=None,
                height="30dp",
            )
        )

        self.passphrase_input = MDTextField(
            hint_text="Passphrase (optional)", password=True, size_hint_y=None, height="50dp"
        )
        content.add_widget(self.passphrase_input)

        show_confirm_dialog(
            title="🔑 Import from Mnemonic",
            content=content,
            confirm_text="🔑 Import Wallet",
            cancel_text="❌ Cancel",
            on_confirm=lambda: self.process_mnemonic_import(None),
            dismiss_on_confirm=True,
        )

    def process_mnemonic_import(self, dialog):
        """Process the mnemonic import."""
        try:
            # Get input values
            mnemonic_text = self.mnemonic_input.text.strip()
            passphrase = self.passphrase_input.text.strip()

            if not mnemonic_text:
                self.show_import_error("Please enter your mnemonic phrase.")
                return

            # Parse mnemonic
            words = mnemonic_manager.parse_mnemonic_input(mnemonic_text)

            if len(words) != 12:
                self.show_import_error(
                    f"Expected 12 words, got {len(words)}. Please check your mnemonic phrase."
                )
                return

            # Validate mnemonic
            if not mnemonic_manager.validate_mnemonic(words):
                self.show_import_error(
                    "Invalid mnemonic phrase. Please check the words and try again."
                )
                return

            # Generate wallet from mnemonic
            wallet = recover_wallet_from_mnemonic(words, passphrase)

            # Set the keys in the UI
            self.ids.private_key.text = wallet.private_key
            self.ids.public_key.text = wallet.public_key

            if dialog:
                dialog.dismiss()

            # Show success message
            show_info_dialog(
                title="🎉 Wallet Imported Successfully!",
                text=(
                    f"✅ Wallet imported from mnemonic phrase!\n\n"
                    f"Address: {wallet.classic_address}\n\n"
                    "The keys have been filled in. Click 'Store keys' to save them securely."
                ),
            )

        except Exception as e:
            self.show_import_error(f"Error importing wallet: {str(e)}")

    def show_import_error(self, message):
        """Show import error dialog."""
        show_error_dialog(title="❌ Import Failed", text=message)

    def store_keys(self):
        # For easy testing, let's check if user wants to use mnemonic import first
        if not self.ids.public_key.text and not self.ids.private_key.text:
            # If no keys are entered, navigate to dedicated mnemonic import screen
            show_confirm_dialog(
                title="🔑 Import Method",
                text=(
                    "No keys detected. How would you like to import your wallet?\n\n"
                    "• Enter keys manually in the fields above\n"
                    "• Import from 12-word mnemonic phrase"
                ),
                confirm_text="🔑 Use 12-Word Phrase",
                cancel_text="📝 Enter Keys Manually",
                on_confirm=lambda: self.start_mnemonic_import(None),
                dismiss_on_confirm=True,
            )
            return

        # Original store_keys functionality
        self._original_store_keys()

    def start_mnemonic_import(self, dialog):
        """Start mnemonic import process with simple dialog."""
        dialog.dismiss()

        # Create a simple mnemonic input dialog
        from kivymd.uix.boxlayout import MDBoxLayout
        from kivymd.uix.label import MDLabel
        from kivymd.uix.textfield import MDTextField

        content = MDBoxLayout(
            orientation="vertical", spacing="10dp", size_hint_y=None, height="200dp"
        )

        instruction_text = """🔑 Enter your 12-word recovery phrase below:

You can enter the words separated by spaces, or with numbers like:
1. word1 2. word2 3. word3...

This will restore your wallet from the mnemonic."""

        content.add_widget(
            MDLabel(
                text=instruction_text,
                theme_text_color="Primary",
                size_hint_y=None,
                height="120dp",
                text_size=(None, None),
            )
        )

        self.mnemonic_input = MDTextField(
            hint_text="Enter your 12 words here...", multiline=True, size_hint_y=None, height="60dp"
        )
        content.add_widget(self.mnemonic_input)

        show_confirm_dialog(
            title="🔑 Import from Mnemonic",
            content=content,
            confirm_text="🔄 Import Wallet",
            cancel_text="❌ Cancel",
            on_confirm=lambda: self.process_mnemonic_import(None),
            dismiss_on_confirm=True,
        )

    def process_mnemonic_import(self, dialog):
        """Process the mnemonic import."""
        try:
            entered_text = self.mnemonic_input.text.strip()
            entered_words = mnemonic_manager.parse_mnemonic_input(entered_text)

            if len(entered_words) != 12:
                self.show_import_error("Please enter exactly 12 words.")
                return

            # Try to recover wallet from mnemonic
            wallet = recover_wallet_from_mnemonic(entered_words)

            # Set the keys in the UI
            self.ids.private_key.text = wallet.private_key
            self.ids.public_key.text = wallet.public_key

            if dialog:
                dialog.dismiss()

            # Show success dialog
            show_confirm_dialog(
                title="✅ Wallet Imported Successfully!",
                text=(
                    f"🎉 Your wallet has been restored from the mnemonic!\n\n📱 Address: {wallet.classic_address}\n\n"
                    "You can now store these keys to complete the import."
                ),
                confirm_text="💾 Store Wallet",
                cancel_text="Close",
                on_confirm=lambda: self.complete_import(None),
                dismiss_on_confirm=True,
            )

        except Exception as e:
            self.show_import_error(f"Import failed: {str(e)}")

    def show_import_error(self, message):
        """Show import error dialog."""
        show_error_dialog(title="❌ Import Failed", text=message)

    def complete_import(self, dialog):
        """Complete the import by storing the keys."""
        if dialog:
            dialog.dismiss()
        self._original_store_keys()

    def _original_store_keys(self):
        # Clear previous error messages
        self.ids.invalid_keys.text = ""

        if not self.ids.public_key.text:
            self.ids.invalid_keys.text = "Public key must be filled"
            return
        if not self.ids.private_key.text:
            self.ids.invalid_keys.text = "Private key must be filled"
            return

        public_key = self.ids.public_key.text.strip()
        private_key = self.ids.private_key.text.strip()

        # Check if it is a valid HEX
        import re

        def is_hex(s):
            # A valid hex string must have an even number of characters and only contain
            # characters from 0-9 and A-F (case-insensitive)
            pattern = re.compile(r"^[0-9a-fA-F]{2,}$")
            return bool(pattern.match(s)) and len(s) % 2 == 0

        if not is_hex(public_key):
            self.ids.invalid_keys.text = "Public key must be a valid hex string"
            return
        if not is_hex(private_key):
            self.ids.invalid_keys.text = "Private key must be a valid hex string"
            return

        try:
            # Derive Public key from Private key for validation
            if private_key.startswith(ED_PREFIX):
                private = ECPrivateKey(
                    int(private_key[len(ED_PREFIX) :], 16), Curve.get_curve("Ed25519")
                )
                public = EDDSA.get_public_key(private, sha512)
                derived_public_key = (
                    ED_PREFIX + Curve.get_curve("Ed25519").encode_point(public.W).hex().upper()
                )
            else:
                private = ECPrivateKey(int(private_key, 16), Curve.get_curve("secp256k1"))
                public = private.get_public_key()
                derived_public_key = (
                    bytes(Curve.get_curve("secp256k1").encode_point(public.W, compressed=True))
                    .hex()
                    .upper()
                )

            # Check if the given public key matches the derived public key
            if public_key.upper() != derived_public_key.upper():
                self.ids.invalid_keys.text = (
                    "Keys don't match - public key doesn't correspond to private key"
                )
                return

        except Exception as e:
            self.ids.invalid_keys.text = f"Error validating keys: {str(e)}"
            return

        # Create wallet and validate account exists
        try:
            classic_address = derive_classic_address(public_key)
            test_wallet = Wallet.create()
            test_wallet.classic_address = classic_address

            # Check if account exists on the ledger
            acct_info = AccountInfo(
                account=test_wallet.classic_address,
                ledger_index="validated",
                strict=True,
            )
            response = client.request(acct_info)

        except Exception as e:
            self.ids.invalid_keys.text = "Account doesn't exist on the XRPL testnet"
            return

        # Store private key with proper error handling
        wallet_data = None
        try:
            wallet_data = shelve.open(WALLET_DATA_PATH)
            if "password" not in wallet_data:
                self.ids.invalid_keys.text = "No password set. Please set up your account first."
                return

            password = wallet_data["password"]
            if isinstance(password, bytes):
                password = password.decode("utf-8").encode("ascii")
            else:
                password = password.encode("ascii")

            salt = get_random_bytes(16)

            # Determine the next available account number
            account_number = 1
            while f"public_key{account_number}" in wallet_data:
                account_number += 1

            # Generate encryption key and encrypt private key
            key = PBKDF2(password, salt, dkLen=32, count=100000)
            cipher = AES.new(key, AES.MODE_GCM)
            nonce = cipher.nonce
            encrypted_private_key = cipher.encrypt(private_key.encode("utf-8"))

            # Store all key data
            wallet_data[f"public_key{account_number}"] = public_key
            wallet_data[f"private_key{account_number}"] = encrypted_private_key
            wallet_data[f"nonce_key{account_number}"] = nonce
            wallet_data[f"salt_key{account_number}"] = salt

            # Set the selected key for the wallet screen
            selected_key = f"public_key{account_number}"

            # Navigate to wallet screen and set the selected key
            self.manager.current = "wallet_screen"
            wallet_screen = self.manager.get_screen("wallet_screen")
            wallet_screen.set_selected_key(selected_key)
            wallet_screen.on_pre_enter()

        except Exception as e:
            self.ids.invalid_keys.text = f"Error storing keys: {str(e)}"
            print(f"Storage error details: {e}")
            traceback.print_exc()
        finally:
            if wallet_data:
                wallet_data.close()

    def go_back(self):
        self.manager.current = "wallet_setup_screen"

    def back_to_wallet_setup(self):
        self.manager.current = "wallet_setup_screen"
