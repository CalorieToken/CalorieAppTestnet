from kivy.core.clipboard import Clipboard
from kivy.uix.screenmanager import Screen

from src.utils.dialogs import show_confirm_dialog, show_error_dialog, show_info_dialog

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
from src.utils.mnemonic_manager import generate_wallet_with_mnemonic, mnemonic_manager

JSON_RPC_URL = "https://testnet.xrpl-labs.com"  # Use XRPL Labs testnet (more reliable)
client = JsonRpcClient(JSON_RPC_URL)


# Create Wallet Screen
class CreateWalletScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.wallet_data = None
        self.current_mnemonic = None  # Store generated mnemonic

    def generate_keys_with_mnemonic(self):
        """Generate wallet with 12-word mnemonic seed phrase."""
        try:
            print("Generating wallet with 12-word mnemonic...")

            # Generate wallet with mnemonic
            wallet, mnemonic = generate_wallet_with_mnemonic()

            # Store the mnemonic for verification
            self.current_mnemonic = mnemonic

            # Set the keys in the UI
            self.ids.private_key.text = wallet.private_key
            self.ids.public_key.text = wallet.public_key

            # Format mnemonic for display
            mnemonic_display = mnemonic_manager.format_mnemonic_display(mnemonic)

            # Try to fund the wallet using multi-faucet system
            try:
                _, funding_status = generate_multi_faucet_wallet(client, existing_wallet=wallet)
            except Exception:
                funding_status = "⚠️ Unable to auto-fund wallet - use external faucets"

            # Show mnemonic dialog
            dialog_content = f"""🔐 12-Word Recovery Phrase:

{mnemonic_display}

⚠️ IMPORTANT: Write down these 12 words in order!
This is the ONLY way to recover your wallet.

{funding_status}

Wallet Details:
• Address: {wallet.classic_address}
• Private Key: {wallet.private_key}
• Public Key: {wallet.public_key}"""

            show_confirm_dialog(
                title="🎉 Wallet Created with Mnemonic!",
                text=dialog_content,
                confirm_text="✅ I Wrote It Down",
                cancel_text="📋 Copy Mnemonic",
                on_confirm=lambda: self.verify_mnemonic_dialog(None),
                on_cancel=lambda: self.copy_mnemonic(),
                dismiss_on_confirm=True,
            )

        except Exception as e:
            print(f"Error generating wallet with mnemonic: {e}")
            # Fallback to regular key generation
            self.generate_keys()

    def copy_mnemonic(self):
        """Copy mnemonic to clipboard."""
        if self.current_mnemonic:
            mnemonic_text = " ".join(self.current_mnemonic)
            Clipboard.copy(mnemonic_text)
            print("✅ Mnemonic copied to clipboard!")

    def verify_mnemonic_dialog(self, parent_dialog):
        """Show mnemonic verification dialog."""
        if parent_dialog:
            parent_dialog.dismiss()

        verification_text = """🔐 Mnemonic Verification

Please enter your 12-word recovery phrase below to confirm you wrote it down correctly.

You can enter the words separated by spaces, or with numbers like:
1. word1 2. word2 3. word3...

This verification ensures you can recover your wallet later."""

        # Create a more complex dialog with text input
        from kivymd.uix.boxlayout import MDBoxLayout
        from kivymd.uix.label import MDLabel
        from kivymd.uix.textfield import MDTextField

        content = MDBoxLayout(
            orientation="vertical", spacing="10dp", size_hint_y=None, height="200dp"
        )

        content.add_widget(
            MDLabel(
                text=verification_text,
                theme_text_color="Primary",
                size_hint_y=None,
                height="120dp",
                text_size=(None, None),
            )
        )

        self.verification_input = MDTextField(
            hint_text="Enter your 12 words here...", multiline=True, size_hint_y=None, height="60dp"
        )
        content.add_widget(self.verification_input)

        show_confirm_dialog(
            title="🔐 Verify Your Mnemonic",
            content=content,
            confirm_text="✅ Verify",
            cancel_text="❌ Skip Verification",
            on_confirm=lambda: self.verify_mnemonic(None),
            on_cancel=lambda: self.skip_verification(None),
            dismiss_on_confirm=True,
        )

    def verify_mnemonic(self, dialog):
        """Verify the entered mnemonic matches the generated one."""
        try:
            entered_text = self.verification_input.text.strip()
            entered_words = mnemonic_manager.parse_mnemonic_input(entered_text)

            if len(entered_words) != 12:
                self.show_verification_error("Please enter exactly 12 words.")
                return

            # Compare with original mnemonic (case-insensitive)
            original_lower = [word.lower() for word in self.current_mnemonic]
            entered_lower = [word.lower() for word in entered_words]

            if original_lower == entered_lower:
                if dialog:
                    dialog.dismiss()
                self.show_verification_success()
            else:
                # Show which words are incorrect
                incorrect_positions = []
                for i, (orig, entered) in enumerate(zip(original_lower, entered_lower)):
                    if orig != entered:
                        incorrect_positions.append(i + 1)

                error_msg = f"Mnemonic doesn't match. Check words at positions: {', '.join(map(str, incorrect_positions))}"
                self.show_verification_error(error_msg)

        except Exception as e:
            self.show_verification_error(f"Verification error: {e}")

    def show_verification_error(self, message):
        """Show verification error dialog."""
        show_error_dialog(
            title="❌ Verification Failed",
            text=f"{message}\n\nPlease try again or copy the mnemonic to double-check.",
        )

    def show_verification_success(self):
        """Show verification success and proceed."""
        show_confirm_dialog(
            title="🎉 Verification Successful!",
            text=(
                "Great! You've successfully verified your mnemonic phrase.\n\n"
                "Your wallet is now ready to use. Remember to keep your mnemonic phrase safe!"
            ),
            confirm_text="🚀 Continue to Wallet",
            cancel_text="Close",
            on_confirm=lambda: self.proceed_after_verification(None),
            dismiss_on_confirm=True,
        )

    def skip_verification(self, dialog):
        """Skip verification and proceed."""
        if dialog:
            dialog.dismiss()
        show_confirm_dialog(
            title="⚠️ Verification Skipped",
            text=(
                "You've chosen to skip mnemonic verification.\n\n"
                "Remember: Your 12-word phrase is the ONLY way to recover your wallet. Make sure you have it written down safely!"
            ),
            confirm_text="✅ I Understand, Continue",
            cancel_text="📝 Go Back to Verify",
            on_confirm=lambda: self.proceed_after_verification(None),
            on_cancel=lambda: self.back_to_verify(None),
            dismiss_on_confirm=True,
        )

    def back_to_verify(self, dialog):
        """Go back to mnemonic verification."""
        if dialog:
            dialog.dismiss()
        self.verify_mnemonic_dialog(None)

    def proceed_after_verification(self, dialog):
        """Proceed to store keys after mnemonic verification."""
        if dialog:
            dialog.dismiss()
        self.store_keys()

    def generate_keys(self):
        """Generate wallet - now navigates to dedicated mnemonic screen."""
        try:
            # Generate wallet with mnemonic
            wallet, mnemonic = generate_wallet_with_mnemonic()

            # Store the generated data temporarily for the dedicated screen
            import json
            import tempfile

            temp_dir = tempfile.gettempdir()
            temp_file = os.path.join(temp_dir, "wallet_generation_data.json")

            with open(temp_file, "w") as f:
                json.dump(
                    {
                        "mnemonic": mnemonic,
                        "private_key": wallet.private_key,
                        "public_key": wallet.public_key,
                        "address": wallet.classic_address,
                        "source_screen": "CreateWalletScreen",
                    },
                    f,
                )

            # For now, let's just use the existing UI to show the keys
            # and display the mnemonic in a simple dialog
            self.ids.private_key.text = wallet.private_key
            self.ids.public_key.text = wallet.public_key

            # Show simple mnemonic dialog
            mnemonic_text = "🔐 Your 12-Word Recovery Phrase:\n\n"
            for i, word in enumerate(mnemonic, 1):
                mnemonic_text += f"{i}. {word}   "
                if i % 4 == 0:
                    mnemonic_text += "\n"

            mnemonic_text += f"\n\n📱 Wallet Address: {wallet.classic_address}"
            mnemonic_text += "\n\n⚠️ IMPORTANT: Write down these 12 words in order!"
            mnemonic_text += "\nThis is the ONLY way to recover your wallet."
            show_confirm_dialog(
                title="🎉 Wallet Created with Mnemonic!",
                text=mnemonic_text,
                confirm_text="✅ Continue",
                cancel_text="📋 Copy Mnemonic",
                on_confirm=lambda: self.close_dialog_and_continue(None),
                on_cancel=lambda: self.copy_mnemonic(mnemonic),
                dismiss_on_confirm=True,
            )

        except Exception as e:
            print(f"Error generating keys: {e}")
            self.ids.invalid_keys.text = f"Error generating keys: {str(e)}"

    def copy_mnemonic(self, mnemonic):
        """Copy mnemonic to clipboard."""
        mnemonic_text = " ".join(mnemonic)
        from kivy.core.clipboard import Clipboard

        Clipboard.copy(mnemonic_text)
        print("✅ Mnemonic copied to clipboard!")

    def close_dialog_and_continue(self, dialog):
        """Close dialog and continue with wallet creation."""
        dialog.dismiss()
        print("✅ User acknowledged mnemonic display")

    def copy_keys(self, private_key, public_key):
        # Copy the private and public keys to the clipboard
        cb = Clipboard
        cb.copy("Private_Key: " + private_key + "\n" + "Public_Key: " + public_key)

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
            salt = get_random_bytes(16)

            # Determine the next available account number
            account_number = 1
            while f"public_key{account_number}" in self.wallet_data:
                account_number += 1

            self.wallet_data[f"salt{account_number}"] = salt

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

    def settingsscreen(self):
        self.manager.current = "settings_screen"

    def go_back(self):
        self.manager.current = "wallet_setup_screen"

    def back_to_wallet_setup(self):
        self.manager.current = "wallet_setup_screen"
