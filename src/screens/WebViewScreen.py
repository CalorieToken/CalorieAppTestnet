from kivy.uix.screenmanager import Screen
from kivy.properties import BooleanProperty, StringProperty
from kivy.utils import platform


class WebViewScreen(Screen):
    """Feature-flagged WebView placeholder.

    Behavior:
    - If WEBVIEW_ENABLED=1 and running on Android -> active native slot.
    - If WEBVIEW_ENABLED=1 and NOT Android -> simulated (for desktop dev & UX tour).
    - Else -> disabled.
    """

    webview_available = BooleanProperty(False)  # True for active or simulated
    webview_mode = StringProperty("disabled")  # active | simulated | disabled

    def on_pre_enter(self):
        from os import environ
        enabled = environ.get("WEBVIEW_ENABLED", "0").lower() in ("1", "true", "yes")
        if enabled:
            if platform == "android":
                self.webview_available = True
                self.webview_mode = "active"
            else:
                # Simulated mode for development environments
                self.webview_available = True
                self.webview_mode = "simulated"
        else:
            self.webview_available = False
            self.webview_mode = "disabled"
