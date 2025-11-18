"""
CalorieDB Configuration Profiles

Pre-configured deployment profiles for different use cases.
Choose the profile that best fits your needs.

Profiles:
1. Pure P2P (Zero Servers) - 100% free, no maintenance
2. With IPFS (Free) - Add decentralized storage
3. Full Decentralized - IPFS + BigchainDB
4. Production Mainnet - Real XRPL with optional services
5. Enterprise/Research - Full stack with analytics
"""

import os
from enum import Enum
from typing import Dict, Any, Optional
from pathlib import Path


class DeploymentProfile(Enum):
    """Deployment profile options"""
    PURE_P2P = "pure_p2p"                    # Profile 1: Zero servers
    WITH_IPFS = "with_ipfs"                  # Profile 2: Add IPFS
    FULL_DECENTRALIZED = "full_decentralized"  # Profile 3: IPFS + BigchainDB
    PRODUCTION_MAINNET = "production_mainnet"  # Profile 4: Real XRPL
    ENTERPRISE = "enterprise"                # Profile 5: Full analytics stack


class CalorieDBConfig:
    """
    CalorieDB Configuration Manager
    
    Manages configuration for different deployment profiles
    """
    
    # Profile configurations
    PROFILES: Dict[DeploymentProfile, Dict[str, Any]] = {
        
        # Profile 1: Pure P2P (Zero Servers) ⭐ RECOMMENDED FOR STARTING
        DeploymentProfile.PURE_P2P: {
            "name": "Pure P2P (Zero Servers)",
            "description": "100% free, zero maintenance, perfect for development and personal use",
            "cost": "$0/month",
            "maintenance": "None",
            
            # XRPL
            "use_xrpl_testnet": True,
            "xrpl_nodes": [
                "https://testnet.xrpl-labs.com",
                "https://s.altnet.rippletest.net:51234"
            ],
            
            # CalorieDB
            "caloriedb_enabled": True,
            "caloriedb_local_only": True,
            "decentralized_mode": False,
            
            # Storage
            "ipfs_enabled": False,
            "bigchaindb_enabled": False,
            
            # Sync
            "xrpl_sync_enabled": True,
            "xrpl_sync_interval": 60,
            
            # Privacy
            "allow_public_contributions": False,
            "anonymization_level": "strict",
            
            # FoodRepo
            "foodrepo_enabled": True,
            "foodrepo_use_cache": True,
            
            # Features
            "features": {
                "food_tracking": True,
                "barcode_scanning": True,
                "xrpl_transactions": True,
                "calorie_tokens": True,
                "encrypted_storage": True,
                "public_data": False,
                "ipfs_storage": False,
                "bigchaindb_records": False
            }
        },
        
        # Profile 2: With IPFS (Free)
        DeploymentProfile.WITH_IPFS: {
            "name": "With IPFS (Free)",
            "description": "Add decentralized storage with public IPFS gateways or Pinata free tier",
            "cost": "$0-15/month (optional Pinata)",
            "maintenance": "Minimal (one-time IPFS setup)",
            
            # XRPL
            "use_xrpl_testnet": True,
            "xrpl_nodes": [
                "https://testnet.xrpl-labs.com",
                "https://s.altnet.rippletest.net:51234"
            ],
            
            # CalorieDB
            "caloriedb_enabled": True,
            "caloriedb_local_only": False,
            "decentralized_mode": True,
            
            # Storage
            "ipfs_enabled": True,
            "ipfs_use_public_gateway": True,
            "ipfs_gateway_url": "https://ipfs.io/ipfs/",
            "ipfs_api_url": None,  # Use public gateway, no local daemon
            "bigchaindb_enabled": False,
            
            # Sync
            "xrpl_sync_enabled": True,
            "xrpl_sync_interval": 60,
            
            # Privacy
            "allow_public_contributions": True,
            "anonymization_level": "strict",
            
            # FoodRepo
            "foodrepo_enabled": True,
            "foodrepo_use_cache": True,
            
            # Features
            "features": {
                "food_tracking": True,
                "barcode_scanning": True,
                "xrpl_transactions": True,
                "calorie_tokens": True,
                "encrypted_storage": True,
                "public_data": True,
                "ipfs_storage": True,
                "bigchaindb_records": False,
                "product_image_ipfs": True
            }
        },
        
        # Profile 3: Full Decentralized
        DeploymentProfile.FULL_DECENTRALIZED: {
            "name": "Full Decentralized",
            "description": "IPFS + BigchainDB for complete decentralization",
            "cost": "$0-15/month",
            "maintenance": "Minimal (IPFS + public BigchainDB)",
            
            # XRPL
            "use_xrpl_testnet": True,
            "xrpl_nodes": [
                "https://testnet.xrpl-labs.com",
                "https://s.altnet.rippletest.net:51234"
            ],
            
            # CalorieDB
            "caloriedb_enabled": True,
            "caloriedb_local_only": False,
            "decentralized_mode": True,
            
            # Storage
            "ipfs_enabled": True,
            "ipfs_use_public_gateway": False,
            "ipfs_api_url": "http://127.0.0.1:5001",  # Local IPFS daemon
            "ipfs_gateway_url": "https://ipfs.io/ipfs/",
            "bigchaindb_enabled": True,
            "bigchaindb_api_url": "https://test.bigchaindb.com/api/v1/",
            
            # Sync
            "xrpl_sync_enabled": True,
            "xrpl_sync_interval": 30,  # Faster sync
            
            # Privacy
            "allow_public_contributions": True,
            "anonymization_level": "moderate",
            
            # FoodRepo
            "foodrepo_enabled": True,
            "foodrepo_use_cache": True,
            
            # Features
            "features": {
                "food_tracking": True,
                "barcode_scanning": True,
                "xrpl_transactions": True,
                "calorie_tokens": True,
                "encrypted_storage": True,
                "public_data": True,
                "ipfs_storage": True,
                "bigchaindb_records": True,
                "product_image_ipfs": True,
                "immutable_records": True
            }
        },
        
        # Profile 4: Production Mainnet
        DeploymentProfile.PRODUCTION_MAINNET: {
            "name": "Production Mainnet",
            "description": "Real XRPL mainnet with real money - use when ready to launch",
            "cost": "$0-50/month (depends on IPFS/BigchainDB usage)",
            "maintenance": "Low (optional paid services)",
            
            # XRPL - MAINNET!
            "use_xrpl_testnet": False,
            "xrpl_nodes": [
                "https://xrplcluster.com",
                "https://xrpl.ws",
                "https://s1.ripple.com:51234"
            ],
            
            # CalorieDB
            "caloriedb_enabled": True,
            "caloriedb_local_only": False,
            "decentralized_mode": True,
            
            # Storage
            "ipfs_enabled": True,
            "ipfs_use_pinata": True,  # Paid IPFS pinning service
            "ipfs_gateway_url": "https://gateway.pinata.cloud/ipfs/",
            "bigchaindb_enabled": True,
            "bigchaindb_api_url": "https://bigchaindb.com/api/v1/",  # Production BigchainDB
            
            # Sync
            "xrpl_sync_enabled": True,
            "xrpl_sync_interval": 15,  # Real-time sync
            
            # Privacy
            "allow_public_contributions": True,
            "anonymization_level": "strict",
            
            # FoodRepo
            "foodrepo_enabled": True,
            "foodrepo_use_cache": True,
            
            # Features
            "features": {
                "food_tracking": True,
                "barcode_scanning": True,
                "xrpl_transactions": True,
                "calorie_tokens": True,
                "encrypted_storage": True,
                "public_data": True,
                "ipfs_storage": True,
                "bigchaindb_records": True,
                "product_image_ipfs": True,
                "immutable_records": True,
                "real_money": True,
                "production_grade": True
            }
        },
        
        # Profile 5: Enterprise/Research
        DeploymentProfile.ENTERPRISE: {
            "name": "Enterprise/Research",
            "description": "Full analytics stack for research institutions or enterprise deployment",
            "cost": "$50-200/month (depends on data volume)",
            "maintenance": "Medium (analytics infrastructure)",
            
            # XRPL
            "use_xrpl_testnet": False,  # Can use mainnet or testnet
            "xrpl_nodes": [
                "https://xrplcluster.com",
                "https://xrpl.ws"
            ],
            
            # CalorieDB
            "caloriedb_enabled": True,
            "caloriedb_local_only": False,
            "decentralized_mode": True,
            
            # Storage
            "ipfs_enabled": True,
            "ipfs_use_pinata": True,
            "ipfs_gateway_url": "https://gateway.pinata.cloud/ipfs/",
            "bigchaindb_enabled": True,
            "bigchaindb_api_url": "https://bigchaindb.com/api/v1/",
            
            # Advanced storage
            "elasticsearch_enabled": True,
            "elasticsearch_url": "http://localhost:9200",
            "postgresql_enabled": True,
            "postgresql_url": "postgresql://localhost/caloriedb",
            
            # Sync
            "xrpl_sync_enabled": True,
            "xrpl_sync_interval": 10,  # High-frequency sync
            
            # Privacy
            "allow_public_contributions": True,
            "anonymization_level": "moderate",  # Research needs data
            
            # FoodRepo
            "foodrepo_enabled": True,
            "foodrepo_use_cache": True,
            "foodrepo_bulk_import": True,
            
            # Analytics
            "analytics_enabled": True,
            "machine_learning_enabled": True,
            "data_export_enabled": True,
            
            # Features
            "features": {
                "food_tracking": True,
                "barcode_scanning": True,
                "xrpl_transactions": True,
                "calorie_tokens": True,
                "encrypted_storage": True,
                "public_data": True,
                "ipfs_storage": True,
                "bigchaindb_records": True,
                "product_image_ipfs": True,
                "immutable_records": True,
                "real_money": True,
                "production_grade": True,
                "advanced_analytics": True,
                "machine_learning": True,
                "data_export": True,
                "research_tools": True,
                "bulk_operations": True,
                "api_access": True
            }
        }
    }
    
    def __init__(self, profile: DeploymentProfile = DeploymentProfile.PURE_P2P):
        """
        Initialize configuration with profile
        
        Args:
            profile: Deployment profile to use
        """
        self.profile = profile
        self.config = self.PROFILES[profile].copy()
        self._load_from_env()
    
    def _load_from_env(self):
        """Load configuration from environment variables (overrides profile)"""
        env_mappings = {
            "use_xrpl_testnet": ("XRPL_TESTNET", lambda x: x == "1"),
            "caloriedb_enabled": ("CALORIEDB_ENABLED", lambda x: x == "1"),
            "ipfs_enabled": ("IPFS_ENABLED", lambda x: x == "1"),
            "bigchaindb_enabled": ("BIGCHAINDB_ENABLED", lambda x: x == "1"),
            "xrpl_sync_interval": ("XRPL_SYNC_INTERVAL", int),
            "foodrepo_api_key": ("FOODREPO_API_KEY", str),
            "ipfs_api_url": ("IPFS_API_URL", str),
            "bigchaindb_api_url": ("BIGCHAINDB_API_URL", str),
        }
        
        for config_key, (env_key, converter) in env_mappings.items():
            env_value = os.environ.get(env_key)
            if env_value:
                try:
                    self.config[config_key] = converter(env_value)
                except:
                    pass
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value"""
        return self.config.get(key, default)
    
    def set(self, key: str, value: Any):
        """Set configuration value"""
        self.config[key] = value
    
    def is_feature_enabled(self, feature: str) -> bool:
        """Check if feature is enabled"""
        return self.config.get("features", {}).get(feature, False)
    
    def get_profile_info(self) -> Dict[str, str]:
        """Get profile information"""
        return {
            "profile": self.profile.value,
            "name": self.config["name"],
            "description": self.config["description"],
            "cost": self.config["cost"],
            "maintenance": self.config["maintenance"]
        }
    
    def save_to_file(self, filepath: Optional[Path] = None):
        """
        Save configuration to file
        
        Args:
            filepath: Path to save config (default: config/caloriedb_profile.json)
        """
        import json
        
        if filepath is None:
            filepath = Path("config/caloriedb_profile.json")
        
        filepath.parent.mkdir(parents=True, exist_ok=True)
        
        save_data = {
            "profile": self.profile.value,
            "config": self.config
        }
        
        filepath.write_text(json.dumps(save_data, indent=2))
    
    @classmethod
    def load_from_file(cls, filepath: Optional[Path] = None) -> "CalorieDBConfig":
        """
        Load configuration from file
        
        Args:
            filepath: Path to config file
            
        Returns:
            CalorieDBConfig instance
        """
        import json
        
        if filepath is None:
            filepath = Path("config/caloriedb_profile.json")
        
        if not filepath.exists():
            return cls()  # Return default profile
        
        data = json.loads(filepath.read_text())
        profile = DeploymentProfile(data["profile"])
        
        return cls(profile)
    
    def generate_env_file(self, filepath: Optional[Path] = None):
        """
        Generate .env file from configuration
        
        Args:
            filepath: Path to save .env (default: .env)
        """
        if filepath is None:
            filepath = Path(".env")
        
        lines = [
            f"# CalorieDB Configuration - {self.config['name']}",
            f"# {self.config['description']}",
            f"# Cost: {self.config['cost']}",
            f"# Maintenance: {self.config['maintenance']}",
            "",
            "# Profile",
            f"CALORIEDB_PROFILE={self.profile.value}",
            "",
            "# XRPL Configuration",
            f"XRPL_TESTNET={'1' if self.config['use_xrpl_testnet'] else '0'}",
            f"XRPL_NODES={','.join(self.config.get('xrpl_nodes', []))}",
            "",
            "# CalorieDB Configuration",
            f"CALORIEDB_ENABLED={'1' if self.config['caloriedb_enabled'] else '0'}",
            f"CALORIEDB_LOCAL_ONLY={'1' if self.config.get('caloriedb_local_only', True) else '0'}",
            f"DECENTRALIZED_MODE={'1' if self.config.get('decentralized_mode', False) else '0'}",
            "",
            "# Storage",
            f"IPFS_ENABLED={'1' if self.config.get('ipfs_enabled', False) else '0'}",
        ]
        
        if self.config.get("ipfs_enabled"):
            lines.extend([
                f"IPFS_API_URL={self.config.get('ipfs_api_url', '')}",
                f"IPFS_GATEWAY_URL={self.config.get('ipfs_gateway_url', '')}",
            ])
        
        lines.extend([
            f"BIGCHAINDB_ENABLED={'1' if self.config.get('bigchaindb_enabled', False) else '0'}",
        ])
        
        if self.config.get("bigchaindb_enabled"):
            lines.append(f"BIGCHAINDB_API_URL={self.config.get('bigchaindb_api_url', '')}")
        
        lines.extend([
            "",
            "# Sync Configuration",
            f"XRPL_SYNC_ENABLED={'1' if self.config.get('xrpl_sync_enabled', True) else '0'}",
            f"XRPL_SYNC_INTERVAL={self.config.get('xrpl_sync_interval', 60)}",
            "",
            "# Privacy Settings",
            f"CALORIEDB_ALLOW_PUBLIC_CONTRIBUTIONS={'1' if self.config.get('allow_public_contributions', False) else '0'}",
            f"CALORIEDB_ANONYMIZATION_LEVEL={self.config.get('anonymization_level', 'strict')}",
            "",
            "# FoodRepo API",
            "FOODREPO_API_KEY=your_api_key_here",
            "",
            "# ⚠️ DO NOT COMMIT THIS FILE TO GIT ⚠️",
        ])
        
        filepath.write_text('\n'.join(lines))


# Convenience functions
def get_config(profile: Optional[DeploymentProfile] = None) -> CalorieDBConfig:
    """
    Get CalorieDB configuration
    
    Args:
        profile: Deployment profile (None = auto-detect from env or file)
        
    Returns:
        CalorieDBConfig instance
    """
    if profile:
        return CalorieDBConfig(profile)
    
    # Try loading from file
    try:
        return CalorieDBConfig.load_from_file()
    except:
        pass
    
    # Check environment variable
    profile_name = os.environ.get("CALORIEDB_PROFILE", "pure_p2p")
    try:
        profile = DeploymentProfile(profile_name)
        return CalorieDBConfig(profile)
    except:
        return CalorieDBConfig()  # Default to pure_p2p


def print_profile_comparison():
    """Print comparison of all profiles"""
    print("\n" + "="*80)
    print("CalorieDB Deployment Profiles Comparison")
    print("="*80 + "\n")
    
    for profile in DeploymentProfile:
        config = CalorieDBConfig(profile)
        info = config.get_profile_info()
        
        print(f"📦 {info['name']}")
        print(f"   {info['description']}")
        print(f"   💰 Cost: {info['cost']}")
        print(f"   🔧 Maintenance: {info['maintenance']}")
        print(f"   Features: {len([f for f, enabled in config.config['features'].items() if enabled])}")
        print()


__all__ = [
    "CalorieDBConfig",
    "DeploymentProfile",
    "get_config",
    "print_profile_comparison"
]
