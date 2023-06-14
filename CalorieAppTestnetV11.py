# Kivy libraries for the GUI.
from kivymd.app import MDApp
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.metrics import dp
from kivymd.uix.button import MDFillRoundFlatButton
from kivy.clock import Clock
from kivymd.uix.dialog import MDDialog
from kivy.core.window import Window
from kivy.uix.screenmanager import Screen
from kivy.core.clipboard import Clipboard
from kivy.uix.boxlayout import BoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.textfield import MDTextField
from kivy.properties import ObjectProperty

# Encryption libraries for password and key encryption.
import logging
logging.basicConfig(level=logging.WARNING)
import string
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
import bcrypt

# XRPL libraries for xrpl functionality
import xrpl
from xrpl.wallet import Wallet
from xrpl.core import addresscodec
from xrpl.core.keypairs import derive_classic_address
from xrpl.core.keypairs.ed25519 import PREFIX as ED_PREFIX
from xrpl.clients import JsonRpcClient
from xrpl.models.requests import AccountInfo
from xrpl.models.requests.account_objects import AccountObjects
from xrpl.models.requests import AccountTx
from xrpl.wallet import Wallet
from xrpl.models.transactions import Payment
from xrpl.transaction import safe_sign_and_autofill_transaction
from xrpl.transaction import send_reliable_submission
from xrpl.core.keypairs import derive_classic_address
from xrpl.core.binarycodec.exceptions import XRPLBinaryCodecException
from xrpl.models.transactions import Payment
from xrpl.models.transactions import NFTokenMint
from xrpl.ledger import get_latest_validated_ledger_sequence
from xrpl.account import get_next_valid_seq_number
from xrpl.models.amounts import IssuedCurrencyAmount
from xrpl.utils import str_to_hex
from xrpl.wallet import generate_faucet_wallet

Window.size = (300, 500)

import json
JSON_RPC_URL = "https://s.altnet.rippletest.net:51234"
client = JsonRpcClient(JSON_RPC_URL)

class WalletScreen(Screen):

    def copy_address(self):
        Clipboard.copy(self.xrp_address.text)

    def on_pre_enter(self):
        self.wallet_data = shelve.open("wallet_data")
        self.public_key = self.wallet_data["public_key"]

        def wallet_from_kp():
            wallet = Wallet.create()
            wallet.classic_address = derive_classic_address(self.public_key)
            return wallet
        test_wallet = wallet_from_kp()

        self.xrp_address.text = test_wallet.classic_address
        self.wallet_data.close()
        self.check_balance(dt=33)

        Clock.schedule_interval(self.check_balance, 33)
        self.check_balance_lipisa(dt=33)
        Clock.schedule_interval(self.check_balance_lipisa, 33)
        self.check_balance_calorietest(dt=33)
        Clock.schedule_interval(self.check_balance_calorietest, 33)

    def check_balance(self, dt):
        try:
            self.wallet_data = shelve.open("wallet_data")
            self.public_key = self.wallet_data["public_key"]

            def wallet_from_kp():
                wallet = Wallet.create()
                wallet.classic_address = derive_classic_address(self.public_key)
                return wallet

            test_wallet = wallet_from_kp()

            acct_info = AccountInfo(
                account=test_wallet.classic_address,
                ledger_index="validated",
                strict=True,
            )
            response = client.request(acct_info)
            data = json.loads((json.dumps(response.result, indent=4, sort_keys=True)))
            # Divide the balance by 1 million to convert to units of 1
            balance = int(data["account_data"]["Balance"]) / 1e6
            self.xrp_balance.text = str(balance)


            # Transaction History

            tx_info = AccountTx(
                account=test_wallet.classic_address,
                ledger_index_min= -1,
                ledger_index_max= -1,
                ledger_index="validated",
                limit= 20
            )
            response2 = client.request(tx_info)
            data2 = json.loads((json.dumps(response2.result, indent=4, sort_keys=True)))

            for i, transaction in enumerate(data2['transactions']):
                meta = transaction["meta"]
                tx = transaction["tx"]
                validated = transaction["validated"]

                label_id = f'transaction{i+1}'
                label = self.ids[label_id]

                if "Amount" in tx and "value" in tx["Amount"]:
                    if '4C69706973610000000000000000000000000000' in tx["Amount"]["currency"]:
                        label.text = f'Amount Lipisa:                        {tx["Amount"]["value"]}'
                    if '43616C6F72696554657374000000000000000000' in tx["Amount"]["currency"]:
                        value = format(float(tx["Amount"]["value"]), ".2f")
                        label.text = f'Amount CalorieTest:              {value}'

                    else:
                        label.text = f'Amount in other currency: {tx["Amount"]["value"]} {tx["Amount"]["currency"]}'
                else:
                    amount = 0
                    if "Amount" in tx:
                        amount = int(tx["Amount"]) / 1e6
                    else:
                        label.text = "Amount: Not specified"
                    label.text = f'Amount XRP:                           {amount}'

                if "Account" in tx:
                    if tx["Account"] == test_wallet.classic_address:
                        label.text += f' (Sent)'
                    else:
                        label.text += f' (Received)'
            self.wallet_data.close()
        except Exception as e:
            print(e)
            self.wallet_data.close()
            self.xrp_balance.text = "Error: Could not get balance"

    def check_balance_lipisa(self, dt):
        try:
            self.wallet_data = shelve.open("wallet_data")
            self.public_key = self.wallet_data["public_key"]

            def wallet_from_kp():
                wallet = Wallet.create()
                wallet.classic_address = derive_classic_address(self.public_key)
                return wallet

            test_wallet = wallet_from_kp()

            acct_objects = AccountObjects(
                account=test_wallet.classic_address,
                ledger_index="validated",
                type="state",
                deletion_blockers_only=False,
                limit=100
            )
            response = client.request(acct_objects)

            # Tokensvalues (all trustlines)

            data = json.loads((json.dumps(response.result, indent=4, sort_keys=True)))
            tokensvalue = dict()
            currenciescheck = dict()

            for currencies in data['account_objects']:
                currency = currencies['Balance']['currency']
                value = currencies['Balance']['value']
                tokensvalue[currency] = value
                currenciescheck[currency] = currency

            # Lipisa (Tokensvalue)
            if '4C69706973610000000000000000000000000000' in currenciescheck:
                self.lipisa_balance.text = (tokensvalue['4C69706973610000000000000000000000000000'])
            else:
                self.lipisa_balance.text = 'No Lipisa Trustline'

            self.wallet_data.close()
        except Exception as e:
            print(e)
            self.wallet_data.close()
            self.lipisa_balance.text = "Error: Could not get balance"

    def check_balance_calorietest(self, dt):
        try:
            self.wallet_data = shelve.open("wallet_data")
            self.public_key = self.wallet_data["public_key"]

            def wallet_from_kp():
                wallet = Wallet.create()
                wallet.classic_address = derive_classic_address(self.public_key)
                return wallet

            test_wallet = wallet_from_kp()

            acct_objects = AccountObjects(
                account=test_wallet.classic_address,
                ledger_index="validated",
                type="state",
                deletion_blockers_only=False,
                limit=100
            )
            response = client.request(acct_objects)

            # Tokensvalues (all trustlines)

            data = json.loads((json.dumps(response.result, indent=4, sort_keys=True)))
            tokensvalue = dict()
            currenciescheck = dict()

            for currencies in data['account_objects']:
                currency = currencies['Balance']['currency']
                value = currencies['Balance']['value']
                tokensvalue[currency] = value
                currenciescheck[currency] = currency

            # CalorieTest (Tokensvalue)
            if '43616C6F72696554657374000000000000000000' in currenciescheck:
                value = format(float(tokensvalue['43616C6F72696554657374000000000000000000']), ".2f")
                self.calorietest_balance.text = value
            else:
                self.calorietest_balance.text = 'No CalorieTest Trustline'


            self.wallet_data.close()
        except Exception as e:
            print(e)
            self.wallet_data.close()
            self.calorietest_balance.text = "Error: Could not get balance"            

    def open_dialog_lipisa(self):

        def wallet_from_kp():
            wallet = Wallet.create()
            wallet.classic_address = derive_classic_address(self.public_key)
            return wallet
        test_wallet = wallet_from_kp()

        acct_objects = AccountObjects(
            account=test_wallet.classic_address,
            ledger_index="validated",
            type="state",
            deletion_blockers_only=False,
            limit=100
        )
        response = client.request(acct_objects)
        data = json.loads((json.dumps(response.result, indent=4, sort_keys=True)))
        currenciescheck = dict()

        for currencies in data['account_objects']:
            currency = currencies['Balance']['currency']
            currenciescheck[currency] = currency

        if '4C69706973610000000000000000000000000000' in currenciescheck:
            self.dialog = MDDialog(
                title="Setting Trustline",
                type="confirmation",
                size_hint=(.8, None),
                md_bg_color=(0.71, 0.75, 0.86, 1),
                height=dp(200),
                text="Trustline for Lipisa is already set. Do you want to set it again?",
                buttons=[
                    MDFillRoundFlatButton(
                        text="CANCEL",
                        md_bg_color=(1, 0.7, 0.13, 1),
                        text_color=(0, 0.55, 0.21, 1),
                        on_release=lambda *x: self.dialog.dismiss()
                    ),
                    MDFillRoundFlatButton(
                        text="OK",
                        md_bg_color=(1, 0.7, 0.13, 1),
                        text_color=(0, 0.55, 0.21, 1),
                        on_release=self.set_trustline
                    ),
                ],
            )
        else:
            self.dialog = MDDialog(
                title="Setting Trustline",
                type="confirmation",
                size_hint=(.8, None),
                md_bg_color=(0.71, 0.75, 0.86, 1),
                height=dp(200),
                text="Are you sure you want to set a trustline for Lipisa? 2 XRP will be stored in escrow to set the trustline.",
                buttons=[
                    MDFillRoundFlatButton(
                        text="CANCEL",
                        md_bg_color=(1, 0.7, 0.13, 1),
                        text_color=(0, 0.55, 0.21, 1),
                        on_release=lambda *x: self.dialog.dismiss()
                    ),
                    MDFillRoundFlatButton(
                        text="OK",
                        md_bg_color=(1, 0.7, 0.13, 1),
                        text_color=(0, 0.55, 0.21, 1),
                        on_release=self.set_trustline
                    ),
                ],
            )
        self.dialog.open()

    def set_trustline(self, *args):
        self.wallet_data = shelve.open("wallet_data")
        self.public_key = self.wallet_data["public_key"]
        nonce = self.wallet_data["nonce"]
        encrypted_private_key = self.wallet_data["private_key"]
        password = self.wallet_data["password"].decode('utf-8').encode('ascii')
        salt = self.wallet_data["salt"]
        key = PBKDF2(password, salt, dkLen=32, count=100000)
        cipher = AES.new(key, AES.MODE_GCM,nonce=nonce)
        private_key = str(cipher.decrypt(encrypted_private_key))
        self.private_key = private_key[2:68]

        def wallet_from_kp():
            wallet = Wallet.create()
            wallet.public_key = self.public_key
            wallet.private_key = self.private_key
            wallet.classic_address = derive_classic_address(self.public_key)
            return wallet
        test_wallet = wallet_from_kp()

        test_account = test_wallet.classic_address
        
        my_tx_payment = xrpl.models.transactions.TrustSet(
            account=test_wallet.classic_address,
            flags=131072,
            limit_amount=xrpl.models.amounts.issued_currency_amount.IssuedCurrencyAmount(
                   currency="4C69706973610000000000000000000000000000",
                    issuer="r4dPUdvD5iGyenACWgDF72Un4M9WVNK4if",
                    value="100000000000"
            )
        )
        # Sign the transaction
        my_tx_payment_signed = safe_sign_and_autofill_transaction(my_tx_payment, test_wallet, client)

        # Submit and send the transaction
        tx_response = send_reliable_submission(my_tx_payment_signed, client)

        if tx_response.result == 'tesSUCCESS':
          print('Transaction successful!')
        else:
          print(f'Transaction failed with error: {tx_response.result}')

        self.dialog.dismiss()
        self.wallet_data.close()

    def open_dialog_calorietest(self):

        def wallet_from_kp():
            wallet = Wallet.create()
            wallet.classic_address = derive_classic_address(self.public_key)
            return wallet
        test_wallet = wallet_from_kp()

        acct_objects = AccountObjects(
            account=test_wallet.classic_address,
            ledger_index="validated",
            type="state",
            deletion_blockers_only=False,
            limit=100
        )
        response = client.request(acct_objects)
        data = json.loads((json.dumps(response.result, indent=4, sort_keys=True)))
        currenciescheck = dict()

        for currencies in data['account_objects']:
            currency = currencies['Balance']['currency']
            currenciescheck[currency] = currency

        if '43616C6F72696554657374000000000000000000' in currenciescheck:
            self.dialog = MDDialog(
                title="Setting Trustline",
                type="confirmation",
                size_hint=(.8, None),
                md_bg_color=(0.71, 0.75, 0.86, 1),
                height=dp(200),
                text="Trustline for CalorieTest is already set. Do you want to set it again?",
                buttons=[
                    MDFillRoundFlatButton(
                        text="CANCEL",
                        md_bg_color=(1, 0.7, 0.13, 1),
                        text_color=(0, 0.55, 0.21, 1),
                        on_release=lambda *x: self.dialog.dismiss()
                    ),
                    MDFillRoundFlatButton(
                        text="OK",
                        md_bg_color=(1, 0.7, 0.13, 1),
                        text_color=(0, 0.55, 0.21, 1),
                        on_release=self.set_trustline
                    ),
                ],
            )
        else:
            self.dialog = MDDialog(
                title="Setting Trustline",
                type="confirmation",
                size_hint=(.8, None),
                md_bg_color=(0.71, 0.75, 0.86, 1),
                height=dp(200),
                text="Are you sure you want to set a trustline for CalorieTest? 2 XRP will be stored in escrow to set the trustline.",
                buttons=[
                    MDFillRoundFlatButton(
                        text="CANCEL",
                        md_bg_color=(1, 0.7, 0.13, 1),
                        text_color=(0, 0.55, 0.21, 1),
                        on_release=lambda *x: self.dialog.dismiss()
                    ),
                    MDFillRoundFlatButton(
                        text="OK",
                        md_bg_color=(1, 0.7, 0.13, 1),
                        text_color=(0, 0.55, 0.21, 1),
                        on_release=self.set_trustline
                    ),
                ],
            )
        self.dialog.open()

    def set_trustline(self, *args):
        self.wallet_data = shelve.open("wallet_data")
        self.public_key = self.wallet_data["public_key"]
        nonce = self.wallet_data["nonce"]
        encrypted_private_key = self.wallet_data["private_key"]
        password = self.wallet_data["password"].decode('utf-8').encode('ascii')
        salt = self.wallet_data["salt"]
        key = PBKDF2(password, salt, dkLen=32, count=100000)
        cipher = AES.new(key, AES.MODE_GCM,nonce=nonce)
        private_key = str(cipher.decrypt(encrypted_private_key))
        self.private_key = private_key[2:68]

        def wallet_from_kp():
            wallet = Wallet.create()
            wallet.public_key = self.public_key
            wallet.private_key = self.private_key
            wallet.classic_address = derive_classic_address(self.public_key)
            return wallet
        test_wallet = wallet_from_kp()

        test_account = test_wallet.classic_address
        
        my_tx_payment = xrpl.models.transactions.TrustSet(
            account=test_wallet.classic_address,
            flags=131072,
            limit_amount=xrpl.models.amounts.issued_currency_amount.IssuedCurrencyAmount(
                   currency="43616C6F72696554657374000000000000000000",
                    issuer="rJps2NCFbbSefuSzibzNBSVv5ywpTdCBDX",
                    value="100000000000"
            )
        )
        # Sign the transaction
        my_tx_payment_signed = safe_sign_and_autofill_transaction(my_tx_payment, test_wallet, client)

        # Submit and send the transaction
        tx_response = send_reliable_submission(my_tx_payment_signed, client)

        if tx_response.result == 'tesSUCCESS':
          print('Transaction successful!')
        else:
          print(f'Transaction failed with error: {tx_response.result}')

        self.dialog.dismiss()
        self.wallet_data.close()

    def send_xrp_screen(self):
        self.manager.current = "sendxrp_screen"

    def send_lipisa_screen(self):

        def wallet_from_kp():
            wallet = Wallet.create()
            wallet.classic_address = derive_classic_address(self.public_key)
            return wallet
        test_wallet = wallet_from_kp()
        acct_objects = AccountObjects(
            account=test_wallet.classic_address,
            ledger_index="validated",
            type="state",
            deletion_blockers_only=False,
            limit=100
        )
        response = client.request(acct_objects)
        data = json.loads((json.dumps(response.result, indent=4, sort_keys=True)))
        currenciescheck = dict()

        for currencies in data['account_objects']:
            currency = currencies['Balance']['currency']
            currenciescheck[currency] = currency

        if '4C69706973610000000000000000000000000000' in currenciescheck:
            self.manager.current = "sendlipisa_screen"
        else:
            self.dialog = MDDialog(
                title="Setting Trustline",
                type="confirmation",
                size_hint=(.8, None),
                md_bg_color=(0.71, 0.75, 0.86, 1),
                height=dp(200),
                text="You need to set a trustline for Lipisa in order to proceed. Are you sure you want to set a trustline for Lipisa? 2 XRP will be stored in escrow to set the trustline.",
                buttons=[
                    MDFillRoundFlatButton(
                        text="CANCEL",
                        md_bg_color=(1, 0.7, 0.13, 1),
                        text_color=(0, 0.55, 0.21, 1),
                        on_release=lambda *x: self.dialog.dismiss()
                    ),
                    MDFillRoundFlatButton(
                        text="OK",
                        md_bg_color=(1, 0.7, 0.13, 1),
                        text_color=(0, 0.55, 0.21, 1),
                        on_release=self.set_trustline
                    ),
                ],
            )
            self.dialog.open()

    def send_calorietest_screen(self):

        def wallet_from_kp():
            wallet = Wallet.create()
            wallet.classic_address = derive_classic_address(self.public_key)
            return wallet
        test_wallet = wallet_from_kp()
        acct_objects = AccountObjects(
            account=test_wallet.classic_address,
            ledger_index="validated",
            type="state",
            deletion_blockers_only=False,
            limit=100
        )
        response = client.request(acct_objects)
        data = json.loads((json.dumps(response.result, indent=4, sort_keys=True)))
        currenciescheck = dict()

        for currencies in data['account_objects']:
            currency = currencies['Balance']['currency']
            currenciescheck[currency] = currency

        if '43616C6F72696554657374000000000000000000' in currenciescheck:
            self.manager.current = "sendcalorietest_screen"
        else:
            self.dialog = MDDialog(
                title="Setting Trustline",
                type="confirmation",
                size_hint=(.8, None),
                md_bg_color=(0.71, 0.75, 0.86, 1),
                height=dp(200),
                text="You need to set a trustline for CalorieTest in order to proceed. Are you sure you want to set a trustline for CalorieTest? 2 XRP will be stored in escrow to set the trustline.",
                buttons=[
                    MDFillRoundFlatButton(
                        text="CANCEL",
                        md_bg_color=(1, 0.7, 0.13, 1),
                        text_color=(0, 0.55, 0.21, 1),
                        on_release=lambda *x: self.dialog.dismiss()
                    ),
                    MDFillRoundFlatButton(
                        text="OK",
                        md_bg_color=(1, 0.7, 0.13, 1),
                        text_color=(0, 0.55, 0.21, 1),
                        on_release=self.set_trustline
                    ),
                ],
            )
            self.dialog.open()

    def nftmintscreen(self):
        self.manager.current = "nftmint_screen"

    def walletgeneratorscreen(self):
        self.manager.current = "walletgenerator_screen"

    def dextradescreen(self):
        self.manager.current = "dextrade_screen"

    def foodtrackscreen(self):
        self.manager.current = "foodtrack_screen"

    def settingsscreen(self):
        self.manager.current = "settings_screen"
class SendXRPScreen(Screen):

    def on_pre_enter(self):
        self.wallet_data = shelve.open("wallet_data")
        self.public_key = self.wallet_data["public_key"]

        def wallet_from_kp():
            wallet = Wallet.create()
            wallet.classic_address = derive_classic_address(self.public_key)
            return wallet
        test_wallet = wallet_from_kp()

        self.xrp_address.text = test_wallet.classic_address
        self.wallet_data.close()
        self.check_balance(dt=16)
        Clock.schedule_interval(self.check_balance, 33)

    def show_error_message(self, message):
        self.dialog = MDDialog(
            title="Error",
            text=message,
            size_hint=(0.7, 0.3),
            md_bg_color=(0.71, 0.75, 0.86, 1),
            buttons=[
                MDFillRoundFlatButton(
                    text="Close",
                    md_bg_color=(1, 0.7, 0.13, 1),
                    text_color=(0, 0.55, 0.21, 1),
                    on_release=lambda x: self.dialog.dismiss()
                )
            ]
        )
        self.dialog.open()

    def check_address(self, destination):
        acct_info = AccountInfo(
            account=destination,
            ledger_index="validated",
            strict=True,
        )
        response = client.request(acct_info)
        print("response.status: ", response.status)
        if response.status == "success":
            return True
        else:
            return False

    def send_xrp(self):
        amount = self.ids['amount_input'].text
        destination = self.ids['destination_input'].text

        # Check for a valid amount
        try:
            amount = float(amount)
            if amount <= 0:
                raise ValueError
        except ValueError:
            self.show_error_message("Enter a valid amount.")
            return

        # Check for a valid destination address
        if not self.check_address(destination):
            self.show_error_message("Enter a valid destination address.")
            return

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
        Amount = MDLabel(
            text= 'Amount:  '+str(amount),
        )
        Amount.font_size= "12sp"

        Destination = MDLabel(
            text= 'Destination:'+str(destination)
        )
        Destination.font_size= "10sp"

        # Define a box layout to contain the text
        content_box = BoxLayout(orientation='vertical', padding=(1,1,1,1))
        content_box.add_widget(MDLabel(text="Confirm transaction",size_hint=(1, 0.2)))
        content_box.add_widget(MDLabel(text="",size_hint=(1, 0.3)))
        content_box.add_widget(Amount)
        content_box.add_widget(Destination)
        content_box.add_widget(self.password_field)
        content_box.add_widget(MDLabel(text="",size_hint=(1, 2.5)))
        content_box.ids['password_field'] = self.password_field

        # Define the dialog with custom parameters
        self.dialog = MDDialog(
            title=' ',
            size_hint=(0.8, 0.3),
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
                    on_release=lambda x: self.perform_send(self.password_field.text)
                )
            ]
        )
        self.dialog.add_widget(content_box)

        # Open the dialog
        self.dialog.open()


    def perform_send(self, entered_password):
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
            self.wallet_data = shelve.open("wallet_data")
            self.public_key = self.wallet_data["public_key"]
            nonce = self.wallet_data["nonce"]
            encrypted_private_key = self.wallet_data["private_key"]
            password = self.wallet_data["password"].decode('utf-8').encode('ascii')
            salt = self.wallet_data["salt"]
            key = PBKDF2(password, salt, dkLen=32, count=100000)
            cipher = AES.new(key, AES.MODE_GCM,nonce=nonce)
            private_key = str(cipher.decrypt(encrypted_private_key))
            self.private_key = private_key[2:68]

            def wallet_from_kp():
                wallet = Wallet.create()
                wallet.public_key = self.public_key
                wallet.private_key = self.private_key
                wallet.classic_address = derive_classic_address(self.public_key)
                return wallet
            test_wallet = wallet_from_kp()

            my_tx_payment = Payment(
                account=test_wallet.classic_address,
                amount=str(int(float(self.amount_input.text)* 1000000)),
                destination=self.destination_input.text,
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


    def check_balance(self, dt):
        try:
            self.wallet_data = shelve.open("wallet_data")
            self.public_key = self.wallet_data["public_key"]

            def wallet_from_kp():
                wallet = Wallet.create()
                wallet.classic_address = derive_classic_address(self.public_key)
                return wallet

            test_wallet = wallet_from_kp()

            acct_info = AccountInfo(
                account=test_wallet.classic_address,
                ledger_index="validated",
                strict=True,
            )
            response = client.request(acct_info)
            data = json.loads((json.dumps(response.result, indent=4, sort_keys=True)))
            # Divide the balance by 1 million to convert to units of 1
            balance = int(data["account_data"]["Balance"]) / 1e6
            self.xrp_balance.text = str(balance)

            # Transaction History

            tx_info = AccountTx(
                account=test_wallet.classic_address,
                ledger_index_min= -1,
                ledger_index_max= -1,
                ledger_index="validated",
                limit= 20
            )
            response2 = client.request(tx_info)
            data2 = json.loads((json.dumps(response2.result, indent=4, sort_keys=True)))

            for i, transaction in enumerate(data2['transactions']):
                meta = transaction["meta"]
                tx = transaction["tx"]
                validated = transaction["validated"]

                label_id = f'transaction{i+1}'
                label = self.ids[label_id]

                if "Amount" in tx and "value" in tx["Amount"]:
                    if '4C69706973610000000000000000000000000000' in tx["Amount"]["currency"]:
                        label.text = f'Amount Lipisa:                        {tx["Amount"]["value"]}'
                    if '43616C6F72696554657374000000000000000000' in tx["Amount"]["currency"]:
                        value = format(float(tx["Amount"]["value"]), ".2f")
                        label.text = f'Amount CalorieTest:              {value}'
                    else:
                        label.text = f'Amount in other currency: {tx["Amount"]["value"]} {tx["Amount"]["currency"]}'
                else:
                    amount = 0
                    if "Amount" in tx:
                        amount = int(tx["Amount"]) / 1e6
                    else:
                        label.text = "Amount: Not specified"
                    label.text = f'Amount XRP:                           {amount}'

                if "Account" in tx:
                    if tx["Account"] == test_wallet.classic_address:
                        label.text += f' (Sent)'
                    else:
                        label.text += f' (Received)'
            self.wallet_data.close()

        except Exception as e:
            print(e)
            self.wallet_data.close()
            self.xrp_balance.text = "Error: Could not get balance"
    def backto_wallet(self):
        self.manager.current = "wallet_screen"

class SendLipisaScreen(Screen):
    def on_pre_enter(self):
        self.wallet_data = shelve.open("wallet_data")
        self.public_key = self.wallet_data["public_key"]

        def wallet_from_kp():
            wallet = Wallet.create()
            wallet.classic_address = derive_classic_address(self.public_key)
            return wallet
        test_wallet = wallet_from_kp()

        self.xrp_address.text = test_wallet.classic_address
        self.wallet_data.close()
        self.check_balance_lipisa(dt=16)
        Clock.schedule_interval(self.check_balance_lipisa, 33)

    def show_error_message(self, message):
        self.dialog = MDDialog(
            title="Error",
            text=message,
            size_hint=(0.7, 0.3),
            md_bg_color=(0.71, 0.75, 0.86, 1),
            buttons=[
                MDFillRoundFlatButton(
                    text="Close",
                    md_bg_color=(1, 0.7, 0.13, 1),
                    text_color=(0, 0.55, 0.21, 1),
                    on_release=lambda x: self.dialog.dismiss()
                )
            ]
        )
        self.dialog.open()

    def check_trustline(self, client, destination):

        acct_objects = AccountObjects(
            account=destination,
            ledger_index="validated",
            type="state",
            deletion_blockers_only=False,
            limit=100
        )
        response = client.request(acct_objects)

        data = json.loads((json.dumps(response.result, indent=4, sort_keys=True)))

        tokensvalue = dict()
        currenciescheck = dict()

        for currencies in data['account_objects']:
            currency = currencies['Balance']['currency']
            value = currencies['Balance']['value']
            tokensvalue[currency] = value
            currenciescheck[currency] = currency

        if '4C69706973610000000000000000000000000000' in currenciescheck:
            return True
        else:
            return False

    def check_address(self, destination):
        acct_info = AccountInfo(
            account=destination,
            ledger_index="validated",
            strict=True,
        )
        response = client.request(acct_info)
        print("response.status: ", response.status)
        if response.status == "success":
            return True
        else:
            return False

    def send_lipisa(self):
        amount = self.ids['amount_lipisa_input'].text
        destination = self.ids['destination_input'].text

        # Check for a valid amount
        try:
            amount = float(amount)
            if amount <= 0:
                raise ValueError
        except ValueError:
            self.show_error_message("Enter a valid amount.")
            return

        # Check for a valid destination address
        if not self.check_address(destination):
            self.show_error_message("Enter a valid destination address.")
            return

        if not self.check_trustline(client, destination):
            self.show_error_message("Destination does not have a trustline for Lipisa.")
            return

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
        Amount = MDLabel(
            text= 'Amount:  '+str(amount),
        )
        Amount.font_size= "12sp"

        Destination = MDLabel(
            text= 'Destination:'+str(destination)
        )
        Destination.font_size= "10sp"

        # Define a box layout to contain the text
        content_box = BoxLayout(orientation='vertical', padding=(1,1,1,1))
        content_box.add_widget(MDLabel(text="Confirm transaction",size_hint=(1, 0.2)))
        content_box.add_widget(MDLabel(text="",size_hint=(1, 0.3)))
        content_box.add_widget(Amount)
        content_box.add_widget(Destination)
        content_box.add_widget(self.password_field)
        content_box.add_widget(MDLabel(text="",size_hint=(1, 2.5)))
        content_box.ids['password_field'] = self.password_field

        # Define the dialog with custom parameters
        self.dialog = MDDialog(
            title=' ',
            size_hint=(0.8, 0.3),
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
                    on_release=lambda x: self.perform_send(self.password_field.text)
                )
            ]
        )
        self.dialog.add_widget(content_box)

        # Open the dialog
        self.dialog.open()


    def perform_send(self, entered_password):


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
            self.wallet_data = shelve.open("wallet_data")
            self.public_key = self.wallet_data["public_key"]
            nonce = self.wallet_data["nonce"]
            encrypted_private_key = self.wallet_data["private_key"]
            password = self.wallet_data["password"].decode('utf-8').encode('ascii')
            salt = self.wallet_data["salt"]
            key = PBKDF2(password, salt, dkLen=32, count=100000)
            cipher = AES.new(key, AES.MODE_GCM,nonce=nonce)
            private_key = str(cipher.decrypt(encrypted_private_key))
            self.private_key = private_key[2:68]

            def wallet_from_kp():
                wallet = Wallet.create()
                wallet.public_key = self.public_key
                wallet.private_key = self.private_key
                wallet.classic_address = derive_classic_address(self.public_key)
                return wallet
            test_wallet = wallet_from_kp()

            my_tx_payment = Payment(
                account=test_wallet.classic_address,
                amount=xrpl.models.amounts.issued_currency_amount.IssuedCurrencyAmount(
                    currency="4C69706973610000000000000000000000000000",
                    issuer="r4dPUdvD5iGyenACWgDF72Un4M9WVNK4if",
                    value=float(self.amount_lipisa_input.text),

                ),
                destination=self.destination_input.text,
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

    def check_balance_lipisa(self, dt):
        try:
            self.wallet_data = shelve.open("wallet_data")
            self.public_key = self.wallet_data["public_key"]

            def wallet_from_kp():
                wallet = Wallet.create()
                wallet.classic_address = derive_classic_address(self.public_key)
                return wallet

            test_wallet = wallet_from_kp()

            acct_objects = AccountObjects(
                account=test_wallet.classic_address,
                ledger_index="validated",
                type="state",
                deletion_blockers_only=False,
                limit=100
            )
            response = client.request(acct_objects)

            # Tokensvalues (all trustlines)

            data = json.loads((json.dumps(response.result, indent=4, sort_keys=True)))

            tokensvalue = dict()
            currenciescheck = dict()

            for currencies in data['account_objects']:
                currency = currencies['Balance']['currency']
                value = currencies['Balance']['value']
                tokensvalue[currency] = value
                currenciescheck[currency] = currency

            # Lipisa (Tokensvalue)
            if '4C69706973610000000000000000000000000000' in currenciescheck:
                self.lipisa_balance.text = (tokensvalue['4C69706973610000000000000000000000000000'])
            else:
                self.lipisa_balance.text = 'No Lipisa Trustline'

            # Transaction History

            tx_info = AccountTx(
                account=test_wallet.classic_address,
                ledger_index_min= -1,
                ledger_index_max= -1,
                ledger_index="validated",
                limit= 20
            )
            response2 = client.request(tx_info)
            data2 = json.loads((json.dumps(response2.result, indent=4, sort_keys=True)))

            for i, transaction in enumerate(data2['transactions']):
                meta = transaction["meta"]
                tx = transaction["tx"]
                validated = transaction["validated"]

                label_id = f'transaction{i+1}'
                label = self.ids[label_id]

                if "Amount" in tx and "value" in tx["Amount"]:
                    if '4C69706973610000000000000000000000000000' in tx["Amount"]["currency"]:
                        label.text = f'Amount Lipisa:                        {tx["Amount"]["value"]}'
                    if '43616C6F72696554657374000000000000000000' in tx["Amount"]["currency"]:
                        value = format(float(tx["Amount"]["value"]), ".2f")
                        label.text = f'Amount CalorieTest:              {value}'
                    else:
                        label.text = f'Amount in other currency: {tx["Amount"]["value"]} {tx["Amount"]["currency"]}'
                else:
                    amount = 0
                    if "Amount" in tx:
                        amount = int(tx["Amount"]) / 1e6
                    else:
                        label.text = "Amount: Not specified"
                    label.text = f'Amount XRP:                           {amount}'

                if "Account" in tx:
                    if tx["Account"] == test_wallet.classic_address:
                        label.text += f' (Sent)'
                    else:
                        label.text += f' (Received)'

            self.wallet_data.close()
        except Exception as e:
            print(e)
            self.wallet_data.close()
            self.lipisa_balance.text = "Error: Could not get balance"
    def backto_wallet(self):
        self.manager.current = "wallet_screen"




class SendCalorieTestScreen(Screen):
    def on_pre_enter(self):
        self.wallet_data = shelve.open("wallet_data")
        self.public_key = self.wallet_data["public_key"]

        def wallet_from_kp():
            wallet = Wallet.create()
            wallet.classic_address = derive_classic_address(self.public_key)
            return wallet
        test_wallet = wallet_from_kp()

        self.xrp_address.text = test_wallet.classic_address
        self.wallet_data.close()
        self.check_balance_calorietest(dt=16)
        Clock.schedule_interval(self.check_balance_calorietest, 33)

    def show_error_message(self, message):
        self.dialog = MDDialog(
            title="Error",
            text=message,
            size_hint=(0.7, 0.3),
            md_bg_color=(0.71, 0.75, 0.86, 1),
            buttons=[
                MDFillRoundFlatButton(
                    text="Close",
                    md_bg_color=(1, 0.7, 0.13, 1),
                    text_color=(0, 0.55, 0.21, 1),
                    on_release=lambda x: self.dialog.dismiss()
                )
            ]
        )
        self.dialog.open()

    def check_trustline(self, client, destination):

        acct_objects = AccountObjects(
            account=destination,
            ledger_index="validated",
            type="state",
            deletion_blockers_only=False,
            limit=100
        )
        response = client.request(acct_objects)

        data = json.loads((json.dumps(response.result, indent=4, sort_keys=True)))

        tokensvalue = dict()
        currenciescheck = dict()

        for currencies in data['account_objects']:
            currency = currencies['Balance']['currency']
            value = currencies['Balance']['value']
            tokensvalue[currency] = value
            currenciescheck[currency] = currency

        if '43616C6F72696554657374000000000000000000' in currenciescheck:
            return True
        else:
            return False

    def check_address(self, destination):
        acct_info = AccountInfo(
            account=destination,
            ledger_index="validated",
            strict=True,
        )
        response = client.request(acct_info)
        print("response.status: ", response.status)
        if response.status == "success":
            return True
        else:
            return False

    def send_calorietest(self):
        amount = self.ids['amount_calorietest_input'].text
        destination = self.ids['destination_input'].text

        # Check for a valid amount
        try:
            amount = float(amount)
            if amount <= 0:
                raise ValueError
        except ValueError:
            self.show_error_message("Enter a valid amount.")
            return

        # Check for a valid destination address
        if not self.check_address(destination):
            self.show_error_message("Enter a valid destination address.")
            return

        if not self.check_trustline(client, destination):
            self.show_error_message("Destination does not have a trustline for CalorieTest.")
            return

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
        Amount = MDLabel(
            text= 'Amount:  '+str(amount),
        )
        Amount.font_size= "12sp"

        Destination = MDLabel(
            text= 'Destination:'+str(destination)
        )
        Destination.font_size= "10sp"

        # Define a box layout to contain the text
        content_box = BoxLayout(orientation='vertical', padding=(1,1,1,1))
        content_box.add_widget(MDLabel(text="Confirm transaction",size_hint=(1, 0.2)))
        content_box.add_widget(MDLabel(text="",size_hint=(1, 0.3)))
        content_box.add_widget(Amount)
        content_box.add_widget(Destination)
        content_box.add_widget(self.password_field)
        content_box.add_widget(MDLabel(text="",size_hint=(1, 2.5)))
        content_box.ids['password_field'] = self.password_field

        # Define the dialog with custom parameters
        self.dialog = MDDialog(
            title=' ',
            size_hint=(0.8, 0.3),
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
                    on_release=lambda x: self.perform_send(self.password_field.text)
                )
            ]
        )
        self.dialog.add_widget(content_box)

        # Open the dialog
        self.dialog.open()


    def perform_send(self, entered_password):


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
            self.wallet_data = shelve.open("wallet_data")
            self.public_key = self.wallet_data["public_key"]
            nonce = self.wallet_data["nonce"]
            encrypted_private_key = self.wallet_data["private_key"]
            password = self.wallet_data["password"].decode('utf-8').encode('ascii')
            salt = self.wallet_data["salt"]
            key = PBKDF2(password, salt, dkLen=32, count=100000)
            cipher = AES.new(key, AES.MODE_GCM,nonce=nonce)
            private_key = str(cipher.decrypt(encrypted_private_key))
            self.private_key = private_key[2:68]

            def wallet_from_kp():
                wallet = Wallet.create()
                wallet.public_key = self.public_key
                wallet.private_key = self.private_key
                wallet.classic_address = derive_classic_address(self.public_key)
                return wallet
            test_wallet = wallet_from_kp()

            my_tx_payment = Payment(
                account=test_wallet.classic_address,
                amount=xrpl.models.amounts.issued_currency_amount.IssuedCurrencyAmount(
                    currency="43616C6F72696554657374000000000000000000",
                    issuer="rJps2NCFbbSefuSzibzNBSVv5ywpTdCBDX",
                    value=float(self.amount_calorietest_input.text),

                ),
                destination=self.destination_input.text,
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

    def check_balance_calorietest(self, dt):
        try:
            self.wallet_data = shelve.open("wallet_data")
            self.public_key = self.wallet_data["public_key"]

            def wallet_from_kp():
                wallet = Wallet.create()
                wallet.classic_address = derive_classic_address(self.public_key)
                return wallet

            test_wallet = wallet_from_kp()

            acct_objects = AccountObjects(
                account=test_wallet.classic_address,
                ledger_index="validated",
                type="state",
                deletion_blockers_only=False,
                limit=100
            )
            response = client.request(acct_objects)

            # Tokensvalues (all trustlines)

            data = json.loads((json.dumps(response.result, indent=4, sort_keys=True)))

            tokensvalue = dict()
            currenciescheck = dict()

            for currencies in data['account_objects']:
                currency = currencies['Balance']['currency']
                value = currencies['Balance']['value']
                tokensvalue[currency] = value
                currenciescheck[currency] = currency

            # CalorieTest (Tokensvalue)
            if '43616C6F72696554657374000000000000000000' in currenciescheck:
                value = format(float(tokensvalue['43616C6F72696554657374000000000000000000']), ".2f")
                self.calorietest_balance.text = value
            else:
                self.calorietest_balance.text = 'No CalorieTest Trustline'

            # Transaction History

            tx_info = AccountTx(
                account=test_wallet.classic_address,
                ledger_index_min= -1,
                ledger_index_max= -1,
                ledger_index="validated",
                limit= 20
            )
            response2 = client.request(tx_info)
            data2 = json.loads((json.dumps(response2.result, indent=4, sort_keys=True)))

            for i, transaction in enumerate(data2['transactions']):
                meta = transaction["meta"]
                tx = transaction["tx"]
                validated = transaction["validated"]

                label_id = f'transaction{i+1}'
                label = self.ids[label_id]

                if "Amount" in tx and "value" in tx["Amount"]:
                    if '4C69706973610000000000000000000000000000' in tx["Amount"]["currency"]:
                        label.text = f'Amount Lipisa:                        {tx["Amount"]["value"]}'
                    if '43616C6F72696554657374000000000000000000' in tx["Amount"]["currency"]:
                        value = format(float(tx["Amount"]["value"]), ".2f")
                        label.text = f'Amount CalorieTest:              {value}'
                    else:
                        label.text = f'Amount in other currency: {tx["Amount"]["value"]} {tx["Amount"]["currency"]}'
                else:
                    amount = 0
                    if "Amount" in tx:
                        amount = int(tx["Amount"]) / 1e6
                    else:
                        label.text = "Amount: Not specified"
                    label.text = f'Amount XRP:                           {amount}'

                if "Account" in tx:
                    if tx["Account"] == test_wallet.classic_address:
                        label.text += f' (Sent)'
                    else:
                        label.text += f' (Received)'

            self.wallet_data.close()
        except Exception as e:
            print(e)
            self.wallet_data.close()
            self.lipisa_balance.text = "Error: Could not get balance"
    def backto_wallet(self):
        self.manager.current = "wallet_screen"


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
            self.wallet_data = shelve.open("wallet_data")
            self.public_key = self.wallet_data["public_key"]
            nonce = self.wallet_data["nonce"]
            encrypted_private_key = self.wallet_data["private_key"]
            password = self.wallet_data["password"].decode('utf-8').encode('ascii')
            salt = self.wallet_data["salt"]
            key = PBKDF2(password, salt, dkLen=32, count=100000)
            cipher = AES.new(key, AES.MODE_GCM,nonce=nonce)
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

    def walletgeneratorscreen(self):
        self.manager.current = "walletgenerator_screen"

    def dextradescreen(self):
        self.manager.current = "dextrade_screen"

    def foodtrackscreen(self):
        self.manager.current = "foodtrack_screen"

    def settingsscreen(self):
        self.manager.current = "settings_screen"

class WalletGeneratorScreen(Screen):
    def walletscreen(self):
        self.manager.current = "wallet_screen"

    def nftmintscreen(self):
        self.manager.current = "nftmint_screen"

    def dextradescreen(self):
        self.manager.current = "dextrade_screen"

    def foodtrackscreen(self):
        self.manager.current = "foodtrack_screen"

    def settingsscreen(self):
        self.manager.current = "settings_screen"
class DEXTradeScreen(Screen):
    def walletscreen(self):
        self.manager.current = "wallet_screen"

    def nftmintscreen(self):
        self.manager.current = "nftmint_screen"

    def walletgeneratorscreen(self):
        self.manager.current = "walletgenerator_screen"

    def foodtrackscreen(self):
        self.manager.current = "foodtrack_screen"

    def settingsscreen(self):
        self.manager.current = "settings_screen"
class FoodTrackScreen(Screen):
    def walletscreen(self):
        self.manager.current = "wallet_screen"

    def nftmintscreen(self):
        self.manager.current = "nftmint_screen"

    def walletgeneratorscreen(self):
        self.manager.current = "walletgenerator_screen"

    def dextradescreen(self):
        self.manager.current = "dextrade_screen"

    def settingsscreen(self):
        self.manager.current = "settings_screen"

class SettingsScreen(Screen):
    def walletscreen(self):
        self.manager.current = "wallet_screen"

    def nftmintscreen(self):
        self.manager.current = "nftmint_screen"

    def walletgeneratorscreen(self):
        self.manager.current = "walletgenerator_screen"

    def dextradescreen(self):
        self.manager.current = "dextrade_screen"

    def foodtrackscreen(self):
        self.manager.current = "foodtrack_screen"
class IntroScreen(Screen):
    def next(self):
        self.manager.current = "first_use_screen"
class FirstUseScreen(Screen):
    def create_password(self):
        password = self.ids.password.text
        confirm_password = self.ids.confirm_password.text

        # Check if password meets the conditions for a difficult password
        if not any(char.isupper() for char in password):
            self.ids.password.helper_text = "Password must contain at least one uppercase letter."
            return
        if not any(char.isdigit() for char in password):
            self.ids.password.helper_text = "Password must contain at least one number."
            return
        if not any(char in string.punctuation for char in password):
            self.ids.password.helper_text = "Password must contain at least one symbol."
            return
        if len(password) < 8:
            self.ids.password.helper_text = "Password must be at least 8 characters long."
            return

        # Check if password and confirmation password match
        if password != confirm_password:
            self.ids.confirm_password.helper_text = "Password and confirmation password must match."
            return

        # Hash the password using bcrypt before storing it
        hashed_password = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())

        # Use password to encrypt private keys
        self.wallet_data = shelve.open("wallet_data")
        self.wallet_data["password"] = hashed_password
        self.wallet_data.close()
        self.manager.current = "wallet_setup_screen"

class ImportKeysScreen(Screen):
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
        self.wallet_data["salt"] = salt
        key = PBKDF2(password, salt, dkLen=32, count=100000)
        cipher = AES.new(key, AES.MODE_GCM)
        nonce = cipher.nonce
        encrypted_private_key = cipher.encrypt(private_key.encode())
        self.wallet_data["public_key"] = public_key
        self.wallet_data["private_key"] = encrypted_private_key
        self.wallet_data["nonce"] = nonce
        self.wallet_data["keys"] = {"public": public_key, "private": private_key}
        self.wallet_data.close()

        # Go to "wallet_screen"
        self.manager.current = "wallet_screen"

class CreateWalletScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.wallet_data = None

    def generate_keys(self):
        test_wallet = generate_faucet_wallet(client, debug=True)
        self.ids.private_key.text = test_wallet.private_key
        self.ids.public_key.text = test_wallet.public_key

        dialog = MDDialog(
            title="Keys",
            text="Copy keypair to store it somewhere safe in order to keep access to your funds!\n"
                 "Private Key: {}\nPublic Key: {}".format(test_wallet.private_key, test_wallet.public_key),
            size_hint=(0.8, None),
            md_bg_color=(0.71, 0.75, 0.86, 1),
            buttons=[
                MDFillRoundFlatButton(
                    text="Copy",
                    md_bg_color=(1, 0.7, 0.13, 1),
                    text_color=(0, 0.55, 0.21, 1),
                    on_release=lambda x: self.copy_keys(self.ids.private_key.text, self.ids.public_key.text)
                ),
                MDFillRoundFlatButton(
                    text="Proceed",
                    md_bg_color=(1, 0.7, 0.13, 1),
                    text_color=(0, 0.55, 0.21, 1),
                    on_press=lambda x: self.proceed(dialog)
                ),
            ],
        )
        dialog.open()

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
        self.wallet_data["salt"] = salt
        key = PBKDF2(password, salt, dkLen=32, count=100000)
        cipher = AES.new(key, AES.MODE_GCM)
        nonce = cipher.nonce
        encrypted_private_key = cipher.encrypt(private_key.encode())
        self.wallet_data["public_key"] = public_key
        self.wallet_data["private_key"] = encrypted_private_key
        self.wallet_data["nonce"] = nonce
        self.wallet_data["keys"] = {"public": public_key, "private": private_key}
        self.wallet_data.close()

        # Go to "wallet_screen"
        self.manager.current = "wallet_screen"

class LoginScreen(Screen):
    def login(self):
        # Load the password hash from the file
        wallet_data = shelve.open("wallet_data")
        hashed_password = wallet_data.get("password")
        wallet_data.close()

        # Check if the password is correct
        password = self.ids.password.text.encode("utf-8")
        if not bcrypt.checkpw(password, hashed_password):

            self.password.hint_text = "Wrong password, try again"
            return

        # Navigate to the appropriate screen based on whether the keys are stored
        wallet_data = shelve.open("wallet_data")
        if wallet_data.get("keys") is None:
            wallet_data.close()
            self.manager.current = "wallet_setup_screen"
        else:
            wallet_data.close()
            self.manager.current = "wallet_screen"

class WalletSetupScreen(Screen):
    def create_wallet_screen(self):
        self.manager.current = "create_wallet_screen"
    
    def import_wallet_screen(self):
        self.manager.current = "importkeys_screen"



            
class CalorieAppTestnetV11(MDApp):
    def build(self):
        self.title = "CalorieAppTestnetV11"
        self.theme_cls.primary_palette = "Green"
        self.theme_cls.accent_palette = "Green"
        self.theme_cls.material_style = "M2"
        self.load_kv('CalorieAppTestnetV11.kv')
        self.manager = ScreenManager()
        self.intro_screen = IntroScreen(name="intro_screen")
        self.first_use_screen = FirstUseScreen(name="first_use_screen")
        self.wallet_setup_screen = WalletSetupScreen(name="wallet_setup_screen")
        self.create_wallet_screen = CreateWalletScreen(name="create_wallet_screen")
        self.importkeys_screen = ImportKeysScreen(name="importkeys_screen")
        self.login_screen = LoginScreen(name="login_screen")
        self.wallet_screen = WalletScreen(name="wallet_screen")
        self.sendxrp_screen = SendXRPScreen(name="sendxrp_screen")
        self.sendlipisa_screen = SendLipisaScreen(name="sendlipisa_screen")
        self.sendcalorietest_screen = SendCalorieTestScreen(name="sendcalorietest_screen")
        self.nftmint_screen = NFTMintScreen(name="nftmint_screen")
        self.walletgenerator_screen = WalletGeneratorScreen(name="walletgenerator_screen")
        self.dextrade_screen = DEXTradeScreen(name="dextrade_screen")
        self.foodtrack_screen = FoodTrackScreen(name="foodtrack_screen")
        self.settings_screen = SettingsScreen(name="settings_screen")       
        self.manager.add_widget(self.intro_screen)
        self.manager.add_widget(self.first_use_screen)
        self.manager.add_widget(self.wallet_setup_screen)
        self.manager.add_widget(self.create_wallet_screen)
        self.manager.add_widget(self.importkeys_screen)
        self.manager.add_widget(self.login_screen)
        self.manager.add_widget(self.wallet_screen)
        self.manager.add_widget(self.sendxrp_screen)
        self.manager.add_widget(self.sendlipisa_screen)
        self.manager.add_widget(self.sendcalorietest_screen)
        self.manager.add_widget(self.nftmint_screen)
        self.manager.add_widget(self.walletgenerator_screen)
        self.manager.add_widget(self.dextrade_screen)
        self.manager.add_widget(self.foodtrack_screen)
        self.manager.add_widget(self.settings_screen)
        try:
            self.wallet_data = shelve.open("wallet_data")
            if "password" in self.wallet_data:
                self.manager.current = "login_screen"
            else:
                self.manager.current = "intro_screen"
        except:
            self.manager.current = "intro_screen"
        finally:
            self.wallet_data.close()
        return self.manager
    
    def on_stop(self):
        self.wallet_data.close()
    

if __name__ == "__main__":
    CalorieAppTestnetV11().run()