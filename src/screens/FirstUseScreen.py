# Kivy libraries for the GUI.
# Encryption libraries for password and key encryption.
import logging
import re

from kivy.uix.screenmanager import Screen

logging.basicConfig(level=logging.WARNING)
import shelve
import string

import bcrypt

from src.utils.storage_paths import WALLET_DATA_PATH
from src.utils.enhanced_dialogs import show_password_error


class PasswordStrength:
    """Password strength validator with detailed feedback"""
    
    @staticmethod
    def calculate_strength(password: str) -> dict:
        """
        Calculate password strength and return detailed feedback
        
        Returns:
            dict with keys: strength (0-100), issues (list), suggestions (list)
        """
        strength = 0
        issues = []
        suggestions = []
        
        # Length check
        if len(password) >= 12:
            strength += 30
        elif len(password) >= 8:
            strength += 20
        else:
            issues.append("Too short")
            suggestions.append("Use at least 8 characters (12+ recommended)")
        
        # Character variety checks
        if re.search(r'[a-z]', password):
            strength += 15
        else:
            issues.append("No lowercase letters")
            suggestions.append("Add lowercase letters (a-z)")
        
        if re.search(r'[A-Z]', password):
            strength += 15
        else:
            issues.append("No uppercase letters")
            suggestions.append("Add uppercase letters (A-Z)")
        
        if re.search(r'\d', password):
            strength += 15
        else:
            issues.append("No numbers")
            suggestions.append("Add numbers (0-9)")
        
        if re.search(r'[!@#$%^&*()_+\-=\[\]{};:\'",.<>?/\\|`~]', password):
            strength += 15
        else:
            issues.append("No special characters")
            suggestions.append("Add special characters (!@#$%^&*)")
        
        # Bonus for extra length
        if len(password) >= 16:
            strength += 10
        
        return {
            'strength': min(strength, 100),
            'issues': issues,
            'suggestions': suggestions,
            'is_strong': strength >= 70,
        }
    
    @staticmethod
    def get_strength_label(strength: int) -> str:
        """Get human-readable strength label"""
        if strength >= 90:
            return "Excellent"
        elif strength >= 70:
            return "Strong"
        elif strength >= 50:
            return "Moderate"
        elif strength >= 30:
            return "Weak"
        else:
            return "Very Weak"


# First Use Screen
class FirstUseScreen(Screen):
    
    def on_password_text(self, text):
        """Real-time password strength feedback"""
        if not text:
            self.ids.password_input.helper_text = "Enter a strong password"
            return
        
        result = PasswordStrength.calculate_strength(text)
        strength = result['strength']
        label = PasswordStrength.get_strength_label(strength)
        
        # Update helper text with strength
        if result['is_strong']:
            self.ids.password_input.helper_text = f"✓ {label} password"
            self.ids.password_input.error = False
        else:
            issues_text = ", ".join(result['issues'][:2])  # Show first 2 issues
            self.ids.password_input.helper_text = f"{label}: {issues_text}"
            self.ids.password_input.error = True
    
    def create_password(self):
        password = self.ids.password_input.text
        confirm_password = self.ids.confirm_password_input.text

        # Validate password strength
        result = PasswordStrength.calculate_strength(password)
        
        if not result['is_strong']:
            # Show detailed error with suggestions
            suggestions_text = "\n".join(f"• {s}" for s in result['suggestions'])
            show_password_error(
                f"Password is {PasswordStrength.get_strength_label(result['strength']).lower()}.\n\n"
                f"Suggestions:\n{suggestions_text}"
            )
            return

        # Check if password and confirmation password match
        if password != confirm_password:
            self.ids.confirm_password_input.helper_text = "Passwords do not match"
            self.ids.confirm_password_input.error = True
            return

        # Show progress dialog
        from src.utils.enhanced_dialogs import show_progress_dialog
        progress_dialog = show_progress_dialog(
            title="Creating Password",
            message="Encrypting your password...\nThis may take a moment."
        )

        # Move encryption to background thread
        from threading import Thread
        from kivy.clock import Clock

        def _encrypt_password():
            try:
                # Hash the password using bcrypt (CPU intensive)
                hashed_password = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())

                # Generate encryption key
                from cryptography.fernet import Fernet
                encryption_key = Fernet.generate_key()

                # Schedule UI update on main thread
                Clock.schedule_once(
                    lambda dt: self._on_password_encrypted(hashed_password, encryption_key, progress_dialog),
                    0
                )
            except Exception as e:
                Clock.schedule_once(
                    lambda dt: self._on_password_error(str(e), progress_dialog),
                    0
                )

        Thread(target=_encrypt_password, daemon=True).start()

    def _on_password_encrypted(self, hashed_password, encryption_key, progress_dialog):
        """Called on main thread after password encryption completes"""
        try:
            # Dismiss progress dialog
            if progress_dialog:
                progress_dialog.dismiss()

            # Store encrypted data
            self.wallet_data = shelve.open(WALLET_DATA_PATH)
            self.wallet_data["password"] = hashed_password
            self.wallet_data["encryption_key"] = encryption_key
            self.wallet_data.close()

            # Navigate to account choice screen
            account_choice_screen = self.manager.get_screen("account_choice_screen")
            account_choice_screen.set_context(is_first_account=True, return_screen="wallet_screen")
            self.manager.current = "account_choice_screen"
        except Exception as e:
            if progress_dialog:
                progress_dialog.dismiss()
            show_password_error(f"Failed to save password: {str(e)}")

    def _on_password_error(self, error_msg, progress_dialog):
        """Called on main thread if password encryption fails"""
        if progress_dialog:
            progress_dialog.dismiss()
        show_password_error(f"Password creation failed: {error_msg}")
