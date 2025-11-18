from kivy.core.clipboard import Clipboard
from kivy.uix.screenmanager import Screen

from src.utils.dialogs import show_confirm_dialog, show_info_dialog

import os
import shelve

from hashlib import sha512

from Crypto.Cipher import AES
from Crypto.Protocol.KDF import PBKDF2
from Crypto.Random import get_random_bytes
from ecpy.curves import Curve
from ecpy.eddsa import EDDSA
from ecpy.keys import ECPrivateKey
from xrpl.clients import JsonRpcClient
from xrpl.core.keypairs.ed25519 import PREFIX as ED_PREFIX
from xrpl.models.requests import AccountInfo

# XRPL libraries for xrpl functionality
from xrpl.wallet import Wallet

from src.utils.storage_paths import WALLET_DATA_PATH
from src.utils.faucet_manager import generate_multi_faucet_wallet
from src.utils.mnemonic_manager import generate_wallet_with_mnemonic
from src.utils.clipboard_utils import secure_copy

JSON_RPC_URL = "https://testnet.xrpl-labs.com"  # Use XRPL Labs testnet (more reliable)
client = JsonRpcClient(JSON_RPC_URL)


# Create Extra Wallet Screen
class CreateExtraWalletScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.wallet_data = None

    def generate_keys(self):
        """Generate extra wallet - now defaults to mnemonic generation."""
        print("🔄 Using mnemonic generation for extra wallet")
        return self.generate_keys_with_mnemonic()

    def generate_keys_with_mnemonic(self):
        """Generate extra wallet with 12-word mnemonic phrase."""
        try:
            print("Generating extra wallet with 12-word mnemonic...")

            # Generate wallet with mnemonic
            wallet, mnemonic = generate_wallet_with_mnemonic()

            # Set the keys in the UI
            self.ids.private_key.text = wallet.private_key
            self.ids.public_key.text = wallet.public_key

            # Show mnemonic dialog for extra wallet
            mnemonic_display = "\n".join([f"{i+1:2d}. {word}" for i, word in enumerate(mnemonic)])

            dialog_content = f"""🔐 Extra Wallet - 12-Word Recovery Phrase:

{mnemonic_display}

⚠️ IMPORTANT: Write down these 12 words!
This is for your EXTRA wallet #{self.get_next_account_number()}.

Address: {wallet.classic_address}
Private Key: {wallet.private_key}"""

            show_confirm_dialog(
                title="🎉 Extra Wallet Created with Mnemonic!",
                text=dialog_content,
                confirm_text="✅ Continue",
                cancel_text="📋 Copy Mnemonic",
                on_confirm=lambda: None,
                on_cancel=lambda: self.copy_mnemonic(mnemonic),
                dismiss_on_confirm=True,
            )

        except Exception as e:
            print(f"Error generating extra wallet with mnemonic: {e}")
            self._original_generate_keys()

    def copy_mnemonic(self, mnemonic):
        """Copy mnemonic to clipboard."""
        mnemonic_text = " ".join(mnemonic)
        secure_copy(mnemonic_text, clear_after=30.0)
        print("✅ Extra wallet mnemonic copied to clipboard!")

    def get_next_account_number(self):
        """Get the next account number for display."""
        try:
            wallet_data = shelve.open(WALLET_DATA_PATH)
            account_number = 1
            while f"public_key{account_number}" in wallet_data:
                account_number += 1
            wallet_data.close()
            return account_number
        except Exception:
            return "X"

    def _original_generate_keys(self):
        # Use the multi-faucet system for robust wallet funding
        try:
            print("Generating extra wallet with multi-faucet system...")
            test_wallet, funding_status = generate_multi_faucet_wallet(client)

            self.ids.private_key.text = test_wallet.private_key
            self.ids.public_key.text = test_wallet.public_key

            # Determine dialog content based on funding success
            if "✅" in funding_status:
                dialog_title = "Extra Wallet Generated & Funded!"
                success_text = (
                    f"{funding_status}\n\n"
                    "Copy keypair to store it somewhere safe in order to keep access to your funds!\n"
                    f"Private Key: {test_wallet.private_key}\nPublic Key: {test_wallet.public_key}"
                )
            else:
                dialog_title = "Extra Wallet Generated (Unfunded)"
                success_text = (
                    f"{funding_status}\n\n"
                    f"Private Key: {test_wallet.private_key}\nPublic Key: {test_wallet.public_key}\n\n"
                    "Alternative funding options:\n"
                    "• Try XRPL.org faucet: https://xrpl.org/xrp-testnet-faucet.html\n"
                    "• Try Ripple faucet: https://faucet.ripple.com/\n"
                    "• Ask in XRPL community channels for testnet XRP"
                )

        except Exception as e:
            # Ultimate fallback if multi-faucet system fails
            print(f"Multi-faucet system failed: {e}. Using basic wallet creation...")
            test_wallet = Wallet.create()
            self.ids.private_key.text = test_wallet.private_key
            self.ids.public_key.text = test_wallet.public_key
            dialog_title = "Extra Wallet Generated (System Error)"
            success_text = (
                f"System error occurred: {e}\n\n"
                f"Private Key: {test_wallet.private_key}\nPublic Key: {test_wallet.public_key}\n\n"
                "Please fund manually using external faucets."
            )

        show_confirm_dialog(
            title=dialog_title,
            text=success_text,
            confirm_text="Proceed",
            cancel_text="Copy",
            on_confirm=lambda: None,
            on_cancel=lambda: self.copy_keys(self.ids.private_key.text, self.ids.public_key.text),
            dismiss_on_confirm=True,
        )

    def copy_keys(self, private_key, public_key):
        # Copy the private and public keys to the clipboard
        secure_copy("Private_Key: " + private_key + "\n" + "Public_Key: " + public_key, clear_after=30.0)

    def proceed(self, dialog):
        dialog.dismiss()

    def store_keys(self):
        if not self.ids.public_key.text:
            self.ids.public_key.hint_text = "Public key must be filled"
            return
        if not self.ids.private_key.text:
            self.ids.private_key.hint_text = "Private key must be filled"
            return

        public_key = self.ids.public_key.text
        private_key = self.ids.private_key.text

        # Check if it is a valid HEX
        import re

        def is_hex(s):
            # A valid hex string must have an even number of characters and only contain
            # characters from 0-9 and A-F (case-insensitive)
            pattern = re.compile(r"^[0-9a-fA-F]{2,}$")
            return bool(pattern.match(s))

        if not is_hex(public_key):
            self.ids.public_key.hint_text = "Public key must be a valid hex string"
            return
        if not is_hex(private_key):
            self.ids.private_key.hint_text = "Private key must be a valid hex string"
            return

        # Derive Public key from Private key
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
        if public_key != derived_public_key:
            self.ids.private_key.hint_text = "Keys aren't valid"
            self.ids.public_key.hint_text = "Keys aren't valid"
            return

        # Check if account exists
        # Create wallet from existing keys using proper XRPL method
        try:
            # The private_key from generate_keys is already in hex format
            # We need to create a wallet from the existing key pair
            from xrpl.core.keypairs import derive_classic_address

            # Validate the key format and derive address
            if private_key.startswith(ED_PREFIX):
                # Ed25519 key
                classic_address = derive_classic_address(public_key)
            else:
                # secp256k1 key
                classic_address = derive_classic_address(public_key)

            # Create a basic wallet object for account info check
            # We'll use the address to check if account exists
            print(f"Checking account status for: {classic_address}")

        except Exception as e:
            self.ids.invalid_keys.text = f"Error creating wallet: {str(e)}"
            return
        try:
            # Try to get account info to check if account exists
            acct_info = AccountInfo(
                account=classic_address,
                ledger_index="validated",
                strict=True,
            )
            response = client.request(acct_info)
            print(f"Account {classic_address} exists on ledger")
        except Exception as e:
            # Account doesn't exist yet - this is expected for new unfunded wallets
            print(f"Account {classic_address} not yet on ledger (normal for new wallets): {e}")
            # We'll still proceed with storing the keys since the wallet is valid

        # Store private key with proper error handling
        try:
            self.wallet_data = shelve.open(WALLET_DATA_PATH)
            if "password" not in self.wallet_data:
                print("No password set. Please set up your account first.")
                return
            password = self.wallet_data["password"].decode("utf-8").encode("ascii")

            # Determine the next available account number
            account_number = 1
            while f"public_key{account_number}" in self.wallet_data:
                account_number += 1

            salt = get_random_bytes(16)
            self.wallet_data[f"salt_key{account_number}"] = salt

            key = PBKDF2(password, salt, dkLen=32, count=100000)
            cipher = AES.new(key, AES.MODE_GCM)
            nonce = cipher.nonce
            encrypted_private_key = cipher.encrypt(private_key.encode("utf-8"))  # Specify encoding

            self.wallet_data[f"public_key{account_number}"] = public_key
            self.wallet_data[f"private_key{account_number}"] = encrypted_private_key
            self.wallet_data[f"nonce_key{account_number}"] = (
                nonce  # Store nonce with the correct key format
            )
            self.wallet_data[f"salt_key{account_number}"] = (
                salt  # Store salt with the correct key format
            )
            self.wallet_data[f"keys{account_number}"] = {
                "public": public_key,
                "private": private_key,
            }

            # Set the selected key
            selected_key = f"public_key{account_number}"

            # Go to "wallet_screen" and pass the selected key as a parameter
            self.manager.current = "wallet_screen"
            wallet_screen = self.manager.get_screen("wallet_screen")
            wallet_screen.set_selected_key(selected_key)

            # Call the on_pre_enter() method manually to update the address and balances
            wallet_screen.on_pre_enter()

        except Exception as e:
            print(f"Error storing keys: {e}")
        finally:
            if hasattr(self, "wallet_data") and self.wallet_data:
                self.wallet_data.close()

    def back_to_createimportwallet(self):
        self.manager.current = "createimportwallet_screen"

    def go_back(self):
        self.manager.current = "wallet_setup_screen"
