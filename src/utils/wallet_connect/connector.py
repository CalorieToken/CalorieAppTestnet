from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any


class WalletConnector(ABC):
    """
    Abstract wallet connector interface.

    Implementations should provide a way to create a session with a wallet
    and request signatures for payloads. This API is transport-agnostic so we
    can plug in XRPL (Xaman/XUMM deeplinks) or EVM (WalletConnect v2) later.
    """

    @abstractmethod
    def connect(self) -> bool:
        """Initialize a session. Returns True if connection flow started."""
        raise NotImplementedError

    @abstractmethod
    def disconnect(self) -> None:
        """Terminate the session and cleanup resources."""
        raise NotImplementedError

    @abstractmethod
    def is_connected(self) -> bool:
        """Whether there is an active session with a wallet."""
        raise NotImplementedError

    @abstractmethod
    def get_session_info(self) -> Dict[str, Any]:
        """Return basic session metadata (addresses, network, etc.)."""
        raise NotImplementedError

    @abstractmethod
    def request_sign(self, payload: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Request a signature for a provided payload.
        Returns a result dict or None if declined/failed.
        """
        raise NotImplementedError
