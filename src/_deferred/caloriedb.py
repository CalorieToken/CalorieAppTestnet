"""Deferred CalorieDB integration layer. DEFERRED.

Original prototype handled decentralized storage (IPFS + BigchainDB).
Extracted from active code path until indexing & sync phase is scheduled.
"""

from typing import Dict, Any
from src.core.feature_flags import ENABLE_CALORIE_DB
from src.utils.ui_feedback import info as ui_info


def record_scan(product: Dict[str, Any], barcode: str):  # DEFERRED stub
    if not ENABLE_CALORIE_DB:
        ui_info("CalorieDB sync deferred")
        return {"status": "deferred", "barcode": barcode}
    # Future: implement full decentralized ingest
    ui_info("CalorieDB ingest not implemented")
    return {"status": "pending", "barcode": barcode}

__all__ = ["record_scan"]
