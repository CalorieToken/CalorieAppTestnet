# Kivy libraries for the GUI.
from kivy.metrics import dp
from kivymd.uix.button import MDFillRoundFlatButton
from kivy.clock import Clock
from kivymd.uix.dialog import MDDialog
from kivy.uix.screenmanager import Screen
from kivy.core.clipboard import Clipboard
from kivymd.uix.menu import MDDropdownMenu
from kivy.utils import get_color_from_hex

# Encryption libraries for password and key encryption.
import bcrypt
import logging
logging.basicConfig(level=logging.WARNING)
import shelve
from Crypto.Cipher import AES
from Crypto.Protocol.KDF import PBKDF2
from Crypto.Cipher import AES

# XRPL libraries for xrpl functionality
import xrpl
from xrpl.wallet import Wallet
from xrpl.core.keypairs import derive_classic_address
from xrpl.clients import JsonRpcClient
from xrpl.models.requests import AccountInfo
from xrpl.models.requests.account_objects import AccountObjects
from xrpl.models.requests import AccountTx
from xrpl.wallet import Wallet
from xrpl.transaction import safe_sign_and_autofill_transaction
from xrpl.transaction import send_reliable_submission
from xrpl.core.keypairs import derive_classic_address

import json
JSON_RPC_URL = "https://s.altnet.rippletest.net:51234"
client = JsonRpcClient(JSON_RPC_URL)

class WalletScreen(Screen):
    def __init__(self, client, **kwargs):
        super().__init__(**kwargs)
        self.client = client
        self.wallet_data = None
        self.selected_key = None
        self.menu = None
        self.check_balance_event = None

    def set_selected_key(self, selected_key):
        self.selected_key = selected_key

    def menu_open(self, caller):
        with shelve.open("wallet_data") as self.wallet_data:
            keys_available = [
                key for key in self.wallet_data.keys() if key.startswith("public_key")
            ]

            menu_items = [
                {
                    "viewclass": "OneLineListItem",
                    "text":f"{derive_classic_address(self.wallet_data[key])}",
                    "on_release": lambda x=key: self.menu_callback(x),
                }
                for key in keys_available
            ]

            background_color = get_color_from_hex("#dadeed")

            self.menu = MDDropdownMenu(
                caller=caller,
                items=menu_items,
                width_mult=8,
                width=dp(400),
                max_height=dp(200),
                background_color=background_color,
            )
            self.menu.open()
            self.wallet_data.close()

    def on_key_selected(self, selected_key):
        with shelve.open("wallet_data") as self.wallet_data:
            if selected_key in self.wallet_data:
                self.public_key = self.wallet_data[selected_key]
                self.private_key = self.wallet_data[selected_key.replace("public", "private")]
                self.nonce = self.wallet_data[selected_key.replace("public", "nonce")]
                self.salt = self.wallet_data[selected_key.replace("public", "salt")]

        if self.public_key:
            def wallet_from_kp():
                wallet = Wallet.create()
                wallet.classic_address = derive_classic_address(self.public_key)
                return wallet

            test_wallet = wallet_from_kp()
            self.xrp_address.text = test_wallet.classic_address
            if self.check_balance_event:
                Clock.unschedule(self.check_balance_event)

            self.check_balance(dt=33)
            self.check_balance_event = Clock.schedule_interval(self.check_balance, 33)
            self.wallet_data.close()

    def menu_callback(self, menu_item):
        self.selected_key = menu_item 
        self.on_key_selected(self.selected_key)
        self.menu.dismiss()

    def on_pre_enter(self):
        if not self.selected_key:
            return

        with shelve.open("wallet_data") as self.wallet_data:
            if self.selected_key in self.wallet_data:
                self.public_key = self.wallet_data[self.selected_key]
                self.private_key = self.wallet_data[self.selected_key.replace("public", "private")]

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

    def on_pre_leave(self):
        Clock.unschedule(self.check_balance)

    def check_balance(self, dt):
        try:
            if not self.selected_key:
                return

            self.wallet_data = shelve.open("wallet_data")

            with shelve.open("wallet_data") as self.wallet_data:
                if self.selected_key in self.wallet_data:
                    self.public_key = self.wallet_data[self.selected_key]
                    self.private_key = self.wallet_data[self.selected_key.replace("public", "private")]

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
                ledger_index_min=-1,
                ledger_index_max=-1,
                ledger_index="validated",
                limit=20
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
                    elif '43616C6F72696554657374000000000000000000' in tx["Amount"]["currency"]:
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

            # Lipisa Balance
            acct_objects = AccountObjects(
                account=test_wallet.classic_address,
                ledger_index="validated",
                type="state",
                deletion_blockers_only=False,
                limit=100
            )
            response3 = self.client.request(acct_objects)
            data3 = json.loads((json.dumps(response3.result, indent=4, sort_keys=True)))

            tokensvalue = dict()
            currenciescheck = dict()

            for currencies in data3['account_objects']:
                currency = currencies['Balance']['currency']
                value = currencies['Balance']['value']
                tokensvalue[currency] = value
                currenciescheck[currency] = currency

            if '4C69706973610000000000000000000000000000' in currenciescheck:
                self.lipisa_balance.text = format(float(tokensvalue['4C69706973610000000000000000000000000000']), ".2f")
            else:
                self.lipisa_balance.text = 'No Lipisa Trustline'

            # CalorieTest Balance
            if '43616C6F72696554657374000000000000000000' in currenciescheck:
                value = format(float(tokensvalue['43616C6F72696554657374000000000000000000']), ".2f")
                self.calorietest_balance.text = value
            else:
                self.calorietest_balance.text = 'No CalorieTest Trustline'

            self.wallet_data.close()
        except Exception as e:
            print(e)
            self.wallet_data.close()
            self.xrp_balance.text = "Error: Could not get balance"
            self.lipisa_balance.text = "Error: Could not get balance"
            self.calorietest_balance.text = "Error: Could not get balance"

    def open_dialog_lipisa(self):
        if not self.selected_key:
            return

        self.wallet_data = shelve.open("wallet_data")

        with shelve.open("wallet_data") as self.wallet_data:
            if self.selected_key in self.wallet_data:
                self.public_key = self.wallet_data[self.selected_key]
                self.private_key = self.wallet_data[self.selected_key.replace("public", "private")]

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
        response = self.client.request(acct_objects)
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
                        on_release=self.set_trustline_lipisa
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
                        on_release=self.set_trustline_lipisa
                    ),
                ],
            )
        self.dialog.open()
        self.wallet_data.close()

    def set_trustline_lipisa(self, *args):
        if not self.selected_key:
            return

        with shelve.open("wallet_data") as self.wallet_data:
            if self.selected_key in self.wallet_data:
                self.public_key = self.wallet_data[self.selected_key]
                self.private_key = self.wallet_data[self.selected_key.replace("public", "private")]
                self.nonce = self.wallet_data[self.selected_key.replace("public", "nonce")]
                self.salt = self.wallet_data[self.selected_key.replace("public", "salt")]

        if self.public_key:
            self.wallet_data = shelve.open("wallet_data")
            self.public_key = self.wallet_data[self.selected_key]
            nonce = self.wallet_data[self.selected_key.replace("public", "nonce")]
            encrypted_private_key = self.wallet_data[self.selected_key.replace("public", "private")]
            password = self.wallet_data["password"].decode('utf-8').encode('ascii')
            salt = self.wallet_data[self.selected_key.replace("public", "salt")]
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
            my_tx_payment_signed = safe_sign_and_autofill_transaction(my_tx_payment, test_wallet, self.client)

            # Submit and send the transaction
            tx_response = send_reliable_submission(my_tx_payment_signed, self.client)

            if tx_response.result == 'tesSUCCESS':
                print('Transaction successful!')
            else:
                print(f'Transaction failed with error: {tx_response.result}')

        self.dialog.dismiss()
        self.wallet_data.close()

    def open_dialog_calorietest(self):
        if not self.selected_key:
            return

        self.wallet_data = shelve.open("wallet_data")

        if self.selected_key in self.wallet_data:
            self.public_key = self.wallet_data[self.selected_key]
            self.private_key = self.wallet_data[self.selected_key.replace("public", "private")]

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
        response = self.client.request(acct_objects)
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
                        on_release=self.set_trustline_calorietest
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
                        on_release=self.set_trustline_calorietest
                    ),
                ],
            )
        self.dialog.open()

        self.wallet_data.close()

    def set_trustline_calorietest(self, *args):
        if not self.selected_key:
            return

        with shelve.open("wallet_data") as self.wallet_data:
            if self.selected_key in self.wallet_data:
                self.public_key = self.wallet_data[self.selected_key]
                self.private_key = self.wallet_data[self.selected_key.replace("public", "private")]
                self.nonce = self.wallet_data[self.selected_key.replace("public", "nonce")]
                self.salt = self.wallet_data[self.selected_key.replace("public", "salt")]

        if self.public_key:
            self.wallet_data = shelve.open("wallet_data")
            self.public_key = self.wallet_data[self.selected_key]
            nonce = self.wallet_data[self.selected_key.replace("public", "nonce")]
            encrypted_private_key = self.wallet_data[self.selected_key.replace("public", "private")]
            password = self.wallet_data["password"].decode('utf-8').encode('ascii')
            salt = self.wallet_data[self.selected_key.replace("public", "salt")]
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
        my_tx_payment_signed = safe_sign_and_autofill_transaction(my_tx_payment, test_wallet, self.client)

        # Submit and send the transaction
        tx_response = send_reliable_submission(my_tx_payment_signed, self.client)

        if tx_response.result == 'tesSUCCESS':
            print('Transaction successful!')
        else:
            print(f'Transaction failed with error: {tx_response.result}')

        self.dialog.dismiss()
        self.wallet_data.close()

    def send_xrp_screen(self):
        self.manager.current = "sendxrp_screen"

    def send_lipisa_screen(self):
        if not self.selected_key:
                return

        self.wallet_data = shelve.open("wallet_data")

        with shelve.open("wallet_data") as self.wallet_data:
            if self.selected_key in self.wallet_data:
                self.public_key = self.wallet_data[self.selected_key]
                self.private_key = self.wallet_data[self.selected_key.replace("public", "private")]

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
        response = self.client.request(acct_objects)
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
                        on_release=self.set_trustline_lipisa
                    ),
                ],
            )
            self.dialog.open()

    def send_calorietest_screen(self):
        if not self.selected_key:
                return

        self.wallet_data = shelve.open("wallet_data")

        with shelve.open("wallet_data") as self.wallet_data:
            if self.selected_key in self.wallet_data:
                self.public_key = self.wallet_data[self.selected_key]
                self.private_key = self.wallet_data[self.selected_key.replace("public", "private")]

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
        response = self.client.request(acct_objects)
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
                        on_release=self.set_trustline_calorietest
                    ),
                ],
            )
            self.dialog.open()

    def copy_address(self):
        Clipboard.copy(self.xrp_address.text)

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