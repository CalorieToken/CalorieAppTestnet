"""
Token Configuration System
==========================
This module provides a flexible configuration system for managing test tokens.
New tokens can be easily added by updating the TOKENS dictionary.
"""

# Token configuration dictionary
# Add new tokens here with their details
TOKENS = {
    # Example token configuration structure:
    # "token_id": {
    #     "name": "Token Display Name",
    #     "currency_code": "Hex currency code for XRPL",
    #     "issuer": "XRPL issuer address",
    #     "default_limit": "Default trustline limit",
    #     "active": True/False  # Set to False to disable
    # }
    # Add new tokens below (examples commented out):
    # "custom_token": {
    #     "name": "CustomToken",
    #     "currency_code": "437573746F6D546F6B656E00000000000000000000",
    #     "issuer": "rYourIssuerAddressHere",
    #     "default_limit": "100000000000",
    #     "active": True
    # }
}


def get_active_tokens():
    """Return list of active tokens"""
    return {k: v for k, v in TOKENS.items() if v.get("active", True)}


def get_token_config(token_id):
    """Get configuration for a specific token"""
    return TOKENS.get(token_id)


def get_all_token_ids():
    """Get all token IDs"""
    return list(TOKENS.keys())


def get_active_token_ids():
    """Get active token IDs"""
    return list(get_active_tokens().keys())
