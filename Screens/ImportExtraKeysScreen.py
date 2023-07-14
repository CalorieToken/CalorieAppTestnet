# Kivy libraries for the GUI.
from kivy.uix.screenmanager import Screen

# Encryption libraries for password and key encryption.
import logging
logging.basicConfig(level=logging.WARNING)
import shelve
from Crypto.Cipher import AES
from Crypto.Protocol.KDF import PBKDF2
from Crypto.Random import get_random_bytes
from ecpy.keys import ECPrivateKey
from hashlib import sha512
from ecpy.curves import Curve
from ecpy.eddsa import EDDSA
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
import shelve

# XRPL libraries for xrpl functionality
from xrpl.wallet import Wallet
from xrpl.core.keypairs.ed25519 import PREFIX as ED_PREFIX
from xrpl.clients import JsonRpcClient
from xrpl.models.requests import AccountInfo
from xrpl.wallet import Wallet
from xrpl.core.binarycodec.exceptions import XRPLBinaryCodecException

JSON_RPC_URL = "https://s.altnet.rippletest.net:51234"
client = JsonRpcClient(JSON_RPC_URL)

# Import Extra Keys Screen
class ImportExtraKeysScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.wallet_data = None

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
            pattern = re.compile(r'^[0-9a-fA-F]{2,}$')
            return bool(pattern.match(s))

        if not is_hex(public_key):
            self.ids.public_key.hint_text = "Public key must be a valid hex string"
            return
        if not is_hex(private_key):
            self.ids.private_key.hint_text = "Private key must be a valid hex string"
            return

        # Derive Public key from Private key
        if private_key.startswith(ED_PREFIX):
            private = ECPrivateKey(int(private_key[len(ED_PREFIX):], 16), Curve.get_curve("Ed25519"))
            public = EDDSA.get_public_key(private, sha512)
            derived_public_key = ED_PREFIX + Curve.get_curve("Ed25519").encode_point(public.W).hex().upper()
        else:
            private = ECPrivateKey(int(private_key, 16), Curve.get_curve("secp256k1"))
            public = private.get_public_key()
            derived_public_key = bytes(Curve.get_curve("secp256k1").encode_point(public.W, compressed=True)).hex().upper()

        # Check if the given public key matches the derived public key
        if public_key != derived_public_key:
            self.ids.private_key.hint_text = "Keys aren't valid"
            self.ids.public_key.hint_text = "Keys aren't valid"
            return

        # Check if account exists
        def wallet_from_public_key():
            wallet = Wallet.create()
            wallet.public_key = (public_key)
            return wallet

        test_wallet = wallet_from_public_key()
        try:
            acct_info = AccountInfo(
                account=test_wallet.classic_address,
                ledger_index="validated",
                strict=True,
            )
            response = client.request(acct_info)
        except (ValueError, XRPLBinaryCodecException):
            self.ids.public_key.hint_text = "Account doesn't exist"
            return

        # Store private key
        self.wallet_data = shelve.open("wallet_data")
        password = self.wallet_data["password"].decode('utf-8').encode('ascii')
        salt = get_random_bytes(16)

        # Determine the next available account number
        account_number = 1
        while f"public_key{account_number}" in self.wallet_data:
            account_number += 1

        self.wallet_data[f"salt_key{account_number}"] = salt

        key = PBKDF2(password, salt, dkLen=32, count=100000)
        cipher = AES.new(key, AES.MODE_GCM)
        nonce = cipher.nonce
        encrypted_private_key = cipher.encrypt(private_key.encode('utf-8'))  # Specify encoding

        self.wallet_data[f"public_key{account_number}"] = public_key
        self.wallet_data[f"private_key{account_number}"] = encrypted_private_key
        self.wallet_data[f"nonce_key{account_number}"] = nonce
        self.wallet_data[f"keys{account_number}"] = {"public": public_key, "private": private_key}
        self.wallet_data.close()

        # Set the selected key
        selected_key = f"public_key{account_number}"  # Replace with the appropriate logic

        # Go to "wallet_screen" and pass the selected key as a parameter
        self.manager.current = "wallet_screen"
        wallet_screen = self.manager.get_screen("wallet_screen")
        wallet_screen.set_selected_key(selected_key)

        # Call the on_pre_enter() method manually to update the address and balances
        wallet_screen.on_pre_enter()
    def go_back(self):
        self.manager.current = "createimportwallet_screen"