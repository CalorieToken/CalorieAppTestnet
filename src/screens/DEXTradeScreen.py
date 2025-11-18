# Kivy libraries for the GUI.
from kivy.uix.screenmanager import Screen
import re
import shelve
from src.utils.performance import debounce
from src.utils.enhanced_dialogs import (
    show_validation_error,
    confirm_transaction,
    show_success,
    show_transaction_error,
)

WALLET_DATA_PATH = "wallet_data"


# DEX Trade Screen
class DEXTradeScreen(Screen):
    def walletscreen(self):
        self.manager.current = "wallet_screen"

    def nftmintscreen(self):
        self.manager.current = "nftmint_screen"

    def createimportwalletscreen(self):
        self.manager.current = "createimportwallet_screen"

    def foodtrackscreen(self):
        self.manager.current = "foodtrack_screen"

    def settingsscreen(self):
        self.manager.current = "settings_screen"

    @debounce(delay=0.5)
    def validate_and_confirm_trade(self):
        """Validate trade inputs and show confirmation dialog."""
        errors = []
        balance_warning = ""

        # Get field references
        base_field = self.ids.base_input
        quote_field = self.ids.quote_input
        amount_field = self.ids.amount_input
        slippage_field = self.ids.slippage_input

        # Clear previous errors
        self._clear_field_error(base_field)
        self._clear_field_error(quote_field)
        self._clear_field_error(amount_field)
        self._clear_field_error(slippage_field)

        # Validate base currency
        base_code = base_field.text.strip()
        if not base_code:
            self._set_field_error(base_field, "Required")
            errors.append("Base currency required")
        elif not self._valid_currency_code(base_code):
            self._set_field_error(base_field, "Invalid code")
            errors.append("Invalid base currency code")

        # Validate quote currency
        quote_code = quote_field.text.strip()
        if not quote_code:
            self._set_field_error(quote_field, "Required")
            errors.append("Quote currency required")
        elif not self._valid_currency_code(quote_code):
            self._set_field_error(quote_field, "Invalid code")
            errors.append("Invalid quote currency code")
        elif base_code and quote_code.upper() == base_code.upper():
            self._set_field_error(quote_field, "Must differ from base")
            errors.append("Quote and base currencies must differ")

        # Validate amount
        amount_text = amount_field.text.strip()
        if not amount_text:
            self._set_field_error(amount_field, "Required")
            errors.append("Amount required")
        else:
            try:
                amount = float(amount_text)
                if amount <= 0:
                    self._set_field_error(amount_field, "Must be positive")
                    errors.append("Amount must be positive")
                else:
                    # Check balance if available
                    try:
                        with shelve.open(WALLET_DATA_PATH) as db:
                            balances = db.get("balances", {})
                            base_balance = float(balances.get(base_code, 0))
                            if amount > base_balance > 0:
                                balance_warning = f"Amount exceeds recorded {base_code} balance ({base_balance})"
                    except Exception:
                        pass
            except ValueError:
                self._set_field_error(amount_field, "Enter positive number")
                errors.append("Amount must be a valid number")

        # Validate slippage (optional, default 1%)
        slippage_text = slippage_field.text.strip() or "1"
        try:
            slippage = float(slippage_text)
            if slippage < 0 or slippage > 10:
                self._set_field_error(slippage_field, "0-10% allowed")
                errors.append("Slippage must be between 0-10%")
        except ValueError:
            self._set_field_error(slippage_field, "Enter number 0-10")
            errors.append("Slippage must be a valid number")

        # Show consolidated errors
        if errors:
            show_validation_error(
                "Trade Validation Failed",
                "\n".join([f"• {e}" for e in errors])
            )
            return

        # Show confirmation dialog
        confirm_transaction(
            amount=str(amount),
            currency=f"{base_code}/{quote_code}",
            destination="DEX Pool",
            warning=f"{balance_warning}\nMax slippage: {slippage}%" if balance_warning else f"Max slippage: {slippage}%",
            on_confirm=lambda: self.perform_trade(base_code, quote_code, amount, slippage),
            on_cancel=lambda: None,
            title="Confirm Trade"
        )

    def perform_trade(self, base_code, quote_code, amount, slippage):
        """Execute the trade (placeholder implementation)."""
        try:
            # Placeholder: simulate trade execution
            # In real implementation, this would interact with XRPL DEX
            quote_received = amount * 2.0  # Demo: 1 base = 2 quote
            quote_with_slippage = quote_received * (1 - slippage / 100)

            show_success(
                "Trade Executed",
                f"Traded {amount} {base_code} for {quote_with_slippage:.6f} {quote_code}\n\nThis is a demo execution."
            )

            # Clear form
            self._clear_input_text()

        except Exception as e:
            show_transaction_error(f"Trade failed: {str(e)}")

    def _valid_currency_code(self, code):
        """Check if currency code is valid (3-12 char alphanumeric or 40-char hex)."""
        return bool(re.fullmatch(r"[A-Za-z0-9]{3,12}", code)) or bool(
            re.fullmatch(r"[0-9A-Fa-f]{40}", code)
        )

    def _set_field_error(self, field, message):
        """Set error state on a field."""
        field.error = True
        field.helper_text = message

    def _clear_field_error(self, field):
        """Clear error state on a field."""
        field.error = False
        field.helper_text = ""

    def _clear_input_text(self):
        """Clear all input fields."""
        self.ids.base_input.text = ""
        self.ids.quote_input.text = ""
        self.ids.amount_input.text = ""
        self.ids.slippage_input.text = ""
