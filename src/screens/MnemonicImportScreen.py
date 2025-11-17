"""
Dedicated Mnemonic Import Screen for importing wallets from 12-word phrases
Provides full-screen experience for mnemonic import with validation
"""

import os
import sys

from kivy.clock import Clock
from kivy.core.clipboard import Clipboard
from kivy.uix.screenmanager import Screen

from src.utils.dialogs import show_error_dialog, show_info_dialog
from src.utils.storage_paths import WALLET_DATA_PATH

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.utils.mnemonic_manager import mnemonic_manager, recover_wallet_from_mnemonic


class MnemonicImportScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.is_first_account = True
        self.return_screen = "wallet_screen"

    def set_context(self, is_first_account=True, return_screen="wallet_screen"):
        """Set the context for this screen."""
        self.is_first_account = is_first_account
        self.return_screen = return_screen

        # Clear previous input if screen has IDs
        if hasattr(self, "ids"):
            for i in range(1, 13):
                field_id = f"word_{i:02d}"
                if field_id in self.ids:
                    self.ids[field_id].text = ""

    def paste_from_clipboard(self):
        """Paste mnemonic from clipboard."""
        try:
            clipboard_content = Clipboard.paste()
            if clipboard_content:
                self.ids.mnemonic_input.text = clipboard_content
                self.ids.paste_status.text = "📋 Pasted from clipboard"
                Clock.schedule_once(lambda dt: setattr(self.ids.paste_status, "text", ""), 3)
            else:
                self.ids.paste_status.text = "📋 Clipboard is empty"
                Clock.schedule_once(lambda dt: setattr(self.ids.paste_status, "text", ""), 3)
        except Exception as e:
            self.ids.paste_status.text = f"📋 Paste error: {e}"
            Clock.schedule_once(lambda dt: setattr(self.ids.paste_status, "text", ""), 3)

    def import_wallet(self):
        """Import wallet from mnemonic phrase."""
        try:
            # Collect words from individual input fields
            entered_words = []
            for i in range(1, 13):
                field_id = f"word_{i:02d}"
                input_field = self.ids.get(field_id)
                if input_field:
                    word = input_field.text.strip().lower()
                    entered_words.append(word)

            # Check word count
            if len(entered_words) != 12:
                self.show_error("Missing Words", "Please fill in all 12 word fields.")
                return

            # Check if any words are empty
            if any(not word for word in entered_words):
                self.show_error("Empty Fields", "Please fill in all 12 word fields.")
                return

            # Validate mnemonic
            if not mnemonic_manager.validate_mnemonic(entered_words):
                self.show_error(
                    "Invalid Mnemonic",
                    "Invalid mnemonic phrase. Please check the words and try again.",
                )
                return

            # Generate wallet from mnemonic
            wallet = recover_wallet_from_mnemonic(entered_words)

            # Check if this account already exists
            import shelve

            with shelve.open(WALLET_DATA_PATH) as wallet_data:
                accounts = wallet_data.get("accounts", [])

                # Check if address already exists
                for account in accounts:
                    if account.get("address") == wallet.classic_address:
                        self.show_error(
                            "Duplicate Account",
                            f"This account is already imported!\n\nAccount: {wallet.classic_address[:10]}...{wallet.classic_address[-10:]}",
                        )
                        return

            # Navigate to account naming screen
            naming_screen = self.manager.get_screen("account_naming_screen")
            naming_screen.set_account_data(
                wallet=wallet,
                mnemonic=entered_words,  # Save mnemonic with the account
                is_first_account=self.is_first_account,
                return_screen=self.return_screen,
            )
            self.manager.current = "account_naming_screen"

        except Exception as e:
            self.show_error("Import Failed", f"Import error: {str(e)}")

    def show_import_error(self, message):
        """Show import error message."""
        self.ids.import_status.text = f"❌ {message}"
        self.ids.import_status.theme_text_color = "Error"

    def show_import_success(self):
        """Show import success and wallet details."""
        if not self.imported_wallet:
            return

        # Update status
        self.ids.import_status.text = "✅ Wallet imported successfully!"
        self.ids.import_status.theme_text_color = "Primary"

        # Show wallet details
        self.ids.wallet_address.text = f"Address: {self.imported_wallet.classic_address}"
        self.ids.private_key_display.text = f"Private Key: {self.imported_wallet.private_key}"
        self.ids.public_key_display.text = f"Public Key: {self.imported_wallet.public_key}"

        # Show wallet details container
        self.ids.wallet_details.opacity = 1
        self.ids.wallet_details.disabled = False

        # Enable continue button
        self.ids.continue_button.disabled = False
        self.ids.continue_button.text = "✅ Save This Wallet"

    def copy_address(self):
        """Copy wallet address to clipboard."""
        if self.imported_wallet:
            Clipboard.copy(self.imported_wallet.classic_address)
            self.ids.copy_status.text = "📋 Address copied!"
            Clock.schedule_once(lambda dt: setattr(self.ids.copy_status, "text", ""), 3)

    def copy_private_key(self):
        """Copy private key to clipboard."""
        if self.imported_wallet:
            Clipboard.copy(self.imported_wallet.private_key)
            self.ids.copy_status.text = "📋 Private key copied!"
            Clock.schedule_once(lambda dt: setattr(self.ids.copy_status, "text", ""), 3)

    def continue_to_save(self):
        """Continue to save the imported wallet."""
        if not self.imported_wallet:
            self.show_import_error("No wallet imported yet.")
            return

        # Navigate back to target screen and set the keys
        if self.target_screen and hasattr(self.manager, "get_screen"):
            target_screen_obj = self.manager.get_screen(self.target_screen)

            # Set the keys in the target screen
            if hasattr(target_screen_obj, "ids"):
                if hasattr(target_screen_obj.ids, "private_key"):
                    target_screen_obj.ids.private_key.text = self.imported_wallet.private_key
                if hasattr(target_screen_obj.ids, "public_key"):
                    target_screen_obj.ids.public_key.text = self.imported_wallet.public_key

            # Navigate back
            self.manager.current = self.target_screen

            # Call store_keys method if available
            if hasattr(target_screen_obj, "store_keys"):
                Clock.schedule_once(lambda dt: target_screen_obj.store_keys(), 0.5)

    def go_back(self):
        """Go back to target screen."""
        if self.target_screen:
            self.manager.current = self.target_screen
        else:
            self.manager.current = "importkeys_screen"

    def clear_form(self):
        """Clear the import form."""
        self.ids.mnemonic_input.text = ""
        self.ids.passphrase_input.text = ""
        self.ids.import_status.text = ""
        self.ids.paste_status.text = ""
        self.ids.copy_status.text = ""

        # Hide wallet details
        self.ids.wallet_details.opacity = 0
        self.ids.wallet_details.disabled = True

        # Reset continue button
        self.ids.continue_button.disabled = True
        self.ids.continue_button.text = "Import Wallet"

        # Clear wallet data
        self.imported_wallet = None

    def validate_input_realtime(self):
        """Validate mnemonic input in real-time."""
        mnemonic_input = self.ids.get("mnemonic_input")
        status_label = self.ids.get("status_label")
        import_button = self.ids.get("import_button")

        if not mnemonic_input:
            return

        mnemonic_text = mnemonic_input.text.strip()

        if not mnemonic_text:
            if status_label:
                status_label.text = "Enter 12 words to continue..."
            if import_button:
                import_button.disabled = True
            return

        words = mnemonic_manager.parse_mnemonic_input(mnemonic_text)
        word_count = len(words)

        if word_count == 12:
            if status_label:
                status_label.text = f"✅ {word_count} words - Ready to import"
            if import_button:
                import_button.disabled = False
        elif word_count < 12:
            if status_label:
                status_label.text = f"📝 {word_count}/12 words"
            if import_button:
                import_button.disabled = True
        else:
            if status_label:
                status_label.text = f"⚠️ {word_count} words (need exactly 12)"
            if import_button:
                import_button.disabled = True

    def show_error(self, title, message):
        """Show error dialog."""
        show_error_dialog(title, message)

    def go_back(self):
        """Go back to import choice screen."""
        # Clear input fields
        for i in range(1, 13):
            field_id = f"word_{i:02d}"
            if hasattr(self.ids, field_id):
                getattr(self.ids, field_id).text = ""
        self.manager.current = "import_choice_screen"

    # Auto-distribute pasted 12 words when user pastes them into the first field
    def on_first_word_text(self, text: str):
        """If the first input receives a multi-word paste, split across all 12 fields.
        Schedule work for the next frame so the original paste doesn't remain in field 1.
        Avoid recursion by guarding with a transient flag.
        """
        try:
            # Prevent recursive calls when we programmatically set field texts
            if getattr(self, "_distributing_words", False):
                return

            if not text:
                return

            # Heuristic: trigger distribution only if more than one token likely present
            multi = (" " in text) or ("\n" in text) or ("\t" in text)
            if not multi:
                return

            # Parse tokens
            words = []
            if mnemonic_manager is not None:
                words = mnemonic_manager.parse_mnemonic_input(text)
            if not words:
                # Fallback simple split
                import re

                words = re.findall(r"[A-Za-z]+", text.lower())

            # Only proceed if we have at least 2 words; cap at 12
            if len(words) < 2:
                return

            words = [w.lower() for w in words][:12]

            # Begin guarded section and schedule the distribution for the next frame.
            self._distributing_words = True

            def _do_distribute(dt):
                try:
                    for i in range(1, 13):
                        field = self.ids.get(f"word_{i:02d}")
                        if field is not None:
                            field.text = words[i - 1] if i - 1 < len(words) else ""
                finally:
                    # Release flag after distribution
                    self._distributing_words = False

                # Focus the next field after the last filled one
                next_index = min(len(words) + 1, 12)
                for j in range(next_index, 13):
                    field = self.ids.get(f"word_{j:02d}")
                    if field is not None and not field.text:
                        try:
                            field.focus = True
                        except Exception:
                            pass
                        break

            # Schedule distribution after the paste completes
            Clock.schedule_once(_do_distribute, 0)
        except Exception:
            # Fail-safe: ignore distribution errors silently to not block user input
            pass
