"""
Pro Account System for CalorieAppTestnet

Manages account tiers (Regular vs Pro) and Pro feature access.
Pro accounts have access to advanced issuer features for token management.
"""

import hashlib
import secrets
import time
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import shelve


class AccountTier:
    """Account tier enumeration"""
    REGULAR = "regular"
    PRO = "pro"


class ProLicense:
    """Represents a Pro account license"""
    
    def __init__(self, license_key: str, account_id: str, expiry_date: Optional[datetime] = None):
        self.license_key = license_key
        self.account_id = account_id
        self.created_at = datetime.now()
        self.expiry_date = expiry_date  # None = lifetime license
        self.is_active = True
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage"""
        return {
            'license_key': self.license_key,
            'account_id': self.account_id,
            'created_at': self.created_at.isoformat(),
            'expiry_date': self.expiry_date.isoformat() if self.expiry_date else None,
            'is_active': self.is_active
        }
    
    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'ProLicense':
        """Create from dictionary"""
        license = ProLicense(
            license_key=data['license_key'],
            account_id=data['account_id'],
            expiry_date=datetime.fromisoformat(data['expiry_date']) if data.get('expiry_date') else None
        )
        license.created_at = datetime.fromisoformat(data['created_at'])
        license.is_active = data.get('is_active', True)
        return license
    
    def is_valid(self) -> bool:
        """Check if license is still valid"""
        if not self.is_active:
            return False
        if self.expiry_date and datetime.now() > self.expiry_date:
            return False
        return True


class ProAccountManager:
    """Manages Pro account licensing and feature access"""
    
    def __init__(self, db_path: str = "wallet_data"):
        self.db_path = db_path
        self._ensure_pro_db_initialized()
    
    def _ensure_pro_db_initialized(self):
        """Ensure Pro account database structures exist"""
        with shelve.open(self.db_path) as db:
            if "pro_licenses" not in db:
                db["pro_licenses"] = {}
            if "pro_features_enabled" not in db:
                db["pro_features_enabled"] = True  # Global Pro features toggle
    
    def generate_license_key(self, account_id: str, duration_days: Optional[int] = None) -> str:
        """
        Generate a Pro license key
        
        Args:
            account_id: The XRPL address or account identifier
            duration_days: License duration in days (None = lifetime)
        
        Returns:
            License key string
        """
        # Generate secure random component
        random_component = secrets.token_hex(16)
        
        # Create hash from account_id + timestamp + random
        hash_input = f"{account_id}{time.time()}{random_component}".encode()
        hash_digest = hashlib.sha256(hash_input).hexdigest()[:16]
        
        # Format: PRO-XXXX-XXXX-XXXX-XXXX
        key_parts = [hash_digest[i:i+4].upper() for i in range(0, 16, 4)]
        license_key = f"PRO-{'-'.join(key_parts)}"
        
        # Store license
        expiry_date = None
        if duration_days:
            expiry_date = datetime.now() + timedelta(days=duration_days)
        
        license = ProLicense(license_key, account_id, expiry_date)
        self.save_license(license)
        
        return license_key
    
    def save_license(self, license: ProLicense):
        """Save a Pro license to database"""
        with shelve.open(self.db_path) as db:
            licenses = db.get("pro_licenses", {})
            licenses[license.account_id] = license.to_dict()
            db["pro_licenses"] = licenses
    
    def activate_license(self, account_id: str, license_key: str) -> bool:
        """
        Activate a Pro license for an account
        
        Args:
            account_id: The XRPL address or account identifier
            license_key: The Pro license key
        
        Returns:
            True if activation successful, False otherwise
        """
        with shelve.open(self.db_path) as db:
            licenses = db.get("pro_licenses", {})
            
            # Check if license exists
            if account_id in licenses:
                stored_license = ProLicense.from_dict(licenses[account_id])
                
                # Verify license key matches
                if stored_license.license_key == license_key:
                    if stored_license.is_valid():
                        # Already activated and valid
                        return True
                    else:
                        # Expired or inactive
                        return False
            
            # License not found - this shouldn't happen in normal flow
            # but we can create it if the key format is valid
            if license_key.startswith("PRO-") and len(license_key) == 23:
                license = ProLicense(license_key, account_id, expiry_date=None)
                licenses[account_id] = license.to_dict()
                db["pro_licenses"] = licenses
                return True
            
            return False
    
    def is_pro_account(self, account_id: str) -> bool:
        """
        Check if an account has active Pro status
        
        Args:
            account_id: The XRPL address or account identifier
        
        Returns:
            True if Pro account, False if Regular
        """
        try:
            with shelve.open(self.db_path) as db:
                licenses = db.get("pro_licenses", {})
                
                if account_id not in licenses:
                    return False
                
                license_data = licenses[account_id]
                license = ProLicense.from_dict(license_data)
                
                return license.is_valid()
        except Exception:
            return False
    
    def get_account_tier(self, account_id: str) -> str:
        """
        Get account tier (Regular or Pro)
        
        Args:
            account_id: The XRPL address or account identifier
        
        Returns:
            AccountTier.REGULAR or AccountTier.PRO
        """
        return AccountTier.PRO if self.is_pro_account(account_id) else AccountTier.REGULAR
    
    def get_license_info(self, account_id: str) -> Optional[Dict[str, Any]]:
        """Get license information for an account"""
        try:
            with shelve.open(self.db_path) as db:
                licenses = db.get("pro_licenses", {})
                
                if account_id not in licenses:
                    return None
                
                license_data = licenses[account_id]
                license = ProLicense.from_dict(license_data)
                
                info = {
                    'tier': self.get_account_tier(account_id),
                    'license_key': license.license_key,
                    'created_at': license.created_at,
                    'expiry_date': license.expiry_date,
                    'is_active': license.is_active,
                    'is_valid': license.is_valid(),
                    'days_remaining': None
                }
                
                if license.expiry_date:
                    days_remaining = (license.expiry_date - datetime.now()).days
                    info['days_remaining'] = max(0, days_remaining)
                
                return info
        except Exception:
            return None
    
    def revoke_license(self, account_id: str) -> bool:
        """Revoke a Pro license (admin only)"""
        try:
            with shelve.open(self.db_path) as db:
                licenses = db.get("pro_licenses", {})
                
                if account_id in licenses:
                    license_data = licenses[account_id]
                    license = ProLicense.from_dict(license_data)
                    license.is_active = False
                    licenses[account_id] = license.to_dict()
                    db["pro_licenses"] = licenses
                    return True
                
                return False
        except Exception:
            return False
    
    def list_all_pro_accounts(self) -> Dict[str, Dict[str, Any]]:
        """List all Pro accounts (admin only)"""
        try:
            with shelve.open(self.db_path) as db:
                licenses = db.get("pro_licenses", {})
                
                result = {}
                for account_id, license_data in licenses.items():
                    license = ProLicense.from_dict(license_data)
                    result[account_id] = {
                        'license_key': license.license_key,
                        'created_at': license.created_at,
                        'expiry_date': license.expiry_date,
                        'is_active': license.is_active,
                        'is_valid': license.is_valid()
                    }
                
                return result
        except Exception:
            return {}


class ProFeatureGate:
    """
    Decorator and utility for gating Pro features
    """
    
    def __init__(self, pro_manager: ProAccountManager):
        self.pro_manager = pro_manager
    
    def require_pro(self, feature_name: str = "Pro feature"):
        """
        Decorator to require Pro account for a method
        
        Usage:
            @pro_gate.require_pro("Token Issuance")
            def issue_token(self, account_id, ...):
                ...
        """
        def decorator(func):
            def wrapper(self, account_id, *args, **kwargs):
                if not self.pro_manager.is_pro_account(account_id):
                    raise PermissionError(
                        f"{feature_name} requires a Pro account. "
                        f"Current tier: {self.pro_manager.get_account_tier(account_id)}"
                    )
                return func(self, account_id, *args, **kwargs)
            return wrapper
        return decorator
    
    def check_feature_access(self, account_id: str, feature_name: str) -> tuple[bool, str]:
        """
        Check if account has access to a feature
        
        Returns:
            (has_access, message)
        """
        is_pro = self.pro_manager.is_pro_account(account_id)
        tier = self.pro_manager.get_account_tier(account_id)
        
        if is_pro:
            return True, f"✅ {feature_name} available (Pro account)"
        else:
            return False, f"🔒 {feature_name} requires Pro account (Current: {tier})"


# Feature flags for Pro accounts
PRO_FEATURES = {
    'token_issuance': {
        'name': 'Token Issuance',
        'description': 'Issue custom tokens on XRPL',
        'requires_pro': True
    },
    'advanced_trustlines': {
        'name': 'Advanced Trustline Management',
        'description': 'Manage trustlines with advanced settings',
        'requires_pro': True
    },
    'batch_operations': {
        'name': 'Batch Operations',
        'description': 'Execute multiple operations in batch',
        'requires_pro': True
    },
    'issuer_controls': {
        'name': 'Issuer Controls',
        'description': 'Token freeze, blacklist, clawback features',
        'requires_pro': True
    },
    'analytics': {
        'name': 'Advanced Analytics',
        'description': 'Detailed transaction and token analytics',
        'requires_pro': True
    }
}


def get_feature_list(tier: str) -> list:
    """Get list of available features for account tier"""
    if tier == AccountTier.PRO:
        return list(PRO_FEATURES.keys())
    else:
        # Regular accounts get basic features only
        return []


# Export main classes
__all__ = [
    'AccountTier',
    'ProLicense',
    'ProAccountManager',
    'ProFeatureGate',
    'PRO_FEATURES',
    'get_feature_list'
]
