# Kivy libraries for the GUI.
from kivymd.uix.button import MDFillRoundFlatButton
from kivy.clock import Clock
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
from Crypto.Cipher import AES
import shelve
import bcrypt

# XRPL libraries for xrpl functionality
from xrpl.wallet import Wallet
from xrpl.core.keypairs import derive_classic_address
from xrpl.clients import JsonRpcClient
from xrpl.models.requests import AccountInfo
from xrpl.models.requests import AccountTx
from xrpl.wallet import Wallet
from xrpl.models.transactions import Payment
from xrpl.transaction import safe_sign_and_autofill_transaction
from xrpl.transaction import send_reliable_submission
from xrpl.core.keypairs import derive_classic_address
from xrpl.core.binarycodec.exceptions import XRPLBinaryCodecException
from xrpl.models.transactions import Payment

import json
JSON_RPC_URL = "https://s.altnet.rippletest.net:51234"
client = JsonRpcClient(JSON_RPC_URL)

# Send XRP Screen
class SendXRPScreen(Screen):
    def __init__(self, client, **kwargs):
        super().__init__(**kwargs)
        self.client = client

    def on_pre_enter(self):
        if not self.manager.get_screen("wallet_screen").selected_key:
            return

        with shelve.open("wallet_data") as self.wallet_data:
            if self.manager.get_screen("wallet_screen").selected_key in self.wallet_data:
                self.public_key = self.wallet_data[self.manager.get_screen("wallet_screen").selected_key]
                self.private_key = self.wallet_data[self.manager.get_screen("wallet_screen").selected_key.replace("public", "private")]       

        if self.public_key:

            def wallet_from_kp():
                wallet = Wallet.create()
                wallet.classic_address = derive_classic_address(self.public_key)
                return wallet
            test_wallet = wallet_from_kp()

            self.xrp_address.text = test_wallet.classic_address
            self.wallet_data.close()
            self.check_balance(dt=33)
            Clock.schedule_interval(self.check_balance, 33)

    def on_leave(self):
        Clock.unschedule(self.check_balance)

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
        response = self.client.request(acct_info)
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

            my_tx_payment = Payment(
                account=test_wallet.classic_address,
                amount=str(int(float(self.amount_input.text)* 1000000)),
                destination=self.destination_input.text,
            )
            # Sign the transaction
            my_tx_payment_signed = safe_sign_and_autofill_transaction(my_tx_payment, test_wallet, self.client)

            # Submit and send the transaction
            send_reliable_submission(my_tx_payment_signed, self.client)

            self.dialog.dismiss()
            self.wallet_data.close()
        except XRPLBinaryCodecException as e:
            self.wallet_data.close()
            self.password_field.hint_text = "XRPLBinaryCodecException Error"

    def check_balance(self, dt):
        try:
            self.wallet_data = shelve.open("wallet_data")
            self.public_key = self.wallet_data[self.manager.get_screen("wallet_screen").selected_key]

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
            response = self.client.request(acct_info)
            data = json.loads((json.dumps(response.result, indent=4, sort_keys=True)))
            # Divide the balance by 1 million to convert to units of 1
            balance = format(int(data["account_data"]["Balance"]) / 1e6, ".2f")
            self.xrp_balance.text = str(balance)

            # Transaction History

            tx_info = AccountTx(
                account=test_wallet.classic_address,
                ledger_index_min= -1,
                ledger_index_max= -1,
                ledger_index="validated",
                limit= 20
            )
            response2 = self.client.request(tx_info)
            data2 = json.loads((json.dumps(response2.result, indent=4, sort_keys=True)))

            for i, transaction in enumerate(data2['transactions']):
                tx = transaction["tx"]

                label_id = f'transaction{i+1}'
                label = self.ids[label_id]

                if "Amount" in tx and "value" in tx["Amount"]:
                    if '4C69706973610000000000000000000000000000' in tx["Amount"]["currency"]:
                        value = format(float(tx["Amount"]["value"]), ".2f")
                        label.text = f'Amount Lipisa:                        {value}'
                    if '43616C6F72696554657374000000000000000000' in tx["Amount"]["currency"]:
                        value = format(float(tx["Amount"]["value"]), ".2f")
                        label.text = f'Amount CalorieTest:              {value}'
                    else:
                        label.text = f'Amount in other currency: {tx["Amount"]["value"]} {tx["Amount"]["currency"]}'
                else:
                    amount = 0
                    if "Amount" in tx:
                        amount = format(int(tx["Amount"]) / 1e6, ".2f")
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