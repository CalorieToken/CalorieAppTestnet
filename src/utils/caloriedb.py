import json
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional

from .decentralized.ipfs_client import get_ipfs_client
from .decentralized.bigchaindb_client import get_bigchaindb_client
from .performance.resource_guard import resource_guard

DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)
SCANS_FILE = DATA_DIR / "caloriedb_scans.json"


def _sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def record_scan(product: Dict[str, Any], barcode: str) -> Dict[str, Any]:
    """Persist a pilot CalorieDB record for a scanned product.

    - Serialize product to canonical JSON bytes
    - Attempt IPFS add -> cid
    - Create BigchainDB asset stub with metadata
    - Append entry to caloriedb_scans.json
    """
    raw = json.dumps(product, sort_keys=True, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    sha = _sha256_bytes(raw)

    ipfs = get_ipfs_client()
    cid: Optional[str] = None
    if ipfs.available:
        allowed_ipfs, retry_after_ipfs = resource_guard.check("ipfs_add")
        if allowed_ipfs:
            try:
                cid = ipfs.add_bytes(raw)
            except Exception:
                cid = None
        else:
            cid = None  # Defer adding; treat as non-critical

    bigchain = get_bigchaindb_client()
    allowed_bc, retry_after_bc = resource_guard.check("bigchaindb_create")
    meta = {
        "type": "calorie_scan",
        "barcode": barcode,
        "content_sha256": sha,
        "ipfs_cid": cid,
        "ingested_at": datetime.utcnow().isoformat() + "Z",
        "product_name": str(product.get("name") or product.get("product_name") or ""),
    }
    asset = bigchain.create_asset(meta) if allowed_bc else {"status": "rate_limited", "tx_id": None}

    entry = {
        "barcode": barcode,
        "product_name": meta["product_name"],
        "ipfs_cid": cid,
        "content_sha256": sha,
        "bigchaindb_status": asset.get("status"),
        "bigchaindb_tx_id": asset.get("tx_id"),
        "timestamp": meta["ingested_at"],
    }

    existing = []
    if SCANS_FILE.exists():
        try:
            data = json.loads(SCANS_FILE.read_text())
            if isinstance(data, list):
                existing = data
        except Exception:
            existing = []
    existing.append(entry)
    SCANS_FILE.write_text(json.dumps(existing, ensure_ascii=False, indent=2))
    return entry


__all__ = ["record_scan"]
