import os
import json
import time
from typing import Optional, Dict, Any
from pathlib import Path

import requests

from .decentralized.data_service import FoodRepoDataService
from .performance.resource_guard import resource_guard


class FoodRepoClient:
    """FoodRepo API client with local-cache fallback by barcode.

    Tries live API if FOODREPO env vars are set; otherwise searches local cache
    for a matching barcode field among common keys (ean, ean13, barcode, gtin).
    Includes short-term in-memory cache (30s TTL) to suppress identical re-queries.
    """

    def __init__(self):
        self.api_url = os.environ.get("FOODREPO_API_URL")
        self.api_token = os.environ.get("FOODREPO_API_TOKEN")
        self.cache_service = FoodRepoDataService()
        self.cache_service.ensure_loaded()
        self._query_cache: Dict[str, tuple] = {}  # {barcode: (result, timestamp)}
        self._cache_ttl = 30.0  # seconds

    def _headers(self) -> Dict[str, str]:
        hdrs = {"Accept": "application/json"}
        if self.api_token:
            hdrs["Authorization"] = self.api_token
        return hdrs

    def get_by_barcode(self, barcode: str) -> Optional[Dict[str, Any]]:
        # Check in-memory cache first
        now = time.time()
        if barcode in self._query_cache:
            cached_result, cached_time = self._query_cache[barcode]
            if now - cached_time < self._cache_ttl:
                return cached_result
            else:
                del self._query_cache[barcode]  # Expire stale entry
        # Try live API first if configured
        if self.api_url:
            allowed, retry_after = resource_guard.check("foodrepo_lookup")
            if not allowed:
                return {"status": "rate_limited", "retry_after": retry_after}  # type: ignore
            try:
                # Example endpoint: /products?barcode=... (actual endpoint may differ)
                url = f"{self.api_url.rstrip('/')}/products"
                resp = requests.get(url, params={"barcode": barcode}, headers=self._headers(), timeout=15)
                if resp.ok:
                    data = resp.json()
                    # Normalize response; accept dict or list
                    if isinstance(data, dict):
                        # Try common keys
                        if "items" in data and isinstance(data["items"], list) and data["items"]:
                            return data["items"][0]
                        if "data" in data and isinstance(data["data"], list) and data["data"]:
                            return data["data"][0]
                        return data
                    if isinstance(data, list) and data:
                        result = data[0]
                        self._query_cache[barcode] = (result, now)
                        return result
            except Exception:
                pass
        # Fallback to local cache
        try:
            keys = ("ean", "ean13", "barcode", "gtin", "code")
            for row in self.cache_service.data:
                for k in keys:
                    v = row.get(k)
                    if v and str(v).strip() == str(barcode).strip():
                        self._query_cache[barcode] = (row, now)
                        return row
        except Exception:
            pass
        # Cache miss as well to avoid repeated lookups
        self._query_cache[barcode] = (None, now)
        return None


__all__ = ["FoodRepoClient"]
