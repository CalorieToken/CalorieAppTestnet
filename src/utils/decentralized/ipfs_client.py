import os
import hashlib
from typing import Optional, Tuple

try:
    import ipfshttpclient  # type: ignore
except Exception:  # pragma: no cover
    ipfshttpclient = None  # Fallback when dependency not installed


class IpfsClient:
    """Thin wrapper around ipfshttpclient with graceful degradation.

    Methods raise RuntimeError if IPFS is unavailable and decentralized mode is requested.
    """

    def __init__(self, api_url: Optional[str] = None):
        self.api_url = api_url or os.environ.get("IPFS_API_URL", "http://127.0.0.1:5001")
        self._client = None
        self._connect()

    @property
    def available(self) -> bool:
        return self._client is not None

    def _connect(self) -> None:
        if ipfshttpclient is None:
            return
        try:
            # ipfshttpclient expects multiaddr style; support http(s) fallback
            if self.api_url.startswith("http"):
                # Strip protocol for ipfshttpclient connect pattern if needed
                addr = self.api_url.replace("http://", "/ip4/127.0.0.1/tcp/").replace("https://", "/ip4/127.0.0.1/tcp/")
                # Simplify: try raw provided URL first
                try:
                    self._client = ipfshttpclient.connect(self.api_url)
                    return
                except Exception:
                    self._client = ipfshttpclient.connect()
            else:
                self._client = ipfshttpclient.connect(self.api_url)
        except Exception:
            self._client = None

    def add_file(self, path: str) -> str:
        client = self._client
        if not client:
            raise RuntimeError("IPFS client not available")
        res = client.add(path)
        # ipfshttpclient returns dict with 'Hash'
        if isinstance(res, dict):
            return res.get("Hash") or res.get("Cid") or ""
        if isinstance(res, list) and res:
            return res[0].get("Hash", "")
        return ""

    def add_bytes(self, data: bytes, filename: str = "data.bin") -> str:
        client = self._client
        if not client:
            raise RuntimeError("IPFS client not available")
        res = client.add_bytes(data)
        return res  # string CID

    def cat(self, cid: str) -> bytes:
        client = self._client
        if not client:
            raise RuntimeError("IPFS client not available")
        return client.cat(cid)

    @staticmethod
    def sha256_bytes(data: bytes) -> str:
        return hashlib.sha256(data).hexdigest()

    def verify(self, cid: str, expected_sha256: str) -> bool:
        try:
            blob = self.cat(cid)
            return self.sha256_bytes(blob) == expected_sha256
        except Exception:
            return False


def get_ipfs_client() -> IpfsClient:
    return IpfsClient()
