import json
import hashlib
import time
from pathlib import Path
from typing import Dict, Any

LINKS_FILE = Path("data") / "calorie_links.json"
LINKS_FILE.parent.mkdir(exist_ok=True)


def hash_calorie_record(record: Dict[str, Any]) -> str:
    canonical = json.dumps(record, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(canonical).hexdigest()


def build_calorie_memo(record_hash: str) -> Dict[str, Any]:
    # MemoType 'calhash' -> hex: 63616C686173
    memo_type_hex = "63616C686173"
    memo_data_hex = record_hash.encode("utf-8").hex()
    return {"Memo": {"MemoType": memo_type_hex, "MemoData": memo_data_hex}}


def _load_links():
    if LINKS_FILE.exists():
        try:
            data = json.loads(LINKS_FILE.read_text())
            if isinstance(data, list):
                return data
        except Exception:
            pass
    return []


def store_link(record_hash: str, tx_hash: str, record_type: str = "unknown") -> None:
    links = _load_links()
    links.append({
        "tx_hash": tx_hash,
        "record_hash": record_hash,
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "type": record_type,
    })
    LINKS_FILE.write_text(json.dumps(links, ensure_ascii=False, indent=2))


def find_by_record_hash(record_hash: str):
    return [l for l in _load_links() if l.get("record_hash") == record_hash]


def find_by_tx_hash(tx_hash: str):
    return [l for l in _load_links() if l.get("tx_hash") == tx_hash]


__all__ = [
    "hash_calorie_record",
    "build_calorie_memo",
    "store_link",
    "find_by_record_hash",
    "find_by_tx_hash",
]
