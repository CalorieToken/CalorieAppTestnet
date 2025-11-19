from kivy.uix.screenmanager import Screen
from src.core.feature_flags import ENABLE_WEB3_BROWSER
from src.utils.ui_feedback import info as ui_info


class Web3BrowserScreen(Screen):  # DEFERRED
    """Deferred Web3 browser screen.

    Currently disabled (ENABLE_WEB3_BROWSER=False). When enabled this will
    provide in-app browsing / WalletConnect session handling.
    """

    def open_url(self, url: str):  # Guarded no-op when disabled
        if not ENABLE_WEB3_BROWSER:
            ui_info("Web3 browser feature deferred")
            return
        ui_info("Web3 browser not yet implemented")
