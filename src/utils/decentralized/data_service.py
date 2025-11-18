import os
import csv
import json
from typing import List, Dict, Optional
from pathlib import Path

from .ipfs_client import get_ipfs_client
from .bigchaindb_client import get_bigchaindb_client

DATA_DIR = Path("data")
INDEX_FILE = DATA_DIR / "foodrepo_index.json"
CACHE_FILE = DATA_DIR / "foodrepo_cache.json"


class FoodRepoDataService:
    """High-level loader for FoodRepo nutritional dataset with decentralized mode support.

    In decentralized mode (DECENTRALIZED_MODE=1):
    - Reads index file for IPFS CID + expected sha256
    - Verifies integrity if possible
    - Loads JSON cache into memory
    Fallback: if index missing or verification fails, disabled flag set.
    """

    def __init__(self):
        self.enabled = os.environ.get("DECENTRALIZED_MODE") == "1"
        self.ipfs = get_ipfs_client() if self.enabled else None
        self.bigchain = get_bigchaindb_client() if self.enabled else None
        self.data: List[Dict] = []
        self._loaded = False

    def ensure_loaded(self) -> None:
        if self._loaded:
            return
        if not self.enabled:
            return
        if not INDEX_FILE.exists() or not CACHE_FILE.exists():
            return
        try:
            index = json.loads(INDEX_FILE.read_text())
            cid = index.get("ipfs_cid")
            expected_sha256 = index.get("content_sha256")
            # Integrity check (best effort)
            if cid and expected_sha256 and self.ipfs and self.ipfs.available:
                verified = self.ipfs.verify(cid, expected_sha256)
                if not verified:
                    # Abort load on mismatch
                    return
            # Load cached JSON
            self.data = json.loads(CACHE_FILE.read_text())
            self._loaded = True
        except Exception:
            pass

    def find_by_name(self, name_substring: str) -> List[Dict]:
        if not self._loaded:
            self.ensure_loaded()
        if not self._loaded:
            return []
        name_substring_lower = name_substring.lower()
        return [row for row in self.data if name_substring_lower in str(row.get("name", "")).lower()]

    def sample(self, n: int = 5) -> List[Dict]:
        if not self._loaded:
            self.ensure_loaded()
        return self.data[:n]

    def status(self) -> Dict[str, Optional[str]]:
        return {
            "enabled": str(self.enabled),
            "loaded": str(self._loaded),
            "count": str(len(self.data)),
            "ipfs_available": str(getattr(self.ipfs, "available", False) if self.ipfs else False),
            "bigchaindb_available": str(getattr(self.bigchain, "available", False) if self.bigchain else False),
        }


__all__ = ["FoodRepoDataService"]
