# Kivy libraries for the GUI.
from kivymd.uix.button import MDFillRoundFlatButton
from kivymd.uix.dialog import MDDialog
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.textfield import MDTextField

# Encryption libraries for password and key encryption.
import logging
logging.basicConfig(level=logging.WARNING)
import shelve
from Crypto.Cipher import AES
from Crypto.Protocol.KDF import PBKDF2
import shelve
import bcrypt

# XRPL libraries for xrpl functionality
import xrpl
from xrpl.wallet import Wallet
from xrpl.core.keypairs import derive_classic_address
from xrpl.clients import JsonRpcClient
from xrpl.wallet import Wallet
from xrpl.transaction import safe_sign_and_autofill_transaction
from xrpl.transaction import send_reliable_submission
from xrpl.core.keypairs import derive_classic_address
from xrpl.core.binarycodec.exceptions import XRPLBinaryCodecException
from xrpl.ledger import get_latest_validated_ledger_sequence
from xrpl.account import get_next_valid_seq_number

JSON_RPC_URL = "https://s.altnet.rippletest.net:51234"
client = JsonRpcClient(JSON_RPC_URL)

# NFT Mint Screen
class NFTMintScreen(Screen):

    def on_enter(self, *args):
        self.input_error.text = ""

    def mint(self):
        uri = self.ids['uri'].text
        taxon = self.ids['taxon'].text

        # Define the password input textfield
        self.password_field = MDTextField(
            id='password_field',
            password=True,
            mode= "fill",
            line_color_focus=(0, 0.55, 0.21, 1),
            hint_text_color_focus=(0, 0.55, 0.21, 1),
            fill_color_normal=(218/255, 222/255, 237/255, 1),
            fill_color_focus=(0.91, 0.92, 0.96, 1),
            hint_text= "Enter your password",
            font_style= "Body1",
        )
        uri_label = MDLabel(
            text= 'URI Link:  '+str(uri),
            size_hint=(1, 2)
        )
        uri_label.font_size= "12sp"

        taxon_label = MDLabel(
            text= 'Taxon: '+str(taxon),
            size_hint=(1, 2)
        )
        taxon_label.font_size= "12sp"

        # Define a box layout to contain the text
        content_box = BoxLayout(orientation='vertical', size_hint_y=None, height=150)
        content_box.add_widget(MDLabel(text="",size_hint=(1, 5)))
        content_box.add_widget(uri_label)
        content_box.add_widget(MDLabel(text="",size_hint=(1, 9)))
        content_box.add_widget(taxon_label)
        content_box.add_widget(MDLabel(text="",size_hint=(1, 3)))
        content_box.add_widget(self.password_field)
        content_box.add_widget(MDLabel(text="",size_hint=(1, 21)))
        # Define the dialog with custom parameters
        self.dialog = MDDialog(
            title=' ',
            size_hint=(0.8, None),
            height=250,
            md_bg_color=(0.71, 0.75, 0.86, 1),
            buttons=[
                MDFillRoundFlatButton(
                    text='Cancel',
                    md_bg_color=(1, 0.7, 0.13, 1),
                    text_color=(0, 0.55, 0.21, 1),
                    on_release=lambda x: self.dialog.dismiss()
                ),
                MDFillRoundFlatButton(
                    text='Proceed',
                    md_bg_color=(1, 0.7, 0.13, 1),
                    text_color=(0, 0.55, 0.21, 1),
                    on_release=lambda x: self.perform_mint(self.password_field.text)
                )
            ]
        )
        self.dialog.add_widget(content_box)

        # Open the dialog
        self.dialog.open()

    def perform_mint(self, entered_password):
        # Load the password hash from the file
        wallet_data = shelve.open("wallet_data")
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

            with shelve.open("wallet_data") as self.wallet_data:
                if self.manager.get_screen("wallet_screen").selected_key in self.wallet_data:
                    self.public_key = self.wallet_data[self.manager.get_screen("wallet_screen").selected_key]
                    self.private_key = self.wallet_data[self.manager.get_screen("wallet_screen").selected_key.replace("public", "private")]
                    self.nonce = self.wallet_data[self.manager.get_screen("wallet_screen").selected_key.replace("public", "nonce")]
                    self.salt = self.wallet_data[self.manager.get_screen("wallet_screen").selected_key.replace("public", "salt")]

            if self.public_key:
                self.wallet_data = shelve.open("wallet_data")
                self.public_key = self.wallet_data[self.manager.get_screen("wallet_screen").selected_key]
                nonce = self.wallet_data[self.manager.get_screen("wallet_screen").selected_key.replace("public", "nonce")]
                encrypted_private_key = self.wallet_data[self.manager.get_screen("wallet_screen").selected_key.replace("public", "private")]
                password = self.wallet_data["password"].decode('utf-8').encode('ascii')
                salt = self.wallet_data[self.manager.get_screen("wallet_screen").selected_key.replace("public", "salt")]
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
                test_wallet.sequence = get_next_valid_seq_number(test_wallet.classic_address, client)
                
                # Prepare transaction
                my_tx_payment = xrpl.models.transactions.NFTokenMint(
                    account=test_wallet.classic_address,
                    flags=8,
                    last_ledger_sequence=current_validated_ledger + 8,
                    sequence=test_wallet.sequence,
                    uri=xrpl.utils.str_to_hex(self.uri.text),
                    nftoken_taxon=int(self.taxon.text),
                )
                # Sign the transaction

                my_tx_payment_signed = safe_sign_and_autofill_transaction(my_tx_payment, test_wallet, client)

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