from kivymd.uix.button import MDButton, MDButtonText
from kivymd.uix.dialog import (
    MDDialog,
    MDDialogButtonContainer,
    MDDialogContentContainer,
    MDDialogHeadlineText,
    MDDialogSupportingText,
)

# Centralized dialog helpers for consistent styling across the app
# KivyMD 2.0 compatible

DEFAULT_BG = (0.74, 0.78, 0.88, 1)  # #bfc6e0
PRIMARY_TEXT = (0.00, 0.55, 0.21, 1)  # #008D36
ACCENT = (0.98, 0.70, 0.20, 1)  # #f9b233


def show_error_dialog(title: str = "Error", text: str = "", on_close=None):
    """Show an error dialog with OK button"""

    def _dismiss_and_close(_):
        dialog.dismiss()
        if callable(on_close):
            on_close()

    dialog = MDDialog(md_bg_color=DEFAULT_BG, size_hint=(0.9, None))
    dialog.add_widget(MDDialogHeadlineText(text=title))
    dialog.add_widget(MDDialogSupportingText(text=text))

    btn_container = MDDialogButtonContainer()
    ok_btn = MDButton(style="text", on_release=_dismiss_and_close)
    ok_btn.add_widget(MDButtonText(text="OK", text_color=PRIMARY_TEXT))
    btn_container.add_widget(ok_btn)
    dialog.add_widget(btn_container)

    dialog.open()
    return dialog


def show_info_dialog(title: str = "Info", text: str = "", on_close=None):
    """Show an info dialog - same as error dialog"""
    return show_error_dialog(title=title, text=text, on_close=on_close)


def show_confirm_dialog(
    title: str = "Confirm",
    text: str = "",
    *,
    content=None,
    confirm_text: str = "OK",
    cancel_text: str = "Cancel",
    secondary_text: str | None = None,
    on_confirm=None,
    on_secondary=None,
    on_cancel=None,
    dismiss_on_confirm: bool = True,
):
    """Show a confirmation dialog with cancel and confirm buttons"""

    def _on_confirm(_):
        if dismiss_on_confirm:
            dialog.dismiss()
        if callable(on_confirm):
            on_confirm()

    def _on_cancel(_):
        dialog.dismiss()
        if callable(on_cancel):
            on_cancel()

    def _on_secondary(_):
        dialog.dismiss()
        if callable(on_secondary):
            on_secondary()

    dialog = MDDialog(md_bg_color=DEFAULT_BG, size_hint=(0.9, None))
    dialog.add_widget(MDDialogHeadlineText(text=title))

    if content is None:
        dialog.add_widget(MDDialogSupportingText(text=text))
    else:
        content_container = MDDialogContentContainer()
        content_container.add_widget(content)
        dialog.add_widget(content_container)

    # Build buttons
    btn_container = MDDialogButtonContainer()

    cancel_btn = MDButton(style="text", on_release=_on_cancel)
    cancel_btn.add_widget(MDButtonText(text=cancel_text, text_color=PRIMARY_TEXT))
    btn_container.add_widget(cancel_btn)

    if secondary_text:
        sec_btn = MDButton(style="text", on_release=_on_secondary)
        sec_btn.add_widget(MDButtonText(text=secondary_text, text_color=PRIMARY_TEXT))
        btn_container.add_widget(sec_btn)

    confirm_btn = MDButton(style="text", on_release=_on_confirm)
    confirm_btn.add_widget(MDButtonText(text=confirm_text, text_color=PRIMARY_TEXT))
    btn_container.add_widget(confirm_btn)

    dialog.add_widget(btn_container)
    dialog.open()
    return dialog
