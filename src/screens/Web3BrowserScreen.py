import webbrowser
from kivy.uix.screenmanager import Screen
from kivy.utils import platform
from src.utils.ui_feedback import info as ui_info, error as ui_error


class Web3BrowserScreen(Screen):
    """
    Lightweight placeholder for an in-app Web3 browser.
    - On desktop: opens URLs in the system browser
    - On Android: this can be upgraded to use a native WebView via pyjnius
    - WalletConnect (future): wire a session controller here
    """

    def open_url(self, url: str):
        url = (url or "").strip()
        if not url:
            ui_info("Enter a URL")
            return
        if not (url.startswith("http://") or url.startswith("https://")):
            url = "https://" + url
        try:
            if platform == "android" and hasattr(self, "_open_in_android_webview"):
                # Future: implement embedded WebView; for now, external browser
                webbrowser.open(url)
                ui_info("Opening in external browser")
            else:
                webbrowser.open(url)
                ui_info("Opening in external browser")
        except Exception:
            ui_error("Could not open URL")

    def open_xrpl_testnet_tools(self):
        # Handy quick-link for XRPL testnet context
        self.open_url("https://testnet.xrpl.org/")

    # --- Android WebView placeholder (to be implemented) ---
    def _open_in_android_webview(self, url: str):
        """
        Placeholder for a native Android WebView using pyjnius.
        Keep the method signature for future use. Currently unused.
        """
        raise NotImplementedError("Android WebView integration pending")
