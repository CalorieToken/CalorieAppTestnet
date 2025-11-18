import os
from typing import Dict, Any, Optional

try:
    from bigchaindb_driver import BigchainDB  # type: ignore
except Exception:  # pragma: no cover
    BigchainDB = None  # type: ignore


class BigchainDbClient:
    """Minimal BigchainDB asset helper with graceful degradation.

    create_asset() returns a synthetic stub dict if driver unavailable, enabling dry-run tests.
    """

    def __init__(self, api_url: Optional[str] = None):
        self.api_url = api_url or os.environ.get("BIGCHAINDB_API_URL", "")
        self._driver = None
        self._connect()

    @property
    def available(self) -> bool:
        return self._driver is not None

    def _connect(self) -> None:
        if not self.api_url or BigchainDB is None:
            return
        try:
            self._driver = BigchainDB(self.api_url)
        except Exception:
            self._driver = None

    def create_asset(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        driver = self._driver
        if not driver:
            # Return stub asset
            return {
                "status": "stub",
                "tx_id": "stub_tx_id",
                "metadata": metadata,
            }
        # BigchainDB transaction creation (simplified unsigned scenario)
        # In a real flow keys and transfer logic would be applied.
        try:
            prepared = driver.transactions.prepare(
                operation="CREATE",
                signers=["public_key_placeholder"],
                asset={"data": metadata},
                metadata={"ingested": metadata.get("ingested_at")},
            )
            # Without private key we cannot fulfill; this is intentionally stubbed.
            return {
                "status": "prepared",
                "tx_id": prepared.get("id"),
                "metadata": metadata,
            }
        except Exception as e:
            return {"status": "error", "error": str(e), "metadata": metadata}

    def query_assets(self, asset_type: str) -> Any:
        driver = self._driver
        if not driver:
            return []
        try:
            return driver.assets.get(search=asset_type)
        except Exception:
            return []


def get_bigchaindb_client() -> BigchainDbClient:
    return BigchainDbClient()
