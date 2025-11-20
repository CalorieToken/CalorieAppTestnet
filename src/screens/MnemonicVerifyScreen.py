"""
Mnemonic Verification Screen - User must enter 12 words to verify they wrote them down
"""

from kivy.clock import Clock
from kivy.uix.screenmanager import Screen

from src.utils.dialogs import show_error_dialog, show_info_dialog

# Helper for parsing user-pasted mnemonic text (handles numbering and whitespace)
try:
    from src.utils.mnemonic_manager import mnemonic_manager
except Exception:
    mnemonic_manager = None


class MnemonicVerifyScreen(Screen):
    """
    Screen where user must enter their 12-word mnemonic to verify they saved it.
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.wallet = None
        self.mnemonic = None
        self.is_first_account = True
        self.return_screen = "wallet_screen"
        self.created_new_wallet = False

    def set_verification_data(
        self,
        wallet,
        mnemonic,
        is_first_account=True,
        return_screen="wallet_screen",
        created_new_wallet=False,
    ):
        """
        Set the data for verification

        Args:
            wallet: XRPL Wallet object
            mnemonic: List of 12 words to verify against
            is_first_account: True if this is the first account
            return_screen: Where to go after completion
        """
        self.wallet = wallet
        self.mnemonic = mnemonic
        self.is_first_account = is_first_account
        self.return_screen = return_screen
        self.created_new_wallet = created_new_wallet

    def verify_mnemonic(self):
        """Verify the entered mnemonic matches"""
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

        # Check if words match
        correct_words = [word.lower() for word in self.mnemonic]

        if entered_words == correct_words:
            # Success! Go to account naming
            self.show_success()
        else:
            # Find which words are wrong
            wrong_positions = []
            for i, (entered, correct) in enumerate(zip(entered_words, correct_words), 1):
                if entered != correct:
                    wrong_positions.append(i)

            if wrong_positions:
                positions_str = ", ".join(map(str, wrong_positions))

                # Show error in label instead of dialog
                error_label = self.ids.get("error_label")
                if error_label:
                    error_label.text = f"❌ Words {positions_str} are incorrect"
                else:
                    self.show_error(
                        "Verification Failed",
                        (
                            f"The words at positions {positions_str} don't match.\n\n"
                            "Please check your written backup and try again."
                        ),
                    )

    def show_success(self):
        """Show success and navigate to naming screen"""
        # Show brief success dialog then auto-continue
        from kivy.clock import Clock
        
        dialog = show_info_dialog(
            title="✅ Verified!",
            text="Your mnemonic phrase is correct!\n\nNow let's give this account a name.",
        )
        
        # Auto-dismiss after 1.5 seconds and continue
        def _auto_continue(dt):
            try:
                if dialog:
                    dialog.dismiss()
            except Exception:
                pass
            # Continue to naming screen
            Clock.schedule_once(lambda dt: self.continue_to_naming(None), 0.1)
        
        Clock.schedule_once(_auto_continue, 1.5)

    def continue_to_naming(self, dialog):
        """Continue to account naming screen"""
        if dialog:
            dialog.dismiss()

        # Clear input fields
        for i in range(1, 13):
            field_id = f"word_{i:02d}"
            input_field = self.ids.get(field_id)
            if input_field:
                input_field.text = ""

        # Clear error label
        error_label = self.ids.get("error_label")
        if error_label:
            error_label.text = ""

        # Navigate to naming screen
        naming_screen = self.manager.get_screen("account_naming_screen")
        naming_screen.set_account_data(
            wallet=self.wallet,
            mnemonic=self.mnemonic,
            is_first_account=self.is_first_account,
            return_screen=self.return_screen,
            created_new_wallet=self.created_new_wallet,
        )
        self.manager.current = "account_naming_screen"

    def show_error(self, title, message):
        """Show error dialog"""
        show_error_dialog(title=title, text=message)

    def go_back_to_display(self):
        """Go back to mnemonic display screen to review"""
        # Clear input fields
        for i in range(1, 13):
            field_id = f"word_{i:02d}"
            input_field = self.ids.get(field_id)
            if input_field:
                input_field.text = ""

        # Clear error label
        error_label = self.ids.get("error_label")
        if error_label:
            error_label.text = ""

        # Go back to display screen
        self.manager.current = "mnemonic_display_screen"

    def go_back(self):
        """Same as go_back_to_display for consistency"""
        self.go_back_to_display()

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
