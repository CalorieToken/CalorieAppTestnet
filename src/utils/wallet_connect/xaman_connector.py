from __future__ import annotations
from typing import Optional, Dict, Any
from kivy.utils import platform
import webbrowser
import os

from ..ui_feedback import success as ui_success, info as ui_info, error as ui_error

from .connector import WalletConnector


class XamanConnector(WalletConnector):
    """
    XRPL wallet connector stub using Xaman (XUMM) deeplinks/xApp flows.

    This is a testnet-friendly placeholder that opens the Xaman app or website
    to handle a sign request. A real implementation would use the XUMM SDK/API
    with app credentials to create payloads server-side and poll for results.
    """

    def __init__(self):
        self._connected = False
        self._address = None
        self._network = "XRPL Testnet"

    def connect(self) -> bool:
        if self._connected:
            return True
        self._connected = True
        ui_success("Wallet connected")
        return True

    def disconnect(self) -> None:
        self._connected = False
        self._address = None
        ui_info("Wallet disconnected")

    def is_connected(self) -> bool:
        return self._connected

    def get_session_info(self) -> Dict[str, Any]:
        return {
            "network": self._network,
            "address": self._address,
            "connected": self._connected,
            "wallet": "Xaman (stub)",
        }

    def request_sign(self, payload: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Open a generic Xaman sign deeplink with XRPL Testnet context.
        This is non-functional without a backend to create a payload, but
        demonstrates the UX and keeps users on the right path.
        """
        if not self._connected:
            ui_error("Sign failed: wallet not connected")
            return {"status": "error", "reason": "not_connected"}
        try:
            ux_mode = os.environ.get("UX_TOUR_MODE") == "1" or os.environ.get("CI") == "true"
            deeplink = "https://xumm.app/detect/user"
            if not ux_mode:
                webbrowser.open(deeplink)
                ui_info("Opening wallet for signing")
            else:
                ui_info("Simulated sign (UX/CI mode)")
            return {"status": "sent", "deeplink": deeplink, "simulated": ux_mode}
        except Exception as e:
            ui_error(f"Sign initiation failed: {e}")
            return {"status": "error", "reason": str(e)}
