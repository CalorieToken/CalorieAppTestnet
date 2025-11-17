# flake8: noqa
# Kivy libraries for the GUI.
# Encryption libraries for password and key encryption.
import logging

from kivy.properties import ObjectProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import Screen
from kivymd.uix.label import MDLabel
from kivymd.uix.textfield import MDTextField

from src.utils.dialogs import show_confirm_dialog, show_error_dialog

logging.basicConfig(level=logging.WARNING)
import shelve

import bcrypt

# XRPL libraries for xrpl functionality
import xrpl
from Crypto.Cipher import AES
from Crypto.Protocol.KDF import PBKDF2
from xrpl.account import get_next_valid_seq_number
from xrpl.clients import JsonRpcClient
from xrpl.core.binarycodec.exceptions import XRPLBinaryCodecException
from xrpl.core.keypairs import derive_classic_address
from xrpl.ledger import get_latest_validated_ledger_sequence
from xrpl.transaction import submit_and_wait
from xrpl.wallet import Wallet

from src.utils.storage_paths import WALLET_DATA_PATH

JSON_RPC_URL = "https://testnet.xrpl-labs.com"  # Use XRPL Labs testnet (more reliable)
client = JsonRpcClient(JSON_RPC_URL)


# NFT Mint Screen
class NFTMintScreen(Screen):

    def on_enter(self, *args):
        self.input_error.text = ""

    def mint(self):
        uri = self.ids["uri"].text
        taxon = self.ids["taxon"].text

        # Basic validation
        if not uri or not uri.strip():
            show_error_dialog("Invalid URI", "Please enter a valid NFT URI.")
            return
        try:
            taxon_int = int(taxon)
            if taxon_int < 0:
                raise ValueError
        except Exception:
            show_error_dialog("Invalid Taxon", "Taxon must be a non-negative integer.")
            return

        # Define the password input field with toggle visibility
        from src.utils.password_field_utils import create_password_field_with_toggle
        self.password_field_container = create_password_field_with_toggle(
            hint_text="Enter your password"
        )
        self.password_field = self.password_field_container.password_field

        uri_label = MDLabel(text=f"URI: {uri}")
        uri_label.font_size = "13sp"
        taxon_label = MDLabel(text=f"Taxon: {taxon}")
        taxon_label.font_size = "12sp"

        # Concise, M3-style content
        content_box = BoxLayout(orientation="vertical", padding=(12, 12, 12, 12))
        content_box.add_widget(uri_label)
        content_box.add_widget(taxon_label)
        content_box.add_widget(self.password_field_container)
        # Use centralized confirm dialog with custom content
        self.dialog = show_confirm_dialog(
            title="Confirm NFT Mint",
            content=content_box,
            confirm_text="Mint",
            cancel_text="Cancel",
            on_confirm=lambda: self.perform_mint(self.password_field.text),
            dismiss_on_confirm=False,
        )

    def perform_mint(self, entered_password):
        # Load the password hash from the file
        wallet_data = shelve.open(WALLET_DATA_PATH)
        hashed_password = wallet_data.get("password")
        wallet_data.close()

        # Check if the password is correct
        password = entered_password.encode("utf-8")
        if not bcrypt.checkpw(password, hashed_password):
            self.password_field.hint_text = "Wrong password, try again"
            return
        try:
            if not self.manager.get_screen("wallet_screen").selected_key:
                return

            with shelve.open(WALLET_DATA_PATH) as self.wallet_data:
                if self.manager.get_screen("wallet_screen").selected_key in self.wallet_data:
                    self.public_key = self.wallet_data[
                        self.manager.get_screen("wallet_screen").selected_key
                    ]
                    self.private_key = self.wallet_data[
                        self.manager.get_screen("wallet_screen").selected_key.replace(
                            "public", "private"
                        )
                    ]
                    self.nonce = self.wallet_data[
                        self.manager.get_screen("wallet_screen").selected_key.replace(
                            "public", "nonce"
                        )
                    ]
                    self.salt = self.wallet_data[
                        self.manager.get_screen("wallet_screen").selected_key.replace(
                            "public", "salt"
                        )
                    ]

            if self.public_key:
                self.wallet_data = shelve.open(WALLET_DATA_PATH)
                self.public_key = self.wallet_data[
                    self.manager.get_screen("wallet_screen").selected_key
                ]
                nonce = self.wallet_data[
                    self.manager.get_screen("wallet_screen").selected_key.replace("public", "nonce")
                ]
                encrypted_private_key = self.wallet_data[
                    self.manager.get_screen("wallet_screen").selected_key.replace(
                        "public", "private"
                    )
                ]
                password = self.wallet_data["password"].decode("utf-8").encode("ascii")
                salt = self.wallet_data[
                    self.manager.get_screen("wallet_screen").selected_key.replace("public", "salt")
                ]
                key = PBKDF2(password, salt, dkLen=32, count=100000)
                cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)
                private_key = str(cipher.decrypt(encrypted_private_key))
                self.private_key = private_key[2:68]

                def wallet_from_kp():
                    wallet = Wallet.create()
                    wallet.public_key = self.public_key
                    wallet.private_key = self.private_key
                    wallet.classic_address = derive_classic_address(self.public_key)
                    return wallet

                test_wallet = wallet_from_kp()

                current_validated_ledger = get_latest_validated_ledger_sequence(client)
                test_wallet.sequence = get_next_valid_seq_number(
                    test_wallet.classic_address, client
                )

                # Prepare transaction
                my_tx_payment = xrpl.models.transactions.NFTokenMint(
                    account=test_wallet.classic_address,
                    flags=8,
                    last_ledger_sequence=current_validated_ledger + 8,
                    sequence=test_wallet.sequence,
                    uri=xrpl.utils.str_to_hex(self.uri.text),
                    nftoken_taxon=taxon_int,
                )
                # Sign the transaction

                tx_response = submit_and_wait(my_tx_payment, client, test_wallet)

                # Submit and send the transaction

                send_reliable_submission(my_tx_payment_signed, client)

                self.dialog.dismiss()
                self.wallet_data.close()
        except XRPLBinaryCodecException as e:
            self.wallet_data.close()
            self.password_field.hint_text = "XRPLBinaryCodecException Error"

    def walletscreen(self):
        self.manager.current = "wallet_screen"

    def createimportwalletscreen(self):
        self.manager.current = "createimportwallet_screen"

    def dextradescreen(self):
        self.manager.current = "dextrade_screen"

    def foodtrackscreen(self):
        self.manager.current = "foodtrack_screen"

    def settingsscreen(self):
        self.manager.current = "settings_screen"
