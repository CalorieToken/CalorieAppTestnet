"""
Dedicated Mnemonic Display Screen for showing generated 12-word phrases
Provides full-screen experience for mnemonic backup and verification
"""

import os
import sys

from kivy.clock import Clock
from kivy.core.clipboard import Clipboard
from kivy.uix.screenmanager import Screen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.textfield import MDTextField

from src.utils.dialogs import show_confirm_dialog

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.utils.mnemonic_manager import mnemonic_manager


class MnemonicDisplayScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.wallet = None
        self.mnemonic = None
        self.source_screen = None
        self.is_first_account = True
        self.return_screen = "wallet_screen"
        self.verification_step = False
        self.created_new_wallet = False

    def setup_mnemonic_display(
        self,
        wallet,
        mnemonic,
        source_screen="create_wallet_screen",
        is_first_account=True,
        return_screen="wallet_screen",
        created_new_wallet=False,
    ):
        """Setup the screen with wallet and mnemonic data."""
        self.wallet = wallet
        self.mnemonic = mnemonic
        self.source_screen = source_screen
        self.is_first_account = is_first_account
        self.return_screen = return_screen
        self.created_new_wallet = created_new_wallet

        # Update UI elements
        self.update_display()

    def update_display(self):
        """Update the display with current mnemonic and wallet info."""
        if not self.wallet or not self.mnemonic:
            return

        # Populate the mnemonic grid with numbered words
        grid = self.ids.get("mnemonic_grid")
        if not grid:
            return

        # Clear previous widgets
        grid.clear_widgets()

        from kivymd.uix.label import MDLabel

        for i, word in enumerate(self.mnemonic, start=1):
            index_label = MDLabel(text=f"{i:02d}", halign="right", size_hint_y=None, height="30dp")
            word_label = MDLabel(text=word, halign="left", size_hint_y=None, height="30dp")
            grid.add_widget(index_label)
            grid.add_widget(word_label)

        # Update key displays if present
        if "public_key_display" in self.ids:
            self.ids.public_key_display.text = self.wallet.public_key
        if "private_key_display" in self.ids:
            self.ids.private_key_display.text = self.wallet.private_key

        # Additional wallet info and step indicators are not used in current KV

    def copy_mnemonic(self):
        """Copy mnemonic to clipboard."""
        if self.mnemonic:
            mnemonic_text = " ".join(self.mnemonic)
            secure_copy(mnemonic_text, clear_after=30.0)

            # Optional: show confirmation if label exists
            if "copy_status" in self.ids:
                self.ids.copy_status.text = "📋 Copied to clipboard!"
                Clock.schedule_once(lambda dt: setattr(self.ids.copy_status, "text", ""), 3)

    def copy_public_key(self):
        """Copy public key to clipboard."""
        if self.wallet and getattr(self.wallet, "public_key", None):
            Clipboard.copy(self.wallet.public_key)

    def copy_private_key(self):
        """Copy private key to clipboard."""
        if self.wallet and getattr(self.wallet, "private_key", None):
            secure_copy(self.wallet.private_key, clear_after=30.0)

    def copy_keypair(self):
        """Copy both public and private keys as a pair to clipboard."""
        if (
            self.wallet
            and getattr(self.wallet, "public_key", None)
            and getattr(self.wallet, "private_key", None)
        ):
            keypair_text = (
                f"Public Key: {self.wallet.public_key}\nPrivate Key: {self.wallet.private_key}"
            )
            secure_copy(keypair_text, clear_after=30.0)

    def continue_process(self):
        """Handle continue button - either start verification or complete process."""
        # Current KV uses a direct "I Wrote It Down" button to verify
        self.verify_mnemonic()

    def verify_mnemonic(self):
        """Navigate to verification screen where user must enter the 12 words."""
        # Navigate to verification screen
        verify_screen = self.manager.get_screen("mnemonic_verify_screen")
        verify_screen.set_verification_data(
            wallet=self.wallet,
            mnemonic=self.mnemonic,
            is_first_account=self.is_first_account,
            return_screen=self.return_screen,
            created_new_wallet=self.created_new_wallet,
        )
        self.manager.current = "mnemonic_verify_screen"

    def show_verification_error(self, message):
        """Show verification error message."""
        if "verification_status" in self.ids:
            self.ids.verification_status.text = f"❌ {message}"
            self.ids.verification_status.theme_text_color = "Error"
            Clock.schedule_once(lambda dt: setattr(self.ids.verification_status, "text", ""), 5)

    def verification_success(self):
        """Handle successful verification."""
        if "verification_status" in self.ids:
            self.ids.verification_status.text = "✅ Verification successful!"
            self.ids.verification_status.theme_text_color = "Primary"
            # Wait a moment then proceed
            Clock.schedule_once(lambda dt: self.complete_wallet_creation(), 1.5)
        else:
            self.complete_wallet_creation()

    def complete_wallet_creation(self):
        """Complete the wallet creation process."""
        # Navigate back to source screen and trigger wallet storage
        if self.source_screen and hasattr(self.manager, "get_screen"):
            source_screen_obj = self.manager.get_screen(self.source_screen)

            # Set the keys in the source screen
            if hasattr(source_screen_obj, "ids"):
                if hasattr(source_screen_obj.ids, "private_key"):
                    source_screen_obj.ids.private_key.text = self.wallet.private_key
                if hasattr(source_screen_obj.ids, "public_key"):
                    source_screen_obj.ids.public_key.text = self.wallet.public_key

            # Navigate back and trigger storage
            self.manager.current = self.source_screen

            # Call store_keys method if available
            if hasattr(source_screen_obj, "store_keys"):
                Clock.schedule_once(lambda dt: source_screen_obj.store_keys(), 0.5)

    def go_back(self):
        """Go back to previous screen."""
        if self.source_screen:
            self.manager.current = self.source_screen
        else:
            self.manager.current = "create_wallet_screen"

    def skip_verification(self):
        """Skip verification (with warning)."""
        # Show warning dialog
        show_confirm_dialog(
            title="⚠️ Skip Verification?",
            text=(
                "Are you sure you want to skip verification?\n\n"
                "Without verification, you might lose access to your wallet if you wrote down the words incorrectly."
            ),
            confirm_text="⚠️ Skip (Not Recommended)",
            cancel_text="📝 Go Back to Verify",
            on_confirm=lambda: self.force_complete(None),
            dismiss_on_confirm=True,
        )

    def force_complete(self, dialog):
        """Force complete without verification."""
        if dialog:
            dialog.dismiss()
        self.complete_wallet_creation()
