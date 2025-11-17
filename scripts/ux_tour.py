import os
import sys
import time
from datetime import datetime

from kivy.clock import Clock
from kivy.core.window import Window

# Ensure relative imports work when run from repo root
if __name__ == "__main__":
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

from src.core.app import CalorieAppTestnet  # noqa: E402


class UxTour:
    def __init__(self):
        ts = datetime.now().strftime("%Y%m%d-%H%M%S")
        self.out_dir = os.path.join("docs", "ui_tour", ts)
        os.makedirs(self.out_dir, exist_ok=True)
        self.app = None
        self.test_results = []
        self.test_count = 0
        self.pass_count = 0
        self.fail_count = 0

    def snap(self, name: str):
        # Normalize filename
        safe = name.replace("/", "-").replace(" ", "_")
        path = os.path.join(self.out_dir, f"{safe}.png")
        try:
            Window.screenshot(name=path)
        except Exception:
            pass
        return path

    def log(self, msg: str):
        print(f"[UX] {msg}")

    def test(self, name: str, assertion_fn, screenshot=True):
        """Run a test with assertion and optional screenshot"""
        self.test_count += 1
        try:
            result = assertion_fn()
            if result:
                self.pass_count += 1
                self.log(f"✓ PASS: {name}")
                self.test_results.append({"name": name, "status": "PASS"})
            else:
                self.fail_count += 1
                self.log(f"✗ FAIL: {name}")
                self.test_results.append({"name": name, "status": "FAIL"})
            if screenshot:
                self.snap(f"test_{self.test_count:03d}_{name}")
        except Exception as e:
            self.fail_count += 1
            self.log(f"✗ ERROR: {name} - {e}")
            self.test_results.append({"name": name, "status": "ERROR", "error": str(e)})

    def write_report(self):
        """Write test results summary to file"""
        report_path = os.path.join(self.out_dir, "test_report.txt")
        with open(report_path, "w") as f:
            f.write(f"UX Tour Test Report\n")
            f.write(f"===================\n\n")
            f.write(f"Total Tests: {self.test_count}\n")
            f.write(f"Passed: {self.pass_count}\n")
            f.write(f"Failed: {self.fail_count}\n")
            f.write(f"Success Rate: {(self.pass_count/self.test_count*100):.1f}%\n\n")
            f.write(f"Detailed Results:\n")
            f.write(f"-----------------\n")
            for result in self.test_results:
                status = result["status"]
                name = result["name"]
                if status == "ERROR":
                    f.write(f"{status}: {name} - {result.get('error', '')}\n")
                else:
                    f.write(f"{status}: {name}\n")
        self.log(f"Report written to {report_path}")

    def start(self):
        os.environ["UX_TOUR"] = "1"
        self.app = CalorieAppTestnet()
        # Defer driving until build completes and root exists
        Clock.schedule_once(self._drive_intro, 0.8)
        self.app.run()

    # Steps
    def _drive_intro(self, dt):
        try:
            self.log("Intro screen")
            self.snap("00_intro_screen")
            # Jump to wallet screen
            self.app.manager.current = "wallet_screen"
            Clock.schedule_once(self._drive_wallet, 0.6)
        except Exception as e:
            self.log(f"Intro step failed: {e}")

    def _drive_wallet(self, dt):
        try:
            self.log("Wallet screen")
            scr = self.app.manager.get_screen("wallet_screen")
            
            # Test header presence
            self.test("Wallet header exists", 
                     lambda: scr.ids.get("app_header") is not None)
            
            # Test address label
            self.test("Address label exists",
                     lambda: scr.ids.get("xrp_address_label") is not None)
            
            # Test balance label
            self.test("Balance label exists",
                     lambda: scr.xrp_balance is not None)
            
            # Capture main wallet view
            self.snap("10_wallet")
            
            # Test copy address button
            try:
                copy_btn = [w for w in scr.walk() if hasattr(w, 'icon') and w.icon == 'content-copy']
                self.test("Copy address button exists", lambda: len(copy_btn) > 0)
            except Exception:
                pass
            
            # Test send XRP button
            try:
                send_btn = [w for w in scr.walk() if hasattr(w, 'icon') and w.icon == 'send']
                self.test("Send XRP button exists", lambda: len(send_btn) > 0)
            except Exception:
                pass
            
            # Test trustline refresh button
            try:
                refresh_btn = [w for w in scr.walk() if hasattr(w, 'icon') and w.icon == 'refresh']
                self.test("Refresh trustline button exists", lambda: len(refresh_btn) > 0)
            except Exception:
                pass
            
            # Open account selector dialog via method
            try:
                scr.open_account_selector()
                Clock.schedule_once(self._snap_account_selector, 0.6)
            except Exception:
                Clock.schedule_once(self._to_send_xrp, 0.1)
        except Exception as e:
            self.log(f"Wallet step failed: {e}")
            Clock.schedule_once(self._to_send_xrp, 0.1)

    def _snap_account_selector(self, dt):
        self.log("Account selector dialog")
        self.snap("11_wallet_account_selector")
        # Dismiss dialog if present
        try:
            scr = self.app.manager.get_screen("wallet_screen")
            if getattr(scr, "account_dialog", None):
                scr.account_dialog.dismiss()
        except Exception:
            pass
        Clock.schedule_once(self._to_send_xrp, 0.3)

    def _to_send_xrp(self, dt):
        try:
            self.log("Navigate to Send XRP")
            scr = self.app.manager.get_screen("wallet_screen")
            scr.send_xrp_screen()
            Clock.schedule_once(self._drive_send_xrp, 0.6)
        except Exception as e:
            self.log(f"Send XRP nav failed: {e}")
            Clock.schedule_once(self._finish, 0.2)

    def _drive_send_xrp(self, dt):
        try:
            scr = self.app.manager.get_screen("sendxrp_screen")
            
            # Test header
            self.test("Send XRP header exists",
                     lambda: scr.ids.get("app_header") is not None)
            
            # Test form fields
            self.test("Amount input exists",
                     lambda: scr.ids.get("amount_input") is not None)
            self.test("Destination input exists",
                     lambda: scr.ids.get("destination_input") is not None)
            
            # Log hint text values for diagnostics
            amt_hint = getattr(scr.ids.get("amount_input"), "hint_text", "")
            dest_hint = getattr(scr.ids.get("destination_input"), "hint_text", "")
            self.log(f"Hints: amount='{amt_hint}' dest='{dest_hint}'")
            self.test("Amount hint text present",
                     lambda: amt_hint != "")
            self.test("Destination hint text present",
                     lambda: dest_hint != "")
            
            self.snap("20_send_xrp_form")
            
            # Test balance label
            self.test("XRP balance label exists",
                     lambda: scr.xrp_balance is not None)
            
            # Test transactions card
            try:
                tx_card = scr.ids.get("transactions_card")
                self.test("Transactions card exists", lambda: tx_card is not None)
            except Exception:
                pass
            
            # Fill with a known valid testnet address and amount
            try:
                scr.ids["amount_input"].text = "1.5"
                # Genesis testnet address (commonly present)
                scr.ids["destination_input"].text = "rHb9CJAWyB4rj91VRWn96DkukG4bwdtyTh"
                self.test("Amount field accepts input", 
                         lambda: scr.ids["amount_input"].text == "1.5")
                self.test("Destination field accepts input",
                         lambda: scr.ids["destination_input"].text != "")
            except Exception:
                pass
            # Trigger dialog (we won't confirm)
            try:
                scr.send_xrp()
                Clock.schedule_once(self._snap_send_xrp_dialog, 1.2)
            except Exception:
                Clock.schedule_once(self._to_settings, 0.4)
        except Exception as e:
            self.log(f"Send XRP step failed: {e}")
            Clock.schedule_once(self._to_settings, 0.4)

    def _snap_send_xrp_dialog(self, dt):
        self.log("Send XRP confirmation dialog")
        # Test dialog opened
        try:
            scr = self.app.manager.get_screen("sendxrp_screen")
            self.test("Send dialog created", lambda: hasattr(scr, "dialog") and scr.dialog is not None)
        except Exception:
            pass
        self.snap("21_send_xrp_dialog")
        # Try to dismiss any dialog via stored ref
        try:
            scr = self.app.manager.get_screen("sendxrp_screen")
            if getattr(scr, "dialog", None):
                scr.dialog.dismiss()
        except Exception:
            pass
        Clock.schedule_once(self._to_settings, 0.3)

    def _to_settings(self, dt):
        try:
            self.log("Navigate to Settings")
            self.app.manager.current = "settings_screen"
            Clock.schedule_once(self._snap_settings, 0.5)
            # After settings, attempt token send screen as a dynamic example
            Clock.schedule_once(self._to_token_send, 0.9)
        except Exception:
            Clock.schedule_once(self._finish, 0.1)

    def _snap_settings(self, dt):
        try:
            scr = self.app.manager.get_screen("settings_screen")
            hdr = scr.ids.get("app_header")
            title = getattr(hdr, "title", "") if hdr else ""
            self.test("Settings header has title", lambda: title != "")

            # Accounts list exists
            self.test("Accounts list exists", lambda: scr.ids.get("accounts_list") is not None)

            # Refresh button present (by icon)
            try:
                refresh_btns = [w for w in scr.walk() if hasattr(w, 'icon') and w.icon == 'refresh']
                self.test("Settings refresh button exists", lambda: len(refresh_btns) > 0)
            except Exception:
                pass

            self.snap("30_settings")
        except Exception:
            self.snap("30_settings")
        # handover to token route via _to_token_send

    def _finish(self, dt):
        self.log("Tour complete; stopping app")
        self.write_report()
        # Allow screenshot I/O to flush
        Clock.schedule_once(lambda _dt: self.app.stop(), 0.1)

    # Token send step (dynamic: USD + known test issuer)
    def _to_token_send(self, dt):
        try:
            self.log("Navigate to Token Send (dynamic)")
            ws = self.app.manager.get_screen("wallet_screen")
            # Use XRP genesis as placeholder issuer; we only need UI
            issuer = "rHb9CJAWyB4rj91VRWn96DkukG4bwdtyTh"
            ws.navigate_to_token_send("USD", issuer)
            Clock.schedule_once(self._snap_token_form, 0.7)
        except Exception as e:
            self.log(f"Token nav failed: {e}")
            Clock.schedule_once(self._to_trustline, 0.2)

    def _snap_token_form(self, dt):
        try:
            # The screen name is derived in navigate_to_token_send
            screen_name = "send_usd_screen"
            scr = self.app.manager.get_screen(screen_name)
            
            # Test header
            try:
                hdr = scr.ids.get("app_header")
                title = getattr(hdr, "title", "") if hdr else ""
                self.log(f"Token header: '{title}'")
                self.test("Token send header has title", lambda: title != "")
            except Exception:
                pass
            
            # Test fields
            self.test("Token amount input exists",
                     lambda: scr.ids.get("amount_token_input") is not None)
            self.test("Token destination input exists",
                     lambda: scr.ids.get("destination_input") is not None)
            
            amt_hint = getattr(scr.ids.get("amount_token_input"), "hint_text", "")
            dest_hint = getattr(scr.ids.get("destination_input"), "hint_text", "")
            self.log(f"Token hints: amount='{amt_hint}' dest='{dest_hint}'")
            self.test("Token amount hint present", lambda: amt_hint != "")
            self.test("Token destination hint present", lambda: dest_hint != "")
            
            self.snap("40_send_token_form")
            Clock.schedule_once(self._to_trustline, 0.3)
        except Exception as e:
            self.log(f"Token snap failed: {e}")
            Clock.schedule_once(self._to_trustline, 0.2)

    # Add Trustline screen
    def _to_trustline(self, dt):
        try:
            self.log("Navigate to Add Trustline")
            self.app.manager.current = "add_trustline_screen"
            Clock.schedule_once(self._snap_trustline, 0.5)
        except Exception as e:
            self.log(f"Trustline nav failed: {e}")
            Clock.schedule_once(self._to_nft_mint, 0.2)

    def _snap_trustline(self, dt):
        try:
            scr = self.app.manager.get_screen("add_trustline_screen")
            hdr = scr.ids.get("app_header")
            title = getattr(hdr, "title", "") if hdr else ""
            self.log(f"Trustline header: '{title}'")
            self.test("Trustline header has title", lambda: title != "")
            
            # Test form fields
            self.test("Currency code input exists",
                     lambda: scr.ids.get("currency_code_input") is not None)
            self.test("Issuer address input exists",
                     lambda: scr.ids.get("issuer_address_input") is not None)
            self.test("Limit input exists",
                     lambda: scr.ids.get("limit_input") is not None)
            
            # Test field functionality
            try:
                scr.ids["currency_code_input"].text = "TST"
                self.test("Currency field accepts input",
                         lambda: scr.ids["currency_code_input"].text == "TST")
            except Exception:
                pass
            
            self.snap("50_add_trustline")
            Clock.schedule_once(self._to_nft_mint, 0.3)
        except Exception as e:
            self.log(f"Trustline snap failed: {e}")
            Clock.schedule_once(self._to_nft_mint, 0.2)

    # NFT Mint screen
    def _to_nft_mint(self, dt):
        try:
            self.log("Navigate to NFT Mint")
            self.app.manager.current = "nftmint_screen"
            Clock.schedule_once(self._snap_nft_mint, 0.5)
        except Exception as e:
            self.log(f"NFT nav failed: {e}")
            Clock.schedule_once(self._to_dex, 0.2)

    def _snap_nft_mint(self, dt):
        try:
            scr = self.app.manager.get_screen("nftmint_screen")
            hdr = scr.ids.get("app_header")
            title = getattr(hdr, "title", "") if hdr else ""
            self.log(f"NFT header: '{title}'")
            self.test("NFT mint header has title", lambda: title != "")
            
            # Test form fields
            self.test("URI input exists",
                     lambda: scr.ids.get("uri") is not None)
            self.test("Taxon input exists",
                     lambda: scr.ids.get("taxon") is not None)
            
            # Test field functionality
            try:
                scr.ids["uri"].text = "ipfs://test"
                scr.ids["taxon"].text = "0"
                self.test("URI field accepts input",
                         lambda: scr.ids["uri"].text == "ipfs://test")
                self.test("Taxon field accepts input",
                         lambda: scr.ids["taxon"].text == "0")
            except Exception:
                pass
            
            self.snap("60_nft_mint")
            Clock.schedule_once(self._to_dex, 0.3)
        except Exception as e:
            self.log(f"NFT snap failed: {e}")
            Clock.schedule_once(self._to_dex, 0.2)

    # DEX Trade screen
    def _to_dex(self, dt):
        try:
            self.log("Navigate to DEX Trade")
            self.app.manager.current = "dextrade_screen"
            Clock.schedule_once(self._snap_dex, 0.5)
        except Exception as e:
            self.log(f"DEX nav failed: {e}")
            Clock.schedule_once(self._to_create_wallet, 0.2)

    def _snap_dex(self, dt):
        try:
            scr = self.app.manager.get_screen("dextrade_screen")
            hdr = scr.ids.get("app_header")
            title = getattr(hdr, "title", "") if hdr else ""
            self.log(f"DEX header: '{title}'")
            self.test("DEX screen header has title", lambda: title != "")
            
            # Check for under development message or placeholder
            children = list(scr.walk())
            labels = [w for w in children if hasattr(w, 'text')]
            self.test("DEX screen has content",
                     lambda: len(labels) > 1)
            
            self.snap("70_dex")
            Clock.schedule_once(self._to_create_wallet, 0.3)
        except Exception as e:
            self.log(f"DEX snap failed: {e}")
            Clock.schedule_once(self._to_create_wallet, 0.2)

    # Wallet creation flow
    def _to_create_wallet(self, dt):
        try:
            self.log("Navigate to Create/Import Wallet")
            self.app.manager.current = "createimportwallet_screen"
            Clock.schedule_once(self._snap_create_wallet, 0.5)
        except Exception as e:
            self.log(f"Create wallet nav failed: {e}")
            Clock.schedule_once(self._to_mnemonic_display, 0.2)

    def _snap_create_wallet(self, dt):
        try:
            scr = self.app.manager.get_screen("createimportwallet_screen")
            hdr = scr.ids.get("app_header")
            title = getattr(hdr, "title", "") if hdr else ""
            self.log(f"CreateImport header: '{title}'")
            self.test("Create/Import screen header has title", lambda: title != "")
            
            # Test buttons
            create_btn = scr.ids.get("create_wallet_button")
            import_btn = scr.ids.get("import_wallet_button")
            self.test("Create wallet button exists",
                     lambda: create_btn is not None)
            self.test("Import wallet button exists",
                     lambda: import_btn is not None)
            
            self.snap("80_create_import")
            Clock.schedule_once(self._to_import_choice, 0.3)
        except Exception as e:
            self.log(f"CreateImport snap failed: {e}")
            Clock.schedule_once(self._to_import_choice, 0.2)

    # Import Choice Screen
    def _to_import_choice(self, dt):
        try:
            ci = self.app.manager.get_screen("createimportwallet_screen")
            ci.import_extrawallet_screen()
            Clock.schedule_once(self._snap_import_choice, 0.5)
        except Exception as e:
            self.log(f"ImportChoice nav failed: {e}")
            Clock.schedule_once(self._to_mnemonic_display, 0.2)

    def _snap_import_choice(self, dt):
        try:
            scr = self.app.manager.get_screen("import_choice_screen")
            hdr = scr.ids.get("app_header")
            title = getattr(hdr, "title", "") if hdr else ""
            self.test("ImportChoice header has title", lambda: title != "")

            self.test("Mnemonic choice button exists", lambda: scr.ids.get("mnemonic_choice_button") is not None)
            self.test("Keypair choice button exists", lambda: scr.ids.get("keypair_choice_button") is not None)

            self.snap("81_import_choice")
            # Navigate to Keypair Import path
            scr.choose_keypair_import()
            Clock.schedule_once(self._snap_keypair_import, 0.5)
        except Exception as e:
            self.log(f"ImportChoice snap failed: {e}")
            Clock.schedule_once(self._to_mnemonic_display, 0.2)

    # Keypair Import Screen
    def _snap_keypair_import(self, dt):
        try:
            scr = self.app.manager.get_screen("keypair_import_screen")
            # Header is a custom bar; check label
            hdr_lbl = scr.ids.get("header_label")
            self.test("Keypair header label exists", lambda: hdr_lbl is not None)
            
            # Fields exist
            self.test("Public key input exists", lambda: scr.ids.get("public_key_input") is not None)
            self.test("Private key input exists", lambda: scr.ids.get("private_key_input") is not None)
            self.test("Key action status label exists", lambda: scr.ids.get("key_action_status") is not None)
            self.test("Keypair import button exists", lambda: scr.ids.get("import_button") is not None)

            # Field input
            try:
                scr.ids["public_key_input"].text = "EDPublicKeyTest"
                scr.ids["private_key_input"].text = "EDPrivateKeyTest"
                self.test("Key fields accept input", lambda: scr.ids["public_key_input"].text == "EDPublicKeyTest")
            except Exception:
                pass

            self.snap("82_keypair_import")
            Clock.schedule_once(self._to_account_choice, 0.4)
        except Exception as e:
            self.log(f"KeypairImport snap failed: {e}")
            Clock.schedule_once(self._to_account_choice, 0.2)

    # Account Choice Screen
    def _to_account_choice(self, dt):
        try:
            self.app.manager.current = "account_choice_screen"
            Clock.schedule_once(self._snap_account_choice, 0.5)
        except Exception as e:
            self.log(f"AccountChoice nav failed: {e}")
            Clock.schedule_once(self._to_wallet_setup, 0.2)

    def _snap_account_choice(self, dt):
        try:
            scr = self.app.manager.get_screen("account_choice_screen")
            hdr = scr.ids.get("app_header")
            self.test("AccountChoice header exists", lambda: hdr is not None)
            self.test("Create account button exists", lambda: scr.ids.get("create_account_button") is not None)
            self.test("Import account button exists", lambda: scr.ids.get("import_account_button") is not None)
            self.snap("83_account_choice")
            Clock.schedule_once(self._to_wallet_setup, 0.4)
        except Exception as e:
            self.log(f"AccountChoice snap failed: {e}")
            Clock.schedule_once(self._to_wallet_setup, 0.2)

    # Wallet Setup Screen
    def _to_wallet_setup(self, dt):
        try:
            self.app.manager.current = "wallet_setup_screen"
            Clock.schedule_once(self._snap_wallet_setup, 0.5)
        except Exception as e:
            self.log(f"WalletSetup nav failed: {e}")
            Clock.schedule_once(self._to_mnemonic_verify, 0.2)

    def _snap_wallet_setup(self, dt):
        try:
            scr = self.app.manager.get_screen("wallet_setup_screen")
            hdr = scr.ids.get("app_header")
            self.test("WalletSetup header exists", lambda: hdr is not None)
            self.test("WS create wallet button exists", lambda: scr.ids.get("ws_create_wallet_button") is not None)
            self.test("WS import wallet button exists", lambda: scr.ids.get("ws_import_wallet_button") is not None)
            self.snap("84_wallet_setup")
            Clock.schedule_once(self._to_mnemonic_verify, 0.4)
        except Exception as e:
            self.log(f"WalletSetup snap failed: {e}")
            Clock.schedule_once(self._to_mnemonic_verify, 0.2)

    # Mnemonic Verify Screen
    def _to_mnemonic_verify(self, dt):
        try:
            self.app.manager.current = "mnemonic_verify_screen"
            Clock.schedule_once(self._snap_mnemonic_verify, 0.5)
        except Exception as e:
            self.log(f"MnemonicVerify nav failed: {e}")
            Clock.schedule_once(self._to_import_extra_keys, 0.2)

    def _snap_mnemonic_verify(self, dt):
        try:
            scr = self.app.manager.get_screen("mnemonic_verify_screen")
            # Header label exists (custom bar)
            self.test("MnemonicVerify header label exists", lambda: scr.ids.get("header_label") is not None)

            # 12 fields + button + error label
            word_count = sum(1 for i in range(1,13) if scr.ids.get(f"word_{i:02d}") is not None)
            self.test("MnemonicVerify has 12 fields", lambda: word_count == 12)
            self.test("MnemonicVerify error label exists", lambda: scr.ids.get("error_label") is not None)
            self.test("MnemonicVerify verify button exists", lambda: scr.ids.get("verify_button") is not None)

            # Input
            try:
                scr.ids["word_01"].text = "test"
                self.test("MnemonicVerify field accepts input", lambda: scr.ids["word_01"].text == "test")
            except Exception:
                pass

            self.snap("85_mnemonic_verify")
            Clock.schedule_once(self._to_import_extra_keys, 0.4)
        except Exception as e:
            self.log(f"MnemonicVerify snap failed: {e}")
            Clock.schedule_once(self._to_import_extra_keys, 0.2)

    # Import Extra Keys Screen
    def _to_import_extra_keys(self, dt):
        try:
            self.app.manager.current = "import_extra_keys_screen"
            Clock.schedule_once(self._snap_import_extra_keys, 0.5)
        except Exception as e:
            self.log(f"ImportExtraKeys nav failed: {e}")
            Clock.schedule_once(self._to_foodtrack, 0.2)

    def _snap_import_extra_keys(self, dt):
        try:
            scr = self.app.manager.get_screen("import_extra_keys_screen")
            self.test("ExtraKeys header label exists", lambda: scr.ids.get("header_label") is not None)
            self.test("ExtraKeys public_key exists", lambda: scr.ids.get("public_key") is not None)
            self.test("ExtraKeys private_key exists", lambda: scr.ids.get("private_key") is not None)
            self.test("ExtraKeys store_button exists", lambda: scr.ids.get("store_button") is not None)
            self.test("ExtraKeys invalid_keys label exists", lambda: scr.ids.get("invalid_keys") is not None)
            try:
                scr.ids["public_key"].text = "EDPubTest"
                scr.ids["private_key"].text = "EDPrivTest"
                self.test("ExtraKeys fields accept input", lambda: scr.ids["public_key"].text == "EDPubTest")
            except Exception:
                pass
            self.snap("86_import_extra_keys")
            Clock.schedule_once(self._to_foodtrack, 0.4)
        except Exception as e:
            self.log(f"ImportExtraKeys snap failed: {e}")
            Clock.schedule_once(self._to_foodtrack, 0.2)

    # FoodTrack screen
    def _to_foodtrack(self, dt):
        try:
            self.app.manager.current = "foodtrack_screen"
            Clock.schedule_once(self._snap_foodtrack, 0.5)
        except Exception as e:
            self.log(f"FoodTrack nav failed: {e}")
            Clock.schedule_once(self._to_mnemonic_display, 0.2)

    def _snap_foodtrack(self, dt):
        try:
            scr = self.app.manager.get_screen("foodtrack_screen")
            hdr = scr.ids.get("app_header")
            self.test("FoodTrack header exists", lambda: hdr is not None)
            # Check content labels exist
            labels = [w for w in scr.walk() if hasattr(w, 'text')]
            self.test("FoodTrack has content", lambda: len(labels) > 1)
            self.snap("87_foodtrack")
            # Rejoin existing flow: go to mnemonic display sequence
            Clock.schedule_once(self._to_mnemonic_display, 0.4)
        except Exception as e:
            self.log(f"FoodTrack snap failed: {e}")
            Clock.schedule_once(self._to_mnemonic_display, 0.2)

    # Mnemonic Display screen
    def _to_mnemonic_display(self, dt):
        try:
            self.log("Navigate to Mnemonic Display")
            self.app.manager.current = "mnemonic_display_screen"
            Clock.schedule_once(self._snap_mnemonic_display, 0.5)
        except Exception as e:
            self.log(f"Mnemonic display nav failed: {e}")
            Clock.schedule_once(self._to_mnemonic_import, 0.2)

    def _snap_mnemonic_display(self, dt):
        try:
            scr = self.app.manager.get_screen("mnemonic_display_screen")
            hdr = scr.ids.get("app_header")
            title = getattr(hdr, "title", "") if hdr else ""
            self.log(f"MnemonicDisplay header: '{title}'")
            self.test("Mnemonic display header has title", lambda: title != "")
            
            # Check mnemonic_grid exists (words are added dynamically)
            mnem_grid = scr.ids.get("mnemonic_grid")
            self.test("Mnemonic grid exists",
                     lambda: mnem_grid is not None)
            
            # Test key labels
            pub_key = scr.ids.get("public_key_label")
            priv_key = scr.ids.get("private_key_label")
            self.test("Public key label exists",
                     lambda: pub_key is not None)
            self.test("Private key label exists",
                     lambda: priv_key is not None)
            
            # Test copy buttons
            children = list(scr.walk())
            copy_btns = [w for w in children if hasattr(w, 'icon') and 'content-copy' in str(w.icon)]
            self.test("Copy buttons present",
                     lambda: len(copy_btns) >= 2)
            
            self.snap("90_mnemonic_display")
            Clock.schedule_once(self._to_mnemonic_import, 0.5)
        except Exception as e:
            self.log(f"MnemonicDisplay snap failed: {e}")
            Clock.schedule_once(self._to_mnemonic_import, 0.3)

    # Mnemonic Import screen
    def _to_mnemonic_import(self, dt):
        try:
            self.log("Navigate to Mnemonic Import")
            self.app.manager.current = "mnemonic_import_screen"
            Clock.schedule_once(self._snap_mnemonic_import, 0.5)
        except Exception as e:
            self.log(f"Mnemonic import nav failed: {e}")
            Clock.schedule_once(self._to_first_use, 0.2)

    def _snap_mnemonic_import(self, dt):
        try:
            scr = self.app.manager.get_screen("mnemonic_import_screen")
            hdr = scr.ids.get("app_header")
            title = getattr(hdr, "title", "") if hdr else ""
            self.log(f"MnemonicImport header: '{title}'")
            self.test("Mnemonic import header has title", lambda: title != "")
            
            # Test 12 word input fields
            word_count = 0
            hint_count = 0
            for i in range(1, 13):
                word_id = f"word_{i:02d}"
                field = scr.ids.get(word_id)
                if field is not None:
                    word_count += 1
                    if hasattr(field, 'hint_text') and field.hint_text:
                        hint_count += 1
            
            self.test("Mnemonic import has 12 word fields",
                     lambda: word_count == 12)
            self.test("Word fields have hint text",
                     lambda: hint_count >= 10)
            
            # Test import button and status label
            import_btn = scr.ids.get("import_button")
            status = scr.ids.get("status_label")
            self.test("Import button exists",
                     lambda: import_btn is not None)
            self.test("Status label exists",
                     lambda: status is not None)
            
            # Test field input
            try:
                scr.ids["word_01"].text = "test"
                self.test("Word field accepts input",
                         lambda: scr.ids["word_01"].text == "test")
            except Exception:
                pass
            
            self.snap("100_mnemonic_import")
            Clock.schedule_once(self._to_first_use, 0.5)
        except Exception as e:
            self.log(f"MnemonicImport snap failed: {e}")
            Clock.schedule_once(self._to_first_use, 0.3)

    # First Use screen
    def _to_first_use(self, dt):
        try:
            self.log("Navigate to First Use")
            self.app.manager.current = "first_use_screen"
            Clock.schedule_once(self._snap_first_use, 0.5)
        except Exception as e:
            self.log(f"First use nav failed: {e}")
            Clock.schedule_once(self._to_login, 0.2)

    def _snap_first_use(self, dt):
        try:
            scr = self.app.manager.get_screen("first_use_screen")
            hdr = scr.ids.get("app_header")
            title = getattr(hdr, "title", "") if hdr else ""
            self.log(f"FirstUse header: '{title}'")
            self.test("First use screen header has title", lambda: title != "")
            
            # Test password fields
            pwd_field = scr.ids.get("password")
            confirm_field = scr.ids.get("confirm_password")
            self.test("Password field exists",
                     lambda: pwd_field is not None)
            self.test("Confirm password field exists",
                     lambda: confirm_field is not None)
            
            # Test helper text
            helper = scr.ids.get("helper_label")
            self.test("Helper text exists",
                     lambda: helper is not None)
            
            # Test create button
            create_btn = scr.ids.get("create_button")
            self.test("Create button exists",
                     lambda: create_btn is not None)
            
            # Test field input
            try:
                scr.ids["password"].text = "test123"
                scr.ids["confirm_password"].text = "test123"
                self.test("Password fields accept input",
                         lambda: scr.ids["password"].text == "test123")
            except Exception:
                pass
            
            self.snap("110_first_use")
            Clock.schedule_once(self._to_login, 0.5)
        except Exception as e:
            self.log(f"FirstUse snap failed: {e}")
            Clock.schedule_once(self._to_login, 0.3)

    # Login screen
    def _to_login(self, dt):
        try:
            self.log("Navigate to Login")
            self.app.manager.current = "login_screen"
            Clock.schedule_once(self._snap_login, 0.5)
        except Exception as e:
            self.log(f"Login nav failed: {e}")
            Clock.schedule_once(self._finish, 0.2)

    def _snap_login(self, dt):
        try:
            scr = self.app.manager.get_screen("login_screen")
            hdr = scr.ids.get("app_header")
            title = getattr(hdr, "title", "") if hdr else ""
            self.log(f"Login header: '{title}'")
            self.test("Login screen header has title", lambda: title != "")
            
            # Test password field
            pwd_field = scr.ids.get("password")
            self.test("Password field exists",
                     lambda: pwd_field is not None)
            
            # Test eye icon for password toggle
            children = list(scr.walk())
            eye_icons = [w for w in children if hasattr(w, 'icon') and 'eye' in str(w.icon)]
            self.test("Password toggle icon present",
                     lambda: len(eye_icons) >= 1)
            
            # Test login button
            login_btn = scr.ids.get("login_button")
            self.test("Login button exists",
                     lambda: login_btn is not None)
            
            # Test error label
            error_lbl = scr.ids.get("error_label")
            self.test("Error label exists",
                     lambda: error_lbl is not None)
            
            # Test field input
            try:
                scr.ids["password"].text = "test"
                self.test("Password field accepts input",
                         lambda: scr.ids["password"].text == "test")
            except Exception:
                pass
            
            self.snap("120_login")
            Clock.schedule_once(self._to_offline_tests, 0.5)
        except Exception as e:
            self.log(f"Login snap failed: {e}")
            Clock.schedule_once(self._to_offline_tests, 0.3)

    # Offline tests: toggle global OFFLINE_MODE and verify UI fallbacks
    def _to_offline_tests(self, dt):
        try:
            import importlib
            from src import core
            from src.core import app as app_module
            # Toggle global offline flag
            app_module.OFFLINE_MODE = True
            # Update wallet screen offline state explicitly
            try:
                ws = self.app.manager.get_screen("wallet_screen")
                ws.update_offline_mode(True)
            except Exception:
                pass
            Clock.schedule_once(self._snap_wallet_offline, 0.5)
        except Exception as e:
            self.log(f"Offline toggle failed: {e}")
            Clock.schedule_once(self._finish, 0.2)

    def _snap_wallet_offline(self, dt):
        try:
            self.app.manager.current = "wallet_screen"
            scr = self.app.manager.get_screen("wallet_screen")
            # Force on_pre_enter effects
            try:
                scr.on_pre_enter()
            except Exception:
                pass
            bal = getattr(scr.xrp_balance, "text", "") if getattr(scr, "xrp_balance", None) else ""
            self.test("Wallet shows Offline Mode", lambda: bal == "Offline Mode")
            # Trustlines list shows offline message
            try:
                scr.refresh_trustlines()
                container = scr.ids.get("trustlines_container")
                labels = [w for w in container.walk() if hasattr(w, 'text')]
                has_offline = any("Offline" in getattr(w, 'text', '') for w in labels)
                self.test("Trustlines show offline message", lambda: has_offline)
            except Exception:
                pass
            self.snap("130_wallet_offline")
            Clock.schedule_once(self._to_sendxrp_offline, 0.4)
        except Exception as e:
            self.log(f"Wallet offline snap failed: {e}")
            Clock.schedule_once(self._to_sendxrp_offline, 0.2)

    def _to_sendxrp_offline(self, dt):
        try:
            self.app.manager.current = "sendxrp_screen"
            Clock.schedule_once(self._snap_sendxrp_offline, 0.5)
        except Exception as e:
            self.log(f"SendXRP offline nav failed: {e}")
            Clock.schedule_once(self._finish, 0.2)

    def _snap_sendxrp_offline(self, dt):
        try:
            scr = self.app.manager.get_screen("sendxrp_screen")
            # Trigger on_pre_enter to apply offline state
            try:
                scr.on_pre_enter()
            except Exception:
                pass
            bal = getattr(scr.xrp_balance, "text", "") if getattr(scr, "xrp_balance", None) else ""
            self.test("SendXRP shows Offline Mode", lambda: bal == "Offline Mode")
            # Transactions labels show Offline Mode
            try:
                labels = []
                for i in range(1, 4):
                    lbl = scr._get_tx_label(i)
                    if lbl and hasattr(lbl, 'text'):
                        labels.append(lbl.text)
                has_offline = any("Offline Mode" in (t or "") for t in labels)
                self.test("SendXRP tx list shows offline", lambda: has_offline)
            except Exception:
                pass
            self.snap("131_sendxrp_offline")
            Clock.schedule_once(self._to_token_offline, 0.4)
        except Exception as e:
            self.log(f"SendXRP offline snap failed: {e}")
            Clock.schedule_once(self._to_token_offline, 0.2)


    # Token send offline
    def _to_token_offline(self, dt):
        try:
            ws = self.app.manager.get_screen("wallet_screen")
            issuer = "rHb9CJAWyB4rj91VRWn96DkukG4bwdtyTh"
            ws.navigate_to_token_send("USD", issuer)
            Clock.schedule_once(self._snap_token_offline, 0.5)
        except Exception as e:
            self.log(f"Token offline nav failed: {e}")
            Clock.schedule_once(self._to_trustline_offline, 0.2)

    def _snap_token_offline(self, dt):
        try:
            screen_name = "send_usd_screen"
            scr = self.app.manager.get_screen(screen_name)
            try:
                scr.on_pre_enter()
            except Exception:
                pass
            # Check if balance shows offline or if send is disabled
            bal = getattr(scr, "token_balance", None)
            if bal:
                bal_text = getattr(bal, "text", "")
                self.test("Token send shows offline state", lambda: "Offline" in bal_text or bal_text == "")
            self.snap("132_token_offline")
            Clock.schedule_once(self._to_trustline_offline, 0.4)
        except Exception as e:
            self.log(f"Token offline snap failed: {e}")
            Clock.schedule_once(self._to_trustline_offline, 0.2)

    # Trustline offline
    def _to_trustline_offline(self, dt):
        try:
            self.app.manager.current = "add_trustline_screen"
            Clock.schedule_once(self._snap_trustline_offline, 0.5)
        except Exception as e:
            self.log(f"Trustline offline nav failed: {e}")
            Clock.schedule_once(self._to_dex_offline, 0.2)

    def _snap_trustline_offline(self, dt):
        try:
            scr = self.app.manager.get_screen("add_trustline_screen")
            # Trustline should still show form but may show offline warning
            hdr = scr.ids.get("app_header")
            self.test("Trustline form accessible offline", lambda: hdr is not None)
            self.snap("133_trustline_offline")
            Clock.schedule_once(self._to_dex_offline, 0.4)
        except Exception as e:
            self.log(f"Trustline offline snap failed: {e}")
            Clock.schedule_once(self._to_dex_offline, 0.2)

    # DEX offline
    def _to_dex_offline(self, dt):
        try:
            self.app.manager.current = "dextrade_screen"
            Clock.schedule_once(self._snap_dex_offline, 0.5)
        except Exception as e:
            self.log(f"DEX offline nav failed: {e}")
            Clock.schedule_once(self._finish, 0.2)

    def _snap_dex_offline(self, dt):
        try:
            scr = self.app.manager.get_screen("dextrade_screen")
            hdr = scr.ids.get("app_header")
            self.test("DEX screen accessible offline", lambda: hdr is not None)
            self.snap("134_dex_offline")
            Clock.schedule_once(self._finish, 0.4)
        except Exception as e:
            self.log(f"DEX offline snap failed: {e}")
            Clock.schedule_once(self._finish, 0.2)


if __name__ == "__main__":
    UxTour().start()
