"""
CalorieDB Manager - Unified Data Layer

Manages the three-tier CalorieDB architecture:
1. Private encrypted data (user-only)
2. Public anonymized data (BigchainDB + IPFS)
3. XRPL-synced data (transaction hashes as base tracking)

XRPL Integration:
- All CalorieDB records linked to XRPL transaction hashes
- Food logs can trigger XRPL payments/memos
- CalorieToken rewards for data contributions
- Pro issuer features sync with XRPL token metadata

Architecture:
    User Action → CalorieDB Record → XRPL Transaction (optional)
                       ↓
              XRPL TX Hash (base tracking ID)
                       ↓
         ┌─────────────┼─────────────┐
         ↓             ↓             ↓
    Private      Public Data    XRPL Ledger
   (Encrypted)   (BigchainDB)   (Immutable)
"""

import os
import json
import shelve
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from pathlib import Path
import hashlib

from xrpl.clients import JsonRpcClient
from xrpl.wallet import Wallet
from xrpl.models.transactions import Payment, Memo
from xrpl.models.amounts import IssuedCurrencyAmount
from xrpl.transaction import safe_sign_and_autofill_transaction, send_reliable_submission
from xrpl.utils import ripple_time_to_datetime, datetime_to_ripple_time

from .decentralized.ipfs_client import get_ipfs_client
from .decentralized.bigchaindb_client import get_bigchaindb_client
from .caloriedb_encryption import CalorieDBEncryption


# CalorieToken issuer on testnet
CALORIE_TOKEN_ISSUER = "rJps2NCFbbSefuSzibzNBSVv5ywpTdCBDX"  # CalorieTest issuer
CALORIE_CURRENCY_CODE = "43616C6F72696554657374000000000000000000"  # "CalorieTest" in hex

# Lipisa token (also on testnet)
LIPISA_TOKEN_ISSUER = "r4dPUdvD5iGyenACWgDF72Un4M9WVNK4if"
LIPISA_CURRENCY_CODE = "4C6970697361000000000000000000000000"  # "Lipisa" in hex


class CalorieDBRecord:
    """
    Base CalorieDB record with XRPL transaction hash as primary tracking ID
    
    All records are anchored to XRPL transactions for immutability and provenance
    """
    
    def __init__(
        self,
        record_type: str,
        xrpl_tx_hash: Optional[str] = None,
        data: Optional[Dict[str, Any]] = None
    ):
        self.record_id = self._generate_record_id()
        self.record_type = record_type  # food_log, product_scan, nutrition_goal, etc.
        self.xrpl_tx_hash = xrpl_tx_hash  # XRPL transaction hash (base tracking)
        self.data = data or {}
        self.created_at = datetime.utcnow().isoformat() + "Z"
        self.updated_at = self.created_at
        self.version = "1.0"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "record_id": self.record_id,
            "record_type": self.record_type,
            "xrpl_tx_hash": self.xrpl_tx_hash,
            "data": self.data,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "version": self.version
        }
    
    @staticmethod
    def _generate_record_id() -> str:
        """Generate unique record ID"""
        timestamp = datetime.utcnow().isoformat()
        random_bytes = os.urandom(8)
        combined = f"{timestamp}{random_bytes.hex()}"
        return hashlib.sha256(combined.encode()).hexdigest()[:16]


class CalorieDBManager:
    """
    Unified CalorieDB Manager
    
    Handles private encrypted data, public data, and XRPL synchronization.
    All records are linked to XRPL transaction hashes for tracking.
    """
    
    def __init__(
        self,
        xrpl_client: JsonRpcClient,
        wallet: Optional[Wallet] = None,
        enable_xrpl_sync: bool = True
    ):
        self.xrpl_client = xrpl_client
        self.wallet = wallet
        self.enable_xrpl_sync = enable_xrpl_sync
        
        # Setup storage
        self.data_dir = Path("data")
        self.data_dir.mkdir(exist_ok=True)
        
        # Private data (encrypted)
        self.private_dir = self.data_dir / "caloriedb_private"
        self.private_dir.mkdir(exist_ok=True)
        
        # Public data (BigchainDB + IPFS)
        self.public_dir = self.data_dir / "caloriedb_public"
        self.public_dir.mkdir(exist_ok=True)
        
        # XRPL sync data
        self.sync_dir = self.data_dir / "caloriedb_sync"
        self.sync_dir.mkdir(exist_ok=True)
        
        # Initialize encryption (if wallet provided)
        self.encryption = None
        if wallet:
            self.encryption = CalorieDBEncryption(wallet.seed)
        
        # Initialize decentralized clients
        self.ipfs = get_ipfs_client()
        self.bigchain = get_bigchaindb_client()
        
        # Load XRPL transaction index
        self.tx_index_file = self.sync_dir / "xrpl_tx_index.json"
        self.tx_index = self._load_tx_index()
        
        # Account state cache (synced from XRPL)
        self.account_state_cache: Dict[str, Dict[str, Any]] = {}
    
    def create_food_log(
        self,
        account_id: str,
        food_items: List[Dict[str, Any]],
        meal_type: str,
        total_calories: float,
        sync_to_xrpl: bool = False,
        reward_tokens: float = 0.0
    ) -> Dict[str, Any]:
        """
        Create food log entry
        
        Args:
            account_id: XRPL account address
            food_items: List of food items consumed
            meal_type: breakfast, lunch, dinner, snack
            total_calories: Total calories consumed
            sync_to_xrpl: Whether to create XRPL transaction
            reward_tokens: CalorieToken reward amount (if contributing to public data)
            
        Returns:
            Food log record with XRPL transaction hash
        """
        # Create food log data
        food_log_data = {
            "account_id": account_id,
            "date": datetime.utcnow().date().isoformat(),
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "meal_type": meal_type,
            "food_items": food_items,
            "total_calories": total_calories,
            "macros": self._calculate_macros(food_items)
        }
        
        # Create XRPL transaction if sync enabled
        xrpl_tx_hash = None
        if sync_to_xrpl and self.wallet:
            xrpl_tx_hash = self._create_food_log_xrpl_tx(
                account_id,
                food_log_data,
                reward_tokens
            )
            food_log_data["xrpl_synced"] = True
        
        # Create CalorieDB record
        record = CalorieDBRecord(
            record_type="food_log",
            xrpl_tx_hash=xrpl_tx_hash,
            data=food_log_data
        )
        
        # Store in private encrypted storage
        self._store_private_record(account_id, record)
        
        # Store anonymized version in public data (if user opted in)
        if self._user_allows_public_contribution(account_id):
            anonymized = self._anonymize_food_log(food_log_data)
            self._store_public_record(record.record_id, anonymized, xrpl_tx_hash)
        
        # Index XRPL transaction
        if xrpl_tx_hash:
            self._index_xrpl_transaction(xrpl_tx_hash, record.record_id, "food_log")
        
        return record.to_dict()
    
    def create_product_scan(
        self,
        account_id: str,
        barcode: str,
        product_data: Dict[str, Any],
        sync_to_xrpl: bool = False
    ) -> Dict[str, Any]:
        """
        Record product scan (barcode lookup)
        
        Links FoodRepo product data to CalorieDB with XRPL transaction tracking
        
        Args:
            account_id: User's XRPL account
            barcode: Product barcode (EAN-13)
            product_data: Product information from FoodRepo
            sync_to_xrpl: Whether to record on XRPL
            
        Returns:
            Product scan record
        """
        scan_data = {
            "account_id": account_id,
            "barcode": barcode,
            "product_name": product_data.get("name"),
            "calories": product_data.get("calories"),
            "nutrients": product_data.get("nutrients", {}),
            "scanned_at": datetime.utcnow().isoformat() + "Z",
            "foodrepo_id": product_data.get("foodrepo_id"),
            "source": "foodrepo"
        }
        
        # Create XRPL transaction if syncing
        xrpl_tx_hash = None
        if sync_to_xrpl and self.wallet:
            xrpl_tx_hash = self._create_scan_xrpl_tx(account_id, scan_data)
            scan_data["xrpl_synced"] = True
        
        # Create record
        record = CalorieDBRecord(
            record_type="product_scan",
            xrpl_tx_hash=xrpl_tx_hash,
            data=scan_data
        )
        
        # Store privately
        self._store_private_record(account_id, record)
        
        # Store in BigchainDB/IPFS for public product database
        self._store_public_product_scan(barcode, product_data, xrpl_tx_hash)
        
        # Index transaction
        if xrpl_tx_hash:
            self._index_xrpl_transaction(xrpl_tx_hash, record.record_id, "product_scan")
        
        return record.to_dict()
    
    def get_food_logs(
        self,
        account_id: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get user's food logs (private encrypted data)
        
        Args:
            account_id: User's XRPL account
            start_date: Filter start date (YYYY-MM-DD)
            end_date: Filter end date (YYYY-MM-DD)
            
        Returns:
            List of food log records
        """
        records = self._get_private_records(account_id, "food_log")
        
        # Filter by date if specified
        if start_date or end_date:
            filtered = []
            for record in records:
                record_date = record["data"].get("date")
                if not record_date:
                    continue
                
                if start_date and record_date < start_date:
                    continue
                if end_date and record_date > end_date:
                    continue
                
                filtered.append(record)
            records = filtered
        
        return records
    
    def get_record_by_xrpl_tx(self, tx_hash: str) -> Optional[Dict[str, Any]]:
        """
        Get CalorieDB record by XRPL transaction hash
        
        This is the primary lookup method - XRPL TX hash is the base tracking ID
        
        Args:
            tx_hash: XRPL transaction hash
            
        Returns:
            CalorieDB record or None
        """
        tx_entry = self.tx_index.get(tx_hash)
        if not tx_entry:
            return None
        
        record_id = tx_entry["record_id"]
        account_id = tx_entry.get("account_id")
        
        if not account_id:
            return None
        
        # Get from private storage
        records = self._get_private_records(account_id)
        for record in records:
            if record["record_id"] == record_id:
                return record
        
        return None
    
    def sync_xrpl_transaction(self, tx_hash: str) -> Dict[str, Any]:
        """
        Sync XRPL transaction to CalorieDB
        
        Monitors XRPL for transactions, enriches with CalorieDB metadata
        
        Args:
            tx_hash: XRPL transaction hash to sync
            
        Returns:
            Sync result
        """
        from xrpl.models.requests import Tx
        
        try:
            # Fetch transaction from XRPL
            tx_request = Tx(transaction=tx_hash)
            response = self.xrpl_client.request(tx_request)
            
            if response.status != "success":
                return {"success": False, "error": "Transaction not found"}
            
            tx_data = response.result
            
            # Extract transaction details
            account = tx_data.get("Account")
            destination = tx_data.get("Destination")
            amount = tx_data.get("Amount")
            memos = tx_data.get("Memos", [])
            
            # Check if this is a CalorieDB transaction (has CalorieDB memo)
            is_caloriedb_tx = False
            caloriedb_data = {}
            
            for memo_wrapper in memos:
                memo = memo_wrapper.get("Memo", {})
                memo_type = self._decode_memo_field(memo.get("MemoType", ""))
                
                if memo_type == "CalorieDB":
                    is_caloriedb_tx = True
                    memo_data = self._decode_memo_field(memo.get("MemoData", ""))
                    try:
                        caloriedb_data = json.loads(memo_data)
                    except:
                        pass
            
            # Store sync data
            sync_data = {
                "xrpl_tx_hash": tx_hash,
                "account": account,
                "destination": destination,
                "amount": amount,
                "is_caloriedb_tx": is_caloriedb_tx,
                "caloriedb_data": caloriedb_data,
                "synced_at": datetime.utcnow().isoformat() + "Z"
            }
            
            sync_file = self.sync_dir / f"{tx_hash}.json"
            sync_file.write_text(json.dumps(sync_data, indent=2))
            
            return {"success": True, "sync_data": sync_data}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_calorie_token_balance(self, account_id: str, use_cache: bool = True) -> float:
        """
        Get user's CalorieToken balance on XRPL
        
        Args:
            account_id: XRPL account address
            use_cache: Use cached balance if available
            
        Returns:
            CalorieToken balance
        """
        # Check cache first
        if use_cache and account_id in self.account_state_cache:
            cached_balance = self.account_state_cache[account_id].get("calorie_balance")
            if cached_balance is not None:
                return cached_balance
        
        from xrpl.models.requests import AccountLines
        
        try:
            request = AccountLines(
                account=account_id,
                ledger_index="validated"
            )
            
            response = self.xrpl_client.request(request)
            
            if response.status != "success":
                return 0.0
            
            lines = response.result.get("lines", [])
            
            # Find CalorieToken trustline
            balance = 0.0
            for line in lines:
                if (line.get("currency") == CALORIE_CURRENCY_CODE and
                    line.get("account") == CALORIE_TOKEN_ISSUER):
                    balance = float(line.get("balance", 0))
                    break
            
            # Update cache
            if account_id not in self.account_state_cache:
                self.account_state_cache[account_id] = {}
            self.account_state_cache[account_id]["calorie_balance"] = balance
            self.account_state_cache[account_id]["last_balance_check"] = datetime.utcnow().isoformat() + "Z"
            
            return balance
            
        except Exception as e:
            print(f"Error getting CalorieToken balance: {e}")
            return 0.0
    
    def reward_calorie_tokens(
        self,
        account_id: str,
        amount: float,
        reason: str
    ) -> Optional[str]:
        """
        Reward user with CalorieTokens for data contributions
        
        Args:
            account_id: User's XRPL account
            amount: CalorieToken amount to reward
            reason: Reason for reward (e.g., "public_data_contribution")
            
        Returns:
            XRPL transaction hash or None
        """
        if not self.wallet:
            return None
        
        try:
            # Create payment transaction
            memo_data = json.dumps({
                "type": "calorie_reward",
                "reason": reason,
                "amount": amount
            })
            
            payment_tx = Payment(
                account=self.wallet.classic_address,
                destination=account_id,
                amount=IssuedCurrencyAmount(
                    currency=CALORIE_CURRENCY_CODE,
                    issuer=CALORIE_TOKEN_ISSUER,
                    value=str(amount)
                ),
                memos=[
                    Memo(
                        memo_type="CalorieDB".encode().hex(),
                        memo_data=memo_data.encode().hex(),
                        memo_format="json".encode().hex()
                    )
                ]
            )
            
            # Sign and submit
            signed = safe_sign_and_autofill_transaction(
                payment_tx,
                self.wallet,
                self.xrpl_client
            )
            result = send_reliable_submission(signed, self.xrpl_client)
            
            return result.result.get("hash")
            
        except Exception as e:
            print(f"Error rewarding CalorieTokens: {e}")
            return None
    
    # Private helper methods
    
    def _create_food_log_xrpl_tx(
        self,
        account_id: str,
        food_log_data: Dict[str, Any],
        reward_tokens: float
    ) -> Optional[str]:
        """Create XRPL transaction for food log"""
        if not self.wallet:
            return None
        
        try:
            # Anonymize data for XRPL memo (no PII)
            memo_data = {
                "type": "food_log",
                "date": food_log_data["date"],
                "meal_type": food_log_data["meal_type"],
                "total_calories": food_log_data["total_calories"],
                "item_count": len(food_log_data["food_items"])
            }
            
            # Self-payment with memo (anchor transaction)
            payment_tx = Payment(
                account=account_id,
                destination=account_id,
                amount="1",  # 1 drop (0.000001 XRP)
                memos=[
                    Memo(
                        memo_type="CalorieDB".encode().hex(),
                        memo_data=json.dumps(memo_data).encode().hex(),
                        memo_format="json".encode().hex()
                    )
                ]
            )
            
            # Sign and submit
            signed = safe_sign_and_autofill_transaction(
                payment_tx,
                self.wallet,
                self.xrpl_client
            )
            result = send_reliable_submission(signed, self.xrpl_client)
            
            tx_hash = result.result.get("hash")
            
            # Reward tokens if applicable
            if reward_tokens > 0:
                self.reward_calorie_tokens(account_id, reward_tokens, "food_log_contribution")
            
            return tx_hash
            
        except Exception as e:
            print(f"Error creating food log XRPL tx: {e}")
            return None
    
    def _create_scan_xrpl_tx(
        self,
        account_id: str,
        scan_data: Dict[str, Any]
    ) -> Optional[str]:
        """Create XRPL transaction for product scan"""
        if not self.wallet:
            return None
        
        try:
            memo_data = {
                "type": "product_scan",
                "barcode": scan_data["barcode"],
                "product_name": scan_data["product_name"],
                "calories": scan_data["calories"]
            }
            
            payment_tx = Payment(
                account=account_id,
                destination=account_id,
                amount="1",
                memos=[
                    Memo(
                        memo_type="CalorieDB".encode().hex(),
                        memo_data=json.dumps(memo_data).encode().hex(),
                        memo_format="json".encode().hex()
                    )
                ]
            )
            
            signed = safe_sign_and_autofill_transaction(
                payment_tx,
                self.wallet,
                self.xrpl_client
            )
            result = send_reliable_submission(signed, self.xrpl_client)
            
            return result.result.get("hash")
            
        except Exception as e:
            print(f"Error creating scan XRPL tx: {e}")
            return None
    
    def _store_private_record(self, account_id: str, record: CalorieDBRecord):
        """Store record in encrypted private storage"""
        if not self.encryption:
            # Fallback to unencrypted if no wallet
            account_file = self.private_dir / f"{account_id}.json"
            records = []
            if account_file.exists():
                records = json.loads(account_file.read_text())
            records.append(record.to_dict())
            account_file.write_text(json.dumps(records, indent=2))
            return
        
        # Encrypted storage
        account_file = self.private_dir / f"{account_id}.enc"
        records = []
        
        if account_file.exists():
            try:
                encrypted_data = account_file.read_bytes()
                records = self.encryption.decrypt(encrypted_data)
            except:
                records = []
        
        records.append(record.to_dict())
        encrypted = self.encryption.encrypt(records)
        account_file.write_bytes(encrypted)
    
    def _get_private_records(
        self,
        account_id: str,
        record_type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get private records for account"""
        # Try encrypted first
        account_file = self.private_dir / f"{account_id}.enc"
        if account_file.exists() and self.encryption:
            try:
                encrypted_data = account_file.read_bytes()
                records = self.encryption.decrypt(encrypted_data)
            except:
                records = []
        else:
            # Fallback to unencrypted
            account_file = self.private_dir / f"{account_id}.json"
            if account_file.exists():
                records = json.loads(account_file.read_text())
            else:
                records = []
        
        # Filter by type if specified
        if record_type:
            records = [r for r in records if r.get("record_type") == record_type]
        
        return records
    
    def _store_public_record(
        self,
        record_id: str,
        data: Dict[str, Any],
        xrpl_tx_hash: Optional[str]
    ):
        """Store anonymized record in public data layer"""
        public_data = {
            "record_id": record_id,
            "xrpl_tx_hash": xrpl_tx_hash,
            "data": data,
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
        
        # Store in IPFS if available
        if self.ipfs.available:
            try:
                data_bytes = json.dumps(public_data, sort_keys=True).encode()
                cid = self.ipfs.add_bytes(data_bytes)
                public_data["ipfs_cid"] = cid
            except:
                pass
        
        # Store in BigchainDB if available
        if self.bigchain.available:
            try:
                metadata = {
                    "type": "caloriedb_public",
                    "record_id": record_id,
                    "xrpl_tx_hash": xrpl_tx_hash
                }
                asset = self.bigchain.create_asset(metadata)
                public_data["bigchaindb_tx_id"] = asset.get("tx_id")
            except:
                pass
        
        # Store locally
        public_file = self.public_dir / f"{record_id}.json"
        public_file.write_text(json.dumps(public_data, indent=2))
    
    def _store_public_product_scan(
        self,
        barcode: str,
        product_data: Dict[str, Any],
        xrpl_tx_hash: Optional[str]
    ):
        """Store product scan in public database"""
        scan_record = {
            "barcode": barcode,
            "product_name": product_data.get("name"),
            "calories": product_data.get("calories"),
            "xrpl_tx_hash": xrpl_tx_hash,
            "scanned_at": datetime.utcnow().isoformat() + "Z"
        }
        
        # Store in public scans file
        scans_file = self.public_dir / "product_scans.json"
        scans = []
        if scans_file.exists():
            scans = json.loads(scans_file.read_text())
        scans.append(scan_record)
        scans_file.write_text(json.dumps(scans, indent=2))
    
    def _index_xrpl_transaction(
        self,
        tx_hash: str,
        record_id: str,
        record_type: str
    ):
        """Index XRPL transaction for lookup"""
        self.tx_index[tx_hash] = {
            "record_id": record_id,
            "record_type": record_type,
            "account_id": self.wallet.classic_address if self.wallet else None,
            "indexed_at": datetime.utcnow().isoformat() + "Z"
        }
        self._save_tx_index()
    
    def _load_tx_index(self) -> Dict[str, Any]:
        """Load XRPL transaction index"""
        if self.tx_index_file.exists():
            return json.loads(self.tx_index_file.read_text())
        return {}
    
    def _save_tx_index(self):
        """Save XRPL transaction index"""
        self.tx_index_file.write_text(json.dumps(self.tx_index, indent=2))
    
    def _anonymize_food_log(self, food_log_data: Dict[str, Any]) -> Dict[str, Any]:
        """Anonymize food log for public data"""
        return {
            "date": food_log_data["date"],
            "meal_type": food_log_data["meal_type"],
            "total_calories": food_log_data["total_calories"],
            "macros": food_log_data["macros"],
            "item_count": len(food_log_data["food_items"])
            # No account_id, no specific food items, no PII
        }
    
    def _calculate_macros(self, food_items: List[Dict[str, Any]]) -> Dict[str, float]:
        """Calculate total macros from food items"""
        total_protein = sum(item.get("protein_g", 0) for item in food_items)
        total_carbs = sum(item.get("carbohydrates_g", 0) for item in food_items)
        total_fat = sum(item.get("fat_g", 0) for item in food_items)
        
        return {
            "protein_g": total_protein,
            "carbohydrates_g": total_carbs,
            "fat_g": total_fat
        }
    
    def _user_allows_public_contribution(self, account_id: str) -> bool:
        """Check if user allows public data contributions"""
        # TODO: Load from user settings
        # For now, default to False (privacy-first)
        return False
    
    def _decode_memo_field(self, hex_str: str) -> str:
        """Decode hex memo field to string"""
        try:
            return bytes.fromhex(hex_str).decode('utf-8')
        except:
            return ""
    
    def get_all_token_balances(self, account_id: str) -> Dict[str, float]:
        """
        Get all token balances for account (CalorieToken, Lipisa, etc.)
        
        Args:
            account_id: XRPL account address
            
        Returns:
            Dictionary of token balances
        """
        from xrpl.models.requests import AccountLines
        
        balances = {}
        
        try:
            request = AccountLines(
                account=account_id,
                ledger_index="validated"
            )
            
            response = self.xrpl_client.request(request)
            
            if response.status != "success":
                return balances
            
            lines = response.result.get("lines", [])
            
            for line in lines:
                currency = line.get("currency", "")
                issuer = line.get("account", "")
                balance = float(line.get("balance", 0))
                
                # Map known tokens
                if currency == CALORIE_CURRENCY_CODE and issuer == CALORIE_TOKEN_ISSUER:
                    balances["CalorieTest"] = balance
                elif currency == LIPISA_CURRENCY_CODE and issuer == LIPISA_TOKEN_ISSUER:
                    balances["Lipisa"] = balance
                else:
                    # Generic token
                    token_name = self._decode_currency_code(currency)
                    balances[token_name] = balance
            
            # Cache balances
            if account_id not in self.account_state_cache:
                self.account_state_cache[account_id] = {}
            self.account_state_cache[account_id]["token_balances"] = balances
            self.account_state_cache[account_id]["last_balance_check"] = datetime.utcnow().isoformat() + "Z"
            
        except Exception as e:
            print(f"Error getting token balances: {e}")
        
        return balances
    
    def get_xrp_balance(self, account_id: str) -> float:
        """
        Get XRP balance for account
        
        Args:
            account_id: XRPL account address
            
        Returns:
            XRP balance
        """
        from xrpl.models.requests import AccountInfo
        
        try:
            request = AccountInfo(
                account=account_id,
                ledger_index="validated"
            )
            
            response = self.xrpl_client.request(request)
            
            if response.status != "success":
                return 0.0
            
            balance_drops = int(response.result["account_data"].get("Balance", 0))
            balance_xrp = balance_drops / 1_000_000  # Convert drops to XRP
            
            # Cache balance
            if account_id not in self.account_state_cache:
                self.account_state_cache[account_id] = {}
            self.account_state_cache[account_id]["xrp_balance"] = balance_xrp
            
            return balance_xrp
            
        except Exception as e:
            print(f"Error getting XRP balance: {e}")
            return 0.0
    
    def get_account_state_summary(self, account_id: str) -> Dict[str, Any]:
        """
        Get complete account state summary (XRP + all tokens + CalorieDB stats)
        
        Combines XRPL state with CalorieDB data for unified view
        
        Args:
            account_id: XRPL account address
            
        Returns:
            Complete account state
        """
        summary = {
            "xrpl_address": account_id,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            
            # XRPL balances
            "xrp_balance": self.get_xrp_balance(account_id),
            "token_balances": self.get_all_token_balances(account_id),
            
            # CalorieDB stats
            "caloriedb": {
                "total_food_logs": 0,
                "total_scans": 0,
                "total_calories_tracked": 0,
                "days_active": 0
            },
            
            # Sync info
            "last_sync": None,
            "sync_source": "live"
        }
        
        # Get CalorieDB records
        food_logs = self.get_food_logs(account_id)
        summary["caloriedb"]["total_food_logs"] = len(food_logs)
        
        product_scans = self._get_private_records(account_id, "product_scan")
        summary["caloriedb"]["total_scans"] = len(product_scans)
        
        # Calculate total calories
        total_calories = sum(
            log["data"].get("total_calories", 0) 
            for log in food_logs
        )
        summary["caloriedb"]["total_calories_tracked"] = total_calories
        
        # Calculate active days
        unique_dates = set(
            log["data"].get("date") 
            for log in food_logs 
            if log["data"].get("date")
        )
        summary["caloriedb"]["days_active"] = len(unique_dates)
        
        return summary
    
    def _decode_currency_code(self, hex_code: str) -> str:
        """Decode currency code from hex"""
        try:
            # Remove trailing zeros
            hex_code = hex_code.rstrip('0')
            if len(hex_code) % 2 != 0:
                hex_code += '0'
            
            # Convert to ASCII
            currency = bytes.fromhex(hex_code).decode('ASCII', errors='ignore')
            return currency.strip('\x00') or hex_code
        except:
            return hex_code


__all__ = ["CalorieDBManager", "CalorieDBRecord"]
