# Kivy libraries for the GUI.
# Encryption libraries for password and key encryption.
import logging

from kivy.uix.screenmanager import Screen

logging.basicConfig(level=logging.WARNING)
import shelve
import traceback
from hashlib import sha512

from Crypto.Cipher import AES
from Crypto.Protocol.KDF import PBKDF2
from Crypto.Random import get_random_bytes
from ecpy.curves import Curve
from ecpy.eddsa import EDDSA
from ecpy.keys import ECPrivateKey
from xrpl.clients import JsonRpcClient
from xrpl.core.binarycodec.exceptions import XRPLBinaryCodecException
from xrpl.core.keypairs import derive_classic_address
from xrpl.core.keypairs.ed25519 import PREFIX as ED_PREFIX
from xrpl.models.requests import AccountInfo

# XRPL libraries for xrpl functionality
from xrpl.wallet import Wallet

from src.utils.storage_paths import WALLET_DATA_PATH

JSON_RPC_URL = "https://testnet.xrpl-labs.com"  # Use XRPL Labs testnet (more reliable)
client = JsonRpcClient(JSON_RPC_URL)


# Import Extra Keys Screen
class ImportExtraKeysScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.wallet_data = None

    def store_keys(self):
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

    def back_to_createimportwallet(self):
        self.manager.current = "createimportwallet_screen"
