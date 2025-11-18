"""
Enhanced Dialog System for CalorieApp
Provides consistent, user-friendly dialogs with proper styling and helpful actions
"""

from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDButton, MDButtonText
from kivymd.uix.label import MDLabel
from kivy.utils import get_color_from_hex


class DialogType:
    """Dialog type constants"""
    SUCCESS = "success"
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"
    CONFIRM = "confirm"


class EnhancedDialog:
    """
    Enhanced dialog system with consistent styling and UX
    
    Features:
    - Color-coded by type (success=green, error=red, warning=yellow, info=blue)
    - Helpful action buttons with clear labels
    - Optional detailed messages
    - Consistent sizing and spacing
    """
    
    # Color schemes for different dialog types
    COLORS = {
        DialogType.SUCCESS: {
            'bg': get_color_from_hex('#e8f5ed'),
            'title_color': get_color_from_hex('#006b2d'),
            'accent': get_color_from_hex('#008D36'),
        },
        DialogType.ERROR: {
            'bg': get_color_from_hex('#fde7e9'),
            'title_color': get_color_from_hex('#c5221f'),
            'accent': get_color_from_hex('#d93025'),
        },
        DialogType.WARNING: {
            'bg': get_color_from_hex('#fef7e0'),
            'title_color': get_color_from_hex('#b06000'),
            'accent': get_color_from_hex('#f9b233'),
        },
        DialogType.INFO: {
            'bg': get_color_from_hex('#e8f0fe'),
            'title_color': get_color_from_hex('#1967d2'),
            'accent': get_color_from_hex('#505CA9'),
        },
        DialogType.CONFIRM: {
            'bg': get_color_from_hex('#e8f0fe'),
            'title_color': get_color_from_hex('#1967d2'),
            'accent': get_color_from_hex('#505CA9'),
        },
    }
    
    @staticmethod
    def show_success(title: str, message: str, on_dismiss=None):
        """Show success dialog"""
        return EnhancedDialog._show_dialog(
            dialog_type=DialogType.SUCCESS,
            title=title,
            message=message,
            buttons=[("OK", on_dismiss)],
        )
    
    @staticmethod
    def show_error(title: str, message: str, details: str = "", on_dismiss=None):
        """Show error dialog with optional details"""
        full_message = message
        if details:
            full_message = f"{message}\n\n{details}"
        
        return EnhancedDialog._show_dialog(
            dialog_type=DialogType.ERROR,
            title=title,
            message=full_message,
            buttons=[("Close", on_dismiss)],
        )
    
    @staticmethod
    def show_warning(title: str, message: str, on_dismiss=None):
        """Show warning dialog"""
        return EnhancedDialog._show_dialog(
            dialog_type=DialogType.WARNING,
            title=title,
            message=message,
            buttons=[("Understood", on_dismiss)],
        )
    
    @staticmethod
    def show_info(title: str, message: str, on_dismiss=None):
        """Show informational dialog"""
        return EnhancedDialog._show_dialog(
            dialog_type=DialogType.INFO,
            title=title,
            message=message,
            buttons=[("Got it", on_dismiss)],
        )
    
    @staticmethod
    def show_confirm(title: str, message: str, on_confirm=None, on_cancel=None, 
                     confirm_text="Confirm", cancel_text="Cancel"):
        """Show confirmation dialog with yes/no actions"""
        return EnhancedDialog._show_dialog(
            dialog_type=DialogType.CONFIRM,
            title=title,
            message=message,
            buttons=[(cancel_text, on_cancel), (confirm_text, on_confirm)],
        )
    
    @staticmethod
    def _show_dialog(dialog_type: str, title: str, message: str, buttons: list):
        """Internal method to create and show dialog"""
        colors = EnhancedDialog.COLORS.get(dialog_type, EnhancedDialog.COLORS[DialogType.INFO])
        
        # Create button widgets
        button_widgets = []
        for btn_text, btn_callback in buttons:
            button = MDButton(
                style="text" if btn_text in ["Close", "Cancel"] else "filled",
            )
            button.add_widget(MDButtonText(text=btn_text))
            
            def make_handler(callback, dlg_ref):
                def handler(*args):
                    if dlg_ref[0]:
                        dlg_ref[0].dismiss()
                    if callback:
                        callback()
                return handler
            
            # Use list to allow modification in closure
            dialog_ref = [None]
            button.bind(on_release=make_handler(btn_callback, dialog_ref))
            button_widgets.append(button)
        
        # Create dialog
        dialog = MDDialog(
            MDLabel(
                text=message,
                theme_text_color="Custom",
                text_color=colors['title_color'],
            ),
            # ----
            MDDialogHeadlineText(
                text=title,
                theme_text_color="Custom",
                text_color=colors['title_color'],
            ),
            MDDialogButtonContainer(
                *button_widgets,
                spacing="8dp",
            ),
            # ----
        )
        
        # Store reference for button handlers
        dialog_ref[0] = dialog
        
        dialog.open()
        return dialog


# Import KivyMD dialog components
try:
    from kivymd.uix.dialog import (
        MDDialogHeadlineText,
        MDDialogButtonContainer,
    )
except ImportError:
    # Fallback for older KivyMD versions
    class MDDialogHeadlineText(MDLabel):
        pass
    
    class MDDialogButtonContainer:
        def __init__(self, *args, **kwargs):
            pass


# Convenience functions for common use cases
def show_password_error(message: str = "Password is too weak", suggestions=None):
    """Show password validation error with optional suggestions"""
    details = "Password must be at least 8 characters long and contain a mix of letters, numbers, and special characters."
    if suggestions:
        details = "\n".join([f"• {s}" for s in suggestions])
    
    return EnhancedDialog.show_error(
        title="Invalid Password",
        message=message,
        details=details
    )


def show_transaction_error(message: str, details: str = ""):
    """Show transaction error"""
    if not details:
        details = "Please check your balance and network connection, then try again."
    return EnhancedDialog.show_error(
        title="Transaction Failed",
        message=message,
        details=details
    )


def show_validation_error(title: str, details: str = ""):
    """Show validation error"""
    return EnhancedDialog.show_error(
        title=title,
        message=details,
    )


def show_success(title: str, message: str):
    """Show success message"""
    return EnhancedDialog.show_success(
        title=title,
        message=message
    )


def show_error(title: str, message: str):
    """Show error message"""
    return EnhancedDialog.show_error(
        title=title,
        message=message
    )


def confirm_transaction(amount: str, currency: str, destination: str, on_confirm=None, on_cancel=None, warning=None, title: str = "Confirm Transaction"):
    """Show transaction confirmation dialog"""
    message = f"You are about to send:\n\n{amount} {currency}\n\nTo: {destination}\n\n"
    if warning:
        message += warning
    else:
        message += "This action cannot be undone."
    
    return EnhancedDialog.show_confirm(
        title=title,
        message=message,
        on_confirm=on_confirm,
        on_cancel=on_cancel,
        confirm_text="Confirm",
        cancel_text="Cancel",
    )


__all__ = [
    'EnhancedDialog',
    'DialogType',
    'show_password_error',
    'show_transaction_error',
    'show_validation_error',
    'show_success',
    'show_error',
    'confirm_transaction',
]
