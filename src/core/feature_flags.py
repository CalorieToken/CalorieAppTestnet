"""Centralized feature flags for deferred/experimental components.

Flags gate visibility and import of modules that are not part of the
current beta production surface. Each flag MUST default to False.

Contributing:
 - Add new flags here for any feature not ready for release.
 - Guard screen registration, menu items, and actions using these flags.
 - Do not perform side effects at import time.
"""
import os

# Deferred screens / modules (respect environment overrides for testing)
ENABLE_WEB3_BROWSER = os.environ.get("ENABLE_WEB3_BROWSER", "0").lower() in ("1", "true", "yes")
ENABLE_CALORIE_DB = os.environ.get("ENABLE_CALORIE_DB", "0").lower() in ("1", "true", "yes")

def is_enabled(name: str) -> bool:
    return {
        "web3_browser": ENABLE_WEB3_BROWSER,
        "calorie_db": ENABLE_CALORIE_DB,
    }.get(name, False)
